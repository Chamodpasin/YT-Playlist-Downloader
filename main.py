import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import threading
import re
import time

# Function to check and install packages
def check_install(package, install_command):
    try:
        # Check if the package is installed
        subprocess.run([package, '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{package} is already installed.")
    except subprocess.CalledProcessError:
        print(f"{package} is not installed. Installing...")
        # Install the package
        subprocess.run(install_command, shell=True)
        print(f"{package} installation complete.")

# Check for yt-dlp
check_install("yt-dlp", "pip install yt-dlp")

# Check for ffmpeg (different method for system-wide package)
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("ffmpeg is already installed.")
        return True
    except subprocess.CalledProcessError:
        print("ffmpeg is not installed.")
        return False

# If ffmpeg is not installed, guide the user to install it
if not is_ffmpeg_installed():
    if sys.platform.startswith("win"):
        print("Please install ffmpeg manually from https://ffmpeg.org/download.html and add it to your system PATH.")
    else:
        print("You can install ffmpeg with the following command: sudo apt install ffmpeg")

def browse_directory():
    folder_selected = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_selected)

def clear_fields():
    """Clear all input fields."""
    link_entry.delete(0, tk.END)
    path_entry.delete(0, tk.END)
    start_entry.delete(0, tk.END)
    end_entry.delete(0, tk.END)
    quality_var.set("1080")
    progress_var.set(0)
    progress_label.config(text="Ready")
    speed_label.config(text="Speed: ")

def download():
    def run_download():
        link = link_entry.get()
        path = path_entry.get()
        quality = quality_var.get()
        start = start_entry.get() if start_entry.get() else "1"  # Default to 1
        end = end_entry.get() if end_entry.get() else "-1"  # Default to last video

        # Check if the path exists
        if not os.path.exists(path):
            messagebox.showerror("Error", "Invalid path. Please enter a valid directory path.")
            return

        if not link:
            messagebox.showerror("Error", "Please enter the link.")
            return

        # Disable clear button during download
        download_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)

        # If MP3 is selected
        if quality == "mp3":
            code = f'yt-dlp -x --audio-format mp3 --playlist-start {start} --playlist-end {end} -P "{path}" {link}'
        else:
            d_code = "yt-dlp -f"
            code = f'{d_code} "bestvideo[height={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height={quality}]" --merge-output-format mp4 --playlist-start {start} --playlist-end {end} -P "{path}" {link}'

        print(f"Running: {code}")

        try:
            # Run yt-dlp command
            process = subprocess.Popen(code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                # Check if the line contains percentage info and update progress
                match = re.search(r'(\d{1,3}\.\d)%', line)
                speed_match = re.search(r'\s(\d+\.\d+\w{1,2}/s)', line)  # Matches download speed
                if match:
                    percentage = float(match.group(1))
                    progress_var.set(percentage)  # Update the progress bar
                    progress_label.config(text=f"Downloading: {percentage:.2f}%")
                if speed_match:
                    speed = speed_match.group(1)
                    speed_label.config(text=f"Speed: {speed}")
                time.sleep(0.1)  # To prevent UI freezing

            process.wait()  # Wait for the command to complete

            if process.returncode == 0:
                progress_label.config(text="Download complete!")
                progress_var.set(100)  # Set progress bar to 100%
            else:
                messagebox.showerror("Error", "Download failed.")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Download failed: {e}")

        # Re-enable clear and download buttons after download completes
        download_button.config(state=tk.NORMAL)
        clear_button.config(state=tk.NORMAL)

    # Run the download in a separate thread
    threading.Thread(target=run_download).start()

# Create the main window
root = tk.Tk()
root.title("DMCP YT Playlist Downloader")

# Set window icon (logo must be in the same directory)
logo_path = os.path.join(os.path.dirname(__file__), 'logo.ico')
if os.path.exists(logo_path):
    root.iconbitmap(logo_path)

# Link of Playlist
link_label = tk.Label(root, text="Link of Playlist:")
link_label.grid(row=0, column=0, padx=5, pady=5)

link_entry = tk.Entry(root, width=50)
link_entry.grid(row=0, column=1, padx=5, pady=5)

# Path
path_label = tk.Label(root, text="Path:")
path_label.grid(row=1, column=0, padx=5, pady=5)

path_entry = tk.Entry(root, width=50)
path_entry.grid(row=1, column=1, padx=5, pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.grid(row=1, column=2, padx=5, pady=5)

# Start Number
start_label = tk.Label(root, text="Playlist Start Number:")
start_label.grid(row=2, column=0, padx=5, pady=5)

start_entry = tk.Entry(root, width=10)
start_entry.grid(row=2, column=1, padx=5, pady=5)

# End Number
end_label = tk.Label(root, text="Playlist End Number:")
end_label.grid(row=3, column=0, padx=5, pady=5)

end_entry = tk.Entry(root, width=10)
end_entry.grid(row=3, column=1, padx=5, pady=5)

# Quality
quality_label = tk.Label(root, text="Quality:")
quality_label.grid(row=4, column=0, padx=5, pady=5)

quality_var = tk.StringVar(value="1080")
quality_options = ["1080", "720", "480", "360", "240", "144", "mp3"]
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, values=quality_options)
quality_dropdown.grid(row=4, column=1, padx=5, pady=5)

# Download and Clear buttons side by side
buttons_frame = tk.Frame(root)
buttons_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=10)

download_button = tk.Button(buttons_frame, text="Download", command=download)
download_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(buttons_frame, text="Clear", command=clear_fields)
clear_button.pack(side=tk.LEFT, padx=5)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=400)  # Increased length
progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Status and Progress
progress_label = tk.Label(root, text="Ready")
progress_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

# Speed Label (Download Speed at Bottom Right)
speed_label = tk.Label(root, text="Speed: ")
speed_label.grid(row=8, column=2, padx=5, pady=5, sticky='e')  # Aligned to bottom right

# Run the main loop
root.mainloop()
