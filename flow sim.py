import timeit
import pygame as pg
import sys
import math
import itertools
import random
import numpy as np
from pygame.locals import *

pg.init()
pg.display.set_caption("my impeccable wave generator")
pg.font.init()
t = pg.time.get_ticks()*0.001

# github test...againsssxd..test3
#################################################
# render_mode:  0 = colour entire window with velocity gradient,
#               1 = use particles to visualize flow on window
render_mode = 1
#################################################

# display settings
xmax = 1400     # width of display window
ymax = 750      # height of display window
"""xmax = 1080
ymax = 720"""
scr = pg.display.set_mode((xmax, ymax))

# colour presets
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
font = pg.font.SysFont("Arial", 17)


# aerodynamics code begins here
origin = [xmax/2, ymax/2]
pos = []
Blit_array = []
arr = pg.surfarray.array3d(scr)


# just a random class i created to future proof this simulation for simulating more properties
class probe:
    def __init__(self, p):
        self.p = p


# simulation properties begin here

# sink: 1 = add sink flow to velocity field
#       0 = don't add sink flow to velocity field
sink = 1

# vortex:   1 = add vortex flow to velocity field
#           0 = don't add vortex flow to velocity field
vortex = 1


vorticity = 24000  # strength of vortex with arbitrary unit
obj_magnitude = 7200000  # strength of sink and source flows with arbitrary unit
Vfreestream = 800  # strength of the freestream velocity
obj_centerx = 0  # center of the "object"
obj_radiusx = 2.5  # distance between source n sink function centers


# ray_count: if the user wants to simulate rays instead of streamlines,
# then this will dictate the nunmber of rays to simulate
ray_count = 160


# rays_or_streamlines:  0 = use short rays to visualize flow
#                       1 = use streamline to visualize flow
# NOTE: rays_or_streamlines only matters if you want to render using particles,
# if you chose to colour the entire window then this changes nothing
rays_or_streamlines = 1


# simulation properties ends here


# the following few functions defines a couple types of flow functions


# source flow function
def v_source(a, b):
    x = a + obj_radiusx + obj_centerx
    y = b + 0
    theta = math.atan2(y, x)
    r = math.sqrt(y ** 2 + x ** 2)
    if int(r) == 0:
        r = 1
    # source strength (arbitrary unit)
    Q = obj_magnitude

    Vr = Q / (2 * math.pi * r)
    Vtheta = 0

    Vx = Vr*math.cos(theta)
    Vy = Vr*math.sin(theta)

    vel = [int(Vx), int(Vy)]

    return vel


# sink flow function
def v_sink(a, b):
    x = a - obj_radiusx + obj_centerx
    y = b - 0
    theta = math.atan2(y, x)
    r = math.sqrt(y ** 2 + x ** 2)
    if int(r) == 0:
        r = 1
    # source strength (arbitrary unit)
    Q = -obj_magnitude * sink

    Vr = Q / (2 * math.pi * r)
    Vtheta = 0

    Vx = Vr*math.cos(theta)
    Vy = Vr*math.sin(theta)

    vel = [int(Vx), int(Vy)]
    # print(vel)

    return vel


# freestream flow from left to right
def v_freestream(x, y):
    theta = math.atan2(y, x)
    r = math.sqrt(y ** 2 + x ** 2)
    if int(r) == 0:
        r = 1
    # free stream strength
    V = Vfreestream

    Vr = V*math.cos(theta)
    Vtheta = -V*math.sin(theta)

    Vx = Vr * math.cos(theta) - Vtheta*math.sin(theta)
    Vy = Vr * math.sin(theta) + Vtheta*math.cos(theta)

    vel = [int(Vx), int(Vy)]
    # print(vel)

    return vel


# vortex flow function
def v_vortex(a, b, c):
    x = a - c
    y = b - 0
    theta = math.atan2(y, x)
    r = math.sqrt(y ** 2 + x ** 2)

    if int(r) == 0:
        r = 1
    # vortex strength
    gamma = vorticity * vortex

    Vr = 0
    Vtheta = gamma/r

    Vx = Vr * math.cos(theta) - Vtheta * math.sin(theta)
    Vy = Vr * math.sin(theta) + Vtheta * math.cos(theta)

    vel = [int(Vx), int(Vy)]
    # print(vel)

    return vel

# flow function definitions ends here


# function to load a bunch of particles
def load_particles(q):
    for i in range(q):
        if rays_or_streamlines == 0:
            x = -xmax / 2 + (random.randint(-0.8 * xmax, 0.2 * xmax))
        else:
            x = -xmax / 2
        y = y_range * (ymax * i / (q - 10) - ymax / 2)
        pos.append(probe([x, y, 1, y]))


# y_range is how much of the y axis do you want the particles to span:
#               1 = spawn particles all along the left edge of window
#               0.5 = spawn particles on half of the left edge
if rays_or_streamlines == 0:
    y_range = 0.68
    # count = number of particles you want to appear on screen
    ray_count = 190
else:
    y_range = 1
    # count = number of particles you want to appear on screen
    ray_count = 55

if sink == 0:
    obj_magnitude = obj_magnitude/90

# logic for deciding how to render the simulation on the window
if render_mode == 0:
    tic = timeit.default_timer()
    print("Rendering...", end =" ")
    # these two following for loops goes through each and every pixel on the window,
    # finds out the magnitude of the velocity at that point,
    # and then returns a colour corresponding to the velocity's magnitude.
    for a in range(xmax):
        for b in range(ymax):
            # shifting the pygame's coordinate origin to the middle of the screen.
            i = a - xmax/2
            j = b - ymax/2
            source = v_source(i, j)
            freestream = v_freestream(i, j)
            vortx = v_vortex(i, j, obj_centerx)
            sinkv = v_sink(i, j)
            velx = source[0] * 1 + freestream[0] * 1 + vortx[0] + sinkv[0]
            vely = source[1] * 1 + freestream[1] * 1 + vortx[1] + sinkv[1]
            vel = vely ** 2 + velx ** 2
            rgb_factor1 = math.sqrt(vel) / Vfreestream
            rgb_factor = 0.5 * (rgb_factor1 ** 4)
            # DO NOT EVER INT() ANY OF THE RGB FACTORS,
            # IF YOU DO THE COLOURS OF THE PIXEL WILL NOT BE COOL LOOKING GRADIENTS
            rgb = [min(1, rgb_factor), min(1, abs(rgb_factor1 - 1))]
            colour = (255 * (1 - rgb[0]), 255 * rgb[1], 255 * rgb[0])
            arr[a][b] = colour
    toc = timeit.default_timer()
    print("Done!")
    print("Rendering time: ", round(toc - tic, 4), "seconds")
else:
    pg.draw.circle(scr, white, [int(origin[0]) + obj_centerx, int(origin[1])], 3)
    load_particles(ray_count)

play = 1
running = 1
while running:
    # refreshes screen
    # scr.fill(black)

    # processing user inputs
    keys = pg.key.get_pressed()
    if keys[K_DOWN]:
        vorticity -= 200
    if keys[K_UP]:
        vorticity += 200

    for event in pg.event.get():
        # Stay in main loop until pygame.quit event is sent
        if event.type == pg.QUIT:
            running = 0
        elif event.type == pg.KEYDOWN:
            # Escape key, end sim
            if event.key == pg.K_ESCAPE:
                running = 0
            # Spacebar, pause sim
            if event.key == pg.K_SPACE:
                if play == 0:
                    play = 1
                else:
                    play = 0
            if event.key == pg.K_BACKSPACE:
                scr.fill(black)
                pg.draw.circle(scr, white, [int(origin[0]) + obj_centerx, int(origin[1])], 3)
                for i in range(len(pos)):
                    pos[i].p[0] = -xmax / 2
                    pos[i].p[1] = pos[i].p[3]
            if event.key == pg.K_s:
                if sink == 1:
                    sink = 0
                    obj_magnitude = obj_magnitude / 55
                else:
                    sink = 1
                    obj_magnitude = obj_magnitude * 55
            if event.key == pg.K_v:
                if vortex == 1:
                    vortex = 0
                else:
                    vortex = 1
            if event.key == pg.K_r:
                pos.clear()
                scr.fill(black)
                pg.draw.circle(scr, white, [int(origin[0]) + obj_centerx, int(origin[1])], 3)
                if rays_or_streamlines == 0:
                    rays_or_streamlines = 1
                    y_range = 1
                    count = 55
                    load_particles(count)
                else:
                    rays_or_streamlines = 0
                    y_range = 0.68
                    ray_count = 220
                    load_particles(ray_count)

    t0 = t
    t = pg.time.get_ticks() * 0.001
    dt = t - t0

    dt_factor = 5  # this number divides the delta t by whatever this value is

    ########################################################################################################
    # Here begins the rendering of the particles
    ########################################################################################################

    # Making sure streak tracing only carried out when window isnt being moved, and when user wants streaks
    if dt < 0.01 and render_mode == 1 and play == 1:
        # iterating over all the loaded particles
        for i in range(len(pos)):
            # finding all the velocity components from the used flow functions
            source = v_source(pos[i].p[0], pos[i].p[1])
            freestream = v_freestream(pos[i].p[0], pos[i].p[1])
            vortx = v_vortex(pos[i].p[0], pos[i].p[1], obj_centerx)
            sinkv = v_sink(pos[i].p[0], pos[i].p[1])

            # summing the velocity components from all the used flow functions
            pos[i].p[0] = pos[i].p[0] + (source[0]*1 + freestream[0]*1 + vortx[0] + sinkv[0]*1)*(dt/dt_factor)
            pos[i].p[1] = pos[i].p[1] + (source[1]*1 + freestream[1]*1 + vortx[1] + sinkv[1]*1)*(dt/dt_factor)

            velx = source[0]*1 + freestream[0]*1 + vortx[0] + sinkv[0]*1
            vely = source[1]*1 + freestream[1]*1 + vortx[1] + sinkv[1]*1
            vel = vely**2 + velx**2
            rgb_factor1 = math.sqrt(vel)/Vfreestream
            rgb_factor = 0.5*(rgb_factor1**4)
            # DO NOT EVER INT() ANY OF THE RGB FACTORS I WILL KILL YOUUU

            rgb = min(1, rgb_factor)
            colour = (255*(1-rgb), 255*min(1, abs(rgb_factor1-1)), 255*rgb)
            position = [int(pos[i].p[0]+origin[0]), int(pos[i].p[1]+origin[1])]
            """pg.draw.circle(scr, colour, position, 1)
            pg.draw.circle(scr, colour, position, 4-(2*pos[i].p[2]))"""

            # drawing the particle on screen
            pg.draw.rect(scr, colour, [position[0], position[1], 2.5, 1])

            # teleport particle to left edge of the screen when it hits the right edge
            if pos[i].p[0] > xmax/2:
                pos[i].p[0] = -xmax/2
                pos[i].p[1] = pos[i].p[3]

            # checking if user wants to see rays, in which case it will manipulate the Blit_array
            if rays_or_streamlines == 0:
                Blit_array.append([position, 0])

        if rays_or_streamlines == 0:
            to_delete = []
            for i in range(len(Blit_array)):
                Blit_array[i][1] += dt
                if Blit_array[i][1] > 0.2:
                    position = [Blit_array[i][0][0], Blit_array[i][0][1]]
                    # pg.draw.circle(scr, black, position, 1)
                    pg.draw.rect(scr, black, [position[0], position[1]-1.2, 2, 3.4])
                    to_delete.append(Blit_array[i])

            for i in to_delete:
                Blit_array.remove(i)

    if render_mode == 1:
        box_x = 200
        box_y = 135
        border_width = 5
        pg.draw.rect(scr, white, [10-border_width/2, 10-border_width/2, box_x+border_width, box_y+border_width])
        pg.draw.rect(scr, black, [10, 10, box_x, box_y])

    if render_mode == 0:
        pg.surfarray.blit_array(scr, arr)
    else:
        text1 = font.render("Backspace = restart*", True, white)
        text2 = font.render("v = toggle vortex on/off", True, white)
        text3 = font.render("s = toggle sink on/off", True, white)
        text4 = font.render("Key up/down = + or - vorticity", True, white)
        """text5 = font.render("Key down = decrease vorticity", True ,white)"""
        text6 = font.render("r = toggle rays or streamlines", True, white)
        text7 = font.render("Space bar = toggle pause", True, white)
        scr.blit(text1, (15, 15))
        scr.blit(text7, (15, 35))
        scr.blit(text3, (15, 55))
        scr.blit(text2, (15, 75))
        scr.blit(text6, (15, 95))
        scr.blit(text4, (15, 115))
        """scr.blit(text5, (15, 135))"""

    # update screen
    pg.display.flip()


pg.quit()

# "restart" simply means particles teleported to left edge
