import os
import shutil
import requests
import tkinter as tk

from tkinter.filedialog import askopenfilename

path = "playlist.m3u8"
url  = "https://videourl.com/12345_mp4_h264_aac_hq_6.m3u8"

session = requests.Session()
session.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36"}
requests.packages.urllib3.disable_warnings()  # turn off SSL warnings
try:
    r = session.get(url, stream=True, verify=False)
    with open(path, "wb") as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
except Exception as e:
    print(e)

tk.Tk().withdraw() # skip root window
path = askopenfilename(filetypes=(("playlist","*.m3u8"),))
if path:
    url = url.split("/sec")[0]
    with open(path) as f:
        data = f.read()
    with open(path, "w") as f:
        slug = url.split("/sec")[0] + "/sec"
        f.write(data.replace("/sec", slug))
    os.system("ffmpeg -protocol_whitelist \"file,http,https,tcp,tls\" -i {} -c copy -bsf:a aac_adtstoasc out.mp4".format(path))
