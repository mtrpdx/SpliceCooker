import pyglet

import os
from pathlib import Path

from splice_cooker.icons import create_icons

# from tests.test_icons import test_icons

window = pyglet.window.Window(width=100, height=100, visible=False)

icon_dir = Path("/Users/teen/Projects/SpliceCooker/resources/icons")
icons = create_icons(window)

button_list = ["rewind", "play", "pause", "stop", "ff"]

for btn in button_list:
    image_data = icons[btn][0].get_image_data()
    image_data.save(os.path.join(icon_dir, f"{btn}.png"))

    image_data = icons[btn][1].get_image_data()
    image_data.save(os.path.join(icon_dir, f"{btn}_pressed.png"))
