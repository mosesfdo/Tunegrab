# TuneGrab

**TuneGrab** is a Python application that allows users to download Spotify tracks and playlists as MP3 files using the Spotify API and `yt-dlp`. With a sleek, dark-themed GUI built with CustomTkinter, it offers an intuitive way to search, download, and manage your music collection.

---

## Features

- **Download Spotify Tracks**: Download individual tracks by Spotify URL or search query.
- **Download Playlists**: Fetch and download entire Spotify playlists with a single click.
- **View and Play Downloads**: Browse and play downloaded MP3 files directly from the app.
- **Modern GUI**: Dark-themed interface with a user-friendly design, built using CustomTkinter.
- **Progress Tracking**: Real-time download progress with a progress bar and status updates.
- **Cross-Platform**: Works on Windows, macOS, and Linux (with FFmpeg installed).

---

## Screenshots

*Coming soon! Screenshots of the TuneGrab interface will be added to showcase the app's look and feel.*

---

## Installation

### Prerequisites
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/).
- **FFmpeg**: Required for audio processing. [Download FFmpeg](https://ffmpeg.org/download.html) or from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
- **Spotify Developer Account**: To get API credentials (`client_id` and `client_secret`).

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/TuneGrab.git
   cd TuneGrab
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   The `requirements.txt` includes:
   - `spotipy`
   - `yt-dlp`
   - `customtkinter`

3. **Set Up Spotify API Credentials**:
   - Sign up for a [Spotify Developer Account](https://developer.spotify.com).
   - Create an app to get a `client_id` and `client_secret`.
   - Replace the placeholders in `app.py`:
     ```python
     client_id = "your_client_id"
     client_secret = "your_client_secret"
     ```
     Alternatively, use environment variables for security:
     ```bash
     export SPOTIFY_CLIENT_ID="your_client_id"
     export SPOTIFY_CLIENT_SECRET="your_client_secret"
     ```
     Add `.env` to `.gitignore` if using a `.env` file.

4. **Install FFmpeg**:
   - **Windows**: Download FFmpeg, extract it, and add the `bin` folder (containing `ffmpeg.exe` and `ffprobe.exe`) to your system PATH. Alternatively, place `ffmpeg.exe` and `ffprobe.exe` in `C:\ffmpeg\bin`.
   - **macOS**: Install via Homebrew:
     ```bash
     brew install ffmpeg
     ```
   - **Linux**: Install via package manager:
     ```bash
     sudo apt install ffmpeg  # Ubuntu/Debian
     sudo yum install ffmpeg  # CentOS/RHEL
     ```
   - Verify installation:
     ```bash
     ffmpeg -version
     ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

---

## Usage

1. **Launch TuneGrab**:
   - Run `python app.py` to open the GUI.
2. **Choose a Download Option**:
   - **Track by URL**: Enter a Spotify track URL (e.g., `https://open.spotify.com/track/...`) and click "Start Download".
   - **Track by Search**: Enter a song name or query (e.g., `Artist - Song Title`) and click "Search and Download".
   - **Playlist**: Enter a Spotify playlist URL, fetch tracks, select tracks to download, and click "Download Selected Tracks" or "Download All Tracks".
3. **View Downloads**:
   - Click "View / Play Downloads" to browse downloaded MP3 files.
   - Double-click an MP3 to play it using your default media player.
4. **Change Download Folder**:
   - Use the "Change Base Folder" button to set a custom directory for downloads.

Downloaded files are saved in the `songs/` directory (or a playlist-specific subdirectory).

---

## Requirements

- **Python Libraries**: Listed in `requirements.txt`.
- **FFmpeg**: For audio extraction and conversion.
- **System**: Windows, macOS, or Linux.
- **Spotify API Access**: Valid `client_id` and `client_secret`.

---

## Troubleshooting

- **FFmpeg Error**:
  - Ensure FFmpeg is installed and in your system PATH or the correct directory (`C:\ffmpeg\bin` on Windows).
  - Test with `ffmpeg -version`.
- **Spotify API Error**:
  - Verify your `client_id` and `client_secret` are correct.
  - Check your Spotify Developer Dashboard for app restrictions.
- **Download Fails**:
  - Update `yt-dlp`:
    ```bash
    pip install --upgrade yt-dlp
    ```
  - Ensure a stable internet connection.
- **Icon Missing**:
  - If `tunegrab.ico` or `tunegrab.png` are missing, the app will still run but may not display a custom icon.

For additional help, open an [issue](https://github.com/your-username/TuneGrab/issues).

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to your fork (`git push origin feature/your-feature`).
5. Open a pull request.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Disclaimer

TuneGrab is intended for **personal, non-commercial use**. Downloading music may violate the Terms of Service of Spotify, YouTube, or other platforms. Ensure compliance with all applicable laws and terms. The developers are not responsible for misuse of this tool.

---

## Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/): For Spotify API integration.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp): For YouTube audio downloading.
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter): For the modern GUI framework.
- [FFmpeg](https://ffmpeg.org/): For audio processing.

---

## Contact

For questions or feedback, open an issue or contact @mosesfdo on GitHub.

*Happy downloading with TuneGrab!*
