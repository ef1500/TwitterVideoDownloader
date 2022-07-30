# Twitter Voice Downloader
# ef1500
import requests
import re
import os
import shutil
import uuid
import subprocess
from mutagen import mp4
from mutagen.id3 import Encoding, PictureType
from mutagen.mp3 import MP3
from mutagen.mp3 import EasyMP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from dataclasses import dataclass
from collections import namedtuple
from colorama import Fore

class TwitterDownloader:
    
    # Add the Bearer Token Here
    auth = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    
    # Tuple for the Video Qualities
    sizes = namedtuple('Sizes', ['small', 'medium', 'large'])
    
    # Dataclasses for the Various URLs
    @dataclass
    class videoURL:
        size: str
        bitrate: str
        video_url: str
    
    # Dataclass for the metadata
    @dataclass
    class metadata:
        creation_date: str
        description: str
        thumbnail: str
        duration: str
        
    # Dataclass for TwitterUsers
    @dataclass
    class TwitterUser:
        author_profile_picture: str
        author_display_name: str
        author_screen_name: str
        author_user_id: str
        
    # Get the Status ID (Parse Link or Take Direct)
    @staticmethod
    def getStatusID(twitterStatus):
        # Parse twitter links
        if len(twitterStatus) > 19:
            twitterStatusID = re.match(r"(status\/)\d{19}", twitterStatus)
            if twitterStatusID:
                twitterStatus = twitterStatusID
            else:
                print(Fore.RED + 'Unable to find a Twitter Status ID.' + Fore.WHITE)
    
    # Query The API for a Guest Token
    @staticmethod
    def getGuestToken():
        headers = {"authorization" : TwitterDownloader.auth}
        tokenRequest = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
        tokenResponse = tokenRequest.json()
        return tokenResponse["guest_token"]
    
    # Now We Get the Tweet
    @staticmethod
    def getTweet(twitterStatus, token):
        videoRequestURL = f"https://twitter.com/i/api/graphql/WyMlJ14PO-bRWaO5ZNUgBA/TweetDetail?variables=%7b%22focalTweetId%22%3a%22{twitterStatus}%22%2c%22with_rux_injections%22%3afalse%2c%22includePromotedContent%22%3afalse%2c%22withCommunity%22%3afalse%2c%22withQuickPromoteEligibilityTweetFields%22%3afalse%2c%22withBirdwatchNotes%22%3afalse%2c%22withSuperFollowsUserFields%22%3afalse%2c%22withDownvotePerspective%22%3afalse%2c%22withReactionsMetadata%22%3afalse%2c%22withReactionsPerspective%22%3afalse%2c%22withSuperFollowsTweetFields%22%3afalse%2c%22withVoice%22%3afalse%2c%22withV2Timeline%22%3afalse%7d&features=%7B%22dont_mention_me_view_api_enabled%22%3Atrue%2C%22interactive_text_enabled%22%3Atrue%2C%22responsive_web_uc_gql_enabled%22%3Atrue%2C%22vibe_api_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Afalse%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D"
        videoRequestHeaders = {"authorization" : TwitterDownloader.auth, "X-Guest-Token" : token}
        videoRequest = requests.get(videoRequestURL, headers=videoRequestHeaders)
        
        if videoRequest.status_code != 200:
            print(Fore.RED + "Unable to get Tweet Metadata." + Fore.WHITE)
            
        videoMeta = videoRequest.json()
        
        #  Now Find the Entry with our desired tweet
        entryID = f"tweet-{twitterStatus}"
        entryNumber = 0
        for entry in videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"]:
            if entry["entryId"] != entryID:
                entryNumber += 1
            if entry["entryId"] == entryID:
                break
        
        # Embed Type
        VideoType = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["type"]
        
                
        # User Meta
        AuthorDisplayName = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["name"]
        AuthorScreenName = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["screen_name"]
        AuthorProfilePicture = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["legacy"]["profile_image_url_https"].replace("_normal", "")
        AuthorUserID = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]["rest_id"]
        
        # Video Meta
        VideoCreatedAt = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["created_at"]
        VideoThumbnail = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["media_url_https"]
        
        # Get the Video Resolution Sizes
        VideoResolutionLarge = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["large"]["w"].__str__() + " x " + videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["large"]["h"].__str__()
        VideoResolutionMedium = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["medium"]["w"].__str__() + " x " + videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["medium"]["h"].__str__()
        VideoResolutionSmall = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["small"]["w"].__str__() + " x " + videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["entities"]["media"][0]["sizes"]["small"]["h"].__str__()
        
        if VideoType == "video":
            variants = list()
            for variant in range(len(videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"])):
                if videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"][variant]["content_type"] == "video/mp4":
                    variants.append((videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"][variant]["bitrate"], videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][0]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"][variant]["url"]))
            variants.sort(key=lambda x: x[0], reverse=True) # Sort for the Highest Resolution Video
            VideoLargeURL = variants[0][1]
            VideoLargeBitrate = variants[0][0]
            VideoMediumURL = variants[1][1]
            VideoMediumBitrate = variants[1][0]
            VideoSmallURL = variants[2][1]
            VideoSmallBitrate = variants[2][0]
            VideoDurationMillis =  videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["duration_millis"]

        # Change the code up if we're downloading an Animated GIF    
        if VideoType == "animated_gif" or VideoType == "photo":
            # With GIF, it's all the same, so we can just set all three to the same thing no issue.
            VideoUrl = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"][0]["url"]
            VideoBitrate = videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][entryNumber]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["extended_entities"]["media"][0]["video_info"]["variants"][0]["bitrate"]
            VideoDurationMillis = 0
            VideoLargeURL, VideoMediumURL, VideoSmallURL = VideoUrl, VideoUrl, VideoUrl
            VideoLargeBitrate, VideoMediumBitrate, VideoSmallBitrate = VideoBitrate, VideoBitrate, VideoBitrate
        
        # Get the Tweet Text and Remove the URL ar the end
        VideoDescription = re.sub(r"https://t\.co/\S{10}$", "", videoMeta["data"]["threaded_conversation_with_injections"]["instructions"][0]["entries"][0]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"])
        
        # Put Everything in their Proper Dataclass
        VideoSizes = TwitterDownloader.sizes(TwitterDownloader.videoURL(VideoResolutionSmall, VideoSmallBitrate, VideoSmallURL), TwitterDownloader.videoURL(VideoResolutionMedium, VideoMediumBitrate, VideoMediumURL), TwitterDownloader.videoURL(VideoResolutionLarge, VideoLargeBitrate, VideoLargeURL))        
        TwitterAuthor = TwitterDownloader.TwitterUser(AuthorProfilePicture, AuthorDisplayName, AuthorScreenName, AuthorUserID)
        Video_Metadata = TwitterDownloader.metadata(VideoCreatedAt, VideoDescription, VideoThumbnail, VideoDurationMillis)
        
        return(TwitterAuthor, VideoSizes, Video_Metadata)
    
    # Download a File
    @staticmethod
    def downloadFile(url, filename, location):
        filedata = requests.get(url, stream=True)
        with open(os.path.join(location, filename), 'wb') as out_file:
            shutil.copyfileobj(filedata.raw, out_file)
            
    # Add Audio Metadata
    @staticmethod
    def addAudioMeta(AudioFile, DownloadPath, TwitterAuthor, VideoMetadata):
        pfp_filename = f"{uuid.uuid4().hex}.jpg"
        TwitterDownloader.downloadFile(TwitterAuthor.author_profile_picture, pfp_filename, DownloadPath)
        
        mp3_meta = EasyMP3(os.path.join(DownloadPath, AudioFile))
        EasyID3.RegisterTXXXKey("description", "COMM")
        mp3_meta["artist"] = TwitterAuthor.author_display_name
        mp3_meta["album"] = TwitterAuthor.author_screen_name
        mp3_meta["albumartist"] = "https://github.com/ef1500"
        mp3_meta["description"] = VideoMetadata.description
        mp3_meta.save()
        
        # Add Cover art
        mp3_art = ID3(os.path.join(DownloadPath, AudioFile)) 
        with open(os.path.join(DownloadPath, pfp_filename), 'rb') as albumart:
            mp3_art['APIC'] = APIC(
                            encoding=Encoding.UTF8,
                            mime='image/jpeg',
                            type=PictureType.COVER_FRONT, desc=u'Cover',
                            data=albumart.read()
                            )
        mp3_art.save(v2_version=3, v1=2)
        os.remove(os.path.join(DownloadPath, pfp_filename))
        
    # Generate the audio File
    @staticmethod
    def generateAudio(VideoFile, DownloadPath, audioFilename, TwitterAuthor, VideoMetadata):
        command = f"ffmpeg -i \"{os.path.join(DownloadPath, VideoFile)}\" -q:a 0 -map a \"{os.path.join(DownloadPath, audioFilename)}\" -loglevel quiet"
        subprocess.run(command, cwd=DownloadPath)
        os.remove(os.path.join(DownloadPath, VideoFile))
        TwitterDownloader.addAudioMeta(audioFilename, DownloadPath, TwitterAuthor, VideoMetadata)
    
    # Add video Metadata     
    @staticmethod
    def addMetadata(VideoFile, DownloadPath, TwitterAuthor, VideoMetadata):
        mp4_meta = mp4.MP4(os.path.join(DownloadPath, VideoFile))
        mp4_meta['\xa9ART'] = TwitterAuthor.author_display_name
        mp4_meta['desc'] = VideoMetadata.description
        mp4_meta['\xa9alb'] = TwitterAuthor.author_screen_name
        mp4_meta['\xa9too'] = "https://github.com/ef1500"
        mp4_meta.save()
        
    # Generate a GIF from an MP4
    @staticmethod
    def generateGIF(VideoFile, DownloadPath, gifFilename):
        command = f"magick -quiet -delay 1 \"{os.path.join(DownloadPath, VideoFile)}\" -layers OptimizeTransparency +remap \"{os.path.join(DownloadPath, gifFilename)}.gif\""
        subprocess.run(command, cwd=DownloadPath)
        os.remove(os.path.join(DownloadPath, VideoFile))
        
    @staticmethod
    def generateGIF_gifsicle(VideoFile, DownloadPath, gifFilename):
        gifName = f"{gifFilename}.gif"
        command = f"magick -quiet -delay 1 \"{os.path.join(DownloadPath, VideoFile)}\" -layers OptimizeTransparency +remap \"{os.path.join(DownloadPath, gifName)}\""
        optimizeCommand = f"gifsicle -O3 --lossy=80 --colors 256 \"{os.path.join(DownloadPath, gifName)}\" -o \"{os.path.join(DownloadPath, gifFilename)}_optimized.gif\""
        subprocess.call(command, cwd=DownloadPath)
        subprocess.run(optimizeCommand, cwd=DownloadPath)
        os.remove(os.path.join(DownloadPath, VideoFile))
        os.remove(os.path.join(DownloadPath, gifName))
    
    # Download the Necessary Files
    @staticmethod
    def downloadPrompt(TwitterAuthor, VideoSizes, Video_Metadata, downloadPath=os.getcwd(), withMeta=False, withThumbs=None, videoFilename=None, auto="large", makeGIF=None, audioOnly=False):
        slowMap = {
            "large" : VideoSizes.large.video_url,
            "medium" : VideoSizes.medium.video_url,
            "small" : VideoSizes.small.video_url            
        }
        
        if videoFilename == None:
            videoFilename = f"{TwitterAuthor.author_screen_name}-{uuid.uuid4().hex}.mp4"
        if makeGIF != None:
            gifFilename = f"{TwitterAuthor.author_screen_name}-{uuid.uuid4().hex}"
        if audioOnly == True:
            audioFilename = f"{TwitterAuthor.author_screen_name}-{uuid.uuid4().hex}.mp3"
        thumbnail_filename = f"{videoFilename}_thumb.jpg"
        

        video = slowMap[auto]
        TwitterDownloader.downloadFile(video, videoFilename, downloadPath)

        if withThumbs == True:
            TwitterDownloader.downloadFile(Video_Metadata.thumbnail, thumbnail_filename, downloadPath)
        
        if withMeta == True:
            TwitterDownloader.addMetadata(videoFilename, downloadPath, TwitterAuthor, Video_Metadata)
            
        if makeGIF == "i":
            TwitterDownloader.generateGIF(videoFilename, downloadPath, gifFilename)
            
        if makeGIF == "g":
            TwitterDownloader.generateGIF_gifsicle(videoFilename, downloadPath, gifFilename)
            
        if audioOnly == True:
            TwitterDownloader.generateAudio(videoFilename, downloadPath, audioFilename, TwitterAuthor, Video_Metadata)
                
    def __init__(self, StatusID, withMeta, withThumbs, videoFilename, whatAuto, makegif, audioOnly):
        token = TwitterDownloader.getGuestToken()
        tweet = TwitterDownloader.getTweet(StatusID, token)
        TwitterDownloader.downloadPrompt(tweet[0], tweet[1], tweet[2], os.getcwd(), withMeta, withThumbs, videoFilename, auto=whatAuto, makeGIF=makegif, audioOnly=audioOnly)
