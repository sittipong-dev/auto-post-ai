import os
from moviepy import AudioFileClip

orig_path = 'assets/voices/female_cute.wav'
temp_path = 'assets/voices/female_cute_temp.wav'

try:
    if os.path.exists(orig_path):
        print("Loading audio...")
        clip = AudioFileClip(orig_path)
        
        # Cut from second 2.0 to the end
        print("Trimming first 2 seconds...")
        trimmed_clip = clip.subclipped(2.0, clip.duration)
        
        # Save to temp
        trimmed_clip.write_audiofile(temp_path, logger=None)
        
        clip.close()
        trimmed_clip.close()
        
        # Replace original
        os.remove(orig_path)
        os.rename(temp_path, orig_path)
        print("? Successfully trimmed female_cute.wav")
    else:
        print("? File not found.")
except Exception as e:
    print(f"? Failed: {e}")
