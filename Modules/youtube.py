import asyncio
import aiohttp
import os
import re
import shutil
import requests
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3
from PIL import Image
from tempfile import TemporaryDirectory

from Modules.settings import settings

def youtube_duration_to_seconds(duration:str) -> int:
    days = 0
    match = re.search(r'(\d+)(DT)', duration)
    if match is not None:
        days = int(match.group(1))

    hours = 0
    match = re.search(r'(\d+)(H)', duration)
    if match is not None:
        hours = int(match.group(1))

    minutes = 0
    match = re.search(r'(\d+)(M)', duration)
    if match is not None:
        minutes = int(match.group(1))

    seconds = 0
    match = re.search(r'(\d+)(S)', duration)
    if match is not None:
        seconds = int(match.group(1))

    return (days * 86400) + (hours * 3600) + (minutes * 60) + seconds

def get_youtube_playlist(playlist_id):
    video_id_list = []

    params = { "part": "contentDetails,snippet", "id": playlist_id, "key": settings.youtube_api_key }
    response = requests.get("https://www.googleapis.com/youtube/v3/playlists", params=params, timeout=5)    

    if response.ok:
        playlist = response.json()
        total_videos = playlist["items"][0]["contentDetails"]["itemCount"]
        album = playlist["items"][0]["snippet"]["title"]


    else:        
        raise Exception(f"Failed to retrieve playlist details: \nAre you sure the playlist is not set to private?") 

    # To ensure this doesnt loop forever i use the total video count to limit the loop.
    # But it might stop early as some videos are unavailable or other issues exist therefore shortening the amount of pages.
    params = { "part": "snippet", "playlistId": playlist_id, "key": settings.youtube_api_key, "maxResults": 50 }
    for x in range(int(total_videos / 50)+1):
        response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params=params, timeout=5)
        data = response.json()

        for dataItem in data["items"]:
            video_id_list.append(dataItem["snippet"]["resourceId"]["videoId"])

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break  # Exit loop when there are no more pages
        else:
            params["pageToken"]= next_page_token

    output = get_youtube_video(video_id_list, album)
    return output

def get_youtube_video(video: list | str, album: str) -> list:
    video_id_list = []

    if isinstance(video, str):
        if "music.youtube.com/watch?v=" in video:
            vid_id = video[34:45]
            video_id_list.append(vid_id)
        elif "www.youtube.com/watch?v=" in video:
            vid_id = video[32:43]
            video_id_list.append(vid_id)
        elif "youtu.be/" in video:
            vid_id = video[17:28]
            video_id_list.append(vid_id)
        else:
            raise Exception("Invalid URL. Please provide a valid YouTube video URL.")
    elif isinstance(video, list):
        video_id_list = video
    else:
        raise Exception("Invalid input. Please provide either a single video URL or a list of video IDs.")

    # We have to split the list into chunks because youtube only allows up to 50 videos in one API request
    chunks = [video_id_list[i:i + 50] for i in range(0, len(video_id_list), 50)]

    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_video_data(session, chunk) for chunk in chunks]
            return await asyncio.gather(*tasks)

    results = asyncio.run(fetch_all())

    # Flatten the result list
    video_data = []
    for result in results:
        video_data.extend(result)
        
    # Convert video data to Song objects
    songs = []
    for video in video_data:
        title = video["snippet"]["title"]
        duration = youtube_duration_to_seconds(video["contentDetails"]["duration"])
        
        songs.append({"title": title, "album": album, "duration": duration, "id": video["id"], "selected": True})

    return songs

async def fetch_video_data(session, chunk):
    params = { "part": "snippet,contentDetails", "id": ",".join(chunk), "key": settings.youtube_api_key }

    async with session.get("https://www.googleapis.com/youtube/v3/videos", params=params, timeout=5) as response:
        if response.status == 200:
            video_response = await response.json()
            video_data = video_response.get("items", [])
            return video_data
        else:
            print(f"Failed to retrieve video details for chunk: {chunk}, Status: {response.status}")
            return []

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_thumbnail(thumbnail_url: str, out_path: str):
    response = requests.get(thumbnail_url, stream=True)
    if response.ok:
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

def crop_thumbnail_to_square(path: str):
    img = Image.open(path)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = (width + min_dim) // 2
    bottom = (height + min_dim) // 2
    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(path)

def embed_metadata(mp3_path: str, entry: dict, tracknumber: int = 1):
    try:
        audio = EasyID3(mp3_path)
    except error:
        audio = MP3(mp3_path, ID3=ID3)
        audio.add_tags()
        audio = EasyID3(mp3_path)

    audio['title'] = entry.get('title', 'Unknown Title')
    audio['artist'] = entry.get('artist') or entry.get('uploader', 'Unknown Artist')
    audio['date'] = str(entry.get('release_year', "Unknown Year"))
    audio['tracknumber'] = str(tracknumber)
    if entry.get('album'):
        audio['album'] = entry['album']
        artists = entry.get('artists')
        if artists and isinstance(artists, list) and len(artists) > 0:
            audio['albumartist'] = artists[0]

    audio.save()

def embed_thumbnail(mp3_path: str, thumbnail_path: str):
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

def download_song(song: dict, track_number: int = 1):
    """
    Downloads a single song dict with keys at least 'title' and 'id'.
    Downloads best audio, converts to mp3, embeds metadata and thumbnail,
    then moves mp3 to DOWNLOAD_DIR.
    """
    with TemporaryDirectory() as temp_dir:
        url = f"https://www.youtube.com/watch?v={song['id']}"
        
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
            info = ydl.extract_info(url, download=False)
            if info is None:
                # Could not get info, abort
                return
            
            # Download the audio and extract to mp3
            ydl.download([url])
            
            mp3_temp_path = os.path.join(temp_dir, f"{song['id']}.mp3")

            # Download and embed thumbnail if available
            thumbnail_url = info.get('thumbnail')
            if thumbnail_url:
                thumbnail_path = os.path.join(temp_dir, f"{song['id']}_thumb.jpg")
                download_thumbnail(thumbnail_url, thumbnail_path)
                crop_thumbnail_to_square(thumbnail_path)
                embed_thumbnail(mp3_temp_path, thumbnail_path)
                os.remove(thumbnail_path)
            
            # Embed metadata (some fields might be missing, fallback accordingly)
            embed_metadata(mp3_temp_path, info, track_number)

            # Sanitize title for filename and move to download dir
            title = sanitize_filename(song.get('title', info.get('title', 'Unknown Title')))

            if settings.group_by_album:
                raw_album_name = song.get("album")
                clean_album_name = re.sub(r'(?i)^album\s*-\s*', '', raw_album_name).strip()
                album_name = sanitize_filename(clean_album_name)
                final_dir = os.path.join(settings.download_dir, album_name)

            os.makedirs(final_dir, exist_ok=True)
            final_path = os.path.join(final_dir, f"{title}.mp3")

            shutil.move(mp3_temp_path, final_path)