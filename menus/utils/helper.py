import curses

from menus.menu_item import MenuItem

class UiHelper:
    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        self.selected_idx = 0

    def render_title(self, title: str) -> None:
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(0, 0, title + "\n")
        self.stdscr.attroff(curses.color_pair(1))

    def render_subtitle(self, subtitle: str) -> None:
        self.stdscr.addstr(1, 0, subtitle + "\n")
            
    def render_option_menu(self, title, subtitle, menu_items) -> MenuItem|None:
        while True:
            self.stdscr.clear()
            self.render_title(title)
            self.render_subtitle(subtitle)

            for idx, item in enumerate(menu_items):
                display_text = item.label

                if isinstance(item.value, bool):
                    display_text = f"{item.label}: [{'ON' if item.value else 'OFF'}]"
                elif item.value is not None:
                    display_text += f": {item.value}"

                if idx == self.selected_idx:
                    self.stdscr.attron(curses.A_REVERSE)
                    self.stdscr.addstr(f"> {idx + 1}. {display_text}\n")
                    self.stdscr.attroff(curses.A_REVERSE)
                else:
                    self.stdscr.addstr(f"  {idx + 1}. {display_text}\n")

            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                self.selected_idx = (self.selected_idx - 1) % len(menu_items)
            elif key == curses.KEY_DOWN:
                self.selected_idx = (self.selected_idx + 1) % len(menu_items)
            elif key in [10, 13]:
                return menu_items[self.selected_idx]
            elif key == 27: #ESC
                return None
            
    def render_input_menu(self, title: str, prompt: str, value="") -> str|None:
        """
        Edits a string input in curses and returns the updated value.
        
        Args:
            title (str): Title to display above the input.
            prompt (str): Prompt to show before the input.
            value (str): Initial text to edit.
        
        Returns:
            str or None: The updated value, or None if ESC was pressed.
        """
        self.stdscr.clear()
        curses.curs_set(1)
        curses.noecho()

        # Print title and prompt
        self.render_title(title)
        self.stdscr.addstr(f"{prompt} (ESC to cancel):\n")

        input_buffer = list(value)
        cursor_pos = len(input_buffer)

        def redraw_input():
            y, _ = self.stdscr.getyx()
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()
            self.stdscr.addstr(''.join(input_buffer))
            self.stdscr.move(y, cursor_pos)

        redraw_input()

        while True:
            key = self.stdscr.getch()

            if key == 27:  # ESC
                curses.curs_set(0)
                return None

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
                    y, _ = self.stdscr.getyx()
                    self.stdscr.move(y, cursor_pos)

            elif key == curses.KEY_RIGHT:
                if cursor_pos < len(input_buffer):
                    cursor_pos += 1
                    y, _ = self.stdscr.getyx()
                    self.stdscr.move(y, cursor_pos)

            elif 0 <= key <= 255 and chr(key).isprintable():
                input_buffer.insert(cursor_pos, chr(key))
                cursor_pos += 1
                redraw_input()

        curses.curs_set(0)
        return ''.join(input_buffer).strip()
