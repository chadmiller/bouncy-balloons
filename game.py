import math
from time import time
from itertools import cycle

import pyglet
from pyglet.window import mouse

window = pyglet.window.Window(width=1400, height=1000)


class Circle(object):
    def __init__(self, center_x, center_y, radius=1, is_growing=True, color=(0xaa, 0xaa, 0xaa)):
        self.birth = time()

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

        self.alive = 1
        self.sparseness = 3  # distance between points in circumference


    def draw(self):
        if not self._last_calculated or time() > (self._last_calculated + self.update_interval):
            self._recalculate()
            self._last_calculated = time()
        if self._vertex_list:
            self._vertex_list.draw(pyglet.gl.GL_POINTS)


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
            self._vertex_list = pyglet.graphics.vertex_list(len(self.points), "v2i", "c3B")

        self._vertex_list.vertices = vertex_list
        self._vertex_list.colors = [i for _ in self.points for i in self.color]

        if self.birth < time() - 10:
            self.alive -= 0.002


    def collides_with(self, other):
        distance_between_centers = math.sqrt((self.center_x-other.center_x)**2 + (self.center_y-other.center_y)**2)

        # Other may encompass self
        #   other---------self+radius==]--]
        if other.radius >= distance_between_centers:
            if abs(other.radius - (distance_between_centers + self.radius)) < 1:
                return True

        # Self may encompass other
        #   self---------other+radius==]--]
        if self.radius >= distance_between_centers:
            if abs(self.radius - (distance_between_centers + other.radius)) < 1:
                return True

        if abs((self.radius + other.radius) - distance_between_centers) < 1:
            return True

        return False


    def bounce(self):
        self.is_growing = not self.is_growing
        

def invalidate_window(dt):
    window.invalid = True


colors = cycle(iter(((0x50, 0x26, 0xa7), (0x8d, 0x44, 0x8b), (0xcc, 0x6a, 0x87), (0xec, 0xcd, 0x8f), (0x42, 0xb8, 0x83), (0x34, 0x74, 0x74), (0x35, 0x49, 0x5e), (0xff, 0x7e, 0x67), (0xc7, 0x0d, 0x3a), (0xed, 0x51, 0x07), (0x23, 0x03, 0x38), (0x02, 0x38, 0x3c), )))

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        all_circles.append(Circle(x, y, color=next(colors)))

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


all_circles = []

window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_CROSSHAIR))

#pyglet.gl.glLineWidth(3)
pyglet.clock.schedule_interval(invalidate_window, 1.0/30)
max_age = 500

all_circles.append(Circle(100, 100, radius=100))

pyglet.app.run()

