from Menus import helper

def settings_menu(stdscr):
    stdscr.clear()
    helper.print_title(stdscr, "⚙️ Settings (WIP)\n")
    stdscr.addstr("\nNothing here yet. Press any key to return.")
    stdscr.getch()
