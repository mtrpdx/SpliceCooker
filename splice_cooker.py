#!/usr/bin/env python3

import argparse
import os
import re

from pathlib import Path
# from collections import Counter
from functools import wraps
from time import time


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(
            "func:%r args:[%r, %r] took: %2.4f sec" %
            (f.__name__, args, kw, te - ts),
            flush=True
        )
        return result

    return wrap


# @timeit
def find_samples(SPLICE_ROOT: str, IGNORE: list):
    """Looks for sample files in directory SPLICE_ROOT.

    Ignores files that match IGNORE and Ableton analysis files.
    Adds sample files to and return sample_list.

    """
    sample_list = []
    for dirname, _, filenames in os.walk(SPLICE_ROOT):
        for filename in filenames:
            if filename not in IGNORE and not filename.endswith(".asd"):
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
                    "sample_match_failed": False
                }
                sample_list.append(file_dict)

    print(f'{len(sample_list)} samples detected.')

    return sample_list


# def match_sample_type(v):
#     switch v:
#         case "one-shots":
#             return "One Shot"

class SampleTypeMatcher:
    """Class to handle learning sample types from file paths and names.
    """

    def __init__(self):
        self.sample_type = None
        self.drum_type = None
        self.inst_type = None

    def get_sample_type(self, dir_strings: list, filename_strings: list):
        default = "Unknown"
        self.sample_type = default
        for string in dir_strings:
            if re.search("one|shot|one_shot|one_shots|one-shot|one-shots|808|percussion|fx|samples|synth_sounds|drum_hits}", string.lower()):
                self.sample_type = "One Shot"
            elif re.search("melodic_Loops|loops", string.lower()):
                self.sample_type = "Melodic Loop"
            elif re.search("percussion_loops|cymbals_loops", string.lower()):
                self.sample_type = "Percussion Loop"
            elif re.search("spoken", string.lower()):
                self.sample_type = "Spoken Loop"
            elif re.search("drum_loops|breaks|break_loops", string.lower()):
                self.sample_type = "Break"

        for string in filename_strings:
            if self.sample_type == default:
                if re.search("one_shot|one_shots|one-shot|one-shots|808|percussion|fx|samples|synth_sounds}", string.lower()):
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
def get_sample_meta(SPLICE_ROOT: str, DEST_DIR: str, sample_list: list):
    sample_types = []
    drum_types = []
    inst_types = []
    for idx, sample in enumerate(sample_list):
        filename = sample['filename']
        origdir_strings = sample['origdir'].partition(SPLICE_ROOT)[2].split('/')[3:]
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
            if sample_type=="Break" or sample_type=="Melodic Loop":
                sample_list[idx]["newdir"] = os.path.join(DEST_DIR, f"{sample_type}/")
                sample_list[idx]["sampletype"] = sample_type

            elif sample_type == "One Shot":
                if drum_type != "Unknown":
                    print(f"Drum type: {drum_type}")
                    sample_list[idx]["newdir"] = os.path.join(DEST_DIR, f"{sample_type}/{drum_type}s/")
                    sample_list[idx]["sampletype"] = sample_type
                    sample_list[idx]["isdrum"] = True
                    sample_list[idx]["drumtype"] = drum_type

                if inst_type != "Unknown":
                    print(f"Instrument type: {inst_type}")
                    sample_list[idx]["newdir"] = os.path.join(DEST_DIR, f"{sample_type}/{inst_type}/")
                    sample_list[idx]["isinst"] = True
                    sample_list[idx]["insttype"] = inst_type

                elif (drum_type == "Unknown") and (inst_type == "Unknown"):
                    sample_list[idx]["sample_match_failed"] = True

            elif (sample_type == "Spoken Loop") or (sample_type == "Percussion Loop"):
                    sample_list[idx]["newdir"] = os.path.join(DEST_DIR, f"{sample_type}/")

        else:
            sample_list[idx]["sample_match_failed"] = True
            raise Exception("Sample match failed.")

        print("============")

    # print(sample_list[0:20])


@timeit
def main(SPLICE_ROOT: str, DEST_DIR:str):

    SPLICE_ROOT = os.path.expanduser(Path(SPLICE_ROOT))
    DEST_DIR = os.path.expanduser(Path(DEST_DIR))
    IGNORE = [".DS_Store"]
    SAMPLE_TYPES_DEFAULT = [
        "One Shot",
        "Melodic Loop",
        "Percussion Loop",
        "Spoken Loop"
        "Break"
    ]
    DRUM_TYPES_DEFAULT = [
        "Kick",
        "Snare",
        "Cymbal",
        "Hat",
        "Ride",
        "Crash",
        "Perc"
    ]
    INST_TYPES_DEFAULT = [
        "Bass",
        "Keys",
        "Synth",
        "Brass",
        "Woodwind",
        "Strings",
        "FX",
        "Vox"
    ]

    sample_list = find_samples(SPLICE_ROOT, IGNORE)
    get_sample_meta(SPLICE_ROOT, DEST_DIR, sample_list)

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="SpliceCooker",
        description="Reorganizes Splice samples in a way that makes sense.",
    )
    parser.add_argument("splice_root")
    parser.add_argument('dest_dir')

    args = parser.parse_args()

    main(args.splice_root, args.dest_dir)
