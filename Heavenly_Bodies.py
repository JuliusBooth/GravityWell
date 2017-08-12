import math
import random
import pygame

import itertools
display_width = 600
display_height = 600
GRAVITATIONAL_CONSTANT = 0.001
DEFAULTSPEED = 3
BLACKHOLE_RADIUS = 30


class Heavenly_Body:
    instances = []
    other_objects = []
    def __init__(self, radius=10, density=1):
        self.density = density
        self.radius = radius
        self.volume = (4 / 3) * math.pi * self.radius ** 3
        self.mass = self.volume * density
        self.get_starting_position()
        self.dx = random.choice([i for i in range(-5,6)])
        self.dy = random.choice([i for i in range(-5,6)])
        self.ddx = 0
        self.ddy = 0

    def get_starting_position(self):
        if bool(random.getrandbits(1)):
            self.x = random.randint(0, display_width)
            self.y = random.choice([0,display_height])
        else:
            self.y = random.randint(0, display_height)
            self.x = random.choice([0, display_width])

    def draw(self, display):
        pygame.draw.circle(display, (0, 0, 200), (int(self.x), int(self.y)), int(self.radius))

    def update_pos(self):
        #self.check_for_wall()
        if len(Heavenly_Body.instances) > 1:
            for instance in Heavenly_Body.instances:
                if instance != self:
                    self.apply_forces(instance)
        for other_object in Heavenly_Body.other_objects:
            self.apply_forces(other_object)
        self.x += self.dx
        self.y += self.dy


    def check_for_wall(self):
        if self.x <= 0 or self.x >= display_width:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= display_height:
            self.dy = -self.dy


    def get_vectors(self,thatx,thaty):
        return(thatx-self.x, thaty-self.y)

    @staticmethod
    def hypotenuse(x,y):
        return (math.sqrt(x**2 + y**2))

    def apply_forces(self, other):
        self.ddx = 0
        self.ddy = 0

        x_length, y_length = self.get_vectors(other.x,other.y)
        distance_squared = x_length ** 2 + y_length ** 2
        distance = math.sqrt(distance_squared)
        theta = math.atan2(y_length, x_length)

        self.gravity(other,theta, distance_squared)

        if distance <= self.radius + other.radius - self.atmosphere - other.atmosphere:
            self.collision(other)
            return

        self.dx += self.ddx
        self.dy += self.ddy

    def gravity(self, other,theta,distance_squared):
        gravity_force = GRAVITATIONAL_CONSTANT * self.mass * other.mass / distance_squared
        x_force = gravity_force * math.cos(theta)
        y_force = gravity_force * math.sin(theta)
        x_acc = x_force / self.mass
        y_acc = y_force / self.mass
        self.ddx += x_acc
        self.ddy += y_acc

    def collision(self, other):
        if other in Heavenly_Body.other_objects:
            if other.identity == "Spaceship":
                other.game.crash()
                return
            else:
                Heavenly_Body.instances.remove(self)
                del self
                return
        total_mass = self.mass + other.mass
        if self.mass < other.mass:
            survivor = other
            loser = self
        else:
            survivor = self
            loser = other
        survivor.dx = (survivor.mass * survivor.dx + loser.mass * loser.dx) / total_mass
        survivor.dy = (survivor.mass * survivor.dy + loser.mass * loser.dy) / total_mass
        survivor.mass = total_mass
        survivor.volume += loser.volume
        survivor.density = survivor.mass / survivor.volume
        survivor.radius = (survivor.volume * (3 / 4) / math.pi) ** (1. / 3.)
        try:
            Heavenly_Body.instances.remove(loser)
            del loser
        except:
            print("error")

    #Not in use right now
    @staticmethod
    def calc_velocities(dx1, dy1, dx2, dy2, m1, m2):
        print(dx1)
        mt = m1 + m2
        dx1f = ((m1 - m2) / mt) * dx1 + dx2 * 2 * m2 / mt
        dx2f = ((m2 - m1) / mt) * dx2 + dx1 * 2 * m1 / mt
        dy1f = ((m1 - m2) / mt) * dy1 + dy2 * 2 * m2 / mt
        dy2f = ((m2 - m1) / mt) * dy2 + dy1 * 2 * m1 / mt

        return (dx1f, dy1f, dx2f, dy2f)


class Planet(Heavenly_Body):
    def __init__(self):
        radius = random.randint(5,9)
        density = random.randint(1, 10)
        Heavenly_Body.__init__(self, radius, density)
        self.atmosphere = 1
        Heavenly_Body.instances.append(self)


class Star(Heavenly_Body):
    def __init__(self, density=1):
        radius = random.randint(10, 20)
        Heavenly_Body.__init__(self, radius, density)
        #So that planets can pass near star without a collision
        self.atmosphere = 5
        self.num_points = 8
        Heavenly_Body.instances.append(self)

    def get_vertices(self):

        point_list = []

        for i in range(self.num_points):
            ang = i*2*math.pi/self.num_points
            x = self.x + int(math.cos(ang) * self.radius)
            y = self.y + int(math.sin(ang) * self.radius)
            point_list.append((x, y))
            ang = (i+0.5) * 2 * math.pi / self.num_points
            x = self.x + int(math.cos(ang) * self.radius/2)
            y = self.y + int(math.sin(ang) * self.radius/2)
            point_list.append((x, y))
        return(point_list)


    def draw(self, display):
        pygame.draw.polygon(display,(0,255,0),self.get_vertices())


class BlackHole(Heavenly_Body):
    def __init__(self):
        Heavenly_Body.__init__(self,radius=BLACKHOLE_RADIUS,density=100)
        self.x = int(display_width / 2)
        self.y = int(display_height / 2)
        self.dx = 0
        self.dy = 0
        self.atmosphere = 3
        self.identity = "Blackhole"
        Heavenly_Body.other_objects.append(self)

    def draw(self, display):
        pygame.draw.circle(display, (0, 0, 0), (int(self.x), int(self.y)), int(self.radius))



class SpaceShip(Heavenly_Body):
    def __init__(self,blackhole,game):
        Heavenly_Body.__init__(self, radius=12, density=10)
        self.x = random.randint(0,display_width)
        self.y = random.randint(0,display_height)
        self.starting_angle = self.get_angle()
        self.previous_angle = self.starting_angle
        self.score = 0
        self.atmosphere = 0
        self.game = game
        self.blackhole = blackhole
        self.get_velocity()
        self.identity = "Spaceship"
        self.image = pygame.image.load("/Users/juliusbooth/PycharmProjects/Gravity/Spaceship.bmp").convert()
        self.image = pygame.transform.scale(self.image, (self.radius*2, self.radius*2))
        self.image.set_colorkey((0,0,0))
        self.rotation()
        Heavenly_Body.other_objects.append(self)

    def get_score(self):
        return(self.score)

    def get_angle(self):
        x_vec, y_vec, dis = self.direction_to_center()
        theta = math.atan2(y_vec, x_vec)
        return(theta * -180 / math.pi)

    def update_score(self):
        angle = self.get_angle()
        if angle <= self.starting_angle and self.previous_angle > self.starting_angle:
            self.score += 1
        self.previous_angle = angle

    def draw(self, display):
        display.blit(pygame.transform.rotate(self.image , self.angle), (self.x-self.radius,self.y-self.radius))

    def direction_to_center(self):
        x_vec = display_width/2 - self.x
        y_vec = display_height/2 - self.y
        dis = math.sqrt(x_vec**2 + y_vec**2)
        return(x_vec, y_vec, dis)

    def collision(self):
        x_vec, y_vec, dis = self.direction_to_center()
        if dis <= self.radius + BLACKHOLE_RADIUS - 5:
            self.game.crash()


    def movedown(self):
        x,y,dis = self.direction_to_center()
        dx, dy = x/dis, y/dis
        self.x += dx*DEFAULTSPEED
        self.y += dy*DEFAULTSPEED

    def moveup(self):
        x,y,dis = self.direction_to_center()
        if dis >= display_height/2:
            pass
        else:
            dx, dy = x / dis, y / dis
            self.x -= dx*DEFAULTSPEED
            self.y -= dy*DEFAULTSPEED

    def update_pos(self):
        for i in range(500):
            self.get_velocity()
            self.x += self.dx
            self.y += self.dy
        self.rotation()
        self.update_score()
        self.collision()

    def rotation(self):
        self.angle = self.get_angle()


    def get_velocity(self):
        x_length, y_length, dis = self.direction_to_center()

        theta = math.atan2(y_length, x_length)

        velocity = math.sqrt(GRAVITATIONAL_CONSTANT*self.blackhole.mass/dis)/1000

        cdx = velocity * math.cos(theta)
        cdy = velocity * math.sin(theta)

        self.dx = cdy
        self.dy = -cdx
        self.dx += 50*GRAVITATIONAL_CONSTANT*x_length/dis**2
        self.dy += 50*GRAVITATIONAL_CONSTANT*y_length/dis**2

