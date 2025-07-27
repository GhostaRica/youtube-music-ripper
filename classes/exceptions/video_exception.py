class VideoDoesNotExist(Exception):
    """Exception raised when a requested video is not found."""

    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f"Video with id '{video_id}' does not exist.")
