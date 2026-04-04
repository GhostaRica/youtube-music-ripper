import os
import re
import shutil
from tempfile import TemporaryDirectory

from yt_dlp import YoutubeDL, DownloadError
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3

from Modules.config import CONFIG
from classes.exceptions import PlaylistNotFoundError, PrivatePlaylistError, UnknownPlaylistError
from classes.music import Album, AlbumType, Song

# TODO We should probably somehow provide information of progress to the menu
def get_youtube_playlist(playlist_id) -> Album:
    """Get an Album from youtube with a playlist_id"""

    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {
        'extract_flat': False,
        'no_warnings': True,
        'quiet': True,
    }

    album = Album()
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(playlist_url, download=False)
        except DownloadError as e:
            error_msg = str(e).lower()
            if "404" in error_msg or "video unavailable" in error_msg:
                raise PlaylistNotFoundError(playlist_id) from e
            elif "private" in error_msg or "sign in" in error_msg:
                raise PrivatePlaylistError(playlist_id) from e
            else:
                raise UnknownPlaylistError(f"Unknown error occurred: {e}") from e

        entries = info["entries"]
        album.name = re.sub(r'(?i)^album\s*-\s*', '', info.get('title')).strip()
        album.cover_url = entries[0]["thumbnails"][-1]["url"]
        album.type = AlbumType.ALBUM if info["playlist_count"] > 1 else AlbumType.SINGLE

        for index, entry in enumerate(entries, start=1):
            song = Song()
            song.video_id = entry.get("id")
            song.title = entry.get("title")
            song.artists = list(dict.fromkeys(entry.get("artists", [])))
            song.duration = entry.get("duration")
            song.year = entry.get("release_year")
            song.track_number = index
            album.add_song(song)

        first_entry = entries[0]
        first_artist_list = list(dict.fromkeys(first_entry.get("artists", [])))

        if first_artist_list:
            album.artist = first_artist_list[0]
        else:
            album.artist = first_entry.get("artist") or first_entry.get("uploader")
        return album

def get_youtube_video(video_id) -> Album:
    """Get an Album-like object for a single YouTube video"""

    video_url = f"https://music.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    album = Album()
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

        album.name = re.sub(r'(?i)^album\s*-\s*', '', info.get("title")).strip()
        album.cover_url = info.get("thumbnail")
        album.type = AlbumType.SINGLE

        song = Song()
        song.video_id = video_id
        song.title = info.get("title")
        song.artists = list(dict.fromkeys(info.get("artists", []))) or [info.get("artist") or info.get("uploader")]
        song.duration = info.get("duration")
        song.year = info.get("release_year")

        album.add_song(song)
        album.artist = song.artists[0] if len(song.artists) == 1 else "Various Artists"

        return album

def download_song(song: Song, album_name: str, album_artist: str, album_type: AlbumType, album_cover_path: str):
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
            'extract_flat': False,
            'no_warnings': True,
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

        if CONFIG.group_by_album and album_type != AlbumType.SINGLE:
            raw_album_name = album_name
            album_name = sanitize_filename(raw_album_name)
            final_dir = os.path.join(final_dir, album_name)

        os.makedirs(final_dir, exist_ok=True)
        title = sanitize_filename(song.title)
        final_dir = os.path.join(final_dir, f"{title}.mp3")

        shutil.move(mp3_path, final_dir)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)
