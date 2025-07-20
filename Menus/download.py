import curses
from urllib.parse import urlparse, parse_qs

from Modules import youtube
from Menus import helper

def format_duration(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

def download_menu(stdscr):
    while True:
        stdscr.clear()
        helper.print_title(stdscr, "📥 Download Menu (WIP)")
        stdscr.addstr("Paste a youtube URL and press Enter:\n")
        stdscr.refresh()

        curses.echo()
        url = stdscr.getstr(2, 0).decode("utf-8")
        curses.noecho()

        if "youtube.com/playlist" in url:
            parsed_url = urlparse(url)
            query = parse_qs(parsed_url.query)
            playlist_id = query.get("list", [None])[0]

            if not playlist_id:
                continue

            songs = youtube.get_youtube_playlist(playlist_id)
            songs = playlist_songs_menu(stdscr, songs)
            start_download(stdscr, songs)

        elif "youtu" in url:
            parsed_url = urlparse(url)
            query = parse_qs(parsed_url.query)
            video_id = query.get("v", [None])[0]

            if not video_id:
                continue

            songs = [youtube.get_youtube_video(video_id)]
            start_download(stdscr, songs)

def playlist_songs_menu(stdscr, songs):
    curses.curs_set(0)
    current = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        header = "Select songs to download (SPACE to toggle, E to edit, ENTER to confirm):"
        stdscr.addstr(0, 0, header[:width - 1], curses.A_BOLD)

        max_visible = height - 3
        start = max(0, current - max_visible + 1)
        end = min(len(songs), start + max_visible)

        for idx in range(start, end):
            song = songs[idx]
            marker = "[X]" if song.get("selected", True) else "[ ]"
            title_str = f"{marker} {song['title']} ({format_duration(song['duration'])})"
            display_line = title_str[:width - 4]
            y = 2 + idx - start

            if idx == current:
                stdscr.addstr(y, 2, display_line, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 2, display_line)

        key = stdscr.getch()

        if key == curses.KEY_UP and current > 0:
            current -= 1
        elif key == curses.KEY_DOWN and current < len(songs) - 1:
            current += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            break
        elif key == ord(' '):
            songs[current]["selected"] = not songs[current].get("selected", True)
        elif key == ord('e'):
            song_menu(stdscr, songs[current])

        stdscr.refresh()

    return [song for song in songs if song.get("selected", True)]

def song_menu(stdscr, song):
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

        helper.print_title(stdscr, f"{song['title']}")
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

def start_download(stdscr, songs):
    total = len(songs)

    for index, song in enumerate(songs):
        stdscr.clear()
        curses.curs_set(0)
        helper.print_title(stdscr, "📥 Downloading songs...\n")
        stdscr.addstr(2, 0, f"Currently downloading: ({index + 1}/{total}): {song['title']}")
        stdscr.refresh()

        youtube.download_song(song)

    stdscr.addstr(4, 0, "All songs downloaded. Press any key to return.")
    stdscr.refresh()
    stdscr.getch()
