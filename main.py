import pygame
import math

# Initialize Pygame
pygame.init()

# Set the window size
window_size = [800, 800]

# Create the window
screen = pygame.display.set_mode((window_size[0], window_size[1]))

# Set the title of the window
pygame.display.set_caption("kys")



def rotateX(P, theta):
    y = (P[1] * math.cos(theta)) + (P[0] * -math.sin(theta))
    x = (P[1] * math.sin(theta)) + (P[0] * math.cos(theta))
    return [x, y, P[2]]
    
def rotateY(P, theta):
    x = (P[0] * math.cos(theta)) + (P[2] * -math.sin(theta))
    z = (P[0] * math.sin(theta)) + (P[2] * math.cos(theta))
    return [x, P[1], z]

def rotateZ(P, theta):
    y = (P[1] * math.cos(theta)) + (P[2] * -math.sin(theta))
    z = (P[1] * math.sin(theta)) + (P[2] * math.cos(theta))
    return [P[0], y, z]
    
def full_rotate_optimized(P, rotation_vector):
    # swap X with Z, i dunno why lol but works tho
    rotation_vector = [rotation_vector[2], rotation_vector[1], rotation_vector[0]]

    sinX, cosX = math.sin(rotation_vector[0]), math.cos(rotation_vector[0])
    sinY, cosY = math.sin(rotation_vector[1]), math.cos(rotation_vector[1])
    sinZ, cosZ = math.sin(rotation_vector[2]), math.cos(rotation_vector[2])

    y = (P[1] * cosX) + (P[0] * (-sinX))
    x = (P[1] * sinX) + (P[0] * cosX)
    P = [x, y, P[2]]

    x = (P[0] * cosY) + (P[2] * -(sinY))
    z = (P[0] * sinY) + (P[2] * cosY)
    P = [x, P[1], z]

    y = (P[1] * cosZ) + (P[2] * -(sinZ))
    z = (P[1] * sinZ) + (P[2] * cosZ)
    P = [P[0], y, z]
    
    return P

def vector_add(V1, V2):
    V = [None for _ in range(len(V1))]
    for i in range(len(V1)):
        V[i] = V1[i] + V2[i]
    return V

def vector_multiply(V1, V2):
    V = [None for _ in range(len(V1))]
    for i in range(len(V1)):
        V[i] = V1[i] * V2[i]
    return V
        


class object:
    def __init__(self, vertex_table, edge_table) -> None:
        self.vertex_table = vertex_table
        self.edge_table = edge_table
        self.origin = [0, 0, 0]
        self.vertices_position = [v for v in self.vertex_table]

    def scale(self, scale_vector):
        vertex_table = [None for _ in range(len(self.vertex_table))]
        for i, vertex in enumerate(self.vertices_position):
            vertex_table[i] = [vertex[0] * scale_vector[0], vertex[1] * scale_vector[1], vertex[2] * scale_vector[2]]
        self.vertices_position = vertex_table


    def rotate(self, rotation_vector):
        vertex_table = [None for _ in range(len(self.vertex_table))]
        for i, vertex in enumerate(self.vertices_position):
            vertex = vector_add(vertex, vector_multiply(self.origin, [-1, -1, -1]))
            vertex_table[i] = vector_add(full_rotate_optimized(vertex, rotation_vector), self.origin)
        self.vertices_position = vertex_table

    def translate(self, translation_vector):
        vertex_table = [None for _ in range(len(self.vertex_table))]
        self.origin = vector_add(self.origin, translation_vector)
        for i, vertex in enumerate(self.vertices_position):
            vertex_table[i] = vector_add(vertex, translation_vector)
        self.vertices_position = vertex_table


class camera:
    def __init__(self, focal_length, screen_size) -> None:
        self.focal_length = focal_length
        self.screen_size = screen_size

    def get_projection(self, vertex_table):
        projection_table = [None for _ in range(len(vertex_table))]
        for i, vertex in enumerate(vertex_table):
            x_projected = (self.focal_length * vertex[1]) / (self.focal_length + vertex[0])
            y_projected = (self.focal_length * vertex[2]) / (self.focal_length + vertex[0])
            projection_table[i] = [x_projected, y_projected]
        return projection_table

    def screen_projection(self, vertex_table):
        projection_table = self.get_projection(vertex_table)
        normalized_projection_table = [None for _ in range(len(projection_table))]
        for i in range(len(normalized_projection_table)):
            normalized_projection_table[i] = vector_add(projection_table[i], [self.screen_size[0] / 2, self.screen_size[1] / 2])
        return normalized_projection_table


# cube object
vertex_table = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1],
]
edge_table = [
    [0, 1],
    [0, 4],
    [0, 3],
    [1, 5],
    [1, 2],
    [2, 6],
    [2, 3],
    [3, 7],
    [7, 4],
    [7, 6],
    [5, 6],
    [5, 4],
]
cube = object(vertex_table, edge_table)
cube.scale([150, 150, 150])
cube.translate([600, 0, 0])


# house object
vertex_table = [
    [-1, -1, 0],    # 0
    [1, -1, 0],    # 1
    [1, 1, 0],    # 2
    [-1, 1, 0],    # 3
    [-1, -1, 2],    # 4
    [1, -1, 2],    # 5
    [1, 1, 2],    # 6
    [-1, 1, 2],    # 7
    [-0.5, 0, 3],    # 8 (left roof point)
    [0.5, 0, 3],    # 9 (right roof point)
]

edge_table = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 0],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 4],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7],
    [8, 9],
    [8, 4],
    [8, 0],
    [9, 5],
    [9, 1],
    [9, 2],
    [8, 3],
]
house = object(vertex_table, edge_table)
house.scale([150, 150, 150])
house.translate([800, 0, -100])



alpha = 0
pi = math.pi


# camera
c = camera(-200, window_size)


point_color = (255, 0, 0)
line_color = (0, 0, 255)
background_color = (0, 0, 0)
rgb_color = (0, 0, 0)

ob_ = cube

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)


    p = c.screen_projection(ob_.vertices_position)
    ob_.rotate([0.00, 0.00, -0.001])
    ob_.translate([0, 0, 0])

    for i in c.screen_projection(ob_.vertices_position):
        point_pos = i
        point_radius = 2
        pygame.draw.circle(screen, rgb_color, point_pos, point_radius)
        
    for edge in ob_.edge_table:
        pos0 = p[edge[0]]
        pos1 = p[edge[1]]
        pygame.draw.line(screen, rgb_color, pos0, pos1, 5)
    

    t = pygame.time.get_ticks() / 10**2
    # RGB effect
    rgb_color = ((math.sin(t) + 1) * 127.5, (math.sin(t + pi/2) + 1) * 127.5, (math.sin(t + pi) + 1) * 127.5)


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()