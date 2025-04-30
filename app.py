import os
import re
import sys
import shutil
import subprocess
import webbrowser
import platform
import threading
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import customtkinter

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

customtkinter.set_appearance_mode("dark")
SPOTIFY_BLACK = "#121212"
SPOTIFY_DARK_GREY = "#0d1b29"
SPOTIFY_GREY = "#B3B3B3"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_GREEN = "#0f6bac"
SPOTIFY_LIGHT_BLACK = "#181818"
SPOTIFY_LIGHT_GREY = "#535353"
SPOTIFY_INPUT_BG = "#3E3E3E"
CORNER_RADIUS = 12
font_name = "Segoe UI" if platform.system() == "Windows" else "Helvetica Neue" if platform.system() == "Darwin" else "Noto Sans"
DEFAULT_FONT = (font_name, 13)
DEFAULT_FONT_BOLD = (font_name, 13, "bold")
TITLE_FONT = (font_name, 18, "bold")
LISTBOX_FONT = (font_name, 12)
SMALL_FONT = (font_name, 11)

#use your own Spotify API credentials (client_id and client_secret)
#Replace these with your own:
client_id = ("SPOTIFY_CLIENT_ID")
client_secret = ("SPOTIFY_CLIENT_SECRET")

BASE_DIR = get_base_path()
SONGS_DIR = os.path.join(BASE_DIR, "songs")
os.makedirs(SONGS_DIR, exist_ok=True)

sp = None
try:
    if client_id != "YOUR_SPOTIFY_CLIENT_ID" and client_secret != "YOUR_SPOTIFY_CLIENT_SECRET":
        sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        print("Spotify authentication attempted.")
    else:
        print("Spotify credentials not set, skipping authentication.")
except Exception as e:
    print(f"CRITICAL: Spotify Auth Error: {e}")

current_playlist_url = None
current_playlist_name = None
current_playlist_dir = None
current_playlist_tracks = []
search_suggestions = []
suggestion_dropdown = None

def check_ffmpeg():
    if getattr(sys, 'frozen', False):
        ffmpeg_path_explicit = os.path.join(BASE_DIR, "ffmpeg", "bin")
    else:
        ffmpeg_path_explicit = r'C:\ffmpeg\bin' if platform.system() == "Windows" else '/usr/local/bin'
    ffmpeg_exe_explicit = os.path.join(ffmpeg_path_explicit, "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
    ffprobe_exe_explicit = os.path.join(ffmpeg_path_explicit, "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")
    explicit_path_exists = os.path.isfile(ffmpeg_exe_explicit) and os.path.isfile(ffprobe_exe_explicit)
    in_system_path = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
    if explicit_path_exists:
        print(f"FFmpeg found at explicit path: {ffmpeg_path_explicit}")
        return True, ffmpeg_path_explicit
    elif in_system_path:
        print("FFmpeg found in system PATH.")
        return True, None
    else:
        msg = (f"FFmpeg not found at '{ffmpeg_path_explicit}' or in system PATH.\n\n"
               "Please install FFmpeg and either:\n"
               "1. Add its 'bin' folder to your system's PATH environment variable.\n"
               "2. OR, ensure ffmpeg/ffmpeg.exe and ffprobe/ffprobe.exe are inside '{ffmpeg_path_explicit}'.\n\n"
               "Download from: https://ffmpeg.org/download.html or https://www.gyan.dev/ffmpeg/builds/")
        messagebox.showerror("FFmpeg Error", msg)
        return False, None

def update_yt_dlp(progress_var):
    if getattr(sys, 'frozen', False):
        progress_var.set("yt-dlp update skipped in executable mode.")
        print("yt-dlp update skipped in frozen executable.")
        if root: root.after(2500, lambda: progress_var.set(""))
        return
    #try:
        progress_var.set("Checking for yt-dlp updates...")
        if root: root.update_idletasks()
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                                capture_output=True, text=True, check=False, encoding='utf-8')
        if result.returncode == 0:
            progress_var.set("yt-dlp updated successfully." if "Requirement already satisfied" not in result.stdout else "yt-dlp is up to date.")
            print(f"yt-dlp update check output:\n{result.stdout}\n{result.stderr}")
        else:
            progress_var.set(f"yt-dlp update check failed (Code: {result.returncode}). See console.")
            print(f"yt-dlp update check failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        if root: root.after(2500, lambda: progress_var.set(""))
    #except Exception as e:
        progress_var.set(f"Failed to update yt-dlp: {e}")
    if root: root.update_idletasks()

def sanitize_filename(name):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    return re.sub(r'\s+', ' ', sanitized).strip()

def progress_hook_gui(d, progress_var, pbar_widget):
    status = d.get('status')
    if status == 'downloading':
        total_size = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        speed = d.get('speed')
        eta = d.get('eta')
        if total_size:
            if pbar_widget.cget('mode') == 'indeterminate':
                pbar_widget.stop()
                pbar_widget.configure(mode='determinate')
            percent = downloaded / total_size
            pbar_widget.set(percent)
            status_msg = f"Downloading: {percent*100:.1f}%"
            if speed:
                status_msg += f" @ {speed / (1024*1024):.1f} MB/s" if speed > 1024 * 1024 else f" @ {speed / 1024:.1f} KB/s"
            if eta: status_msg += f" (ETA: {int(eta)}s)"
            progress_var.set(status_msg)
        else:
            if pbar_widget.cget('mode') == 'determinate':
                pbar_widget.configure(mode='indeterminate')
                pbar_widget.start()
            status_msg = f"Downloading: {downloaded / (1024 * 1024):.2f} MB"
            if speed: status_msg += f" @ {speed / (1024*1024):.1f} MB/s" if speed > 1024 * 1024 else f" @ {speed / 1024:.1f} KB/s"
            progress_var.set(status_msg)
    elif status == 'finished':
        if pbar_widget.cget('mode') == 'indeterminate': pbar_widget.stop(); pbar_widget.configure(mode='determinate')
        pbar_widget.set(1.0)
        progress_var.set("Download complete!")
        if root: root.after(800, lambda: progress_var.set(""))
    elif status == 'error':
        if pbar_widget.cget('mode') == 'indeterminate': pbar_widget.stop(); pbar_widget.configure(mode='determinate')
        error_msg = d.get('error') or d.get('_message') or 'Unknown download error'
        progress_var.set(f"Error: {str(error_msg)[:100]}...")
        pbar_widget.set(0)
    if root: root.update_idletasks()

def download_song_from_youtube(song_name, save_path, progress_var, pbar_widget, ffmpeg_loc):
    sanitized_name = sanitize_filename(song_name)
    os.makedirs(save_path, exist_ok=True)
    final_mp3_path = os.path.join(save_path, f"{sanitized_name}.mp3")
    if os.path.exists(final_mp3_path):
        progress_var.set(f"Skipped (already exists): {sanitized_name}")
        pbar_widget.set(1.0)
        if root: root.after(1000, lambda: progress_var.set(""))
        return final_mp3_path
    progress_var.set(f"Searching YouTube for: {song_name}")
    pbar_widget.set(0)
    if pbar_widget.cget('mode') == 'indeterminate': pbar_widget.stop(); pbar_widget.configure(mode='determinate')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, f'{sanitized_name}.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                           {'key': 'FFmpegMetadata', 'add_metadata': True},
                           {'key': 'EmbedThumbnail'}],
        'quiet': True,
        'progress_hooks': [lambda d: progress_hook_gui(d, progress_var, pbar_widget)],
        'default_search': 'ytsearch1:',
        'nocheckcertificate': True,
        'playlist_items': '1',
    }
    if ffmpeg_loc and os.path.isdir(ffmpeg_loc):
        ydl_opts['ffmpeg_location'] = ffmpeg_loc
    try:
        with YoutubeDL(ydl_opts) as ydl:
            download_info = ydl.extract_info(f"ytsearch1:{song_name} audio", download=True)
            if os.path.exists(final_mp3_path):
                return final_mp3_path
            else:
                raise FileNotFoundError(f"Postprocessing finished, but MP3 not found: {final_mp3_path}")
    except Exception as e:
        print(f"ERROR during download of '{song_name}': {e}")
        progress_var.set(f"Error: {str(e)[:100]}...")
        return None

def get_track_info(track_url):
    if not sp: return None
    try:
        track_id = track_url.split("/")[-1].split("?")[0]
        track = sp.track(track_id)
        artist_names = ", ".join([artist['name'] for artist in track['artists']])
        return f"{track['name']} - {artist_names}"
    except Exception as e:
        messagebox.showerror("Spotify Error", f"Could not fetch track info: {e}")
        return None

def get_playlist_name(playlist_url):
    if not sp: return None
    try:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        playlist = sp.playlist(playlist_id, fields='name')
        return playlist["name"]
    except Exception as e:
        messagebox.showerror("Spotify Error", f"Could not fetch playlist info: {e}")
        return None

def get_playlist_tracks(playlist_url):
    if not sp: return []
    tracks = []
    try:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        offset = 0
        limit = 100
        while True:
            results = sp.playlist_items(playlist_id, fields='items(track(name, artists(name))), next', additional_types=['track'], offset=offset, limit=limit)
            for item in results['items']:
                track = item.get('track')
                if track and track.get('name') and track.get('artists'):
                    artist_names = ", ".join([artist['name'] for artist in track['artists']])
                    tracks.append(f"{track['name']} - {artist_names}")
            if results.get('next'):
                offset += len(results['items'])
            else:
                break
        return tracks
    except Exception as e:
        messagebox.showerror("Spotify Error", f"Could not fetch playlist tracks: {e}")
        return []

def fetch_search_suggestions(query):
    global search_suggestions
    if not sp or not query.strip():
        search_suggestions = []
        return
    try:
        results = sp.search(q=query, type='track', limit=5)
        search_suggestions = [f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}" for track in results['tracks']['items']]
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        search_suggestions = []

def update_suggestion_dropdown(event=None):
    global suggestion_dropdown
    query = url_entry.get().strip()
    if selected_item_type != "track_search" or not query:
        if suggestion_dropdown and suggestion_dropdown.winfo_exists():
            suggestion_dropdown.destroy()
            suggestion_dropdown = None
        return
    threading.Thread(target=fetch_search_suggestions, args=(query,), daemon=True).start()
    root.after(300, show_suggestion_dropdown)

def show_suggestion_dropdown():
    global suggestion_dropdown, search_suggestions
    if not search_suggestions or selected_item_type != "track_search":
        return
    if suggestion_dropdown and suggestion_dropdown.winfo_exists():
        suggestion_dropdown.destroy()
    entry_pos = url_entry.winfo_rootx() - root.winfo_rootx()
    entry_y = url_entry.winfo_rooty() - root.winfo_rooty() + url_entry.winfo_height()
    suggestion_dropdown = customtkinter.CTkFrame(
        download_frame,
        fg_color=SPOTIFY_LIGHT_BLACK,
        width=url_entry.winfo_width(),
        height=len(search_suggestions) * 32
    )
    suggestion_dropdown.place(x=entry_pos, y=entry_y)
    for suggestion in search_suggestions:
        suggestion_label = customtkinter.CTkButton(
            suggestion_dropdown, text=suggestion, command=lambda s=suggestion: select_suggestion(s),
            fg_color=SPOTIFY_LIGHT_BLACK, hover_color=SPOTIFY_DARK_GREY, text_color=SPOTIFY_WHITE,
            font=LISTBOX_FONT, anchor="w", height=30, corner_radius=0
        )
        suggestion_label.pack(fill="x", padx=2, pady=1)

def select_suggestion(suggestion):
    global suggestion_dropdown
    url_entry.delete(0, tk.END)
    url_entry.insert(0, suggestion)
    if suggestion_dropdown and suggestion_dropdown.winfo_exists():
        suggestion_dropdown.destroy()
        suggestion_dropdown = None

def show_home_page():
    download_frame.pack_forget()
    songs_frame.pack_forget()
    playlist_selection_frame.pack_forget()
    home_frame.pack(padx=20, pady=20, fill="both", expand=True)
    progress_var.set("")
    progress_bar.set(0)
    if progress_bar.cget('mode') == 'indeterminate': 
        progress_bar.stop()
        progress_bar.configure(mode='determinate')
    if 'progress_label_playlist' in globals() and progress_label_playlist.winfo_exists():
        progress_label_playlist.configure(text="")
    global selected_item_type, current_playlist_url, current_playlist_name, current_playlist_dir, current_playlist_tracks, suggestion_dropdown
    selected_item_type = None
    current_playlist_url = None
    current_playlist_name = None
    current_playlist_dir = None
    current_playlist_tracks = []
    if suggestion_dropdown and suggestion_dropdown.winfo_exists():
        suggestion_dropdown.destroy()
        suggestion_dropdown = None

def show_download_section(item_type):
    home_frame.pack_forget()
    songs_frame.pack_forget()
    playlist_selection_frame.pack_forget()
    progress_bar.set(0)
    if progress_bar.cget('mode') == 'indeterminate':
        progress_bar.stop()
        progress_bar.configure(mode='determinate')
    progress_var.set("")
    if progress_label_playlist.winfo_exists():
        progress_label_playlist.configure(text="")
    download_frame.pack(padx=10, pady=10, fill="both", expand=True)
    global selected_item_type, suggestion_dropdown
    selected_item_type = item_type
    url_entry.delete(0, 'end')
    url_entry.focus()
    if item_type == "track_search":
        url_entry.bind("<KeyRelease>", update_suggestion_dropdown)
    else:
        url_entry.unbind("<KeyRelease>")
        if suggestion_dropdown and suggestion_dropdown.winfo_exists():
            suggestion_dropdown.destroy()
            suggestion_dropdown = None
    if item_type == "track_url":
        url_label.configure(text="Enter Spotify Track URL:")
        download_button.configure(text="Start Download", command=start_single_track_download)
    elif item_type == "track_search":
        url_label.configure(text="Enter Song Name / Search Query (e.g., Artist - Title):")
        download_button.configure(text="Search and Download", command=start_search_download)
    elif item_type == "playlist":
        url_label.configure(text="Enter Spotify Playlist URL:")
        download_button.configure(text="Fetch Playlist Tracks", command=handle_playlist_url)

def start_single_track_download():
    url = url_entry.get().strip()
    if not url: messagebox.showerror("Input Error", "Please enter a Spotify Track URL."); return
    download_button.configure(state=tk.DISABLED); back_button_dl.configure(state=tk.DISABLED); root.update_idletasks()
    ffmpeg_ok, ffmpeg_location = check_ffmpeg()
    if not ffmpeg_ok: return
    try:
        song_search_term = get_track_info(url)
        if song_search_term:
            result_path = download_song_from_youtube(song_search_term, SONGS_DIR, progress_var, progress_bar, ffmpeg_location)
            if result_path and not progress_var.get().startswith("Skipped"):
                messagebox.showinfo("Success", f"Downloaded: {os.path.basename(result_path)}")
            elif not result_path:
                messagebox.showerror("Download Failed", f"Could not download '{song_search_term}'.")
        show_home_page()
    finally:
        if download_button.winfo_exists(): download_button.configure(state=tk.NORMAL)
        if back_button_dl.winfo_exists(): back_button_dl.configure(state=tk.NORMAL)

def start_search_download():
    global suggestion_dropdown
    search_query = url_entry.get().strip()
    if not search_query: messagebox.showerror("Input Error", "Please enter a song name or search query."); return
    if suggestion_dropdown and suggestion_dropdown.winfo_exists():
        suggestion_dropdown.destroy()
        suggestion_dropdown = None
    download_button.configure(state=tk.DISABLED); back_button_dl.configure(state=tk.DISABLED); root.update_idletasks()
    ffmpeg_ok, ffmpeg_location = check_ffmpeg()
    if not ffmpeg_ok: return
    try:
        result_path = download_song_from_youtube(search_query, SONGS_DIR, progress_var, progress_bar, ffmpeg_location)
        if result_path and not progress_var.get().startswith("Skipped"):
            messagebox.showinfo("Success", f"Downloaded: {os.path.basename(result_path)}")
        elif not result_path:
            messagebox.showerror("Download Failed", f"Could not download '{search_query}'.")
        show_home_page()
    finally:
        if download_button.winfo_exists(): download_button.configure(state=tk.NORMAL)
        if back_button_dl.winfo_exists(): back_button_dl.configure(state=tk.NORMAL)

def handle_playlist_url():
    url = url_entry.get().strip()
    if not url: messagebox.showerror("Input Error", "Please enter a Spotify Playlist URL."); return
    global current_playlist_url, current_playlist_name, current_playlist_dir, current_playlist_tracks
    current_playlist_url = url
    download_button.configure(state=tk.DISABLED); back_button_dl.configure(state=tk.DISABLED); root.update_idletasks()
    current_playlist_name = get_playlist_name(url)
    if not current_playlist_name: return
    playlist_name_sanitized = sanitize_filename(current_playlist_name)
    current_playlist_dir = os.path.join(SONGS_DIR, playlist_name_sanitized)
    current_playlist_tracks = get_playlist_tracks(url)
    if not current_playlist_tracks:
        messagebox.showinfo("Info", f"No tracks found for playlist '{current_playlist_name}'.")
        return
    populate_playlist_selection_listbox()
    playlist_selection_title.configure(text=f"Playlist: {current_playlist_name} ({len(current_playlist_tracks)} tracks)")
    download_frame.pack_forget()
    playlist_selection_frame.pack(padx=10, pady=10, fill="both", expand=True)
    if download_button.winfo_exists(): download_button.configure(state=tk.NORMAL)
    if back_button_dl.winfo_exists(): back_button_dl.configure(state=tk.NORMAL)

def populate_playlist_selection_listbox():
    playlist_track_listbox.delete(0, tk.END)
    for track_name in current_playlist_tracks:
        playlist_track_listbox.insert(tk.END, track_name)

def select_all_playlist_tracks():
    playlist_track_listbox.select_set(0, tk.END)

def deselect_all_playlist_tracks():
    playlist_track_listbox.selection_clear(0, tk.END)

def go_back_to_url_entry():
    playlist_selection_frame.pack_forget()
    download_frame.pack(padx=10, pady=10, fill="both", expand=True)

def start_playlist_download_selected():
    selected_indices = playlist_track_listbox.curselection()
    if not selected_indices: messagebox.showinfo("Selection Required", "Please select at least one track."); return
    songs_to_download = [playlist_track_listbox.get(i) for i in selected_indices]
    run_playlist_download(songs_to_download)

def start_playlist_download_all():
    if not current_playlist_tracks: messagebox.showerror("Error", "Track list is empty."); return
    run_playlist_download(current_playlist_tracks)

def run_playlist_download(songs_to_download):
    if not current_playlist_name or not current_playlist_dir: messagebox.showerror("Error", "Playlist information missing."); return
    playlist_dl_selected_button.configure(state=tk.DISABLED); playlist_dl_all_button.configure(state=tk.DISABLED)
    playlist_back_button.configure(state=tk.DISABLED); select_all_button.configure(state=tk.DISABLED); deselect_all_button.configure(state=tk.DISABLED)
    root.update_idletasks()
    ffmpeg_ok, ffmpeg_location = check_ffmpeg()
    if not ffmpeg_ok: return
    try:
        os.makedirs(current_playlist_dir, exist_ok=True)
        total_to_download = len(songs_to_download); success_count = 0; fail_count = 0; skipped_count = 0
        for idx, song in enumerate(songs_to_download, 1):
            progress_label_playlist.configure(text=f"Playlist: '{current_playlist_name}' - Downloading {idx}/{total_to_download}")
            result_path = download_song_from_youtube(song, current_playlist_dir, progress_var, progress_bar, ffmpeg_location)
            if result_path:
                if progress_var.get().startswith("Skipped"): skipped_count += 1
                success_count += 1
            else: fail_count += 1
            if root: root.after(100); root.update_idletasks()
        progress_var.set(""); progress_bar.set(0); progress_label_playlist.configure(text="")
        actual_downloaded = success_count - skipped_count
        summary_msg = f"Playlist '{current_playlist_name}' download finished.\n\nAttempted: {total_to_download} tracks.\nSucceeded: {actual_downloaded} tracks.\n"
        if skipped_count: summary_msg += f"Skipped: {skipped_count} tracks.\n"
        if fail_count: summary_msg += f"Failed: {fail_count} tracks.\n"
        summary_msg += f"Files saved to:\n{current_playlist_dir}"
        messagebox.showinfo("Playlist Download Complete", summary_msg)
        show_home_page()
    except Exception as e:
        messagebox.showerror("Playlist Download Error", f"An unexpected error occurred: {e}")
        show_home_page()
    finally:
        for btn in [playlist_dl_selected_button, playlist_dl_all_button, playlist_back_button, select_all_button, deselect_all_button]:
            if btn.winfo_exists(): btn.configure(state=tk.NORMAL)

def show_downloaded_songs():
    home_frame.pack_forget(); download_frame.pack_forget(); playlist_selection_frame.pack_forget()
    songs_frame.pack(padx=10, pady=10, fill="both", expand=True)
    update_current_folder_label(SONGS_DIR); list_songs()

def list_songs(folder=None):
    current_folder = folder if folder else SONGS_DIR
    update_current_folder_label(current_folder)
    song_list.delete(0, tk.END)
    try:
        all_items = sorted(os.listdir(current_folder), key=str.lower)
        dirs = [d for d in all_items if os.path.isdir(os.path.join(current_folder, d))]
        files = [f for f in all_items if f.lower().endswith(".mp3") and os.path.isfile(os.path.join(current_folder, f))]
        if os.path.normpath(current_folder) != os.path.normpath(SONGS_DIR):
            song_list.insert(tk.END, ".. (Go Up)"); song_list.itemconfig(tk.END, {'fg': SPOTIFY_GREEN})
        for directory in dirs: song_list.insert(tk.END, f"[DIR] {directory}"); song_list.itemconfig(tk.END, {'fg': SPOTIFY_GREY})
        if not files and not dirs and os.path.normpath(current_folder) == os.path.normpath(SONGS_DIR):
            song_list.insert(tk.END, " (No songs or playlists found) "); song_list.itemconfig(tk.END, {'fg': SPOTIFY_GREY})
        for song in files: song_list.insert(tk.END, os.path.basename(song))
    except Exception as e:
        song_list.insert(tk.END, f" Error listing files: {e} "); song_list.itemconfig(tk.END, {'fg': 'red'})

def open_mp3_file(filepath):
    try:
        if platform.system() == "Windows": os.startfile(filepath)
        elif platform.system() == "Darwin": subprocess.run(["open", filepath], check=True)
        else: subprocess.run(["xdg-open", filepath], check=True)
    except Exception as e: messagebox.showerror("Error", f"Could not open file: {e}")

def handle_song_list_action(event=None):
    selected_indices = song_list.curselection()
    if not selected_indices: return
    selected_item = song_list.get(selected_indices[0])
    current_folder = current_folder_var.get()
    if selected_item == ".. (Go Up)":
        parent_folder = os.path.dirname(current_folder)
        if os.path.normpath(parent_folder).startswith(os.path.normpath(SONGS_DIR)): list_songs(parent_folder)
    elif selected_item.startswith("[DIR] "):
        list_songs(os.path.join(current_folder, selected_item.replace("[DIR] ", "")))
    elif selected_item.lower().endswith(".mp3"):
        open_mp3_file(os.path.join(current_folder, selected_item))

def update_current_folder_label(folder):
    current_folder_var.set(os.path.normpath(folder))

def change_songs_directory():
    global SONGS_DIR
    new_songs_dir = filedialog.askdirectory(initialdir=SONGS_DIR, title="Select Base Directory for Songs")
    if new_songs_dir:
        SONGS_DIR = new_songs_dir
        update_current_folder_label(SONGS_DIR)
        list_songs(SONGS_DIR)

root = customtkinter.CTk()
root.title("TuneGrab")
try:
    base_dir = get_base_path()
    if platform.system() == "Windows":
        ico_path = os.path.join(base_dir, "tunegrab.ico")
        if os.path.exists(ico_path):
            root.iconbitmap(ico_path)
        else:
            print(f"Error: 'tunegrab.ico' not found at {ico_path}")
    png_path = os.path.join(base_dir, "tunegrab.png")
    if os.path.exists(png_path):
        icon = tk.PhotoImage(file=png_path)
        root.iconphoto(True, icon)
        print("Icon set successfully with iconphoto!")
    else:
        print(f"Error: 'tunegrab.png' not found at {png_path}")
except tk.TclError as e:
    print(f"Warning: Could not load icon: {e}")
desired_width = 550
desired_height = 700
root.geometry(f"{desired_width}x{desired_height}")
root.minsize(500, 650)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

style = ttk.Style()
style.theme_use('clam')
style.configure("Vertical.TScrollbar", troughcolor=SPOTIFY_LIGHT_BLACK, background=SPOTIFY_DARK_GREY, bordercolor=SPOTIFY_LIGHT_BLACK, arrowcolor=SPOTIFY_GREY, relief='flat')
style.map("Vertical.TScrollbar", background=[('active', SPOTIFY_LIGHT_GREY)])

button_height = 45
home_button_fg = SPOTIFY_GREEN; home_button_hover = "#1a8cd8"; home_button_text = SPOTIFY_BLACK
sec_button_fg = SPOTIFY_DARK_GREY; sec_button_hover = SPOTIFY_LIGHT_GREY; sec_button_text = SPOTIFY_WHITE

home_frame = customtkinter.CTkFrame(root, fg_color="transparent")
download_frame = customtkinter.CTkFrame(root, fg_color=SPOTIFY_BLACK)
playlist_selection_frame = customtkinter.CTkFrame(root, fg_color="transparent")
songs_frame = customtkinter.CTkFrame(root, fg_color="transparent")
progress_frame = customtkinter.CTkFrame(root, fg_color="transparent", height=50)

home_frame.columnconfigure(0, weight=1)
home_title = customtkinter.CTkLabel(home_frame, text="TuneGrab", font=TITLE_FONT, text_color=SPOTIFY_WHITE)
home_title.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
customtkinter.CTkButton(home_frame, text="Download Track by URL", command=lambda: show_download_section("track_url"), font=DEFAULT_FONT_BOLD, fg_color=home_button_fg, hover_color=home_button_hover, text_color=home_button_text, height=button_height, corner_radius=CORNER_RADIUS).grid(row=1, column=0, padx=30, pady=8, sticky="ew")
customtkinter.CTkButton(home_frame, text="Download Track by Search", command=lambda: show_download_section("track_search"), font=DEFAULT_FONT_BOLD, fg_color=home_button_fg, hover_color=home_button_hover, text_color=home_button_text, height=button_height, corner_radius=CORNER_RADIUS).grid(row=2, column=0, padx=30, pady=8, sticky="ew")
customtkinter.CTkButton(home_frame, text="Download Playlist", command=lambda: show_download_section("playlist"), font=DEFAULT_FONT_BOLD, fg_color=home_button_fg, hover_color=home_button_hover, text_color=home_button_text, height=button_height, corner_radius=CORNER_RADIUS).grid(row=3, column=0, padx=30, pady=8, sticky="ew")
customtkinter.CTkButton(home_frame, text="View / Play Downloads", command=show_downloaded_songs, font=DEFAULT_FONT_BOLD, fg_color=sec_button_fg, hover_color=sec_button_hover, text_color=sec_button_text, height=button_height, corner_radius=CORNER_RADIUS).grid(row=4, column=0, padx=30, pady=8, sticky="ew")

download_frame.columnconfigure(0, weight=1)
url_label = customtkinter.CTkLabel(download_frame, text="Input:", font=DEFAULT_FONT, text_color=SPOTIFY_GREY, anchor='w')
url_label.pack(padx=15, pady=(15,0), anchor="w", fill="x")
url_entry = customtkinter.CTkEntry(download_frame, font=DEFAULT_FONT, fg_color=SPOTIFY_INPUT_BG, text_color=SPOTIFY_WHITE, border_color=SPOTIFY_LIGHT_GREY, corner_radius=CORNER_RADIUS - 4)
url_entry.pack(padx=15, pady=5, fill="x")
download_button = customtkinter.CTkButton(download_frame, text="Go", font=DEFAULT_FONT_BOLD, fg_color=SPOTIFY_GREEN, hover_color=home_button_hover, text_color=SPOTIFY_BLACK, height=button_height, corner_radius=CORNER_RADIUS)
download_button.pack(padx=15, pady=15, fill="x")
back_button_dl = customtkinter.CTkButton(download_frame, text="Back to Home", command=show_home_page, font=DEFAULT_FONT_BOLD, fg_color=sec_button_fg, hover_color=sec_button_hover, text_color=sec_button_text, height=button_height, corner_radius=CORNER_RADIUS)
back_button_dl.pack(padx=15, pady=(0, 15), fill="x")
progress_label_playlist = customtkinter.CTkLabel(download_frame, text="", font=SMALL_FONT, text_color=SPOTIFY_GREY, anchor='w')
progress_label_playlist.pack(padx=15, pady=(5,5), fill="x")

playlist_selection_frame.columnconfigure(0, weight=1)
playlist_selection_frame.rowconfigure(2, weight=1)
playlist_selection_title = customtkinter.CTkLabel(playlist_selection_frame, text="Playlist: ", font=DEFAULT_FONT_BOLD, text_color=SPOTIFY_WHITE, anchor="w")
playlist_selection_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
select_buttons_frame = customtkinter.CTkFrame(playlist_selection_frame, fg_color="transparent")
select_buttons_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=(5,5), sticky="ew")
select_all_button = customtkinter.CTkButton(select_buttons_frame, text="Select All", command=select_all_playlist_tracks, font=DEFAULT_FONT, fg_color=SPOTIFY_DARK_GREY, hover_color=SPOTIFY_LIGHT_GREY, text_color=SPOTIFY_WHITE, height=30, width=100, corner_radius=CORNER_RADIUS - 4)
select_all_button.pack(side=tk.LEFT, padx=(5, 5))
deselect_all_button = customtkinter.CTkButton(select_buttons_frame, text="Deselect All", command=deselect_all_playlist_tracks, font=DEFAULT_FONT, fg_color=SPOTIFY_DARK_GREY, hover_color=SPOTIFY_LIGHT_GREY, text_color=SPOTIFY_WHITE, height=30, width=100, corner_radius=CORNER_RADIUS - 4)
deselect_all_button.pack(side=tk.LEFT, padx=5)
listbox_frame_pl = customtkinter.CTkFrame(playlist_selection_frame, fg_color=SPOTIFY_LIGHT_BLACK, corner_radius=CORNER_RADIUS-4)
listbox_frame_pl.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
listbox_frame_pl.columnconfigure(0, weight=1)
listbox_frame_pl.rowconfigure(0, weight=1)
playlist_track_listbox = tk.Listbox(listbox_frame_pl, height=15, selectmode=tk.EXTENDED, bg=SPOTIFY_LIGHT_BLACK, fg=SPOTIFY_WHITE, selectbackground=SPOTIFY_GREEN, selectforeground=SPOTIFY_BLACK, highlightthickness=0, borderwidth=0, relief="flat", font=LISTBOX_FONT, activestyle='none')
playlist_track_listbox.grid(row=0, column=0, padx=(5,0), pady=5, sticky="nsew")
playlist_scrollbar = ttk.Scrollbar(listbox_frame_pl, orient="vertical", command=playlist_track_listbox.yview, style="Vertical.TScrollbar")
playlist_scrollbar.grid(row=0, column=1, padx=(2,5), pady=5, sticky="ns")
playlist_track_listbox.config(yscrollcommand=playlist_scrollbar.set)
playlist_dl_selected_button = customtkinter.CTkButton(playlist_selection_frame, text="Download Selected Tracks", command=start_playlist_download_selected, font=DEFAULT_FONT_BOLD, fg_color=SPOTIFY_GREEN, hover_color=home_button_hover, text_color=SPOTIFY_BLACK, height=button_height, corner_radius=CORNER_RADIUS)
playlist_dl_selected_button.grid(row=3, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="ew")
playlist_dl_all_button = customtkinter.CTkButton(playlist_selection_frame, text="Download All Tracks", command=start_playlist_download_all, font=DEFAULT_FONT_BOLD, fg_color=SPOTIFY_DARK_GREY, hover_color=SPOTIFY_LIGHT_GREY, text_color=SPOTIFY_WHITE, height=button_height, corner_radius=CORNER_RADIUS)
playlist_dl_all_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
playlist_back_button = customtkinter.CTkButton(playlist_selection_frame, text="Back to URL Entry", command=go_back_to_url_entry, font=DEFAULT_FONT_BOLD, fg_color=sec_button_fg, hover_color=sec_button_hover, text_color=sec_button_text, height=button_height, corner_radius=CORNER_RADIUS)
playlist_back_button.grid(row=5, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")

songs_frame.columnconfigure(0, weight=1)
songs_frame.rowconfigure(2, weight=1)
current_folder_var = tk.StringVar()
current_folder_label = customtkinter.CTkLabel(songs_frame, textvariable=current_folder_var, font=SMALL_FONT, text_color=SPOTIFY_GREY, anchor="w", wraplength=desired_width-40)
current_folder_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
button_frame_songs = customtkinter.CTkFrame(songs_frame, fg_color="transparent")
button_frame_songs.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
change_dir_button = customtkinter.CTkButton(button_frame_songs, text="Change Base Folder", command=change_songs_directory, font=DEFAULT_FONT_BOLD, fg_color=sec_button_fg, hover_color=sec_button_hover, text_color=sec_button_text, height=35, corner_radius=CORNER_RADIUS - 2)
change_dir_button.pack(side=tk.LEFT, padx=(5, 0))
listbox_frame_sv = customtkinter.CTkFrame(songs_frame, fg_color=SPOTIFY_LIGHT_BLACK, corner_radius=CORNER_RADIUS-4)
listbox_frame_sv.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
listbox_frame_sv.columnconfigure(0, weight=1)
listbox_frame_sv.rowconfigure(0, weight=1)
song_list = tk.Listbox(listbox_frame_sv, height=15, selectmode=tk.SINGLE, bg=SPOTIFY_LIGHT_BLACK, fg=SPOTIFY_WHITE, selectbackground=SPOTIFY_GREEN, selectforeground=SPOTIFY_BLACK, highlightthickness=0, borderwidth=0, relief="flat", font=LISTBOX_FONT, activestyle='none')
song_list.grid(row=0, column=0, padx=(5,0), pady=5, sticky="nsew")
song_list.bind("<Double-Button-1>", handle_song_list_action)
song_list.bind("<Return>", handle_song_list_action)
scrollbar_sv = ttk.Scrollbar(listbox_frame_sv, orient="vertical", command=song_list.yview, style="Vertical.TScrollbar")
scrollbar_sv.grid(row=0, column=1, padx=(2,5), pady=5, sticky="ns")
song_list.config(yscrollcommand=scrollbar_sv.set)
play_button = customtkinter.CTkButton(songs_frame, text="Play / Open Selected", command=handle_song_list_action, font=DEFAULT_FONT_BOLD, fg_color=SPOTIFY_GREEN, hover_color=home_button_hover, text_color=SPOTIFY_BLACK, height=button_height, corner_radius=CORNER_RADIUS)
play_button.grid(row=3, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="ew")
back_to_home_button_sv = customtkinter.CTkButton(songs_frame, text="Back to Home", command=show_home_page, font=DEFAULT_FONT_BOLD, fg_color=sec_button_fg, hover_color=sec_button_hover, text_color=sec_button_text, height=button_height, corner_radius=CORNER_RADIUS)
back_to_home_button_sv.grid(row=4, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")

progress_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=(5, 10))
progress_frame.columnconfigure(0, weight=1)
progress_var = tk.StringVar()
progress_label = customtkinter.CTkLabel(progress_frame, textvariable=progress_var, font=SMALL_FONT, text_color=SPOTIFY_GREY, anchor='w')
progress_label.grid(row=0, column=0, sticky="ew", padx=5)
progress_var.set("")
progress_bar = customtkinter.CTkProgressBar(progress_frame, orientation="horizontal", height=8, corner_radius=4, progress_color=SPOTIFY_GREEN, fg_color=SPOTIFY_DARK_GREY)
progress_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=(2,0))
progress_bar.set(0)


if __name__ == "__main__":
    selected_item_type = None
    ffmpeg_ready, _ = check_ffmpeg()
    if ffmpeg_ready:
        root.after(200, lambda: update_yt_dlp(progress_var))
        show_home_page()
    else:
        messagebox.showwarning("FFmpeg Missing", "FFmpeg setup incomplete.\nDownloads will fail until FFmpeg is configured.")
        show_home_page()

    root.mainloop()
