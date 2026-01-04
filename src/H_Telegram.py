import os
import pprint
import random
import time
import requests

debug = False

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



    #send intro pic and caption
    if not debug:
        resIntro = safe_send(
            send_intro,
            BASE_URL,
            chat_id,
            self.config["intro_pic_folder"],
            MSG="Sending Intro"
        )

    for index in range(send_count):
        music_name, info = music_list[index]

        print(f"\n=== Sending music {index + 1}/{send_count} ===")
        pprint.pprint(info)

        if debug:
            return
        # 1) ارسال عکس

        resCover = safe_send(
            send_pic,
            BASE_URL,
            chat_id,
            info["cover"] if info.get("cover") and os.path.exists(info["cover"]) else info["default_cover"],
            info["caption"] + "\n" + info.get("hashtag") + "\n\n👽@TechnoHouseRapMusic ☠️☠️",
            MSG="Sending Cover"
        )
        # 2) ارسال ویس OGG
        resOGG = safe_send(
            send_voice,
            BASE_URL,
            chat_id,
            info["OGG"],
            info["caption"],
            MSG="Sending OGG"
        )

        # 3) ارسال MP3 کامل
        resMP3 = safe_send(
            send_audio,
            BASE_URL,
            chat_id,
            info["MP3"],
            info["caption"] + "\n\n👽@TechnoHouseRapMusic ☠️☠️",
            MSG="Sending MP3"
        )

        print(resCover)
        print(resOGG)
        print(resMP3)
        if resCover["ok"] and resOGG["ok"] and resMP3["ok"]:
            os.remove(info["MP4"])
            print("Deleted:", info["MP4"])
            if info["cover"]:
                os.remove(info["cover"])
                print("Deleted:", info["cover"])

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


def send_intro(BASE_URL, chat_id: int,folder: str):

    introCaption = ("دانلود موزیک مهمونی و ماشین🎼🎼🎼\n"
                    "آهنگ های سبک هاوس، دیپ هاوس، میکس رپی🎼🎼🎼\n"
                    "#دانلود #دانلودآهنگ #دانلود_آهنگ #دانلود_رایگان #دانلود_موزیک #آهنگ #اهنگ #آهنگساز #آهنگ_جدید #اهنگ_جدید #موزیک_جدید #هاوس #تکنو #technomusic #technolovers #technoparty #housemusic #rapmusic #techno\n\n"
                    "@TechnoHouseRapMusic\n\n"
                    "https://t.me/TechnoHouseRapMusic")

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    if not files:
        print("No pictures in folder!")
        return {"ok": True}
    else:
        pic_file = random.choice(files)
        pic_path = os.path.join(folder, pic_file)
        print(f"Sending picture: {pic_path}")

        resIntro = send_pic(BASE_URL, chat_id, pic_path, introCaption)

        try:
            os.remove(pic_path)
            print(f"Picture deleted: {pic_path}")
        except Exception as e:
            print(f"Error deleting picture: {e}")

        return resIntro

def safe_send(send_func, *args, retry_delay=300, MSG="", **kwargs):
    """
    send_func : تابع ارسال (send_pic / send_voice / send_audio)
    args      : پارامترهای تابع
    kwargs    : پارامترهای کلیدی تابع
    """
    while True:
        try:
            print(MSG)
            response = send_func(*args, **kwargs)

            # اگر پاسخ معتبر بود
            if isinstance(response, dict) and response.get("ok"):
                return response

            print("❌ Telegram error:", response)
            print("⏳ Retrying in 5 minutes...")

        except requests.RequestException as e:
            print("❌ Network error:", e)
            print("⏳ Retrying in 5 minutes...")

        except Exception as e:
            print("❌ Unexpected error:", e)
            print("⏳ Retrying in 5 minutes...")

        time.sleep(retry_delay)
