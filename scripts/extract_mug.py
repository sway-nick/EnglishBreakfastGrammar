import os
from PIL import Image, ImageFilter
import numpy as np

def extract_mug():
    src_path = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5/.user_uploaded/media_1790961333546.jpg'
    img = Image.open(src_path).convert('RGBA')
    arr = np.array(img, dtype=np.float32)
    
    # Background color estimate from corners and margins
    # Corners are around [244, 228, 196]
    bg_r = arr[:, :, 0]
    bg_g = arr[:, :, 1]
    bg_b = arr[:, :, 2]
    
    # Color distance to parchment cream
    # Parchment typically: R~240-255, G~225-245, B~190-215
    # The mug interior/wood is dark brown (R<150, G<100, B<70), iron bands (dark grey/black R<80),
    # foam (creamy white with highlights R>250, G>240, B>220, but with dark outline).
    # All outer boundaries of the mug and foam have a crisp dark ink outline (R<80, G<60, B<40)!
    # Let's use flood fill from the borders to find the outside background.
    
    h, w, _ = arr.shape
    
    # We can use PIL's flood fill or BFS from image boundary
    from collections import deque
    
    # Binary mask: 1 = background, 0 = foreground
    # A pixel is considered potential background if it matches the parchment tone and is outside the mug dark contour
    # Let's inspect the RGB distance from parchment background:
    # Parchment reference: (244, 228, 196)
    # Ink outlines: dark (brightness < 120)
    
    # Let's check brightness
    luminance = 0.299 * bg_r + 0.587 * bg_g + 0.114 * bg_b
    
    # Seed flood fill from the four borders
    visited = np.zeros((h, w), dtype=bool)
    is_bg = np.zeros((h, w), dtype=bool)
    
    # Parchment background detector:
    # A pixel is background if:
    # 1) Its luminance is > 185
    # 2) It is warm-toned: R >= G and G >= B and (R - B) between 20 and 70
    # 3) Not inside the foam (foam is surrounded by dark ink outline)
    
    # Queue for BFS
    queue = deque()
    
    # Add border pixels that are parchment
    for y in range(h):
        for x in [0, 1, w-2, w-1]:
            queue.append((y, x))
            visited[y, x] = True
            is_bg[y, x] = True
            
    for x in range(w):
        for y in [0, 1, h-2, h-1]:
            if not visited[y, x]:
                queue.append((y, x))
                visited[y, x] = True
                is_bg[y, x] = True
                
    # BFS flood fill
    # Stop when hitting the dark contour of the mug/foam/decorations
    # Dark contour or distinct wood/hop colors have luminance < 165 or color difference
    while queue:
        cy, cx = queue.popleft()
        
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                visited[ny, nx] = True
                
                # Check if this neighbor is background parchment:
                r, g, b = arr[ny, nx, :3]
                lum = 0.299*r + 0.587*g + 0.114*b
                
                # Parchment criteria: light background, not dark ink line
                # The ink outlines of foam and mug have lum < 155
                # Hop leaves/lines also have dark outlines
                # Background parchment has lum > 175 and (r > 200 and b > 150)
                if lum > 170 and r > 195 and g > 175 and b > 140:
                    is_bg[ny, nx] = True
                    queue.append((ny, nx))

    # Also handle the hole inside the handle!
    # Inside the handle is also parchment background surrounded by handle wood
    # Let's find handle center (~x=700, y=470)
    for y in range(250, 650):
        for x in range(630, 770):
            r, g, b = arr[y, x, :3]
            lum = 0.299*r + 0.587*g + 0.114*b
            if lum > 185 and r > 210 and g > 190 and b > 160:
                if not visited[y, x]:
                    # Start BFS for handle interior hole
                    h_queue = deque([(y, x)])
                    visited[y, x] = True
                    is_bg[y, x] = True
                    while h_queue:
                        hy, hx = h_queue.popleft()
                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            hny, hnx = hy + dy, hx + dx
                            if 200 <= hny < 700 and 600 <= hnx < 800 and not visited[hny, hnx]:
                                visited[hny, hnx] = True
                                hr, hg, hb = arr[hny, hnx, :3]
                                hlum = 0.299*hr + 0.587*hg + 0.114*hb
                                if hlum > 170 and hr > 195 and hg > 175 and hb > 140:
                                    is_bg[hny, hnx] = True
                                    h_queue.append((hny, hnx))
                                    
    # Generate clean alpha channel
    alpha = np.where(is_bg, 0, 255).astype(np.uint8)
    
    # Create mask image and smooth edge slightly (1px antialiasing)
    mask_img = Image.fromarray(alpha, mode='L')
    
    # Find bounding box of foreground (mug itself)
    # Let's crop tight to the mug
    # We want the mug + foam + handle. The bottom decorations/lines can either be kept or cleanly cropped.
    bbox = mask_img.getbbox()
    print('Bounding box:', bbox)
    
    # Apply alpha
    img.putalpha(mask_img)
    cropped = img.crop(bbox)
    
    out_dir = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5'
    out_path = os.path.join(out_dir, 'mug_transparent.png')
    cropped.save(out_path, format='PNG')
    print('Saved transparent cropped mug to:', out_path)

if __name__ == '__main__':
    extract_mug()
