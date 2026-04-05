import curses
from urllib.parse import urlparse, parse_qs

from Modules import youtube, image_utils
from menus.utils.helper import UiHelper
from classes.music.album import Album

#TODO this needs a refactor to use the general ui helper instead of doing all this custom stuff

def format_duration(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

def download_playlist_menu(stdscr):
    helper = UiHelper(stdscr)
    title = "📥 Download playlist (experimental)"
    subtitle = "Provide a youtube URL and press Enter"

    while True:
        result = helper.render_input_menu(title, subtitle)

        if result == "__ESC__":
            break

        if result != "":
            pre_download_menu(stdscr, result)

def pre_download_menu(stdscr, url:str):
    helper = UiHelper(stdscr)

    stdscr.clear()
    helper.render_title("📥 Download Menu")
    stdscr.addstr("Please wait whilst song metadata is being loaded:\n")
    stdscr.refresh()

    if "youtube.com/playlist" in url:
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        playlist_id = query.get("list", [None])[0]

        video_ids = youtube.get_youtube_playlist_video_ids(playlist_id)

        start_download(stdscr, video_ids)

def start_download(stdscr, video_ids: list[str]):
    helper = UiHelper(stdscr)
    total = len(video_ids)

    for index, video_id in enumerate(video_ids, start=1):
        stdscr.clear()
        curses.curs_set(0)
        helper.render_title("📥 Downloading songs...\n")
        album = youtube.get_youtube_video(video_id)
        song = album.songs.pop()
        stdscr.addstr(2, 0, f"Currently downloading: ({index}/{total}): {song.title}")
        stdscr.refresh()

        downloaded_cover = image_utils.download_thumbnail(album.cover_url)

        youtube.download_song(song, album.name, album.artist, album.type, downloaded_cover)

    stdscr.addstr(4, 0, "All songs downloaded. Press any key to return.")
    stdscr.refresh()
    stdscr.getch()
