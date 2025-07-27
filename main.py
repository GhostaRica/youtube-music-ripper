import curses

from Menus.download_menu import download_menu
from Menus.settings_menu import settings_menu

menu_items = ["Download", "Settings", "Exit"]

def print_title(stdscr, title):
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, title + "\n")
    stdscr.attroff(curses.color_pair(1))

def main_menu(stdscr):
    selected_idx = 0

    while True:
        stdscr.clear()
        print_title(stdscr, "🎼 Youtube Music Downloader")
        stdscr.addstr("Use ↑↓ to navigate, Enter to select, or press number keys (1-3).\n\n")

        for idx, item in enumerate(menu_items):
            if idx == selected_idx:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(f"> {idx + 1}. {item}\n")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {idx + 1}. {item}\n")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_idx = (selected_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected_idx = (selected_idx + 1) % len(menu_items)
        elif key in [ord("1"), ord("2"), ord("3")]:
            selected_idx = int(chr(key)) - 1
            return menu_items[selected_idx]
        elif key in [10, 13]:
            return menu_items[selected_idx]

def run(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    while True:
        choice = main_menu(stdscr)

        if choice == "Download":
            download_menu(stdscr)
        elif choice == "Settings":
            settings_menu(stdscr)
        elif choice == "Exit":
            break

if __name__ == "__main__":
    curses.wrapper(run)
