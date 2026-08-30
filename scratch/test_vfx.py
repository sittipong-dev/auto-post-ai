from moviepy import ImageClip, vfx
clip = ImageClip('assets/test.jpg', duration=2) if __import__('os').path.exists('assets/test.jpg') else None
if not clip:
    import numpy as np
    clip = ImageClip(np.zeros((1920, 1080, 3), dtype=np.uint8)).with_duration(2)
try:
    c2 = clip.with_effects([vfx.Resize(lambda t: 1.0 + 0.1 * t)])
    print("vfx.Resize with lambda worked!")
except Exception as e:
    print("Error:", e)
