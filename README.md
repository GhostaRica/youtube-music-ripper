# YouTube Downloader Script

This Python script allows you to download YouTube videos or audio using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

# Features

* Download audio from a YouTube URL
* Automatically embed thumbnails and metadata
* Easy to run in a virtual environment

# Installation

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

# Usage
### Recommended: Use the launcher script

Instead of running `main.py` directly, run the launcher script:

```bash
python launcher.py <youtube_link> [options]
```

The launcher script will:

* Automatically check for and download the latest version of the downloader script from GitHub
* Save the latest commit info
* Then run `main.py` with all the arguments you provide

### Optional: Run `main.py` directly

If you want to **bypass the launcher’s auto-update functionality**, this is useful incase the machine you are running this on doesn't have git installed this way you can run the downloader script directly:

```bash
python main.py <youtube_link> [options]
```

However, running the launcher is recommended to always keep your downloader script up to date.
Once everything is set up, run the script with a YouTube URL:

### Example:

```bash
python main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

# 📁 Output

The downloaded file(s) will be saved in the downloads folder located in the same directory as `main.py`, or as specified in the script.

* Download the highest-quality audio or video
* Convert the format (e.g. to MP3)
* Add metadata like title, artist, or thumbnail

# Deactivation

When you’re done, you can deactivate the virtual environment:

```bash
deactivate
```

