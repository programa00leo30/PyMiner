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

class Player:
    def __init__(self):

        self.batch = pyglet.graphics.Batch()

        self.position = (0,0,0)
        self.rotation = (0,0)
        self.width=0
        self.height=0
        
        self.batch = pyglet.graphics.Batch()
        self.inventory=[]
        self.indice = 0 # el nro de indice selecionado en el inventario.
        self.flying = False
        '''para realizar saltos'''
        self.dy=0

        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]
        #windows tamaño por defecto
        # width, height=800,600
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            # x=height-10, y=width - 10, anchor_x='left', anchor_y='top',
            x= 10, y= 10, anchor_x='left', anchor_y='bottom',
            color=(0, 0, 0, 255))
        # rutas de recursos
        self.__ui=[]
        self._showInventori=False
        self._iniciaUI_JUGADOR()
        self.reticle = None


    def _iniciaUI_JUGADOR(self):
        #pyglet.resource.path = [u'img']
        pyglet.resource.path = [u'/home/leandro/nec2_files/programas/python/minecraft/PyMiner/core/img']
        pyglet.resource.reindex()
        # imagen
        #imagen = pyglet.resource.image('uiPlayer.png')
        # imagen
        #imagen = pyglet.resource.image(u'ui_form_bg.png')
        #  anclas (anchors)
        #imagen.anchor_x = imagen.width / 2
        #imagen.anchor_y = imagen.height / 2

        #parametros de posicionamiento x,y, profundidad 0 es el fondo.
        self.__ui.append( [ pyglet.resource.image(u'ui_form_bg.png') , [0 , 0 , 0 ] ] )
        self.__ui.append( [ pyglet.resource.image(u'ui_main_inventory.png'),[10,10,1]] )
        # x,y,z,n=0,0,0,20
        # #
        # self.reticle = pyglet.graphics.vertex_list(4,
        #        #('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        #        ('v2f', (x - n, y, x + n, y, x, y - n, x, y + n))
        #               )


    def draw_ui(self,posicion):
        # print(posicion)
        # alpha blending
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        for img in self.__ui :
            pos = img[1]
            pos = pos[0]+posicion.width/8, pos[1]+posicion.height/8,0
            img[0].blit(*pos)
        #
        # pos = self.__ui[1][1]
        # pos = pos[0]+posicion.width/8, pos[1]+posicion.height/8,0
        # self.__ui[1][0].blit(*pos)

    def addInventory(self,objeto,cantidad=1):
        # obtener blocke u objeco.
        #objeto, cantidad, posicion en el inventario
        tn=False
        for t in self.inventory:
            if t[0] == objeto :
                tn=True
                t[1]+=cantidad
                break
        if not tn:
            self.inventory.append( [objeto,cantidad,len(self.inventory)] )
        # agregar=[objeto,10,len(self.inventory)]
        print(len(self.inventory))
        if len(self.inventory) > 0:   #no hay inventario.
            if self.indice < 0 :
                self.indice = 1  #el primer elemento.
        else :
            self.indice = -1

    def removeInventory(self,cantidad):
        t=self.inventory[self.indice]
        if t[1] > 0 and (t[1]-cantidad) > 0 :
            t[1]-=1
            # self.inventory[self.indice] = t
        else :
            self.inventory.pop(self.indice)
        print ("objetos:",t)
        return t

    def cantidadItemsSelecionado(self):
        if(self.isSelectedItem()):
            t=self.inventory[self.indice]
            return t[1]
        else :
            return 0

    def selectInventory(self,indice):
        if not ( len(self.inventory) <= indice ) :
            t=self.inventory[indice]
            self.indice=indice
            return t[1]
        else:
            return 0

    def isSelectedItem(self):
        #si un item esta seleccionado.
        return not ( len(self.inventory) <= self.indice )

    def selectInventoryBlock(self):
         if len(self.inventory) <= self.indice :
             return AIR #blocke((0, 3), (0, 3), (0, 3),"Invalido")
         else:
             return self.inventory[self.indice][0]

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # label
        # self.label.y = height - 10
        # reticle
        if self.reticle:
            print("reescribiendo la cruz")
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
             #   ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
                ('v2f', (x - n, y, x + n, y, x, y - n, x, y + n))
            )
    def on_draw_ui(self,window):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        #self.draw_focused_block(self.model)
        self.set_2d(window)
        self.draw_label()
        if self._showInventori :
            self.draw_ui(window)
        else :
            self.draw_reticle()

    def set_2d(self,window):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = window.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = window.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        if not self.reticle :
            width , height = 800 , 600
            x, y = width // 2, height // 2
            n = 10
            self.reticle = pyglet.graphics.vertex_list(4,
                   ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
                   )
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        #return self.reticle.draw(GL_LINES)

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = self.position
        rx,ry = self.rotation
        cantidad = self.cantidadItemsSelecionado()
        text = 'position (%.2f, %.2f, %.2f) pich: %d,%d item select: %s cantidad %d ' % (
             x, y, z,
            # len(self.model._shown), len(self.model.world),
            rx,ry ,
             str( self.selectInventoryBlock().nombre ),
            cantidad
            )
        self.label.text = text
        return self.label.draw()
    def fisic(self,dt,collide):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            # if self.dy != 0 :
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        #print("dy:",dy)
        # collisions
        x, y, z = self.position
        x, y, z = collide((x + dx, y + dy+0, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)
        return self

    def on_jump(self,JUMP_SPEED):
        if self.dy == 0:
            self.dy = JUMP_SPEED

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
        #pyglet.window.key._key_names
        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.SPACE:
            self.on_jump(JUMP_SPEED)
            # if self.player.dy == 0:
            #     self.player.dy = JUMP_SPEED
        #elif symbol == key.ESCAPE:
            #esc : se debe utilizar para salir.
            #self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            # si es un numero del teclado
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            # self.block = self.inventory[index][1]
            self.block = self.selectInventory(index)

    def on_key_release(self,symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

    def on_right_hand(self,model ):

        '''
            al acionar con la mano derecha (boton derecho del mouse
            recibe la base completa y el bloque seleccionado.
        '''
        print("on_right_hand")
        vector = self.get_sight_vector()
        block, previous = model.hit_test(self.position, vector)
        blocke = model.on_hit(block)
        if blocke :
            self.addInventory(blocke)
        # texture = self.model.world[block]
        # if texture != STONE: # si es una piedra no remover.
        #     self.model.remove_block(block)

        #blocke = model.world[PositionBlock]
        #print("blocke:", blocke)
        #blocke.goleandome()
        #if blocke.roto :
        #    model.world.remove_block( PositionBlock)
        # if texture != STONE:  # si es una piedra no remover.
        #     self.model.remove_block(PositionBlock)

    def on_left_hand(self,model):
        '''al acionar con la mano derecha (boton izquierdo del mouse'''
        print("on_left_hand")
        vector = self.get_sight_vector()
        block, previous = model.hit_test(self.position, vector)
        addBlock = self.selectInventoryBlock()
        if addBlock != AIR :
            if previous:
                print("agregando bloque..",addBlock.nombre," en: ",previous )
                model.add_worl_block(previous, addBlock,debug=True)
                self.removeInventory(1)

    def on_inventory(self,NoMostrar):
        self._showInventori = not NoMostrar
        #self._showInventori = not self._showInventori

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def draw_focused_block(self,model):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """

        vector = self.get_sight_vector()
        block = model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            # utilizando funcion externa declarada en config.py
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        return self

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)