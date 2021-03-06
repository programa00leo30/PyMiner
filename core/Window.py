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
from .blocke import *
from .Model import *
from .player import *
from .Objetos import *
from .vida import *


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.iniciando = True
        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        self.player = Player()
        # When flying gravity has no effect and speed is increased.
        self.player.flying = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.player.strafe = [0, 0]

        # mostrar informacion de depuracion:
        self.debug = True


        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        # self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        # self.rotation = (0, 0)

        # Which sector the player is currently in.
        # parte del mapa que se carga en memoria.
        self.sector = None

        # The crosshairs at the center of the screen.
        # self.reticle = None

        # Velocity in the y (upward) direction.
        # self.dy = 0

        # A list of blocks the player can place. Hit num keys to cycle.
        # self.inventory = [GRASS,SAND,BRICK,STONE,WATER]

        # The current block the user can place. Hit num keys to cycle.
        # self.block = self.inventory[0]
        # self.block = object() #blocke()
        
        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model()
        self.objetos = Objetos()
        self.vida = Vida()
        
        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
           x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
           color=(0, 0, 0, 255))

        # mostrar un mesnsaje por n segundos.
        self.ShowMesgSeg =0
        self.msg=pyglet.text.Label('',
            font_size=20,
            x=self.width / 2, y=self.height / 2,
            anchor_x='center', anchor_y='center')
        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        #if not exclusive :
        self.player.on_inventory(exclusive)

    # def get_sight_vector(self):
    #     """ Returns the current line of sight vector indicating the direction
    #     the player is looking.
    #
    #     """
    #
    #     x, y = self.player.rotation
    #     # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
    #     # is 1 when looking ahead parallel to the ground and 0 when looking
    #     # straight up or down.
    #     m = math.cos(math.radians(y))
    #     # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
    #     # looking straight up.
    #     dy = math.sin(math.radians(y))
    #     dx = math.cos(math.radians(x - 90)) * m
    #     dz = math.sin(math.radians(x - 90)) * m
    #     return (dx, dy, dz)

    # def get_motion_vector(self):
    #     """ Returns the current motion vector indicating the velocity of the
    #     player.
    #
    #     Returns
    #     -------
    #     vector : tuple of len 3
    #         Tuple containing the velocity in x, y, and z respectively.
    #
    #     """
    #     if any(self.player.strafe):
    #         x, y = self.player.rotation
    #         strafe = math.degrees(math.atan2(*self.strafe))
    #         y_angle = math.radians(y)
    #         x_angle = math.radians(x + strafe)
    #         if self.flying:
    #             m = math.cos(y_angle)
    #             dy = math.sin(y_angle)
    #             if self.player.strafe[1]:
    #                 # Moving left or right.
    #                 dy = 0.0
    #                 m = 1
    #             if self.player.strafe[0] > 0:
    #                 # Moving backwards.
    #                 dy *= -1
    #             # When you are flying up or down, you have less left and right
    #             # motion.
    #             dx = math.cos(x_angle) * m
    #             dz = math.sin(x_angle) * m
    #         else:
    #             dy = 0.0
    #             dx = math.cos(x_angle)
    #             dz = math.sin(x_angle)
    #     else:
    #         dy = 0.0
    #         dx = 0.0
    #         dz = 0.0
    #     return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.iniciando = False
        self.model.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        # speed = FLYING_SPEED if self.player.flying else WALKING_SPEED
        # d = dt * speed # distance covered this tick.
        # dx, dy, dz = self.get_motion_vector()
        # # New position in space, before accounting for gravity.
        # dx, dy, dz = dx * d, dy * d, dz * d
        # # gravity
        # if not self.flying:
        #     # Update your vertical speed: if you are falling, speed up until you
        #     # hit terminal velocity; if you are jumping, slow down until you
        #     # start falling.
        #     self.dy -= dt * GRAVITY
        #     self.dy = max(self.dy, -TERMINAL_VELOCITY)
        #     dy += self.dy * dt
        # # collisions
        # x, y, z = self.player.position
        # x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        # self.player.position = (x, y, z)
        self.player.fisic(dt, self.collide )

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    # es el mismo bloque
                    continue
                # buscar en tamaño del jugador.
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy #el suelo?
                    op[i] += face[i]
                    '''text: esta es la parte de visualizar objeto:'''
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.player.dy = 0
                    break
        if p[1] < -5 :
            p[1]=15
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if not self.iniciando :
            if self.exclusive  :
                self.mensaje("se ha precionado un boton del mouse")

                if (button == mouse.RIGHT) or \
                        ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                    # ON OSX, control + left click = right click.
                    self.player.on_left_hand(self.model)
                elif button == pyglet.window.mouse.LEFT:
                    '''al precionar boton izquierdo.'''
                    self.player.on_right_hand(  self.model )
            else:
                self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive:
            m = 0.15
            x, y = self.player.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            if (x > 180 ): x = -179
            if (x < -179 ): x = 180
            self.player.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        # if symbol == key.W:
        #     self.player.strafe[0] -= 1
        # elif symbol == key.S:
        #     self.player.strafe[0] += 1
        # elif symbol == key.A:
        #     self.player.strafe[1] -= 1
        # elif symbol == key.D:
        #     self.player.strafe[1] += 1
        # elif symbol == key.SPACE:
        #     self.player.on_jump(JUMP_SPEED)
        #     # if self.player.dy == 0:
        #     #     self.player.dy = JUMP_SPEED
        # el
        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        if symbol == key.F5 :
            self.debug = not self.debug
            print("debugmode:",self.debug)
        else :
            self.player.on_key_press(symbol, modifiers)
        # if symbol == key.TAB:
        #     self.player.flying = not self.player.flying
        # elif symbol in self.num_keys:
        #     # si es un numero del teclado
        #     index = (symbol - self.num_keys[0]) % len(self.inventory)
        #     self.block = self.inventory[index]

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        self.player.on_key_release(symbol,modifiers)

        
    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # label
        self.label.y = height - 10
        self.player.on_resize( width , height)
        # reticle

        # if self.reticle:
        #     self.reticle.delete()
        # x, y = self.width // 2, self.height // 2
        # n = 10
        # self.reticle = pyglet.graphics.vertex_list(4,
        #     ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        # )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        #self.model.batch.draw()
        #self.draw_focused_block()
        #self.player.batch.draw()
        self.model.on_draw()
        self.player.draw_focused_block(self.model)
        #self.set_2d()
        self.player.on_draw_ui(self)
        if self.debug:
            self.draw_label()

        #self.draw_label()
        #self.draw_reticle()

    # def draw_focused_block(self):
    #     """ Draw black edges around the block that is currently under the
    #     crosshairs.
    #
    #     """
    #     self.player.draw_focused_block(self.model)
        # vector = self.get_sight_vector()
        # block = self.model.hit_test(self.position, vector)[0]
        # if block:
        #     x, y, z = block
        #     vertex_data = cube_vertices(x, y, z, 0.51)
        #     glColor3d(0, 0, 0)
        #     glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        #     pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
        #     glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.
            informacion de depuracion.
        """
        self.label.text = 'fps:%02d cubos(modelo/mundo): %d / %d ' % (
            pyglet.clock.get_fps(),
            len(self.model._shown), len(self.model.world)
            )
        self.label.draw()
        if self.ShowMesgSeg > 0 :
            self.msg.draw()
            self.ShowMesgSeg -= 0.1

    def mensaje(self,mensaje,seg=10):
        # self.msg = pyglet.text.Label(
        #     mensaje,
        #     font_size=20,
        #     x=self.width / 2, y=self.height / 2,
        #     anchor_x='center', anchor_y='center'
        # )
        self.ShowMesgSeg = seg
        self.msg.text=mensaje



    #
    # def draw_iu(self):
    #     self.player.draw()
        
    # def draw_reticle(self):
    #     """ Draw the crosshairs in the center of the screen.
    #
    #     """
    #     self.player.draw_reticle()
    #     # glColor3d(0, 0, 0)
    #     # self.reticle.draw(GL_LINES)
