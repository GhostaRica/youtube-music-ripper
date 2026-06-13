import os
import curses

from menus.main_menu import main_menu

os.environ.setdefault("ESCDELAY", "50")

def print_title(stdscr, title):
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, title + "\n")
    stdscr.attroff(curses.color_pair(1))

def run(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    main_menu(stdscr)

if __name__ == "__main__":
    curses.wrapper(run)
