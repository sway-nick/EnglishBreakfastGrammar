import os
from PIL import Image, ImageFilter
import numpy as np
from collections import deque

def process_mug():
    src_path = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5/.user_uploaded/media_1790961333546.jpg'
    img = Image.open(src_path).convert('RGBA')
    arr = np.array(img, dtype=np.float32)
    
    h, w, _ = arr.shape
    visited = np.zeros((h, w), dtype=bool)
    is_bg = np.zeros((h, w), dtype=bool)
    
    queue = deque()
    
    # Outer boundaries flood fill
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
                
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                visited[ny, nx] = True
                r, g, b = arr[ny, nx, :3]
                lum = 0.299*r + 0.587*g + 0.114*b
                if lum > 170 and r > 195 and g > 175 and b > 140:
                    is_bg[ny, nx] = True
                    queue.append((ny, nx))

    # Inner handle hole flood fill
    for y in range(250, 650):
        for x in range(630, 770):
            r, g, b = arr[y, x, :3]
            lum = 0.299*r + 0.587*g + 0.114*b
            if lum > 185 and r > 210 and g > 190 and b > 160:
                if not visited[y, x]:
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

    # Remove the thin decorative bottom lines (below y=720 outside the mug barrel base)
    # The mug bottom ends at around y=695..710
    # Let's inspect rows > 705
    for y in range(705, h):
        for x in range(w):
            if y > 705 and (x < 240 or x > 680):
                is_bg[y, x] = True
            if y > 730:
                is_bg[y, x] = True

    # Also clean the tiny curls on left (x<190) and right (x>840)
    for y in range(h):
        for x in range(w):
            if x < 190 and y > 500:
                is_bg[y, x] = True
            if x > 840 and y > 500:
                is_bg[y, x] = True

    alpha = np.where(is_bg, 0, 255).astype(np.uint8)
    mask = Image.fromarray(alpha, mode='L')
    
    # Smooth edges slightly to eliminate jaggies
    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.7))
    # Slight contrast enhancement on mask to keep crisp ink contours
    mask_arr = np.array(mask, dtype=np.float32)
    mask_arr = np.clip((mask_arr - 60) / (200 - 60) * 255.0, 0, 255).astype(np.uint8)
    clean_mask = Image.fromarray(mask_arr, mode='L')
    
    img.putalpha(clean_mask)
    bbox = clean_mask.getbbox()
    cropped = img.crop(bbox)
    
    # Save main cropped mug
    dest_icons = r'frontend/assets/icons'
    os.makedirs(dest_icons, exist_ok=True)
    
    mug_png = os.path.join(dest_icons, 'mug_icon.png')
    mug_webp = os.path.join(dest_icons, 'mug_icon.webp')
    
    cropped.save(mug_png, format='PNG')
    cropped.save(mug_webp, format='WEBP', quality=95)
    print(f'Saved mug to {mug_png} ({cropped.size}) and {mug_webp}')
    
    # Generate square favicon versions (with balanced padding)
    max_dim = max(cropped.size)
    pad_w = int(max_dim * 1.08)
    pad_h = int(max_dim * 1.08)
    sq_img = Image.new('RGBA', (pad_w, pad_h), (0, 0, 0, 0))
    offset_x = (pad_w - cropped.size[0]) // 2
    offset_y = (pad_h - cropped.size[1]) // 2
    sq_img.paste(cropped, (offset_x, offset_y), cropped)
    
    # Favicon sizes: 32x32, 48x48, 64x64, 128x128, 192x192, 512x512
    fav_32 = sq_img.resize((32, 32), Image.Resampling.LANCZOS)
    fav_48 = sq_img.resize((48, 48), Image.Resampling.LANCZOS)
    fav_64 = sq_img.resize((64, 64), Image.Resampling.LANCZOS)
    fav_192 = sq_img.resize((192, 192), Image.Resampling.LANCZOS)
    
    fav_192.save(os.path.join(dest_icons, 'favicon-192.png'), format='PNG')
    fav_64.save(os.path.join(dest_icons, 'favicon-64.png'), format='PNG')
    fav_32.save(os.path.join(dest_icons, 'favicon-32.png'), format='PNG')
    
    # Also save root favicon.png / favicon.ico
    sq_img.resize((64, 64), Image.Resampling.LANCZOS).save(r'frontend/favicon.png', format='PNG')
    
    # Generate SVG wrapper for favicon.svg (embedded Base64 WebP/PNG)
    import base64
    from io import BytesIO
    buf = BytesIO()
    sq_img.resize((128, 128), Image.Resampling.LANCZOS).save(buf, format='PNG')
    b64_str = base64.b64encode(buf.getvalue()).decode('ascii')
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%">
  <image href="data:image/png;base64,{b64_str}" x="0" y="0" width="128" height="128" />
</svg>
'''
    with open(r'frontend/favicon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
        
    print('Favicons generated successfully!')

if __name__ == '__main__':
    process_mug()
