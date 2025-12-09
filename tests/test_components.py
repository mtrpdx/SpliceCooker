import pytest
import pyglet

from splice_cooker.components import OScope


def test_oscope():
    window = pyglet.window.Window(caption="test_window")
    oscope = OScope(window)
