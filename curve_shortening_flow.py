import pygame
import math
import numpy as np

# Curve shortening flow in Pygame. 
# Run the script and draw a shape of your liking. 
# Press space and watch the curve evolve!

dims = 1200, 1000
screen = pygame.display.set_mode(dims, 0, 32)
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 40)
textsurface = myfont.render('Curve shortening flow', False, (190, 200, 190))

points = []

# Computes the area of the shape (which is a polygon) using
# the 'shoelace formula'.
def area(points):
    return np.abs(sum([points[i-1][0]*points[i][1]-points[i][0]*points[i-1][1] for i in range(len(points))])/2)/(dims[0]*dims[1])

# Computes the radius of a sphere with the points p0,.., p2
# on its perimeter. Used a measure of curvature.
def radius(p0, p1, p2):
    p0 = np.array(p0)
    p1 = np.array(p1)
    p2 = np.array(p2)
    p1 -= p0
    p2 -= p0
    try:
        return np.linalg.norm(np.linalg.solve([2*p1, 2*p2], [np.dot(p1, p1), np.dot(p2, p2)]))
    except:
        return 0.0

def unit_vector(vector):
    size = np.linalg.norm(vector)
    if size == 0:
        return (0,0)
    return (vector[0]/size, vector[1]/size)

# Curve shortening flow algorithm.
# Moves points according to curvature.
def curve_shortening_flow(points, ds, iterations):
    points = np.array(points)
    new_points = []
    curvature_points = []
    direction_points = []
    length = len(points)
    for _ in range(iterations-1):
        for i in range(length):
            p0, p1, p2 = points[i-1], points[i], points[(i+1)%length]
            uv = unit_vector(((p2[0]+p0[0])/2-p1[0], (p2[1]+p0[1])/2-p1[1]))
            if uv[0] == 0 and uv[1] == 0:
                new_points += [p1]
            else:
                r = radius(p0, p1, p2)
                if not r:
                    new_points += [p1]
                else:
                    kappa = 1/r
                    new_y = p1[1] + 40*uv[1]*ds*kappa
                    new_x = p1[0] + 40*uv[0]*ds*kappa
                    curvature_points.append(kappa)
                    new_points += [(new_x, new_y)]
        points = new_points
        new_points = []
    for i in range(length):
        p0, p1, p2 = points[i-1], points[i], points[(i+1)%length]
        uv = unit_vector(((p2[0]+p0[0])/2-p1[0], (p2[1]+p0[1])/2-p1[1]))
        if uv[0] == 0 and uv[1] == 0:
            curvature_points.append(0)
            new_points += [p1]
        else:
            r = radius(p0, p1, p2)
            if not r:
                curvature_points.append(0)
                new_points += [p1]
            else:
                kappa = 1/r
                new_y = p1[1] + 40*uv[1]*ds*kappa
                new_x = p1[0] + 40*uv[0]*ds*kappa
                curvature_points.append(kappa)
                new_points += [(new_x, new_y)]
        direction_points.append(uv)
    return new_points, curvature_points, direction_points


def dist(p0, p1):
    return ((p0[0]-p1[0])**2 + (p0[1]-p1[1])**2)**0.5

# Removes points which are too close to reduce calculations
def kill_the_points(points, graininess):
    length = len(points)
    i = 0
    while i < length:
        if dist(points[i-1], points[i]) < 5 + graininess*5 and dist(points[i], points[(i+1)%length]) < 5 + graininess*5:
            del points[i]
            length -= 1
        else:
            i += 1
    return points

# Adds points when points are too far apart.
def generate_the_points(points, graininess):
    length = len(points)
    i = 0
    while i < length:
        if dist(points[i-1], points[i]) > 6+graininess*5:
            points.insert(i, ((points[i-1][0]+points[i][0])/2, (points[i-1][1]+points[i][1])/2))
            length += 1
        else:
            i += 1
    return points

running = True
clicked_last = False
last_mouse_click = False
finished  = True
was_begun = False
b = False
graininess = 1
speed = 1
grain_bool = False
while running:
    screen.fill((15,25,35))
    grain_bool = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                b = not b
                was_begun = True
                points = generate_the_points(points, graininess)
            if event.key == pygame.K_UP:
                speed *= 1.1
            if event.key == pygame.K_DOWN:
                speed /= 1.1
                grain_bool = True

    if pygame.mouse.get_pressed()[0] and not last_mouse_click \
    and 0 < pygame.mouse.get_pos()[0] < 100 \
        and 0 < pygame.mouse.get_pos()[1] < 50:
        finished = not finished
    else:
        if pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pos() in points:
            p = pygame.mouse.get_pos()
            points.append((float(p[0]), float(p[1])))
            clicked_last = True
            was_begun = False
        elif clicked_last:
            clicked_last = False
    if len(points) > 5:
        if b:
            if grain_bool:
                points = generate_the_points(points, speed*graininess/10)
            else:
                points = kill_the_points(points, speed*graininess/10)
            if len(points) > 2:
                points, curvature_points, direction_points = curve_shortening_flow(points, speed*graininess/10, 5)
                max_curvature = 255/np.max(curvature_points)
                c_area = 10*area(points)
                graininess = c_area if c_area > 1 else 1;

                screen.blit(myfont.render(f'Area: {c_area:0.3f}', False, (190, 200, 190)), (dims[0]-210, 0))
                for i in range(len(points)):
                    pygame.draw.line(screen, (curvature_points[i]*max_curvature,
                    150-120/255*curvature_points[i]*max_curvature, 255-curvature_points[i]*max_curvature),
                    points[i-1], points[i], 1)
            else:
                points = list()
                was_begun = False
                b = False

        else:
            if not was_begun:
                pygame.draw.lines(screen, (212, 212, 212), False, points)
            else:
                points = generate_the_points(points, graininess*speed)
                c_area = 10*area(points)
                graininess = c_area if c_area > 1 else 1;
                screen.blit(myfont.render(f'Area: {c_area:0.3f}', False, (190, 200, 190)), (dims[0]-210, 0))
                for i in range(len(points)):
                    pygame.draw.line(screen, (212, 212, 212), points[i-1], points[i])
    elif was_begun:
        points = []
        was_begun = False
        b = False;
    screen.blit(myfont.render(f'Speed: {speed:.2f}', False, (190, 200, 190)), (0,dims[1]-50))
    screen.blit(textsurface,(0,0))
    pygame.display.update()
    last_mouse_click = pygame.mouse.get_pressed()[0]
