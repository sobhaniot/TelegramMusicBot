import os
import sys

from pydub import AudioSegment
from mutagen.mp3 import EasyMP3
from mutagen.id3 import ID3, APIC
from mutagen.oggvorbis import OggVorbis
from pydub.utils import which

ffmpeg_path  = r"G:\Python\.venv\Lib\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

def do_convert(self):
    pass
    for music_name in self.music_dict:
        # print(music_name)
        # print(self.music_dict[music_name])
        convert_to_mp3(self.music_dict[music_name])
        convert_to_ogg(self.music_dict[music_name])
        add_cover_to_mp3(self.music_dict[music_name])
        # add_cover_to_ogg(self.music_dict[music_name])

def convert_to_mp3(info):
    # print(info)
    input_file = info["MP4"]
    output_file = info["MP3"]
    bitrate = "192k"

    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="mp3", bitrate=bitrate)


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
    cover_image = info["cover"]

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

