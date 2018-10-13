import youtube_dl

vid_url = "https://www.youtube.com/watch?v=0HJEARRKNxM"  # HEBREW
# vid_url = "https://www.youtube.com/watch?v=N3oCS85HvpY" #WORKS

ydl_opts = {
    'quiet': True,
}

ydl = youtube_dl.YoutubeDL(ydl_opts)
with ydl:
    r = ydl.extract_info(vid_url, download=False)  # don't download, much faster

print(r['artist'] + " , " + r['track'])
print(r['title'])

# TODO

### CHECK HEBREW NAMES and log file and writing and etc...
### need to parse title if one of them is empty




