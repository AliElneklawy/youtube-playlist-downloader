import argparse
from oopYPLD import *



def main():
    parser = argparse.ArgumentParser(description="Youtube Downloader")

    parser.add_argument(
        '-v',
        '--video',
        help='Download a video',
        required=True
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
        default='en'
    )

    parser.add_argument(
        "-q",
        "--quality",
        help="The quality of the video to download",
        choices=Qualities,
        default="720p",
    )

    parser.add_argument(
        "-s",
        "--save_path",
        help="The path to save the downloaded files",
        default=".",
    )

    args = parser.parse_args()
    oDownloader = Downloader()

    if args.video:
        oDownloader.Video_downloader(args.video, args.quality, args.save_path)

if __name__ == '__main__':
    main()
