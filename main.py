import os
import sys
import re
import requests
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3

# Output folder
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_thumbnail(thumbnail_url: str, out_path: str):
    response = requests.get(thumbnail_url, stream=True)
    if response.ok:
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download thumbnail: {thumbnail_url}")

def embed_thumbnail(mp3_path: str, thumbnail_path: str):
    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        with open(thumbnail_path, 'rb') as img:
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover(front)
                    desc='Cover',
                    data=img.read()
                )
            )
        audio.save()
        print(f"✅ Embedded thumbnail into {mp3_path}")
    except Exception as e:
        print(f"❌ Failed to embed thumbnail: {e}")

def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'quiet': False,
        'extract_flat': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info['entries'] if 'entries' in info else [info]

        for entry in entries:
            if entry is None:
                continue

            title = sanitize_filename(entry['title'])
            mp3_file = os.path.join(DOWNLOAD_DIR, f"{title}.mp3")
            thumbnail_url = entry.get('thumbnail')
            print(f"🎵 Downloading: {title}")
            ydl.download([entry['webpage_url']])

            if thumbnail_url:
                thumbnail_path = os.path.join(DOWNLOAD_DIR, f"{title}_thumb.jpg")
                download_thumbnail(thumbnail_url, thumbnail_path)
                embed_thumbnail(mp3_file, thumbnail_path)
                os.remove(thumbnail_path)

def main():
    if len(sys.argv) != 2:
        print("Usage: python youtube_to_mp3.py <YouTube Video or Playlist URL>")
        return

    url = sys.argv[1]
    download_audio(url)

if __name__ == "__main__":
    main()
