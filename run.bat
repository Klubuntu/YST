@echo off
set PATH=C:\Python\Python38;%PATH%

@REM echo Enter Video ID 
@REM set /p videoid=Video ID:
@REM 2RJFvNU08-4
set videoid=Xknt3_QJY7o

python YST.py -channel_id=UCifZaTQPiHE2QRgEwDNfhug -video_id=%videoid% -sleep_time=3 -log_mode=True