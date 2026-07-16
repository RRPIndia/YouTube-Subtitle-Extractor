#!/data/data/com.termux/files/usr/bin/python3
# Improved version of the user's script.
import json
import os
import re
import subprocess
from datetime import datetime
from glob import glob
from time import sleep
from typing import List, Optional
import shutil

import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

CHANNEL_FILE="/data/data/com.termux/files/home/storage/shared/YouTube-Subtitle-Extractor/channels.txt"
ARCHIVE_FILE="/data/data/com.termux/files/home/storage/shared/projects/YouTube-Subtitle-Extraxtor/archive.txt"
LOG_FILE="/data/data/com.termux/files/home/storage/shared/projects/YouTube-Subtitle-Extraxtor/log.txt"


YTDLP = shutil.which("yt-dlp")
if YTDLP is None:
    raise RuntimeError("yt-dlp not found in PATH")
cmd = [YTDLP, ...]

def ran_at(log_file):
    with open(log_file,"a",encoding="utf-8") as f:
        f.write(str(datetime.now())+"\n")

def channel_list(path)->List[str]:
    try:
        with open(path,"r",encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Channel file not found.")
        return []

def read_json(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"JSON error {path}: {e}")
        return None

def get_link_to_file(channel_url):
    print(f"Checking {channel_url}")
    cmd=[
        "cmd","--simulate","--sleep-interval","10","--no-quiet",
        "--lazy-playlist","--dateafter","now-20day","--break-on-reject",
        "--force-write-archive","--download-archive",ARCHIVE_FILE,
        "--print-to-file",
        '%(.{channel,title,upload_date,webpage_url})#j',
        f'📺 @{channel_url.split("/")[-1]} || %(title)s || 📆 %(upload_date>%Y-%m-%d)s || yt_subtitle.json',
        channel_url
    ]
    subprocess.run(cmd,capture_output=True,text=True)

def make_json_files_of_urls(channels):
    for c in channels:
        get_link_to_file(c)

def get_files():
    return glob("*yt_subtitle.json")

def send_to_tg(message):
    token=os.getenv("BOT_TOKEN")
    chat=os.getenv("CHAT_ID")
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r=requests.post(url,data={"chat_id":chat,"text":message,"parse_mode":"HTML"},timeout=30)
        print(r.status_code)
    except Exception as e:
        print(e)

def get_id(url)->Optional[str]:
    m=re.findall(r"(?:v=|/)([0-9A-Za-z_-]{11}).*",url)
    return m[0] if m else None

def get_subtitle(vid):
    try:
        t=YouTubeTranscriptApi.get_transcript(vid,languages=("hi","en"),preserve_formatting=True)
        return " ".join(x["text"] for x in t)
    except Exception as e:
        print(f"Subtitle error: {e}")
        return None

def save_to_device(filename,channel,year,month,text):
    folder=f"subtitles/{channel}/{year}/{month}"
    os.makedirs(folder,exist_ok=True)
    out=os.path.splitext(filename)[0]+".txt"
    with open(os.path.join(folder,out),"w",encoding="utf-8") as f:
        f.write(text)

def split_subtitle(text,max_chars=4000):
    words=text.split()
    parts=[]
    cur=""
    for w in words:
        if len(cur)+len(w)+1<=max_chars:
            cur+=(" " if cur else "")+w
        else:
            parts.append(cur)
            cur=w
    if cur:
        parts.append(cur)
    return parts

def main():
    channels=channel_list(CHANNEL_FILE)
    print(f"{len(channels)} channels")
    make_json_files_of_urls(channels)
    sleep(10)
    for file in get_files():
        try:
            data=read_json(file)
            if not data:
                continue
            title=data.get("title","No Title")
            url=data.get("webpage_url","")
            upload=data.get("upload_date","Unknown")
            year=upload[:4]
            month=upload[4:6]
            channel=data.get("channel","Unknown")
            vid=get_id(url)
            subtitle=get_subtitle(vid) if vid else None
            if subtitle is None:
                subtitle="No Subtitle"
            msg=f"<b>{title}</b>\n📅 {upload}\n📺 {channel}\n🔗 {url}"
            send_to_tg(msg)
            save_to_device(file,channel,year,month,msg+"\n\n"+subtitle)
            for i,part in enumerate(split_subtitle(subtitle),1):
                print(f"Sending {i}")
                send_to_tg(part)
            os.remove(file)
        except Exception as e:
            print(f"Failed {file}: {e}")
            continue
    ran_at(LOG_FILE)

if __name__=="__main__":
    main()
