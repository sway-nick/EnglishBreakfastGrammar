import os
import sys, io
from PIL import Image, ImageFilter
import numpy as np
from collections import deque

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_and_extract_cards():
    src_path = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5/.user_uploaded/media_1790950358626.jpg'
    img = Image.open(src_path).convert('RGB')
    src_arr = np.array(img)
    
    # Strictly isolated bounding regions for each card cell
    # No overlap with neighbor rows or columns
    cards_def = [
        # Row 0 (A1, A2) - Divider below is y=284..304
        ('card_a1',        (12, 26, 338, 284)),
        ('card_a2',        (354, 26, 679, 284)),
        
        # Row 1 (B1, B1+) - Divider above is y=284..304, divider below is y=554..567
        ('card_b1',        (12, 304, 338, 554)),
        ('card_b1_b2',     (354, 304, 679, 554)),
        
        # Row 2 (B2, C1) - Divider above is y=554..567, divider below is y=794..808
        ('card_b2',        (12, 567, 338, 794)),
        ('card_c1',        (354, 567, 679, 794)),
        
        # Row 3 (Shorts, Favorites) - Divider above is y=794..808
        ('card_shorts',    (12, 808, 338, 1024)),
        ('card_favorites', (354, 808, 679, 1024))
    ]
    
    out_dir = 'frontend/assets/cards'
    os.makedirs(out_dir, exist_ok=True)
    
    TARGET_WIDTH = 650
    TARGET_HEIGHT = 500
    
    for name, (x1, y1, x2, y2) in cards_def:
        crop_rgb = src_arr[y1:y2, x1:x2].astype(np.float32)
        h, w = crop_rgb.shape[:2]
        
        brightness = 0.299 * crop_rgb[..., 0] + 0.587 * crop_rgb[..., 1] + 0.114 * crop_rgb[..., 2]
        
        # Wood background detection
        is_wood = (brightness < 70) | ((crop_rgb[..., 0] < 85) & (crop_rgb[..., 1] < 60) & (crop_rgb[..., 2] < 50))
        
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
                        
        paper_mask = ~bg_mask
        
        # Extract connected components of paper_mask to keep ONLY the largest component (the main parchment card)
        # and discard any small isolated debris
        labeled = np.zeros((h, w), dtype=np.int32)
        current_label = 0
        component_sizes = {}
        
        for r in range(h):
            for c in range(w):
                if paper_mask[r, c] and labeled[r, c] == 0:
                    current_label += 1
                    comp_q = deque([(r, c)])
                    labeled[r, c] = current_label
                    size = 0
                    while comp_q:
                        cr, cc = comp_q.popleft()
                        size += 1
                        for nr, nc in ((cr+1, cc), (cr-1, cc), (cr, cc+1), (cr, cc-1)):
                            if 0 <= nr < h and 0 <= nc < w:
                                if paper_mask[nr, nc] and labeled[nr, nc] == 0:
                                    labeled[nr, nc] = current_label
                                    comp_q.append((nr, nc))
                    component_sizes[current_label] = size
                    
        if component_sizes:
            largest_label = max(component_sizes, key=component_sizes.get)
            clean_paper_mask = (labeled == largest_label)
        else:
            clean_paper_mask = paper_mask
            
        # Build clean RGBA image
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[..., :3] = src_arr[y1:y2, x1:x2]
        rgba[..., 3] = np.where(clean_paper_mask, 255, 0).astype(np.uint8)
        
        # Tight crop to clean paper
        ys, xs = np.where(clean_paper_mask)
        if len(ys) > 0 and len(xs) > 0:
            top, bottom = ys.min(), ys.max()
            left, right = xs.min(), xs.max()
        else:
            top, bottom, left, right = 0, h-1, 0, w-1
            
        tight_card = Image.fromarray(rgba).crop((left, top, right + 1, bottom + 1))
        
        # Smooth anti-aliased edge
        alpha_img = tight_card.getchannel('A')
        smooth_alpha = alpha_img.filter(ImageFilter.GaussianBlur(radius=0.6))
        smooth_alpha_arr = np.array(smooth_alpha)
        smooth_alpha_arr = np.where(smooth_alpha_arr > 160, 255, smooth_alpha_arr)
        tight_card.putalpha(Image.fromarray(smooth_alpha_arr))
        
        # Resize uniformly to EXACT TARGET_WIDTH x TARGET_HEIGHT
        final_img = tight_card.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        
        out_path = os.path.join(out_dir, f"{name}.png")
        final_img.save(out_path, 'PNG', optimize=True)
        print(f"✓ {name:15s}: paper tight = {right-left+1}x{bottom-top+1} -> uniform = {final_img.size}")
        
    print(f"\nAll 8 cards cleaned of all artifacts and normalized to {TARGET_WIDTH}x{TARGET_HEIGHT}px.")

if __name__ == '__main__':
    clean_and_extract_cards()
