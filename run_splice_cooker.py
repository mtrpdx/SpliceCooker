import pyglet
from pyglet import shapes
from tqdm.auto import tqdm
import yaml

import argparse
import hashlib
import os
import re
from pathlib import Path
from math import sin, cos

# from collections import Counter
from splice_cooker.components import OScope
from splice_cooker.utils import timeit
from splice_cooker.user import User
from splice_cooker.theme import theme
from splice_cooker.file_dialog import FileOpenDialog, FileSaveDialog

# from hash_utils import _

# def hash_sample_info(sample):
#     """Take sample info and hash it, returning the hash."""
#     m = hashlib.md5()
#     m.update(sample.encode())
#     print(m.hex_digest())
#     breakpoint()
#     return 0


total_time = 0


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="SpliceCooker",
        description="Reorganizes Splice samples in a way that makes sense.",
    )
    parser.add_argument(
        "--user_config",
        type=str,
        default="./user_config.yaml",
        help="YAML file to load for user configuration",
    )
    # parser.add_argument(
    #     "-s",
    #     "--sample_hierarchy",
    #     choices=["category_first", "instrument_first"],
    #     default="category_first",
    # )
    parser.add_argument("-c", "--copy_only", default=True, action="store_true")

    arguments = parser.parse_args()
    user_config = arguments.user_config
    copy_only = arguments.copy_only
    return user_config, copy_only


# def load_user_config():


def create_dirs(
    splice_root: str,
    dest_dir: str,
    sample_types: list,
    drum_types: list,
    inst_types: list,
    sample_hierarchy: str,
):

    if sample_hierarchy == "category_first":
        for sample_type in sample_types:
            if sample_type == "One Shots":
                for drum_type in drum_types:
                    os.makedirs(
                        os.path.join(dest_dir, f"{sample_type}/Drums/{drum_type}"),
                        exist_ok=True,
                    )
                for inst_type in inst_types:
                    os.makedirs(
                        os.path.join(
                            dest_dir, f"{sample_type}/Instruments/{inst_type}"
                        ),
                        exist_ok=True,
                    )
            elif sample_type == "Melodic Loops":
                for inst_type in inst_types:
                    os.makedirs(
                        os.path.join(dest_dir, f"{sample_type}/{inst_type}"),
                        exist_ok=True,
                    )
            elif sample_type == "Perc Loops":
                for drum_type in drum_types:
                    os.makedirs(
                        os.path.join(dest_dir, f"{sample_type}/{drum_type}"),
                        exist_ok=True,
                    )
            else:
                # print(sample_type)
                os.makedirs(os.path.join(dest_dir, sample_type), exist_ok=True)

    if sample_hierarchy == "instrument_first":
        for div in ["Drums", "Instruments", "Vocals"]:
            if div == "Drums":
                for drum_type in drum_types:
                    for sample_type in ["One Shots", "Loops"]:
                        os.makedirs(
                            os.path.join(dest_dir, f"{div}/{drum_type}/{sample_type}"),
                            exist_ok=True,
                        )
            if div == "Instruments":
                for inst_type in inst_types:
                    for sample_type in ["One Shots", "Loops"]:
                        os.makedirs(
                            os.path.join(dest_dir, f"{div}/{inst_type}/{sample_type}"),
                            exist_ok=True,
                        )
            if div == "Vocals":
                for vox_type in ["One Shots", "Loops", "Spoken"]:
                    os.makedirs(
                        os.path.join(dest_dir, f"{div}/{vox_type}"), exist_ok=True
                    )

    return 0


# @timeit
def find_samples(splice_root: str, ignore: list):
    """Looks for sample files in directory SPLICE_ROOT.

    Ignores files that match IGNORE and Ableton analysis files.
    Adds sample files to and return sample_list.

    """
    sample_list = []
    for dirname, _, filenames in os.walk(splice_root):
        for filename in filenames:
            if filename not in ignore and not filename.endswith(".asd"):
                file_dict = {
                    "filename": filename,
                    "origdir": dirname,
                    "newdir": None,
                    "sampletype": None,
                    "isdrum": None,
                    "drumtype": None,
                    "isinst": None,
                    "insttype": None,
                    "key": None,
                    "bpm": None,
                    "status": "not_moved",
                    "sample_match_failed": False,
                }
                sample_list.append(file_dict)

    print(f"{len(sample_list)} samples detected.")

    return sample_list


# def match_sample_type(v):
#     switch v:
#         case "one-shots":
#             return "One Shot"


class Sample:
    """Class to facilitate metadata storage for"""


class SampleTypeMatcher:
    """Class to handle learning sample types from file paths and names."""

    def __init__(self):
        self.sample_type = None
        self.drum_type = None
        self.inst_type = None

    def get_sample_type(self, dir_strings: list, filename_strings: list):
        default = "Unknown"
        self.sample_type = default
        for string in dir_strings:
            if re.search(
                "one|shot|one_shot|one_shots|one-shot|one-shots|808|percussion|fx|samples|synth_sounds|drum_hits}",
                string.lower(),
            ):
                self.sample_type = "One Shot"
            elif re.search("melodic_Loops|loops", string.lower()):
                self.sample_type = "Melodic Loop"
            elif re.search("percussion_loops|cymbals_loops", string.lower()):
                self.sample_type = "Perc Loop"
            elif re.search("spoken", string.lower()):
                self.sample_type = "Spoken Loop"
            elif re.search("drum_loops|breaks|break_loops", string.lower()):
                self.sample_type = "Break"

        for string in filename_strings:
            if self.sample_type == default:
                if re.search(
                    "one_shot|one_shots|one-shot|one-shots|808|percussion|fx|samples|synth_sounds}",
                    string.lower(),
                ):
                    self.sample_type = "One Shot"
                elif re.search("melodic_Loops|loops", string.lower()):
                    self.sample_type = "Melodic Loop"
                elif re.search("percussion_loops|cymbals_loops", string.lower()):
                    self.sample_type = "Percussion Loop"
                elif re.search("spoken", string.lower()):
                    self.sample_type = "Spoken Loop"
                elif re.search("drum_loops|breaks|break_loops", string.lower()):
                    self.sample_type = "Break"

        return self.sample_type

    def get_drum_type(self, dir_strings: list, filename_strings: list):
        default = "Unknown"
        self.drum_type = default
        for string in filename_strings:
            if re.search("kick", string):
                self.drum_type = "Kick"
            elif re.search("snare", string.lower()):
                self.drum_type = "Snare"
            elif re.search("cymbal", string.lower()):
                self.drum_type = "Cymbal"
            elif re.search("hat", string.lower()):
                self.drum_type = "Hat"
            elif re.search("ride", string.lower()):
                self.drum_type = "Ride"
            elif re.search("crash", string.lower()):
                self.drum_type = "Crash"
            elif re.search("perc", string.lower()):
                self.drum_type = "Perc"
        return self.drum_type

    def get_inst_type(self, dir_strings: list, filename_strings: list):
        default = "Unknown"
        self.inst_type = default
        for string in filename_strings:
            if re.search("bass|subbass", string.lower()):
                self.inst_type = "Bass"
            if re.search("keys|piano", string.lower()):
                self.inst_type = "Keys"
            if re.search("synth", string.lower()):
                self.inst_type = "Synth"
            if re.search("brass", string.lower()):
                self.inst_type = "Brass"
            if re.search("woodwind", string.lower()):
                self.inst_type = "Woodwind"
            if re.search("strings", string.lower()):
                self.inst_type = "Strings"
            if re.search("fx", string.lower()):
                self.inst_type = "FX"
            if re.search("vocal", string.lower()):
                self.inst_type = "Vox"
        return self.inst_type

    # def case_one_shots(self):
    #     return "One Shot"

    # def case_melodic_loop(self):
    #     return "Melodic Loop"

    # def case_break(self):
    #     return "Break"


# @timeit
def get_sample_meta(splice_root: str, dest_dir: str, sample_list: list):
    sample_types = []
    drum_types = []
    inst_types = []
    for idx, sample in enumerate(sample_list):
        filename = sample["filename"]
        origdir_strings = sample["origdir"].partition(splice_root)[2].split("/")[3:]
        filename_strings = sample["filename"].partition(".")[0].split("_")
        print(f"Filename: {filename}")
        print(f"Original dir: {origdir_strings}")
        print(f"Filename strings: {filename_strings}")

        stm = SampleTypeMatcher()

        sample_type = stm.get_sample_type(origdir_strings, filename_strings)
        drum_type = stm.get_drum_type(origdir_strings, filename_strings)
        inst_type = stm.get_inst_type(origdir_strings, filename_strings)

        if sample_type != "Unknown":
            print(f"Sample type: {sample_type}")
            if sample_type == "Break" or sample_type == "Melodic Loop":
                sample_list[idx]["newdir"] = os.path.join(dest_dir, f"{sample_type}/")
                sample_list[idx]["sampletype"] = sample_type

            elif sample_type == "One Shot":
                if drum_type != "Unknown":
                    print(f"Drum type: {drum_type}")
                    sample_list[idx]["newdir"] = os.path.join(
                        dest_dir, f"{sample_type}/{drum_type}s/"
                    )
                    sample_list[idx]["sampletype"] = sample_type
                    sample_list[idx]["isdrum"] = True
                    sample_list[idx]["drumtype"] = drum_type

                if inst_type != "Unknown":
                    print(f"Instrument type: {inst_type}")
                    sample_list[idx]["newdir"] = os.path.join(
                        dest_dir, f"{sample_type}/{inst_type}/"
                    )
                    sample_list[idx]["isinst"] = True
                    sample_list[idx]["insttype"] = inst_type

                elif (drum_type == "Unknown") and (inst_type == "Unknown"):
                    sample_list[idx]["sample_match_failed"] = True

            elif (sample_type == "Spoken Loop") or (sample_type == "Percussion Loop"):
                sample_list[idx]["newdir"] = os.path.join(dest_dir, f"{sample_type}/")

        else:
            sample_list[idx]["sample_match_failed"] = True
            raise Exception("Sample match failed.")

        print("============")

    # print(sample_list[0:20])


@timeit
def main(user_config_file: str, copy_only: True):

    with open(user_config_file, "r") as stream:
        user = yaml.load(stream, Loader=yaml.Loader)

    # breakpoint()

    window = pyglet.window.Window(caption="SpliceCooker")

    # oscope = OScope(window)

    # breakpoint()

    batch = pyglet.graphics.Batch()

    # label = pyglet.text.Label(
    #     "Hello, _",
    #     font_name="Times New Roman",
    #     font_size=36,
    #     x=window.width // 2,
    #     y=window.height // 2,
    #     anchor_x="center",
    #     anchor_y="center",
    #     batch=batch,
    # )
    user_theme = theme["pink"]

    border = shapes.Box(
        x=0,
        y=0,
        width=window.width,
        height=window.height,
        thickness=24.0,
        color=user_theme,
        batch=batch,
    )

    # open_dialog = FileOpenDialog(
    #     # initial_dir=user.config["splice_root"],
    #     filetypes=[("WAV", ".wav"), ("AIFF", ".aiff")],
    #     multiple=True,
    # )

    # @open_dialog.event
    # def on_dialog_open(filenames):
    #     print("List of seleted filenames:", filenames)

    # cursor = shapes.Rectangle(
    #     x=window.width / 2,
    #     y=window.height / 2,
    #     width=24.0,
    #     height=48.0,
    #     color=(181, 181, 181),
    #     batch=batch,
    # )

    # Oscilloscope demo
    # =================
    # aspect_x = 4.0
    # aspect_y = 3.0
    # rectangles = []
    # n_rectangles = 100  # this determines x pixel count and screen size
    # rectangle_width = 2
    # gap = rectangle_width
    # total_width = (n_rectangles * rectangle_width) + ((n_rectangles - 1) * gap)
    # total_height = total_width / (aspect_x / aspect_y)
    # # left_shift = (40 * n_rectangles) / 2
    # # x = (window.width / 2) - left_shift
    # start_x = (window.width - total_width) / 2  # left edge of screen
    # # breakpoint()
    # oscope_border = shapes.Box(
    #     x=start_x,
    #     y=(window.height / 2) - (total_height / 2),
    #     width=total_width,
    #     height=total_height,
    #     color=user_theme,
    #     batch=batch,
    # )

    # # Create row of rectangles
    # for i in range(n_rectangles):
    #     x = start_x + i * (rectangle_width + gap)
    #     y = window.height / 2
    #     rect = shapes.Rectangle(
    #         x=x,
    #         y=y,
    #         width=rectangle_width,
    #         height=rectangle_width,
    #         color=user_theme,
    #         batch=batch,
    #     )
    #     rect.original_x = x
    #     rectangles.append(rect)

    oscope = OScope(window, batch, user_theme)
    oscope.create_border()
    oscope.create_rectangles()

    def update_wave(rectangles, speed, amplitude, freq, base_y):
        """Update demo wave in lieu of real data."""
        global total_time
        for rect in rectangles:
            angle = (rect.original_x * freq) + (total_time * speed)
            rect.y = base_y + amplitude * sin(angle)

    def update(dt):
        global total_time
        total_time += dt

        # wave settings
        speed = 14.0
        amplitude = 50.0
        freq = 0.04
        base_y = window.height / 2
        # for rect in rectangles:
        #     angle = (rect.original_x * freq) + (total_time * speed)
        #     rect.y = base_y + amplitude * sin(angle)

        update_wave(oscope.rectangles, speed, amplitude, freq, base_y)
        # offset += 0.10
        # cursor.opacity += int(sin(value))
        # print(cursor.opacity)

    @window.event
    def on_key_press(symbol, modifiers):
        print("A key was pressed")

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.clock.schedule_interval(update, 1 / 60)
    pyglet.app.run()

    # SPLICE_ROOT = os.path.expanduser(Path(splice_root))
    # DEST_DIR = os.path.expanduser(Path(dest_dir))
    SPLICE_ROOT = Path(user.config["splice_root"])
    DEST_DIR = Path(user.config["dest_dir"])

    IGNORE = [".DS_Store"]
    SAMPLE_TYPES_DEFAULT = [
        "One Shots",
        "Melodic Loops",
        "Perc Loops",
        "Spoken Loops",
        "Breaks",
    ]
    DRUM_TYPES_DEFAULT = [
        "Kicks",
        "Snares",
        "Cymbals",
        "Hats",
        "Rides",
        "Crashes",
        "Percs",
    ]
    INST_TYPES_DEFAULT = [
        "Bass",
        "Keys",
        "Synth",
        "Brass",
        "Woodwind",
        "Strings",
        "FX",
        "Vox",
    ]
    SAMPLE_HIERARCHY = user.config["sample_hierarchy"]

    sample_list = find_samples(SPLICE_ROOT, IGNORE)
    breakpoint()
    # get_sample_meta(SPLICE_ROOT, DEST_DIR, sample_list)
    create_dirs(
        SPLICE_ROOT,
        DEST_DIR,
        SAMPLE_TYPES_DEFAULT,
        DRUM_TYPES_DEFAULT,
        INST_TYPES_DEFAULT,
        SAMPLE_HIERARCHY,
    )
    # print(sample_list)
    for sample in tqdm(sample_list):
        hash_sample_info(sample)

    breakpoint()

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    # breakpoint()
    main(*args)
