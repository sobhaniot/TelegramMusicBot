import os
import pprint
import random
import time

import requests

def send_music_package(self):
    """
    info شامل مسیر فایل‌ها است:
    info["cover"]  → عکس آهنگ
    info["OGG"]    → فایل ویس OGG
    info["MP3"]    → فایل کامل mp3
    """

    print(self.config)
    token = self.config["telegram_token"]
    chat_id = self.config["telegram_chat_id"]
    delay = self.config["send_delay"]
    daily_limit = int(self.config["daily_count"])

    BASE_URL = "https://api.telegram.org/bot" + token + "/"

    music_list = list(self.music_dict.items())
    random.shuffle(music_list)

    send_count = min(daily_limit, len(music_list))

    for index in range(send_count):
        music_name, info = music_list[index]

        print(f"\n=== Sending music {index + 1}/{send_count} ===")
        pprint.pprint(info)

        # 1) ارسال عکس
        if info.get("cover") and os.path.exists(info["cover"]):
            resCover = send_pic(BASE_URL, chat_id, info["cover"], info["caption"])

        # 2) ارسال ویس OGG
        if info.get("OGG") and os.path.exists(info["OGG"]):
            resOGG = send_voice(BASE_URL, chat_id, info["OGG"], info["caption"])

        # 3) ارسال MP3 کامل
        if info.get("MP3") and os.path.exists(info["MP3"]):
            resMP3 = send_audio(BASE_URL, chat_id, info["MP3"], info["caption"])

        print(resCover)
        print(resOGG)
        print(resMP3)
        if resCover["ok"] and resOGG["ok"] and resMP3["ok"]:
            os.remove(info["MP4"])
            print("Deleted:", info["MP4"])

        # اگر delay تنظیم شده باشد
        if delay and delay > 0:
            time.sleep(delay)


def send_pic(BASE_URL, chat_id: int, photo_name: str, caption: str = ""):
    url = BASE_URL + "sendPhoto"

    with open(photo_name, "rb") as photo:
        files = {"photo": photo}
        params = {"chat_id": chat_id, "caption": caption}

        response = requests.post(url, data=params, files=files)

    return response.json()


def send_voice(BASE_URL, chat_id: int, voice_name: str, caption: str = ""):
    url = BASE_URL + "sendVoice"

    with open(voice_name, "rb") as voice:
        files = {"voice": voice}
        params = {"chat_id": chat_id, "caption": caption}

        response = requests.post(url, data=params, files=files)

    return response.json()


def send_audio(BASE_URL, chat_id: int, audio_name: str, caption: str = "", duration: int = 0):
    url = BASE_URL + "sendAudio"

    with open(audio_name, "rb") as audio:
        files = {"audio": audio}
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
        }

        # تلگرام خودش duration را تشخیص می‌دهد، لازم نیست حتماً بسپاری
        if duration > 0:
            payload["duration"] = duration

        response = requests.post(url, data=payload, files=files)

    return response.json()


