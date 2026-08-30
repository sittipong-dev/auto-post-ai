import os
import subprocess
from moviepy import AudioFileClip
import glob

temp_pattern = 'scratch/male_cute_temp.*'
vid_url = 'https://www.youtube.com/watch?v=Od3XyEUVsmo'

# Clean old temp files if any
for f in glob.glob(temp_pattern):
    os.remove(f)

print(f"Downloading from {vid_url}...")
cmd = [
    'yt-dlp', 
    '-f', '140', 
    '-o', 'scratch/male_cute_temp.%(ext)s',
    vid_url
]

try:
    subprocess.run(cmd, check=True)
    downloaded_files = glob.glob(temp_pattern)
    if downloaded_files:
        temp_file = downloaded_files[0]
        print(f"Trimming audio (120 to 130 seconds) from {temp_file}...")
        clip = AudioFileClip(temp_file).subclipped(120, 130)
        out_path = 'assets/voices/male_cute.wav'
        if os.path.exists(out_path):
            os.remove(out_path)
        clip.write_audiofile(out_path, logger=None)
        clip.close()
        os.remove(temp_file)
        print("? Successfully created male_cute.wav")
except Exception as e:
    print(f"? Failed: {e}")
