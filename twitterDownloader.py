import argparse
import twitterVoice

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-s", "--status", type=str, help="Status ID for the tweet to download")
parser.add_argument("-t", "--thumbnail", action="store_true", help="Also Download the thumbnail")
group.add_argument("-m", "--metadata", action="store_true", help="Add Metadata to the downloaded File")
parser.add_argument("-r", "--resolution", type=str, choices=["small", "medium", "large"], help="Resolution to download the video at")
parser.add_argument("-f", "--filename", type=str, help="The Filename for the video (Defaults to <screen_name>-UUID)")
group.add_argument("-g", "--gif", type=str, choices=["i", "g"], default="i",const='i', nargs='?', help="Convert the file into a gif after downloading (Requires Imagemagick and gifsicle)")
group.add_argument("-a", "--audio", action="store_true", help="Download the Audio (Requires FFMPEG)")

args=parser.parse_args()

if not args.filename:
    args.filename = None

twitterVoice.TwitterDownloader(args.status, withMeta=args.metadata, withThumbs=args.thumbnail, videoFilename=None, whatAuto=args.resolution, makegif=args.gif, audioOnly=args.audio)
