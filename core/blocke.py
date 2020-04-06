from __future__ import division

import sys
import math
import random
import time

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from .config import *

class blocke:
    def __init__(self,top, bottom, side, nombre=None,tag=None,durable=1):
        self.texture = []
        self.tex_coords(top, bottom, side)
        self.nombre = nombre
        self.tag = tag
        self.__durabilidad = durable
        self.live = durable
        self.roto=False
        self.selected=False

        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

    def __eq__(self, other):
        '''comparacion entre dos blocques.
        '''
        return self.nombre == other.nombre
    def on_destroy(self):
        return self

    def on_select(self):
        '''cuando estaselccionado este blque'''
        self.selected=True

    def on_deSelected(self):
        '''cuando se deselecciona'''
        self.curandome();

    def on_action(self):
        # mostrar propiedades o capacidades
        # si existe alguna modificacion o actualizacion
        return False
    def on_hit(self):
        #al golpearlo.
        return False

    def on_golpeado(self):
        '''cuando se esta golpeando'''
        self.goleandome()

    def goleandome(self):
        # al golpear el bloque se debe debilitar.

        self.live -= 1
        # print("bloque golpeado",self.live)
        if ( self.live < 0 ):
            self.live = 0
            # self.roto = True

    def curandome(self):
        self.live = self.__durabilidad
    
    def tex_coords(self,top, bottom, side):
        """ Return a list of the texture squares for the top, bottom and side.

        """
        top = self.tex_coord(*top)
        bottom = self.tex_coord(*bottom)
        side = self.tex_coord(*side)
        result = []
        result.extend(top)
        result.extend(bottom)
        result.extend(side * 4)
        self.texture = result
        return result

    def tex_coord(self, x, y, n=4):
        """ Return the bounding vertices of the texture square.

        """
        m = 1.0 / n
        dx = x * m
        dy = y * m
        return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

    def cube_vertices(self, x, y, z, n):
        """ Return the vertices of the cube at position x, y, z with size 2*n.

        """
        return [
            x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n,  # top
            x - n, y - n, z - n, x + n, y - n, z - n, x + n, y - n, z + n, x - n, y - n, z + n,  # bottom
            x - n, y - n, z - n, x - n, y - n, z + n, x - n, y + n, z + n, x - n, y + n, z - n,  # left
            x + n, y - n, z + n, x + n, y - n, z - n, x + n, y + n, z - n, x + n, y + n, z + n,  # right
            x - n, y - n, z + n, x + n, y - n, z + n, x + n, y + n, z + n, x - n, y + n, z + n,  # front
            x + n, y - n, z - n, x - n, y - n, z - n, x - n, y + n, z - n, x + n, y + n, z - n,  # back
        ]