from time import localtime, sleep, strftime
from YST_lib.required import *
from YST_lib.arguments import *

def main():
    print(sep)
    print("	YouTube Stats Tool (v 1.0 by https://github.com/klubuntu)")
    print("")

    def date():
        t = localtime()
        current_time = strftime("(%d-%m-%Y) - %H:%M:%S", t)
        print(f"{bcolors.REMBOLD}{current_time}")

    def get_latest_eventid(channel_id):
        query = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&type=video&order=date&key={API_KEY}"
        response = requests.get(query)
        data = json.loads(response.text)
        return data["items"][0]["id"]["videoId"]

    def request_channel(channel_id):
        global subs, videoCount, viewCount
        query = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}"
        response = requests.get(query)
        todos = json.loads(response.text)
        try:
            subs = todos['items'][0]['statistics']['subscriberCount']
            videoCount = todos['items'][0]['statistics']['videoCount']
            viewCount = todos['items'][0]['statistics']['viewCount']
            f = open(f"{soft_dir}/channel_subscribers.txt", "w")
            f.write(subs)
            f.close()
            f = open(f"{soft_dir}/channel_videoCount.txt", "w")
            f.write(videoCount)
            f.close()
            f = open(f"{soft_dir}/channel_viewsCount.txt", "w")
            f.write(viewCount)
            f.close()
        except KeyError as e:
            print(e)
            print(f"{bcolors.FAIL}Invalid URL or Channel ID{bcolors.DEFAULT}")
            exit(sep)

    def request_video(video_id):
        global views,likes,comments
        query2 = x = f'https://youtube.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}'
        response2 = requests.get(query2)
        todos2 = json.loads(response2.text)
        try:
            views = todos2['items'][0]['statistics']['viewCount']
            likes = todos2['items'][0]['statistics']['likeCount']
            comments = todos2['items'][0]['statistics']['commentCount']
            f = open(f"{soft_dir}/video_likes.txt", "w")
            f.write(likes)
            f.close()
            f = open(f"{soft_dir}/video_views.txt", "w")
            f.write(views)
            f.close()
            f = open(f"{soft_dir}/video_comments.txt", "w")
            f.write(views)
            f.close()
        except IndexError as e:
            # print(e)
            print(f"{bcolors.FAIL}Invalid URL or Video ID{bcolors.DEFAULT}")
            exit(sep)
    def test():
        print(1)
    def result():
        print(f"{bcolors.DEFAULT}{bcolors.LIGHTGREEN}Subscribers: {subs}")
        print(f"{bcolors.OKCYAN}Channel Views: {viewCount}")
        print(f"{bcolors.OKBLUE}Channel Videos: {videoCount}")
        print(f"{bcolors.HEADER}Video Likes: {likes}")
        print(f"{bcolors.FAIL}Video Comments: {comments}")
        print(f"{bcolors.WARNING}Video Views: {views}{bcolors.DEFAULT}")
        print("")
    try:
        if (arguments2.get('channel_id')):
             channel_id = arguments2.get('channel_id')
        if (arguments2.get('video_id')):
             video_id = arguments2.get('video_id')
        #video_id = arguments.get('video_id') if 'video_id' in arguments and arguments['video_id'] is not None else ""
        log_mode = arguments['log_mode'] if arguments['log_mode'] is not None else False
        latest_video = arguments.get('latest_video') if 'latest_video' in arguments and arguments['latest_video'] is not None else False
        if (latest_video):
           video_id = get_latest_eventid(channel_id)
                
            
        if not (log_mode):
            progress = "-"
            print(f"Start Logging to Folder {soft_dir}")
            while(True):
                request_channel(channel_id)
                request_video(video_id)
                print(f'{bcolors.WARNING}{progress}', end='\r')
                progress = progress + "-"
                if (progress == "------------------------------------------------------------"):
                    progress = "-"
                sleep(sleep_time)
        else:
            while(True):
                date()
                request_channel(channel_id)
                request_video(video_id)
                result()
                sleep(sleep_time)
                
          

    except KeyboardInterrupt:
        print(
            f"{bcolors.FAIL}                          User Exit                {bcolors.DEFAULT}")


if __name__ == '__main__':

    try:
        get_eventid(channel_id)
        # main()
        
    except KeyboardInterrupt:
        print(sep)
        try:
          sys.exit(0)
        except SystemExit:
          os._exit(0)
