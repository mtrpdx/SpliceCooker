import pytest
import pyglet

import os
from pathlib import Path

from splice_cooker.icons import create_icons


def test_icons(window):
    output_dir = Path("/Users/teen/Projects/SpliceCooker/resources/buttons")
    icons = create_icons(window)
    # breakpoint()
    image_data = icons["rewind"][0].get_image_data()
    image_data.save(os.path.join(output_dir, "rewind.png"))
