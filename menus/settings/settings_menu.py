from menus.menu_item import MenuItem
from menus.utils.helper import UiHelper
from Modules.config import CONFIG

def settings_menu(stdscr):
    helper = UiHelper(stdscr)
    title = "⚙️ Settings"
    subtitle = "Use ↑↓ to navigate, Enter to select/toggle, ESC to go back\n"

    menu_items = [
        MenuItem("download_dir", "Download Directory", CONFIG.download_dir, action=edit_download_dir),
        MenuItem("group_artist", "Group by Artist Folder", CONFIG.group_by_artist, action=toggle_group_artist),
        MenuItem("group_album", "Group by Album Folder", CONFIG.group_by_album, action=toggle_group_album),
        MenuItem("back", "Return to Main Menu")
    ]

    while True:
        selected = helper.render_option_menu(title, subtitle, menu_items)

        if selected is None or selected.id == "back":
            break

        # Execute the associated action
        if selected.action:
            selected.action(stdscr)

        # Update displayed value after action
        if selected.id == "download_dir":
            selected.value = CONFIG.download_dir
        elif selected.id == "group_artist":
            selected.value = CONFIG.group_by_artist
        elif selected.id == "group_album":
            selected.value = CONFIG.group_by_album

def edit_download_dir(stdscr):
    helper = UiHelper(stdscr)
    result = helper.render_input_menu(
        "📁 Edit Download Directory", 
        "Enter new path", 
        CONFIG.download_dir
    )

    if result != "__ESC__" or result != "":
        CONFIG.download_dir = result

def toggle_group_artist(stdscr):
    CONFIG.group_by_artist = not CONFIG.group_by_artist

def toggle_group_album(stdscr):
    CONFIG.group_by_album = not CONFIG.group_by_album