# YouTube Downloader Script

This Python script allows you to download YouTube videos or audio using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

# Features

* Download songs from a YouTube playlist or video
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
   pip install -r requirements.txt
   ```

# Usage
### Recommended: Use the launcher script

Instead of running `main.py` directly, run the launcher script:

```bash
python launcher.py
```

The launcher script will:

* Automatically check for and download the latest version of the downloader script from GitHub
* Save the latest commit info
* Then run `main.py` with all the arguments you provide

### Optional: Run `main.py` directly

If you want to **bypass the launcher’s auto-update functionality**, this is useful incase the machine you are running this on doesn't have git installed this way you can run the downloader script directly:

```bash
python main.py
```

However, running the launcher is recommended to always keep your downloader script up to date.
Once everything is set up, run the script with a YouTube URL:

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

