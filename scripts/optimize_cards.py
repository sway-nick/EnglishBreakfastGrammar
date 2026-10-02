import os
from PIL import Image

def optimize_cards():
    cards_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'assets', 'cards')
    cards_dir = os.path.abspath(cards_dir)
    
    total_orig = 0
    total_webp = 0
    
    for fname in sorted(os.listdir(cards_dir)):
        if not fname.endswith('.png'):
            continue
        path = os.path.join(cards_dir, fname)
        img = Image.open(path)
        out_webp = os.path.join(cards_dir, fname.replace('.png', '.webp'))
        
        # Save as optimized WebP with alpha preservation
        img.save(out_webp, format='WEBP', quality=85, method=6)
        
        orig_sz = os.path.getsize(path) / 1024
        webp_sz = os.path.getsize(out_webp) / 1024
        total_orig += orig_sz
        total_webp += webp_sz
        print(f"{fname} -> {os.path.basename(out_webp)}: {orig_sz:.1f} KB -> {webp_sz:.1f} KB (-{100 - (webp_sz/orig_sz*100):.1f}%)")
        
    print(f"\nTOTAL SIZE: {total_orig:.1f} KB -> {total_webp:.1f} KB (-{100 - (total_webp/total_orig*100):.1f}%)")

if __name__ == '__main__':
    optimize_cards()
