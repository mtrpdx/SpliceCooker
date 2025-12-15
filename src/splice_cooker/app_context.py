"""
This file defines the AppContext class.

AppContext is reponsible for setting up the app, assigning its properties,
and providing a container for them.

"""

import pyglet
from pyglet import shapes
import numpy as np
import librosa
import os
import yaml

from splice_cooker.icons import create_icons, load_icons
from splice_cooker.theme import theme
from splice_cooker.user import User
from splice_cooker.shader import vertex_source, fragment_source


class AppContext:
    def __init__(self, user_config_file: str, debug: bool = False):
        self.audio_filename = "test_audio.wav"
        "../../../resources"
        self.resource_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
        )
        breakpoint()
        # test RESOURCE_DIR
        self.icon_dir = os.path.join(self.resource_dir, "icons")
        self.audio_dir = os.path.join(self.resource_dir, "audio")

        pyglet.resource.path = [self.resource_dir, self.icon_dir, self.audio_dir]
        pyglet.resource.reindex()

        with open(user_config_file, "r") as stream:
            self.user = yaml.load(stream, Loader=yaml.Loader)

        self.main_window = pyglet.window.Window(caption="SpliceCooker")
        if debug:
            self.event_logger = pyglet.window.event.WindowEventLogger()
            self.main_window.push_handlers(self.event_logger)

    def _load_audio_data(self, filename):
        """
        Load audio data using librosa.

        Returns
        -------
        samples (np.array) : audio data, float32, between -1.0 and 1.0
        sr (int) : sample rate
        """

        # sr=None preserves the file's original sample rate.
        # mono=True mixes stereo down to one channel (easier for oscilloscopes).
        samples, sr = librosa.load(filename, sr=None, mono=True)

        return samples, sr

    def load_audio(self):
        print("Loading audio data...")
        # AUDIO_FILE = pyglet.resource.media(AUDIO_FILENAME)
        self.audio_samples, self.sample_rate = self._load_audio_data(
            os.path.join(self.audio_dir, self.audio_filename)
        )
        print(f"Loaded {len(self.audio_samples)} samples.")

    def init_audio_player(self):
        self.player = pyglet.media.Player()
        if self.audio_samples is not None:
            source = pyglet.media.load(
                "/Users/teen/Projects/SpliceCooker/resources/audio/"
                + self.audio_filename,
                streaming=False,
            )
            self.player.queue(source)
            self.player.play()
            self.player.loop = True

    def init_framebuffer(self):
        # Set up framebuffer
        self.fbo_texture = pyglet.image.Texture.create(
            self.main_window.width, self.main_window.height
        )
        self.fbo = pyglet.image.Framebuffer()
        self.fbo.attach_texture(self.fbo_texture)
        # Set up shader ===
        self.vert_shader = pyglet.graphics.shader.Shader(vertex_source, "vertex")
        self.frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        self.dither_program = pyglet.graphics.shader.ShaderProgram(
            self.vert_shader, self.frag_shader
        )

        # Create a full-screen quad to display the final image
        # This quad will have the 'dither_program' attached to it.
        self.background_group = pyglet.graphics.Group()
        self.dither_group = pyglet.graphics.ShaderGroup(
            self.dither_program, parent=self.background_group
        )
        # Create a Sprite that uses the FBO texture and the Dither Shader
        self.screen_sprite = pyglet.sprite.Sprite(
            img=self.fbo_texture,
            x=0,
            y=0,
            batch=pyglet.graphics.Batch(),
            group=self.dither_group,
        )

    def load_ui(self):
        self.batch = pyglet.graphics.Batch()

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
        self.user_theme = theme["pink"]

        # icons = create_icons()
        self.icons = load_icons(self.resource_dir)
        self.border = shapes.Box(
            x=0,
            y=0,
            width=self.main_window.width,
            height=self.main_window.height,
            thickness=24.0,
            color=self.user_theme,
            batch=self.batch,
        )
