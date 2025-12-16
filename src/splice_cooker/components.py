"""
This file contains component base class and component classes.

Current list of components
==========================
OScope : Oscilloscope
ControlStrip : Control strip for audio transport
  - Play/Pause
  - Stop
  - Fast Forward/Forward
  - Rewind/Back
  - Shuffle

"""

from pyglet import shapes
from pyglet.graphics import Batch
from pyglet.gui import WidgetBase, PushButton, ToggleButton
from pyglet.media import Player
from pyglet.resource import image
from pyglet.text import Label
from pyglet.window import Window

from abc import ABC, abstractmethod
from typing import Protocol, Tuple, Dict
from math import sin, cos


# def push_button_handler(widget):
#     push_label.text = "Push Button: True"


# def release_button_handler(widget):
#     push_label.text = "Push Button: False"


class ControlStrip(WidgetBase):
    """Control strip class that inherits from WidgetBase."""

    def __init__(
        self,
        window: Window,
        player: Player,
        icons: Dict,
        batch: Batch,
        user_theme: Dict,
    ):
        """
        Initialize ControlStrip widget.

        We want to inherit the final init procedure from WidgetBase that
        assigns x, y, width, and height, but calculate them according to
        our params beforehand.
        """
        self.button_width = 60
        self.button_height = 60
        self.icons = icons
        self.button_list = ["rewind", "play", "stop", "ff"]
        self.n_buttons = len(self.button_list)
        self.gap = self.button_width * 1.25
        width = (self.n_buttons * self.button_width) + ((self.n_buttons - 1) * self.gap)
        height = self.button_height
        x = (window.width - width) / 2  # left edge of border
        y = (window.height / 2) - (height / 2) - 210
        self.window = window
        self.player = player
        self.user_theme = user_theme
        self.batch = batch

        super().__init__(x, y, width, height)
        self.create_border()
        self.create_buttons()

    def create_border(self):
        """Create border around control strip."""
        ctrlstrip_border = shapes.Box(
            x=self._x - 10,
            y=self._y - 10,
            width=self._width + 10,
            height=self._height + 10,
            color=self.user_theme["fg"],
            batch=self.batch,
        )
        self.border = ctrlstrip_border

    def create_buttons(self):
        self.buttons = []
        # breakpoint()
        # unpressed = image("resources/buttons/button_unpressed.png")
        # pressed = image("resources/buttons/button_pressed.png")
        for i, b in enumerate(self.button_list):
            x = self._x + i * (self.button_width + self.gap)
            y = self._y
            pb = ToggleButton(
                x=x,
                y=y,
                pressed=self.icons[self.button_list[i]][1],
                unpressed=self.icons[self.button_list[i]][0],
                batch=self.batch,
            )
            # breakpoint()
            # match b:
            #     case "rewind":
            #         pb.set_handler("on_toggle", rewind_button_handler)
            #     case "play":
            #         pb.set_handler("on_toggle", play_button_handler)
            #     case "pause":
            #         pb.set_handler("on_toggle", pause_button_handler)
            #     case "stop":
            #         pb.set_handler("on_toggle", stop_button_handler)
            #     case "ff":
            #         pb.set_handler("on_toggle", ff_button_handler)

            self.buttons.append(pb)


class OScope(WidgetBase):
    """Oscilloscope class that inherits from WidgetBase."""

    def __init__(self, window: Window, batch: Batch, user_theme: Tuple):
        """
        Initialize OScope widget.

        We want to inherit the final init procedure from WidgetBase that
        assigns x, y, width, and height, but calculate them according to
        our params beforehand.
        """
        self.aspect_x = 4
        self.aspect_y = 3
        # self.rectangles = []
        self.rectangle_width = 8
        self.n_rectangles = int(
            (2 * 100) / self.rectangle_width
        )  # this determines x pixel count and screen size
        self.gap = self.rectangle_width
        width = (self.n_rectangles * self.rectangle_width) + (
            (self.n_rectangles - 1) * self.gap
        )
        height = width / (self.aspect_x / self.aspect_y)
        x = (window.width - width) / 2  # left edge of screen
        y = (window.height / 2) - (height / 2)

        self.user_theme = user_theme
        self.batch = batch

        super().__init__(x, y, width, height)
        self.create_border()
        self.create_rectangles()

    def create_border(self):
        """Create border around oscilloscope."""
        oscope_border = shapes.Box(
            x=self._x,
            y=self._y,
            width=self._width,
            height=self._height,
            color=self.user_theme["fg"],
            batch=self.batch,
        )
        self.border = oscope_border

    def create_rectangles(self):
        """Create initial row of rectangles."""
        self.rectangles = []
        for i in range(self.n_rectangles):
            x = self._x + i * (self.rectangle_width + self.gap)
            y = self._height / 2
            rect = shapes.Rectangle(
                x=x,
                y=y,
                width=self.rectangle_width,
                height=self.rectangle_width,
                color=self.user_theme["fg"],
                batch=self.batch,
            )
            rect.opacity = 200
            rect.original_x = x
            self.rectangles.append(rect)
