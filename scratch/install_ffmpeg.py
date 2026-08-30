import urllib.request
import zipfile
import os
import shutil

url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
zip_path = "scratch/ffmpeg.zip"
extract_dir = "scratch/ffmpeg_extracted"
target_dir = "C:/ffmpeg"

print("Downloading FFmpeg shared build...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Find the bin directory
bin_dir = None
for root, dirs, files in os.walk(extract_dir):
    if "bin" in dirs and "ffmpeg.exe" in os.listdir(os.path.join(root, "bin")):
        bin_dir = os.path.join(root, "bin")
        break

if bin_dir:
    print(f"Found bin directory: {bin_dir}")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy all files from bin_dir to target_dir
    for item in os.listdir(bin_dir):
        s = os.path.join(bin_dir, item)
        d = os.path.join(target_dir, item)
        shutil.copy2(s, d)
        
    print(f"? FFmpeg copied to {target_dir}")
    print("Please add C:\\ffmpeg to your system PATH.")
else:
    print("? Could not find bin directory in extracted files.")
