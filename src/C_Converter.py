import os
import sys

from pydub import AudioSegment
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
from mutagen.mp3 import MP3

ffmpeg_path  = r"G:\Python\.venv\Lib\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

def do_convert(self):
    for music_name in list(self.music_dict.keys()):
        # print(music_name)
        # print(self.music_dict[music_name])
        if not convert_to_mp3(self.music_dict[music_name]):
            print(f"[REMOVED] {music_name}")
            del self.music_dict[music_name]
            continue

        convert_to_ogg(self.music_dict[music_name])
        add_cover_to_mp3(self.music_dict[music_name])
        # add_cover_to_ogg(self.music_dict[music_name])

def convert_to_mp3(info):
    # print(info)
    input_file = info["MP4"]
    output_file = info["MP3"]
    bitrate = "192k"
    if not input_file or not os.path.isfile(input_file):
        print(f"[SKIP] Input file not found: {input_file}")
        return False

    try:

        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="mp3", bitrate=bitrate)

        mp3 = MP3(output_file, ID3=ID3)

        try:
            mp3.add_tags()
        except:
            pass

        if "Song" in info:
            mp3.tags.add(TIT2(encoding=3, text=info["Song"]))

        if "Artist" in info:
            mp3.tags.add(TPE1(encoding=3, text=info["Artist"]))

        if "album" in info:
            mp3.tags.add(TALB(encoding=3, text=info["album"]))

        if "year" in info:
            mp3.tags.add(TDRC(encoding=3, text=info["year"]))

        if "genre" in info:
            mp3.tags.add(TCON(encoding=3, text=info["genre"]))

        mp3.save()
        print(f"[OK] Converted & tagged: {output_file}")
        return True


    except Exception as e:
        print(f"[ERROR] {input_file} -> {e}")

    return False


def convert_to_ogg(info):
    input_file = info["MP3"]

    # آهنگ را لود می‌کنیم
    sound = AudioSegment.from_file(input_file)

    # مدت آهنگ (بر حسب میلی‌ثانیه)
    duration = len(sound)

    # اگر آهنگ کمتر از 45 ثانیه بود همان کلش را می‌گیریم
    clip_length = 45 * 1000
    if duration <= clip_length:
        middle_part = sound
    else:
        # محاسبه شروع 45 ثانیه از وسط آهنگ
        start = (duration // 2) - (clip_length // 2)
        end = start + clip_length
        middle_part = sound[start:end]

    # تبدیل به ogg opus مخصوص تلگرام
    middle_part.export(
        info["OGG"],
        format="ogg",
        codec="libopus",
        parameters=["-b:a", "64k", "-ar", "48000", "-ac", "1"]
    )

def add_cover_to_mp3(info):
    mp3_file = info["MP3"]
    if info["cover"]:
        cover_image = info["cover"]
    else:
        cover_image = info["default_cover"]

    audio = ID3(mp3_file)
    with open(cover_image, "rb") as img:
        audio["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc=u"Cover",
            data=img.read()
        )
    audio.save()


# def add_cover_to_ogg(info):
#     ogg_file = info["OGG"]
#     cover_image = info["cover"]
#     audio = OggVorbis(ogg_file)
#     # with open(cover_image, "rb") as img:
#     #     audio["metadata_block_picture"] = [img.read()]
#     # audio.save()

