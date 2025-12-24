import os
import difflib
import pprint


def find_best_cover(self):
    # self.music_dict
    image_folder = self.config["image_folder"]

    for music_name in self.music_dict:

        best_ratio = 0
        best_match = None

        for img in os.listdir(image_folder):
            img_path = os.path.join(image_folder, img)
            if not os.path.isfile(img_path):
                continue

            img_name = os.path.splitext(img)[0]

            ratio = difflib.SequenceMatcher(None, music_name, img_name).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = img_path



        if best_ratio >= 0.9:
            print(f"{music_name} --> {best_ratio:.2f} --> {best_match}")
            self.music_dict[music_name]["cover"] = best_match
        else:
            self.music_dict[music_name]["cover"] = None


    # pprint.pprint(self.music_dict)