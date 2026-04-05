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

def download_album_menu(stdscr):
    helper = UiHelper(stdscr)
    title = "📥 Download Menu"
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

        album = youtube.get_youtube_playlist(playlist_id)
        if album.get_songs_count() == 1:
            # TODO when there is only one song i should show the single song menu
            pass
        else:
            playlist_menu(stdscr, album)

        start_download(stdscr, album)

    elif "youtu" in url:
        parsed_url = urlparse(url)

        # Case 1: Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        query = parse_qs(parsed_url.query)
        video_id = query.get("v", [None])[0]

        # Case 2: Share URL: https://youtu.be/VIDEO_ID?si=...
        if not video_id and parsed_url.netloc == "youtu.be":
            video_id = parsed_url.path.lstrip("/")

        album = youtube.get_youtube_video(video_id)
        start_download(stdscr, album)

def playlist_menu(stdscr, album: Album):
    curses.curs_set(0)
    current = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        header = "Select songs to download (SPACE to toggle, E to edit, ENTER to confirm):"
        stdscr.addstr(0, 0, header[:width - 1], curses.A_BOLD)

        max_visible = height - 3
        start = max(0, current - max_visible + 1)
        end = min(album.get_songs_count(), start + max_visible)

        for idx in range(start, end):
            song = album.songs[idx]
            marker = "[X]" if song.selected else "[ ]"
            title_str = f"{marker} {song.title} ({format_duration(song.duration)})"
            display_line = title_str[:width - 4]
            y = 2 + idx - start

            if idx == current:
                stdscr.addstr(y, 2, display_line, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 2, display_line)

        key = stdscr.getch()

        if key == curses.KEY_UP and current > 0:
            current -= 1
        elif key == curses.KEY_DOWN and current < album.get_songs_count() - 1:
            current += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            break
        elif key == ord(' '):
            album.songs[current].selected = not album.songs[current].selected
        elif key == ord('e'):
            song_menu(stdscr, album.songs[current])

        stdscr.refresh()

    return [song for song in album.songs if song.selected]

def song_menu(stdscr, song):
    helper = UiHelper(stdscr)
    curses.curs_set(1)
    current = 0
    fields = ["start", "end"]
    field_prompts = {
        "start": "Start time (seconds)",
        "end": "End time (seconds)",
    }

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        helper.render_title(f"{song['title']}")
        stdscr.addstr(2, 0, f"Duration: {format_duration(int(song['duration']))}")

        for idx, field in enumerate(fields):
            label = field_prompts[field]
            value = song.get(field, "")
            line = f"{label}: {value}"
            attr = curses.A_REVERSE if idx == current else curses.A_NORMAL
            stdscr.addstr(3 + idx, 2, line[:width - 4], attr)

        stdscr.addstr(1, 0, "Use ↑↓ to select a field, ENTER to edit, Q to return", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')) and current > 0:
            current -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and current < len(fields) - 1:
            current += 1
        elif key in (10, 13):
            field = fields[current]
            curses.echo()
            stdscr.addstr(5 + len(fields), 2, f"New value for {field_prompts[field]}: ")
            stdscr.clrtoeol()
            stdscr.refresh()
            try:
                value = stdscr.getstr().decode().strip()
                if value:
                    song[field] = int(value)
            except ValueError:
                pass
            curses.noecho()
        elif key in (ord('q'), ord('Q')):
            break

def start_download(stdscr, album: Album):
    helper = UiHelper(stdscr)
    total = album.get_selected_songs_count()
    downloaded_cover = image_utils.download_thumbnail(album.cover_url)

    for index, song in enumerate(album.get_selected_songs(), start=1):
        stdscr.clear()
        curses.curs_set(0)
        helper.render_title("📥 Downloading songs...\n")
        stdscr.addstr(2, 0, f"Currently downloading: ({index}/{total}): {song.title}")
        stdscr.refresh()

        youtube.download_song(song, album.name, album.artist, album.type, downloaded_cover)

    stdscr.addstr(4, 0, "All songs downloaded. Press any key to return.")
    stdscr.refresh()
    stdscr.getch()
