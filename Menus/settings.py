import curses
from Modules.config import CONFIG
from Menus import helper

def settings_menu(stdscr):
    curses.curs_set(0)

    options = [
        "YouTube API Key",
        "Download Directory",
        "Group by Album Folder",
        "Return to Main Menu"
    ]
    selected_idx = 0

    while True:
        stdscr.clear()
        helper.print_title(stdscr, "⚙️ Settings")
        stdscr.addstr("Use ↑↓ to navigate, Enter to select.\n\n")

        key_display = CONFIG.youtube_api_key or "(not set)"
        dir_display = CONFIG.download_dir or "(not set)"
        group_by_album = "On" if CONFIG.group_by_album else "Off"

        for idx, option in enumerate(options):
            if idx == 0:
                label = f"{option}: {key_display}"
            elif idx == 1:
                label = f"{option}: {dir_display}"
            elif idx == 2:
                label = f"{option}: {group_by_album}"
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
        elif key in [10, 13]:  # Enter
            if selected_idx == 0:
                edit_setting(
                    stdscr,
                    title="✏️ Edit YouTube API Key",
                    prompt="Enter new API key",
                    get_value=lambda: CONFIG.youtube_api_key,
                    set_value=lambda val: setattr(CONFIG, 'youtube_api_key', val),
                )
            elif selected_idx == 1:
                edit_setting(
                    stdscr,
                    title="📁 Edit Download Directory",
                    prompt="Enter new path",
                    get_value=lambda: CONFIG.download_dir,
                    set_value=lambda val: setattr(CONFIG, 'download_dir', val),
                )

            elif selected_idx == 2:
                CONFIG.group_by_album = not CONFIG.group_by_album

            elif selected_idx == 3:
                break

def edit_setting(stdscr, title, prompt, get_value, set_value):
    stdscr.clear()
    helper.print_title(stdscr, f"{title}\n")
    stdscr.addstr(f"{prompt} (ESC to cancel):\n")
    curses.curs_set(1)
    curses.noecho()

    input_buffer = list(get_value() or "")
    cursor_pos = len(input_buffer)

    def redraw_input():
        y, x = stdscr.getyx()
        stdscr.move(y, 0)
        stdscr.clrtoeol()
        stdscr.addstr(''.join(input_buffer))
        stdscr.move(y, cursor_pos)

    redraw_input()

    while True:
        key = stdscr.getch()

        if key == 27:  # ESC
            curses.curs_set(0)
            return

        elif key in (10, 13):  # Enter
            break

        elif key in (8, 127, curses.KEY_BACKSPACE):
            if cursor_pos > 0:
                cursor_pos -= 1
                del input_buffer[cursor_pos]
                redraw_input()

        elif key == curses.KEY_LEFT:
            if cursor_pos > 0:
                cursor_pos -= 1
                y, _ = stdscr.getyx()
                stdscr.move(y, cursor_pos)

        elif key == curses.KEY_RIGHT:
            if cursor_pos < len(input_buffer):
                cursor_pos += 1
                y, _ = stdscr.getyx()
                stdscr.move(y, cursor_pos)

        elif 0 <= key <= 255 and chr(key).isprintable():
            input_buffer.insert(cursor_pos, chr(key))
            cursor_pos += 1
            redraw_input()

    set_value(''.join(input_buffer).strip())
    curses.curs_set(0)

