import curses

def print_title(stdscr, title):
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, title + "\n")
    stdscr.attroff(curses.color_pair(1))
