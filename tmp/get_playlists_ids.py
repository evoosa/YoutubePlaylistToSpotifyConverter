import youtube_dl

pl_url = "https://www.youtube.com/watch?v=2PkrftWoluU&list=PL_YrT8uPt_neh98FvB1RIpYuGfZdCXxDB"  # HEBREW
ydl_opts = {'quiet': True}
ydl = youtube_dl.YoutubeDL(ydl_opts)

with ydl:
    playlist_metadata = ydl.extract_info(pl_url, download=False)
    videos = playlist_metadata['entries']
    for i in range(len((videos))):
        video_metadata = videos[i]
        print(video_metadata['']) # ID, title, artist, track