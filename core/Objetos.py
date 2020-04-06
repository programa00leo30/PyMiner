from __future__ import division

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from .config import *

class Objetos(object):

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.cosas={}


    def on_draw(self):
        self.batch.draw()
        return self

