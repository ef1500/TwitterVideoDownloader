# Twitter Video Downloader
Hacky Script I made to download Twitter Videos and GIFs

I was getting frustrated with having to go to various websites to get mp4s converted into GIFs, or mp4s into mp3s. I thought it would be a fun personal project to make something I could simply use from the terminal. Without having to be bombarded by pricing options and paid services.

## Usage
```
usage: twitterDownloader.py [-h] [-s STATUS] [-t] [-m] [-r {small,medium,large}] [-f FILENAME] [-g] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -s STATUS, --status STATUS
                        Status ID for the tweet to download
  -t, --thumbnail       Also Download the thumbnail
  -m, --metadata        Add Metadata to the downloaded File
  -r {small,medium,large}, --resolution {small,medium,large}
                        Resolution to download the video at
  -f FILENAME, --filename FILENAME
                        The Filename for the video (Defaults to <screen_name>-UUID)
  -g, --gif             Convert the file into a gif after downloading (Requires Imagemagick)
  -a, --audio           Download the Audio (Requires FFMPEG)
  ```
  Examples:
  Downloading a video: `python3 twitterDownloader.py -s 1553099632606998528 -m -r="large"`
  
  Downloading a gif: `python3 twitterDownloader.py -s 1541584470368976896 -g -r="large"`
  
  Downloading audio: `python3 twitterDownloader.py -s 1553099632606998528 -a -r="large"` (use -r="large" for best audio quality)
  
