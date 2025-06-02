# YouTube Downloader Script

This Python script allows you to download YouTube videos or audio using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

## Features

* Download audio from a YouTube URL
* Automatically embed thumbnails and metadata
* Easy to run in a virtual environment

## Installation

1. **Clone or download the repository**

   ```bash
   git clone https://github.com/GhostaRica/youtube-music-ripper.git
   cd youtube-music-ripper
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**

    On **Linux/macOS**:

     ```bash
     source .venv/bin/activate
     ```
    On **Windows**:

     ```cmd
     .venv\Scripts\activate
     ```

4. **Install the required dependencies**

   ```bash
   pip install yt-dlp mutagen pillow requests
   ```

## Usage

Once everything is set up, run the script with a YouTube URL:

```bash
python main.py <youtube_link>
```

Replace `<youtube_link>` with the full URL of the video you want to download.

### Example:

```bash
python main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## 📁 Output

The downloaded file(s) will be saved in the downloads folder located in the same directory as `main.py`, or as specified in the script.

* Download the highest-quality audio or video
* Convert the format (e.g. to MP3)
* Add metadata like title, artist, or thumbnail

## Deactivation

When you’re done, you can deactivate the virtual environment:

```bash
deactivate
```

