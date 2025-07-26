class PlaylistDoesNotExist(Exception):
    """Exception raised when a requested playlist is not found."""

    def __init__(self, playlist_id: str):
        self.playlist_id = playlist_id
        super().__init__(f"Playlist with id '{playlist_id}' does not exist.")
