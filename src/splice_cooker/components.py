"""This file contains component base class and component classes."""

from pyglet import shapes
from pyglet.graphics import Batch
from pyglet.gui import WidgetBase
from pyglet.window import Window

from abc import ABC, abstractmethod
from typing import Protocol, Tuple
from math import sin, cos


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
        self.n_rectangles = 100  # this determines x pixel count and screen size
        self.rectangle_width = 2
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
            color=self.user_theme,
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
                color=self.user_theme,
                batch=self.batch,
            )
            rect.original_x = x
            self.rectangles.append(rect)
