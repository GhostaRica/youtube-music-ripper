import curses
from Modules.settings import settings
from Menus import helper

def settings_menu(stdscr):
    curses.curs_set(0)

    options = [
        "YouTube API Key",
        "Download Directory",
        "Return to Main Menu"
    ]
    selected_idx = 0

    while True:
        stdscr.clear()
        helper.print_title(stdscr, "⚙️ Settings")
        stdscr.addstr("Use ↑↓ to navigate, Enter to select.\n\n")

        key_display = settings.youtube_api_key or "(not set)"
        dir_display = settings.download_dir or "(not set)"

        for idx, option in enumerate(options):
            if idx == 0:
                label = f"{option}: {key_display}"
            elif idx == 1:
                label = f"{option}: {dir_display}"
            else:
                label = option

            if idx == selected_idx:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(f"> {idx + 1}. {label}\n")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {idx + 1}. {label}\n")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_idx = (selected_idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected_idx = (selected_idx + 1) % len(options)
        elif key in [ord("1"), ord("2"), ord("3")]:
            selected_idx = int(chr(key)) - 1
        elif key in [10, 13]:  # Enter
            if selected_idx == 0:
                edit_setting(
                    stdscr,
                    title="✏️ Edit YouTube API Key",
                    prompt="Enter new API key",
                    get_value=lambda: settings.youtube_api_key,
                    set_value=lambda val: setattr(settings, 'youtube_api_key', val),
                )
            elif selected_idx == 1:
                edit_setting(
                    stdscr,
                    title="📁 Edit Download Directory",
                    prompt="Enter new path",
                    get_value=lambda: settings.download_dir,
                    set_value=lambda val: setattr(settings, 'download_dir', val),
                )
            elif selected_idx == 2:
                break

def edit_setting(stdscr, title, prompt, get_value, set_value):
    stdscr.clear()
    helper.print_title(stdscr, f"{title}\n")
    stdscr.addstr(f"{prompt} (ESC to cancel):\n")
    curses.curs_set(1)
    curses.noecho()

    input_buffer = get_value() or ""
    stdscr.addstr(input_buffer)

    while True:
        key = stdscr.getch()
        if key == 27:  # ESC
            curses.noecho()
            curses.curs_set(0)
            return
        elif key in (10, 13):  # Enter
            break
        elif key in (8, 127, curses.KEY_BACKSPACE):
            if input_buffer:
                input_buffer = input_buffer[:-1]
                y, x = stdscr.getyx()
                stdscr.move(y, x - 1)
                stdscr.delch()
        else:
            input_buffer += chr(key)
            stdscr.addch(key)

    set_value(input_buffer.strip())
    curses.noecho()
    curses.curs_set(0)
