from moviepy import ColorClip
clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=2)
try:
    from moviepy import vfx
    looped = clip.with_effects([vfx.Loop(duration=5)])
    print('Loop using vfx.Loop success')
except Exception as e:
    print('Error with vfx.Loop:', e)

try:
    looped = clip.loop(duration=5)
    print('Loop using .loop success')
except Exception as e:
    print('Error with .loop:', e)
