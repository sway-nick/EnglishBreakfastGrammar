import os
import sys, io
from PIL import Image, ImageFilter
import numpy as np
from collections import deque

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def process_and_cut_cards():
    src_path = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5/.user_uploaded/media_1790950358626.jpg'
    img = Image.open(src_path).convert('RGB')
    src_arr = np.array(img)
    
    # Precise bounding regions in full image (x1, y1, x2, y2)
    # 4 rows x 2 cols
    cards_def = [
        ('card_a1',        (10, 24, 340, 288)),
        ('card_a2',        (350, 24, 682, 288)),
        ('card_b1',        (10, 300, 340, 557)),
        ('card_b1_b2',     (350, 302, 682, 557)),
        ('card_b2',        (10, 552, 340, 797)),
        ('card_c1',        (350, 552, 682, 797)),
        ('card_shorts',    (10, 792, 340, 1024)),
        ('card_favorites', (350, 792, 682, 1024))
    ]
    
    out_dir = 'frontend/assets/cards'
    os.makedirs(out_dir, exist_ok=True)
    
    # Target uniform dimensions for all card images
    TARGET_WIDTH = 650
    TARGET_HEIGHT = 500
    
    processed_results = []
    
    for name, (x1, y1, x2, y2) in cards_def:
        crop_rgb = src_arr[y1:y2, x1:x2].astype(np.float32)
        h, w = crop_rgb.shape[:2]
        
        # Calculate brightness and wood probability
        brightness = 0.299 * crop_rgb[..., 0] + 0.587 * crop_rgb[..., 1] + 0.114 * crop_rgb[..., 2]
        
        # Wood is dark / brown
        # Paper is bright / warm parchment
        # A pixel is definitely wood if brightness < 70 or (R < 80 and G < 55 and B < 45)
        is_wood = (brightness < 68) | ((crop_rgb[..., 0] < 82) & (crop_rgb[..., 1] < 58) & (crop_rgb[..., 2] < 46))
        
        # Flood fill from image boundary to find exterior wood
        bg_mask = np.zeros((h, w), dtype=bool)
        q = deque()
        
        for x in range(w):
            if is_wood[0, x]:
                bg_mask[0, x] = True
                q.append((0, x))
            if is_wood[h-1, x]:
                bg_mask[h-1, x] = True
                q.append((h-1, x))
        for y in range(h):
            if is_wood[y, 0]:
                bg_mask[y, 0] = True
                q.append((y, 0))
            if is_wood[y, w-1]:
                bg_mask[y, w-1] = True
                q.append((y, w-1))
                
        while q:
            cy, cx = q.popleft()
            for ny, nx in ((cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)):
                if 0 <= ny < h and 0 <= nx < w:
                    if not bg_mask[ny, nx] and is_wood[ny, nx]:
                        bg_mask[ny, nx] = True
                        q.append((ny, nx))
                        
        # The paper region is ~bg_mask
        paper_mask = ~bg_mask
        
        # Build RGBA array
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[..., :3] = src_arr[y1:y2, x1:x2]
        rgba[..., 3] = np.where(paper_mask, 255, 0).astype(np.uint8)
        
        # Find tight bounding box of paper
        ys, xs = np.where(paper_mask)
        if len(ys) > 0 and len(xs) > 0:
            top, bottom = ys.min(), ys.max()
            left, right = xs.min(), xs.max()
        else:
            top, bottom, left, right = 0, h-1, 0, w-1
            
        tight_crop = Image.fromarray(rgba).crop((left, top, right + 1, bottom + 1))
        
        # Soft anti-aliased edge: smooth alpha slightly
        alpha_img = tight_crop.getchannel('A')
        # Apply slight blur to alpha for smooth edge blending
        smooth_alpha = alpha_img.filter(ImageFilter.GaussianBlur(radius=0.7))
        # Ensure interior is 100% solid
        smooth_alpha_arr = np.array(smooth_alpha)
        smooth_alpha_arr = np.where(smooth_alpha_arr > 180, 255, smooth_alpha_arr)
        tight_crop.putalpha(Image.fromarray(smooth_alpha_arr))
        
        # Resize uniformly to identical TARGET_WIDTH x TARGET_HEIGHT
        resized_card = tight_crop.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        
        out_path = os.path.join(out_dir, f"{name}.png")
        resized_card.save(out_path, 'PNG', optimize=True)
        
        processed_results.append({
            'name': name,
            'orig_size': (right - left + 1, bottom - top + 1),
            'final_size': resized_card.size,
            'path': out_path
        })
        print(f"✓ {name:15s}: raw paper size={right-left+1}x{bottom-top+1} -> final uniform size={resized_card.size}")
        
    print(f"\nAll 8 cards generated with identical height ({TARGET_HEIGHT}px) and width ({TARGET_WIDTH}px).")

if __name__ == '__main__':
    process_and_cut_cards()
