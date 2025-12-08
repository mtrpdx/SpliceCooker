import argparse
import hashlib
import os
import re
from pathlib import Path
import yaml
from tqdm.auto import tqdm

# from collections import Counter
from utils import timeit

# from hash_utils import _

# def hash_sample_info(sample):
#     """Take sample info and hash it, returning the hash."""
#     m = hashlib.md5()
#     m.update(sample.encode())
#     print(m.hex_digest())
#     breakpoint()
#     return 0


class User(yaml.YAMLObject):
    yaml_tag = "!User"

    def __init__(self, name, config):
        self.name = name
        self.config = config
        # self.splice_root = splice_root
        # self.dest_dir = dest_dir
        # self.sample_hierarchy = sample_hierarchy

    def __repr__(self):
        # return "%s(name=%r, splice_root=%r, dest_dir=%r, sample_hierarchy=%r)" % (
        return "%s(name=%r, config=%r)" % (
            self.__class__.__name__,
            self.name,
            self.config,
            # self.splice_root,
            # self.dest_dir,
            # self.sample_hierarchy,
        )


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
    breakpoint()

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
    breakpoint()
    main(*args)
