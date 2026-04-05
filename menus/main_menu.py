from version import check_for_update
from menus.menu_item import MenuItem
from menus.utils.helper import UiHelper
from menus.settings.settings_menu import settings_menu
from menus.download.download_album_menu import download_album_menu
from menus.download.donwload_playlist_menu import download_playlist_menu

def main_menu(stdscr):
    helper = UiHelper(stdscr)
    title = "🎼 Youtube Music Downloader"
    subtitle = "Use ↑↓ to navigate, Enter to select\n"
    
    latest_version = check_for_update()
    if latest_version is not None:
        title += f" (v{latest_version} Available)"
    
    menu_items = [
        MenuItem("download_album", "Download Album", action=download_album_action),
        MenuItem("download_playlist", "Download Playlist (Experimental)", action=download_playlist_action),
        MenuItem("settings", "Settings", action=settings_action),
        MenuItem("exit", "Exit", action=exit_action),
    ]

    while True:
        selected = helper.render_option_menu(title, subtitle, menu_items)

        if selected is not None and selected.action:
            result = selected.action(stdscr)

            if result == "exit":
                break

def download_album_action(stdscr):
    download_album_menu(stdscr)

def download_playlist_action(stdscr):
    download_playlist_menu(stdscr)

def settings_action(stdscr):
    settings_menu(stdscr)

def exit_action(stdscr):
    return "exit"