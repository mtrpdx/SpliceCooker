import pyglet
from pyglet.gl import (
    glClear,
    glClearColor,
    glViewport,
    GL_COLOR_BUFFER_BIT,
    GL_VIEWPORT,
)
from pyglet.math import Vec2
from pyglet import shapes, gui

import ctypes
import os

from splice_cooker.theme import theme, theme_green


def shift_left(point, index, x_offset):
    shifted = Vec2(point.x - (index * x_offset), point.y)
    return shifted


def shift_right(point, index, x_offset):
    shifted = Vec2(point.x + (index * x_offset), point.y)
    return shifted


# === 1. The Helper Function ===
def create_shape_texture(width, height, window, draw_func) -> pyglet.image.Texture:
    """
    Creates a texture (image) by running a drawing function.

    1. Create a blank texture
    2. Create a Framebuffer to draw onto this texture
    3. Attach the texture to the framebuffer's color attachment point
    4. Activate the framebuffer
    5. Clear any garbage data from the texture
    6. Run the user's custom draw code
    7. Deactivate framebuffer (go back to drawing to screen)
    """
    texture = pyglet.image.Texture.create(width, height)
    framebuffer = pyglet.image.Framebuffer()
    framebuffer.attach_texture(texture)

    framebuffer.bind()

    # Save Viewport:
    old_viewport = (ctypes.c_int * 4)()
    pyglet.gl.glGetIntegerv(GL_VIEWPORT, old_viewport)

    # Save Projection:
    # Assume 'window' is globally available. If not, pass it as an arg.
    old_projection = window.projection

    try:
        # Set Viewport to match the icon size
        glViewport(0, 0, width, height)

        # Set Projection to match the icon size
        # (0,0) is bottom-left, (width,height) is top-right
        window.projection = pyglet.math.Mat4.orthogonal_projection(
            0, width, 0, height, -255, 255
        )

        # Clear to Transparent
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)

        draw_func()

    finally:
        framebuffer.unbind()
        framebuffer.delete()

        window.projection = old_projection
        glViewport(old_viewport[0], old_viewport[1], old_viewport[2], old_viewport[3])

    return texture


def find_triangle_center(p1: Vec2, p2: Vec2, p3: Vec2):
    center_x = (p1.x + p2.x + p3.x) / 3
    center_y = (p1.y + p2.y + p3.y) / 3
    return Vec2(center_x, center_y)


def find_rectangle_center(p, w, h):
    center_x = (p[0] + (p[0] + w)) / 2
    center_y = (p[1] + (p[1] + h)) / 2
    return (center_x, center_y)


def draw_rewind_icon(color) -> None:
    # Two triangles pointing left
    # (0,0) is bottom-left of the BUTTON, not the screen
    n_triangles = 2
    x_offset = 15.0

    # template triangle, centered
    p1 = Vec2(40.0, 10.0)
    p2 = Vec2(40.0, 50.0)
    p3 = Vec2(20.0, 30.0)
    # triangle = [p1, p2, p3]

    # Create new points offset by half of final offset
    p1 = shift_right(p1, 1, x_offset / 2)
    p2 = shift_right(p2, 1, x_offset / 2)
    p3 = shift_right(p3, 1, x_offset / 2)
    # total_width = p3.x - p1.x + x_offset

    for i in range(n_triangles):
        # Create triangles, with one offset by total offset so
        # two triangles are centered together as one unit
        p1 = shift_left(p1, i, x_offset)
        p2 = shift_left(p2, i, x_offset)
        p3 = shift_left(p3, i, x_offset)
        tri = shapes.Triangle(
            p1.x,
            p1.y,
            p2.x,
            p2.y,
            p3.x,
            p3.y,
            color=color,
        )
        tri.draw()
    shapes.Box(0, 0, 60, 60, thickness=2.0, color=color).draw()


def draw_play_icon(color) -> None:
    # Triangle pointing right
    # (0,0) is bottom-left of the BUTTON, not the screen
    p1 = Vec2(15.0, 10.0)
    p2 = Vec2(15.0, 50.0)
    p3 = Vec2(45.0, 30.0)
    shapes.Triangle(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, color=color).draw()
    shapes.Box(0, 0, 60, 60, thickness=2.0, color=color).draw()


def draw_pause_icon(color) -> None:
    # Two vertical bars
    # x,y,w,h
    p1 = Vec2(10.0, 10.0)
    p2 = Vec2(35.0, 10.0)
    w1 = 15.0
    h1 = 40.0
    w2 = 15.0
    h2 = 40.0
    rect1 = shapes.Rectangle(p1.x, p1.y, w1, h1, color=color)
    rect2 = shapes.Rectangle(p2.x, p2.y, w2, h2, color=color)
    # rect1.anchor_position = find_rectangle_center(p1, w1, h1)
    # rect1.anchor_position = find_rectangle_center(p2, w2, h2)
    # rect1.position = (10.0, 10.0)
    # rect2.position = (40.0, 10.0)
    rect1.draw()
    rect2.draw()
    shapes.Box(0, 0, 60, 60, thickness=2.0, color=color).draw()


def draw_stop_icon(color) -> None:
    # One solid square
    shapes.Rectangle(10, 10, 40, 40, color=color).draw()
    shapes.Box(0, 0, 60, 60, thickness=2.0, color=color).draw()


def draw_ff_icon(color) -> None:
    # Two triangles pointing right
    # (0,0) is bottom-left of the BUTTON, not the screen

    n_triangles = 2
    x_offset = 15.0

    # template triangle, centered
    p1 = Vec2(20.0, 10.0)
    p2 = Vec2(20.0, 50.0)
    p3 = Vec2(40.0, 30.0)
    # triangle = [p1, p2, p3]

    # Create new points offset by half of final offset
    p1 = shift_right(p1, 1, x_offset / 2)
    p2 = shift_right(p2, 1, x_offset / 2)
    p3 = shift_right(p3, 1, x_offset / 2)
    # total_width = p3.x - p1.x + x_offset

    for i in range(n_triangles):
        # Create triangles, with one offset by total offset so
        # two triangles are centered together as one unit
        p1 = shift_left(p1, i, x_offset)
        p2 = shift_left(p2, i, x_offset)
        p3 = shift_left(p3, i, x_offset)
        tri = shapes.Triangle(
            p1.x,
            p1.y,
            p2.x,
            p2.y,
            p3.x,
            p3.y,
            color=color,
        )
        # tri.anchor_position = find_triangle_center(p1, p2, p3)
        # tri.rotation = 180
        # tri.position = (10.0 + (i * 30), 10.0)
        tri.draw()

    shapes.Box(0, 0, 60, 60, thickness=2.0, color=color).draw()


def create_icons(window):
    # We need two states for every button: Normal (unpressed) and Pressed (darker)
    color_normal = theme_green["fg"]
    color_pressed = theme_green["fg-alt"]  # Darker grey when clicked

    # -- REWIND BUTTON IMAGES --
    rewind_img = create_shape_texture(
        60, 60, window, lambda: draw_rewind_icon(color_normal)
    )
    rewind_pressed_img = create_shape_texture(
        60, 60, window, lambda: draw_rewind_icon(color_pressed)
    )

    # -- PLAY BUTTON IMAGES --
    play_img = create_shape_texture(
        60, 60, window, lambda: draw_play_icon(color_normal)
    )
    play_pressed_img = create_shape_texture(
        60, 60, window, lambda: draw_play_icon(color_pressed)
    )

    # -- PAUSE BUTTON IMAGES --
    pause_img = create_shape_texture(
        60, 60, window, lambda: draw_pause_icon(color_normal)
    )
    pause_pressed_img = create_shape_texture(
        60, 60, window, lambda: draw_pause_icon(color_pressed)
    )

    # -- STOP BUTTON IMAGES --
    stop_img = create_shape_texture(
        60, 60, window, lambda: draw_stop_icon(color_normal)
    )
    stop_pressed_img = create_shape_texture(
        60, 60, window, lambda: draw_stop_icon(color_pressed)
    )

    # -- FF BUTTON IMAGES --
    ff_img = create_shape_texture(60, 60, window, lambda: draw_ff_icon(color_normal))
    ff_pressed_img = create_shape_texture(
        60, 60, window, lambda: draw_ff_icon(color_pressed)
    )

    icons = {
        "rewind": (rewind_img, rewind_pressed_img),
        "play": (play_img, play_pressed_img),
        "pause": (pause_img, pause_pressed_img),
        "stop": (stop_img, stop_pressed_img),
        "ff": (ff_img, ff_pressed_img),
    }

    return icons


def load_icons(resource_dir):

    # -- REWIND BUTTON IMAGES --
    rewind_img = pyglet.resource.image("rewind.png")
    rewind_pressed_img = pyglet.resource.image("rewind_pressed.png")

    # -- PLAY BUTTON IMAGES --
    play_img = pyglet.resource.image("play.png")
    play_pressed_img = pyglet.resource.image("play_pressed.png")

    # -- PAUSE BUTTON IMAGES --
    pause_img = pyglet.resource.image("pause.png")
    pause_pressed_img = pyglet.resource.image("pause_pressed.png")

    # -- STOP BUTTON IMAGES --
    stop_img = pyglet.resource.image("stop.png")
    stop_pressed_img = pyglet.resource.image("stop_pressed.png")

    # -- FF BUTTON IMAGES --
    ff_img = pyglet.resource.image("ff.png")
    ff_pressed_img = pyglet.resource.image("ff_pressed.png")

    icons = {
        "rewind": (rewind_img, rewind_pressed_img),
        "play": (play_img, pause_pressed_img),
        # "pause": (pause_img, pause_pressed_img),
        "stop": (stop_img, stop_pressed_img),
        "ff": (ff_img, ff_pressed_img),
    }

    return icons
