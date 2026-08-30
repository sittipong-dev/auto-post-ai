import os
import subprocess
from moviepy import AudioFileClip

voices = {
    'female_formal': '6I29pPubiW0',  # 5 min news
    'male_deep': 'kL1819NMiKo',      # 50 min podcast
    'female_cute': 'nhpb1owQxGw'     # 10 min vlog
}

for name, vid in voices.items():
    print(f"Downloading {name}...")
    temp_file = f'scratch/{name}_temp.m4a'
    
    # Download full audio (yt-dlp can do this without ffmpeg if we just grab the format directly)
    cmd = [
        'yt-dlp', 
        '-f', '140', 
        '-o', temp_file,
        f'https://www.youtube.com/watch?v={vid}'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        # Convert to wav using moviepy and subclip
        if os.path.exists(temp_file):
            clip = AudioFileClip(temp_file).subclipped(60, 70)
            clip.write_audiofile(f'assets/voices/{name}.wav', logger=None)
            clip.close()
            os.remove(temp_file)
            print(f"? Created {name}.wav")
    except Exception as e:
        print(f"? Failed for {name}: {e}")

