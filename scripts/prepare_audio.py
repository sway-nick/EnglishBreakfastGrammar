import os
import sys, io
import soundfile as sf
import numpy as np
import lameenc

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def prepare_intro_audio():
    src_path = r'C:/Users/user/.gemini/antigravity/brain/50a1383d-6d8f-434e-99c6-90c7eea9b4d5/.user_uploaded/uploaded_media_1790952437913.mp3'
    if not os.path.exists(src_path):
        print(f"Error: Source file not found at {src_path}")
        return
        
    print(f"Reading source audio: {src_path}...")
    data, sr = sf.read(src_path)
    orig_duration = len(data) / sr
    
    # Detect silence / empty tail at the end
    mono = np.abs(data).max(axis=1) if data.ndim > 1 else np.abs(data)
    threshold = 0.002 # -54 dB threshold
    
    above_indices = np.where(mono > threshold)[0]
    last_idx = above_indices[-1] if len(above_indices) > 0 else len(mono)
    
    # Keep 0.6s tail for natural acoustic reverb decay
    end_idx = min(last_idx + int(0.6 * sr), len(data))
    trimmed = data[:end_idx].copy()
    new_duration = len(trimmed) / sr
    
    # Apply smooth cosine fade-out over the final 0.8s
    fade_len = int(0.8 * sr)
    fade_curve = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, fade_len)))
    if trimmed.ndim > 1:
        trimmed[-fade_len:, 0] *= fade_curve
        trimmed[-fade_len:, 1] *= fade_curve
    else:
        trimmed[-fade_len:] *= fade_curve
        
    # Convert float32 [-1.0, 1.0] to int16 for LAME
    int16_data = np.clip(trimmed * 32767, -32768, 32767).astype(np.int16)
    
    # Encode with LAME MP3 encoder at 96 kbps high quality joint stereo
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(96)
    encoder.set_in_sample_rate(sr)
    encoder.set_channels(2 if trimmed.ndim > 1 else 1)
    encoder.set_quality(2) # 2 = High quality LAME encoding
    
    mp3_bytes = encoder.encode(int16_data.tobytes())
    mp3_bytes += encoder.flush()
    
    # Save to frontend and root assets
    targets = [
        'frontend/assets/audio/intro_theme.mp3',
        'assets/audio/intro_theme.mp3'
    ]
    for t in targets:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        with open(t, 'wb') as f:
            f.write(mp3_bytes)
            
    orig_kb = os.path.getsize(src_path) / 1024
    new_kb = len(mp3_bytes) / 1024
    
    print(f"✓ Audio trimmed from {orig_duration:.2f}s to {new_duration:.2f}s (removed {orig_duration - new_duration:.2f}s of silence).")
    print(f"✓ File compressed from {orig_kb:.1f} KB to {new_kb:.1f} KB (saved {100 - (new_kb/orig_kb*100):.1f}%).")
    print(f"✓ Saved to {targets}")

if __name__ == '__main__':
    prepare_intro_audio()
