import os
import re
import shutil
from tempfile import TemporaryDirectory

from yt_dlp import YoutubeDL
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3

from Modules.config import CONFIG
from classes.exceptions import PlaylistDoesNotExist, VideoDoesNotExist
from classes.music import Album, AlbumType, Song

# TODO We should probably somehow provide information of progress to the menu
async def get_youtube_playlist(playlist_id) -> Album:
    """Get an Album from youtube with a playlist_id"""

    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {
        'extract_flat': False,
        'quiet': True,
    }

    album = Album()
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        entries = info["entries"]

        raw_album_name = info.get('title')
        album.name = re.sub(r'(?i)^album\s*-\s*', '', raw_album_name).strip()

        album.cover_url = entries[0]["thumbnails"][-1]["url"]

        album.type = AlbumType.ALBUM if info["playlist_count"] > 1 else AlbumType.SINGLE

        album_artists = set()
        for index, entry in enumerate(entries, start=1):
            song = Song()
            song.video_id = entry.get("id")
            song.title = entry.get("title")
            song.artists = list(dict.fromkeys(entry["artists"]))
            song.duration = entry.get("duration")
            song.year = entry.get("release_year")
            song.track_number = index
            album.add_song(song)

            album_artists.add(entry.get('artist') or entry.get('uploader'))

        if len(album_artists) == 1:
            album.artist = album_artists.pop()
        else:
            album.artist = "Various Artists"

        return album

def get_youtube_video() -> Album:
    pass

def download_song(song: Song, album_name: str, album_artist: str, album_cover_path: str):
    with TemporaryDirectory() as temp_dir:
        url = f"https://www.youtube.com/watch?v={song.video_id}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'quiet': True,
            'noprogress': True,
            'ignoreerrors': True,
            'noplaylist': True,
            'extract_flat': False
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_path = os.path.join(temp_dir, f"{song.video_id}.mp3")

        audio = EasyID3(mp3_path)
        audio['title'] = song.title
        audio['artist'] = ", ".join(song.artists)
        audio['date'] = str(song.year)
        audio['tracknumber'] = str(song.track_number)

        audio['album'] = album_name
        audio['albumartist'] = album_artist
        audio.save()

        audio = ID3(mp3_path)
        with open(album_cover_path, 'rb') as img:
            audio.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img.read()
            ))
        audio.save()

        final_dir = CONFIG.download_dir

        if CONFIG.group_by_artist:
            raw_album_artist = album_artist
            album_artist = sanitize_filename(raw_album_artist)
            final_dir = os.path.join(CONFIG.download_dir, album_artist)

        if CONFIG.group_by_album:
            raw_album_name = album_name
            album_name = sanitize_filename(raw_album_name)
            final_dir = os.path.join(final_dir, album_name)

        os.makedirs(final_dir, exist_ok=True)
        title = sanitize_filename(song.title)
        final_dir = os.path.join(final_dir, f"{title}.mp3")

        shutil.move(mp3_path, final_dir)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)
