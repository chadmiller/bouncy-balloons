import random
import math
from time import time
from itertools import cycle

import pyglet
from pyglet.window import mouse

LINE_WIDTH = 4

COLORS = cycle(iter(((0x50, 0x26, 0xa7), (0x8d, 0x44, 0x8b), (0xcc, 0x6a, 0x87), (0xec, 0xcd, 0x8f), (0x42, 0xb8, 0x83), (0x34, 0x74, 0x74), (0xff, 0x7e, 0x67), (0xc7, 0x0d, 0x3a), (0xed, 0x51, 0x07), (0x02, 0x38, 0x3c), )))

window = pyglet.window.Window(fullscreen=True)



class Circle(object):
    def __init__(self, center_x, center_y, radius=1, is_growing=True, color=(0x33, 0x33, 0xaa)):
        self.update_interval = 0.07
        self.growth_speed = 0.7

        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.is_growing = is_growing
        self.color = color
        
        self._vertex_list = None
        self.points = ()
        self._last_calculated = None

        self.alive = 30
        self.sparseness = 3  # distance between points in circumference

        #self.draw_mode = pyglet.gl.GL_POINTS
        self.draw_mode = pyglet.gl.GL_POLYGON


    def draw(self):
        self.alive -= 0.01
        if not self._last_calculated or time() > (self._last_calculated + self.update_interval):
            self._recalculate()
            self._last_calculated = time()
        if self._vertex_list:
            self._vertex_list.draw(self.draw_mode)

    def _recalculate(self):
        if self.is_growing:
            self.radius += self.growth_speed
        else:
            self.radius -= self.growth_speed

        points = list()
        circumference = self.radius * 2 * math.pi
        increment_angle_degrees = 360.0 / circumference
        for θ in range(0, math.ceil(circumference), self.sparseness):
            angleInRadians = (increment_angle_degrees * θ) * (math.pi / 180)
            cosθ = math.cos(angleInRadians)
            sinθ = math.sin(angleInRadians)
            x = cosθ*self.radius + self.center_x
            y = sinθ*self.radius + self.center_y
            points.append((int(round(x)), int(round(y))))

        self.points = tuple(points)

        vertex_list = [i for (x1, y1) in self.points for i in (x1, y1)]

        if not self._vertex_list or len(self.points) != len(self._vertex_list.vertices):
            self._vertex_list = pyglet.graphics.vertex_list(len(self.points), "v2i", "c4B")

        self._vertex_list.vertices = vertex_list
        self._vertex_list.colors = tuple(i for _ in self.points for i in self.color+(int(round(min(255, self.alive*255))),))


    def collides_with(self, other):
        distance_between_centers = math.sqrt((self.center_x-other.center_x)**2 + (self.center_y-other.center_y)**2)

        # Other may encompass self
        #   other---------self+radius==]--]
        if other.radius >= distance_between_centers:
            # Edges are within some distance?
            if abs(other.radius - (distance_between_centers + self.radius)) < LINE_WIDTH:
                return True

        # Self may encompass other
        #   self---------other+radius==]--]
        if self.radius >= distance_between_centers:
            # Edges are within some distance?
            if abs(self.radius - (distance_between_centers + other.radius)) < LINE_WIDTH:
                return True

        if abs((self.radius + other.radius) - distance_between_centers) < LINE_WIDTH:
            return True

        return False

    def bounce(self):
        self.is_growing = not self.is_growing
        

def invalidate_window(dt):
    window.invalid = True



@window.event
def on_key_press(symbol, modifiers):
    if symbol in (113, 120):
        pyglet.app.exit()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        add_circle(x, y)


@window.event
def on_draw():
    window.clear()
    for circle in all_circles[:]:
        if circle.alive > 0:
            circle.draw()
        else:
            all_circles.remove(circle)

    has_bounce = set()
    for circle1 in all_circles[:]:
        if circle1.radius < 1:
            has_bounce.add(circle1)
            continue
        for circle2 in all_circles:
            if circle1 == circle2: continue
            if circle1.collides_with(circle2):
                has_bounce.add(circle1)
                has_bounce.add(circle2)

    for circle in has_bounce:
        circle.bounce()

def add_circle(x, y):
    new = Circle(x, y, color=next(COLORS))
    if any(circle.collides_with(new) for circle in all_circles):
        pass
        # BWOMP, illegal
    else:
        all_circles.append(new)

def spontaneous_circle(event):
    x, y = (random.randint(10, length-10) for length in window.get_size())
    add_circle(x, y)



all_circles = []

window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_CROSSHAIR))

pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
pyglet.gl.glLineWidth(LINE_WIDTH)

pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_DONT_CARE)

pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

pyglet.clock.schedule_interval(invalidate_window, 1.0/30)

spontaneous_circle(None)

pyglet.clock.schedule_interval(spontaneous_circle, 10)


pyglet.app.run()

