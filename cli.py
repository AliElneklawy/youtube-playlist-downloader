import argparse
from oopYPLD import *



def main():
    parser = argparse.ArgumentParser(description="Youtube Downloader")

    parser.add_argument(
        '-v',
        '--video',
        help='Download a video',
    )

    parser.add_argument(
        '-p',
        '--playlist',
        help='Download a playlist',
    )

    parser.add_argument(
        '-a',
        '--audio',
        help='Download the audio file',
    )

    parser.add_argument(
        '-c',
        '--captions',
        help='Download captions',
        default='en',
    )

    parser.add_argument(
        "-q",
        "--quality",
        help="The quality of the video to download. Defualt 720p",
        choices=Qualities,
        default="720p",
    )

    parser.add_argument(
        "-s",
        "--save_path",
        help="The path to save the downloaded files. Default curretn working directory",
        default=".",
    )

    args = parser.parse_args()
    oDownloader = Downloader()

    if args.video:
       # print(args.video)
        #print(args.quality)
        #print(args.save_path)
        oDownloader.Video_downloader(args.video, args.quality, args.save_path)
    elif args.playlist:
        oDownloader.Playlist_downlaoder(args.url, args.quality, args.save_path)
    elif args.audio:
        oDownloader.extract_audio(args.audio, args.save_path)
    elif args.captions:
        oDownloader.download_captions(args.captions, args.save_path)

if __name__ == '__main__':
    main()
