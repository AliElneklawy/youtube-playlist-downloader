from collections import deque

Qualities = ["240", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
itags = {"240p": 133, "480p": 135, "1080p": 137, "1440p": 271, "2160p": 313}
undownloaded_vids_urls = deque()
