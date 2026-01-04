import json
import os
import sys

# پیدا کردن مسیر فولدر برنامه (چه exe باشد چه py)
if getattr(sys, 'frozen', False):
    # حالت EXE
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # حالت script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "Z_Config.json")
print(f"CONFIG_PATH: {CONFIG_PATH}")

DEFAULT_CONFIG = {
    "music_folder": "",
    "MP3_Folder": ""
}

def ensure_config():
    """اگر فایل کانفیگ وجود نداشت، ایجادش کند"""
    if not os.path.exists(CONFIG_PATH):
        print(f"Config file not found, creating default at {CONFIG_PATH}")
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)


def validate_config(self):
    # لیست کلیدهایی که حتماً باید مقدار داشته باشند
    required_keys = ['music_folder', 'MP3_Folder', 'default_cover','telegram_token','telegram_chat_id',
                     'image_folder']

    for key in required_keys:
        # چک می‌کند که آیا کلید وجود دارد و مقدار آن خالی یا None نیست
        value = self.config.get(key)
        if not value:
            print(f"Error: Key '{key}' is missing or empty in config.")
            self.output.append(f"Error: Key '{key}' is missing or empty in config.")
            return False

    if not os.path.isfile(self.config["default_cover"] + "\\Cover.jpg"):
        print("Please add Cover.jpg to the Cover folder in ImageFolder.")
        return False

    return True

def load_config():
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(self):
    if self.config["image_folder"]:
        self.config["intro_pic_folder"] = check_and_create_dir(self.config["image_folder"] + "\\Intro")
        self.config["default_cover"] = check_and_create_dir(self.config["image_folder"] + "\\Cover")

    self.config["MP3_Folder"] = create_sibling_folder(self.config["music_folder"])

    if not validate_config(self):
        return False

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(self.config, f, indent=4, ensure_ascii=False)

    return True


def check_and_create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory created: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

    return dir_path


def create_sibling_folder(base_folder):
    """
    یک فولدر جدید در کنار فولدر base_folder ایجاد می‌کند.

    :param base_folder: مسیر فولدر موجود
    :param new_folder_name: نام فولدر جدید که در کنار base_folder ساخته شود
    :return: مسیر فولدر جدید
    """
    # مسیر والد فولدر base_folder
    parent_dir = os.path.dirname(os.path.abspath(base_folder))

    # مسیر فولدر جدید
    new_folder_path = os.path.join(parent_dir, "MP3")

    # اگر وجود نداشت، بساز
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        print(f"Folder created: {new_folder_path}")
    else:
        print(f"Folder already exists: {new_folder_path}")

    return new_folder_path

