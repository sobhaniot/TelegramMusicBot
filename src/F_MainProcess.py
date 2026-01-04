import os
import shutil
import threading
import time
import datetime
from src import G_FindMusicz as GFM
from src import E_FindBestCover as EFBC
from src import C_Converter as CC
from src import H_Telegram as HT
from src import D_Utils as DU

def start_processing(self):
    if not DU.validate_config(self):
        return False
    clear_mp3_folder(self)
    GFM.FindMusicz(self)
    if len(self.music_dict):
        EFBC.find_best_cover(self)
        CC.do_convert(self)
        HT.send_music_package(self)

    return True


def clear_mp3_folder(self):

    if "MP3_Folder" in self.config:
        folder = self.config["MP3_Folder"]
    else:
        print("این کلید در دیکشنری وجود ندارد")
        return

    if os.path.exists(folder):
        shutil.rmtree(folder)
        os.makedirs(folder)

    print(">>> MP3 folder cleared.")


def is_now_in_range(start_str, end_str):
    print(start_str, end_str)
    now = datetime.datetime.now().time()
    print(now)
    start = datetime.time(int(start_str.split(":")[0]), int(start_str.split(":")[1]))
    end = datetime.time(int(end_str.split(":")[0]), int(end_str.split(":")[1]))
    print(start, end)
    # حالت عادی: 09:00 تا 11:00
    if start < end:
        print(">>> Time window reached. Starting daily cycle...")
        return start <= now <= end
    # بازه نیمه‌شب: 22:00 تا 03:00
    else:
        return now >= start or now <= end

