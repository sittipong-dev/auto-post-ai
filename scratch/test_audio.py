from moviepy import AudioFileClip, CompositeAudioClip
try:
    from moviepy import afx
    print('afx available')
except:
    print('no afx')
