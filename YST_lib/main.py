from YST_lib.required import *
from YST_lib.arguments import *
def main():
    print(sep)
    print("	YouTube Stats Tool (v 0.8 by https://github.com/klubuntu)                 ")
    print("")

    def date():
        t = localtime()
        current_time = strftime("(%d-%m-%Y) - %H:%M:%S", t)
        print(f"{bcolors.REMBOLD}{current_time}")

    def request1():
        global subs
        global videoCount
        global viewCount
        query = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key=AIzaSyBGX0yQtfRPu9CRBEC4mZ95fnvNj00msik"
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
        except KeyError:
            print(f"{bcolors.FAIL}Invalid URL or Channel ID{bcolors.DEFAULT}")
            exit(sep)

    def request2():
        global views
        global likes
        global comments
        query2 = x = f'https://youtube.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key=AIzaSyBGX0yQtfRPu9CRBEC4mZ95fnvNj00msik'
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
        # Complete code for display video thumbnail
            #thumbnail = todos2['items']
            #print(thumbnail)
            #f = open(f"{soft_dir}/video_thumbnail.txt", "w")
            #f.write(thumbnail)
            #f.close()




        except IndexError:
            print(f"{bcolors.FAIL}Invalid URL or Video ID{bcolors.DEFAULT}")
            exit(sep)

    def result():
        print(f"{bcolors.DEFAULT}{bcolors.LIGHTGREEN}Subscribers: {subs}")
        print(f"{bcolors.OKCYAN}Channel Views: {viewCount}")
        print(f"{bcolors.OKBLUE}Channel Videos: {videoCount}")
        print(f"{bcolors.HEADER}Video Likes: {likes}")
        print(f"{bcolors.FAIL}Video Comments: {comments}")
        print(f"{bcolors.WARNING}Video Views: {views}{bcolors.DEFAULT}")
        print("")
    try:
        if not (logmode):
            progress = "-"
            print(f"Start Logging to Folder {soft_dir}")
            while(1):
                request1()
                request2()
                print(f'{bcolors.WARNING}{progress}', end='\r')
                progress = progress + "-"
                if (progress == "------------------------------------------------------------"):
                    progress = "-"
                sleep(sleep_time)
        else:
            while(1):
                date()
                request1()
                request2()
                result()
                sleep(sleep_time)

    except KeyboardInterrupt:
        print(
            f"{bcolors.FAIL}                          User Exit                {bcolors.DEFAULT}")


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print(sep)
        try:
          sys.exit(0)
        except SystemExit:
          os._exit(0)
