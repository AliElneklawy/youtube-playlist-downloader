from tkinter import filedialog as fd
from tkinter.filedialog import Tk
from os import remove, sys, rename, system
from os.path import join
from string import punctuation
from pytube import YouTube, Playlist
import pyinputplus as pyip
import moviepy.editor as movie
from constants import *
from ffmpeg import concat, input
import pafy
pafy.backend = "yt_dlp"
import time
import urllib.error
import yt_dlp
import re


class DowloadErr(Exception):
    pass

class CaptionDowloadErr(Exception):
    pass


class Downloader:
    """
    This class is used to download videos, playlists, audios and captions from Youtube
    and covert some video formats (mkv and mp4) to mp3.

    methods:-
        _undownloaded_videos(self, undownloaded_vids_urls, file_path)

        available_captions(self, url)

        Video_downloader(self, url, quality, file_path, i="")

        Playlist_downlaoder(self, url, quality, file_path)

        download_captions(self, url, file_path, lang_code)

        extract_audio(self, url)

        converter(self, file_path, file_name)
    """

    def __init__(self) -> None:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

    def __check_invalid_title(self, title):
        for char in title:
            if char in punctuation:
                title = title.replace(char, " ")
        return title

    def __show_info(self, yt, choice, pafy_url=None, quality="720p"):
        self.quality_int = int(quality.replace("p", ""))
        if choice == 1:
            print(
                f"""\n
                Title: {pafy_url.title}
                Duration: {pafy_url.duration}
                Number of views: {pafy_url.viewcount:,} views
                Size: {round((yt.streams.get_by_resolution(quality).filesize)/1024/1024, 2) 
                        if self.quality_int == 720 or self.quality_int == 360
                        else round((yt.streams.get_by_itag(itags[quality]).filesize)/1024/1024, 2)} MB
                """
            )
        elif choice == 2:
            print(
                f"""\n
                Number of videos: {yt.length}
                Total number of views: {yt.views:,}
                Last updated: {yt.last_updated}
                """
            )
        elif choice == 3:
            print(
                f"""\n
                Title: {pafy_url.title}
                Duration: {pafy_url.duration}
                Number of views: {pafy_url.viewcount:,} views
                Size: {round((pafy_url.getbestaudio().get_filesize())/1024/1024, 2)} MB
                """
            )

    def __progress_function(self, chunk=None, file_handling=None, bytes_remaining=None, dlp=None):
        global filesize
        if dlp is None:
            filesize = chunk.filesize
            current = (filesize - bytes_remaining) / filesize
            percent = ("{0:.1f}").format(current * 100)
            progress = int(50 * current)
            status = "█" * progress + "-" * (50 - progress)
            if bytes_remaining == 0:
                status = "\033[92m" + status + "\033[0m"
            sys.stdout.write(" ↳ |{bar}| {percent}%\r".format(bar=status, percent=percent))
            sys.stdout.flush()
        else:
            status = ""
            if dlp['status'] == 'downloading':
                p = dlp['_percent_str']
                percent = float(re.sub(r'\x1b\[.*?m', '', dlp['_percent_str']).replace('%', '').strip())
                progress = int(50 * percent / 100)
                status = "█" * progress + "-" * (50 - progress)
                sys.stdout.write(f" ↳ |{status}| {p}\r")
                sys.stdout.flush()
            elif dlp['status'] == 'finished':
                status = "\033[92m" + status + "\033[0m"


    def _undownloaded_videos(self, undownloaded_vids_urls, file_path):
        """
        Videos that were not downloaded for any reason will be handeled here
        undownloaded_vids: list of the names of the undownloaded videos
        undownloaded_vids_urls: list of the URLs of the undownloaded videos
        """
        choice = pyip.inputMenu(
            ["Re-download the videos that were not downloaded", "Return"],
            "\nDo you want to download them again? \n",
            numbered=True,
        )

        if choice == "Re-download the videos that were not downloaded":
            i = -4
            while undownloaded_vids_urls != deque([]):
                check = self.Video_downloader(
                    undownloaded_vids_urls[0][0],
                    Qualities[i],
                    file_path,
                    undownloaded_vids_urls[0][1],
                )
                if check == 1:
                    undownloaded_vids_urls.pop()
                    i -= 1
                    if i == -8:
                        undownloaded_vids_urls.popleft()
                        i = -4
                        raise DowloadErr
                else:
                    undownloaded_vids_urls.popleft()
                    i = -4
        elif choice == "Return":
            undownloaded_vids_urls.clear()
            return

    def available_captions(self, url):
        """
        Check if there are captions available for the video
        :param url: url of the youtube video
        """
        yt = YouTube(url)
        cap = yt.captions
        langs = {}
        for capt in cap:
            if "(auto-generated)" in capt.name:
                continue
            langs.update({capt.name: capt.code})
        if len(langs) > 0:
            lang = pyip.inputMenu(list(langs), "Choose a language: \n", numbered=True)
            return langs[lang]
        return False

    def Video_downloader(self, url, quality, save_path, add_numbering="No", i=""):
        """
        Download videos from youtube
        :param url: URL of the video
        :param quality: the quality chosen by the user
        :param save_path: the file path to save the files
        :param i: used to number the videos when downloading playlists,
            default = "" for downloading one video
        """
        yt = YouTube(url, on_progress_callback=self.__progress_function)
        pafy_url = pafy.new(url)
        title = self.__check_invalid_title(pafy_url.title)
        stream = yt.streams.filter(resolution=quality).first()
        if not stream:
            undownloaded_vids_urls.append([url, i])
            print(
                f"Could not download video: {title}. Quality {quality} not available."
            )
            return 1

        self.__show_info(yt, 1, pafy_url, quality)

        if add_numbering == 'Yes':
        	title = f"{i} " + title

        max_retries, delay = 3, 5
        quality_int = self.quality_int
        for _ in range(max_retries):
            try:
                if quality_int > 720 or quality_int == 480:
                    self.__download_480_1080p_or_higher(yt, title, save_path, url, stream, quality_int)
                    break

                stream.download(output_path=save_path, 
                        filename=f"{title}.mp4")
                break
            except urllib.error.URLError as e:
                print(f"Connection failed: {e}")
                time.sleep(delay)
                delay *= 2
        else:
            print(f"Failed to establish a connection after {max_retries} attempts.")

        return 2

    def __download_480_1080p_or_higher(self, yt, title, save_path, url, stream, quality_int=480):
        try:
            if quality_int == 480: format = 135
            elif quality_int == 1080: format = 399
            elif quality_int == 1440: format = 400
            elif quality_int == 2160: format = 401

            ydl_opts = {
                'format': f'{format}+bestaudio/best',
                'progress_hooks': [lambda d: self.__progress_function(dlp=d)],
                'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
            
            return
        except Exception as e:
            print()
            print(str(e))
            stream.download(output_path=save_path, 
                        filename=f"{title}.mp4")
            yt.streams.filter(only_audio=True).first().download(save_path, f"{title}.mp3")
            video_file = input(join(save_path, f"{title}.mp4"))
            audio_file = input(join(save_path, f"{title}.mp3"))
            concat(video_file, audio_file, v=1, a=1).output(
                join(save_path, f"{title} .mp4")
            ).run()
            remove(join(save_path, f"{title}.mp4"))
            remove(join(save_path, f"{title}.mp3"))

    def Playlist_downlaoder(self, url, quality, save_path, add_numbering):
        """
        Download playlists from youtube
        :param url: URL of the playlist
        :param quality: the quality chosen by the user
        :param save_path: the file path to save the files
        """
        yt = Playlist(url)

        if len(yt.video_urls) == 1:
            self.Video_downloader(yt.video_urls[0], quality, save_path, i=1)
            return

        self.__show_info(yt, 2)

        higher_range = ""
        lower_range = 1
        all_some = pyip.inputMenu(
            ["All", "Some"], "Download all or some videos: \n", numbered=True
        )
        if all_some == "Some":
            lower_range = pyip.inputNum(
                "Download from video number: ", min=1, max=yt.length
            )
            higher_range = pyip.inputNum(
                "to video number (leave it blank to download till the last video): ",
                min=lower_range + 1,
                max=yt.length,
                blank=True,
            )

        for i in range(
            lower_range, yt.length + 1 if higher_range == "" else higher_range + 1
        ):
            self.Video_downloader(yt.video_urls[i - 1], quality, save_path, add_numbering, i)

    def download_captions(self, url, save_path, lang_code):
        """
        Download captions from youtube
        :param url: URL of the video
        :param save_path: the file path to save the file
        """
        yt = YouTube(url)

        try:
            caption = yt.captions[lang_code]
        except KeyError:
            raise CaptionDowloadErr
        
        caption.generate_srt_captions()
        caption.download(title=yt.title, output_path=save_path)
        oldname = save_path + "/" + yt.title + " (" + lang_code + ")" + ".srt"
        newname = save_path + "/" + yt.title + ".srt"

        try:
            rename(oldname, newname)
        except:
            invalid_chars = punctuation
            if any(char in invalid_chars for char in yt.title):
                newname = (
                    save_path
                    + "/"
                    + yt.title.translate(str.maketrans("", "", invalid_chars))
                    + ".srt"
                )
                oldname = (
                    save_path
                    + "/"
                    + yt.title.translate(str.maketrans("", "", invalid_chars))
                    + " ("
                    + lang_code
                    + ")"
                    + ".srt"
                )
                try:
                    rename(oldname, newname)
                except (OSError, IOError):
                    raise DowloadErr(
                        "Could not rename the file. Maybe, the file already exists. Rename it manually."
                    )

    def extract_audio(self, url, save_path):
        """
        Download audio from youtube
        :param url: the url of the youtube video
        """
        yt = YouTube(url, on_progress_callback=self.__progress_function)
        pafy_url = pafy.new(url)
        self.__show_info(None, 3, pafy_url)
        
        max_retries = 5
        delay = 5
        for _ in range(max_retries):
            try:
                stream = yt.streams.get_audio_only()
                stream.download(save_path, f"{pafy_url.title}.mp3")
                break
            except:
                print(f"Connection failed. Retrying in {delay} seconds.")
                time.sleep(delay)
                delay *= 1.5
        else:
            best_quality_audio = pafy_url.getbestaudio()
            best_quality_audio.download(save_path)
            
        # try:
            # stream = yt.streams.get_audio_only()
            # stream.download(save_path, f"{pafy_url.title}.mp3")
        #except:
            # best_quality_audio = pafy_url.getbestaudio()
            # best_quality_audio.download(save_path)
        

    def converter(self, file_path, file_name):
        """convert mp4 or mkv to mp3"""
        clip = movie.VideoFileClip(file_path)
        save_file = fd.askdirectory(title="Save")
        clip.audio.write_audiofile(f"{save_file}/{file_name}.mp3")
        clip.close()
        print("Conversion completed")
