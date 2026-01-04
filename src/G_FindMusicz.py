import os
import pprint
import re


def FindMusicz(self):
    print("Starting Processing")
    music_folder = self.config['music_folder']
    self.output.append("Starting Processing")
    if not music_folder:
        self.output.append("Select music folder first!\n")
        return

    music_dict = {}

    for file in os.listdir(music_folder):
        print(file)
        music_name = os.path.splitext(file)[0]

        original_name = music_name

        clean_name = re.sub(r"[-–—_~]+", "-", music_name)
        clean_name = clean_name.strip()
        print(clean_name)

        if clean_name != original_name:
            old_path = os.path.join(music_folder, original_name)
            new_path = os.path.join(music_folder, clean_name)

            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"Renamed: {original_name}  →  {clean_name}")

            music_name = clean_name

        print(music_name)
        music_dict[music_name] = {"MP4" : os.path.join(music_folder, file)}
        music_dict[music_name]["MP3"] =  os.path.join(self.config['MP3_Folder'], f"{music_name}.mp3")
        music_dict[music_name]["OGG"] =  os.path.join(self.config['MP3_Folder'], f"{music_name}.ogg")

        artist, song = music_name.split("-", 1)
        music_dict[music_name]["Artist"] = artist.strip()
        music_dict[music_name]["Song"] = song.strip()

        music_dict[music_name]["caption"] = f"Artist: {music_dict[music_name]['Artist']} \nSong: {music_dict[music_name]['Song']}"

        music_dict[music_name]["default_cover"] = self.config['default_cover']

        print("finished")

    self.output.append(f"Found {len(music_dict)} music files.\n")
    # for name, path in music_dict.items():
    #     self.output.append(f"{name} --> {path}")

    # در صورت نیاز بعداً به self.music_dict ذخیره‌اش می‌کنیم
    self.music_dict = music_dict
    pprint.pprint(self.music_dict)


