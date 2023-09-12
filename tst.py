import yt_dlp
import sys
import re
import pandas as pd

def __progress_function(d):
    """
    method to show the progress of the download
    """
    if d['status'] == 'downloading':
        p = d['_percent_str']
        percent = float(re.sub(r'\x1b\[.*?m', '', d['_percent_str']).replace('%','').strip())
        progress = int(50 * percent / 100)
        status = "█" * progress + "-" * (50 - progress)
        sys.stdout.write(f" ↳ |{status}| {p}\r")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\nDone downloading, now converting ...")


def my_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading {d['filename']}")

ydl_opts = {
    'format': '135+bestaudio/best',
    'progress_hooks': [__progress_function],
}

url = ['https://www.youtube.com/watch?v=Qc7_zRjH808']  # replace with your URLs

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(url)
