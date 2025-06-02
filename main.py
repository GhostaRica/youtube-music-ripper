import os
import sys
import re
import requests
import shutil
from tempfile import TemporaryDirectory
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3
from PIL import Image

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_thumbnail(thumbnail_url: str, out_path: str):
    try:
        response = requests.get(thumbnail_url, stream=True)
        if response.ok:
            with open(out_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"📸 Downloaded thumbnail")
        else:
            print(f"⚠️ Failed to download thumbnail: {thumbnail_url}")
    except Exception as e:
        print(f"❌ Error downloading thumbnail: {e}")

def crop_thumbnail_to_square(path: str):
    try:
        img = Image.open(path)
        width, height = img.size
        min_dim = min(width, height)

        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2

        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(path)
        print(f"🖼️ Cropped thumbnail to square")
    except Exception as e:
        print(f"❌ Failed to crop thumbnail: {e}")

def embed_metadata(mp3_path: str, entry: dict):
    try:
        audio = EasyID3(mp3_path)
    except error:
        audio = MP3(mp3_path, ID3=ID3)
        audio.add_tags()
        audio = EasyID3(mp3_path)

    audio['title'] = entry.get('title', 'Unknown Title')
    audio['artist'] = entry.get('artist') or entry.get('uploader', 'Unknown Artist')
    audio['date'] = str(entry.get('release_year', "Unknown Year"))
    audio['tracknumber'] = str(entry.get('playlist_autonumber', '1'))
    if entry.get('album'):
        audio['album'] = entry['album']
        audio['albumartist'] = entry.get('artists')[0]

    audio.save()
    print(f"📝 Embedded metadata")

def embed_thumbnail(mp3_path: str, thumbnail_path: str):
    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        with open(thumbnail_path, 'rb') as img:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img.read()
            ))
        audio.save()
        print(f"✅ Embedded thumbnail into {mp3_path}")
    except Exception as e:
        print(f"❌ Failed to embed thumbnail: {e}")

def youtube_download(url, temp_dir):
    # TODO look into the "post processors" if there isnt a better way for the highest possible quality
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'quiet': False,
        'ignoreerrors': True,
        'extract_flat': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info['entries'] if 'entries' in info else [info]

        # Determine album folder (only if > 1 song)
        is_playlist = len(entries) > 1
        raw_album_name = info.get('title', 'Album')
        clean_album_name = re.sub(r'(?i)^album\s*-\s*', '', raw_album_name).strip()
        album_name = sanitize_filename(clean_album_name) if is_playlist else ""

        album_path = os.path.join(DOWNLOAD_DIR, album_name) if is_playlist else DOWNLOAD_DIR
        os.makedirs(album_path, exist_ok=True)

        for entry in entries:
            if entry is None:
                continue

            title = sanitize_filename(entry['title'])
            mp3_file_temp = os.path.join(temp_dir, f"{entry.get('id')}.mp3")
            thumbnail_url = entry.get('thumbnail')

            print(f"🎵 Downloading: {title}")
            ydl.download([entry['webpage_url']])

            if thumbnail_url:
                thumbnail_path = os.path.join(temp_dir, f"{entry.get('id')}_thumb.jpg")
                download_thumbnail(thumbnail_url, thumbnail_path)
                crop_thumbnail_to_square(thumbnail_path)
                embed_thumbnail(mp3_file_temp, thumbnail_path)
                os.remove(thumbnail_path)
            
            embed_metadata(mp3_file_temp, entry)

            final_path = os.path.join(album_path, f"{title}.mp3")
            shutil.move(mp3_file_temp, final_path)
            print(f"📁 Moved to {final_path}")

def main():
    # Make sure an URL is passed
    if len(sys.argv) != 2:
        print("Usage: python main.py <YouTube Video or Playlist URL>")
        return
    
    # Do a regex check for valid youtube urls 
    pattern = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|music\.youtube\.com|youtu\.be)/'
    r'((watch\?v=|playlist\?list=|embed/|shorts/)?[A-Za-z0-9_\-]{11,}|playlist\?list=[A-Za-z0-9_\-]+)')

    if not pattern.match(sys.argv[1]):
        print("\033[1;31mERROR:\033[0m Invalid YouTube or YouTube Music URL")
        return 
    
    # We create a temporary folder where the downloaded mp3 and album cover will be stored until everything is combined at the end
    with TemporaryDirectory() as temp_dir:
        try:
            youtube_download(sys.argv[1], temp_dir)
        except:
            print("\033[1;31mERROR:\033[0m An exception occurred while trying to download the song")

if __name__ == "__main__":
    main()
