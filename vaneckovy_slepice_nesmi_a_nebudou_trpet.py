import math
import copy
import pygame


# Initialize Pygame
pygame.init()

# Set the window size
window_size = [800, 800]

# Create the window
win = pygame.display.set_mode(window_size)

# Set the title of the window
pygame.display.set_caption("kys")


class Vector:
    def __init__(self, nums: list):
        self.nums = nums  # Data vektoru, představující čísla ve vektoru

    def __add__(self, other_vector: "Vector"):
        if isinstance(other_vector, Vector):

            if len(self.nums) == len(other_vector.nums):
                return Vector([a + b for a, b in zip(self.nums, other_vector.nums)])
            else:
                raise ValueError("Vectors have different dimensions")
        
        elif type(other_vector) == float or type(other_vector) == int:
            return Vector([a + other_vector for a in self.nums])
        
        else:
            raise TypeError("Addition with invalid type")
    

    def __sub__(self, other_vector: "Vector"):
        if isinstance(other_vector, Vector):

            if len(self.nums) == len(other_vector.nums):
                return Vector([a - b for a, b in zip(self.nums, other_vector.nums)])
            else:
                raise ValueError("Vectors have different dimensions")
            
        elif type(other_vector) == float or type(other_vector) == int:
            return Vector([a - other_vector for a in self.nums])

        else:
            raise TypeError("Addition with non-Vector type")
        
    def __mul__(self, other_vector):
        if isinstance(other_vector, Vector):

            if len(self.nums) == len(other_vector.nums):
                return Vector([a * b for a, b in zip(self.nums, other_vector.nums)])
            else:
                raise ValueError("Vectors have different dimensions")
            
        elif type(other_vector) == float or type(other_vector) == int:
            return Vector([a * other_vector for a in self.nums])

        else:
            raise TypeError("Addition with non-Vector type")
        
    def __truediv__(self, other_vector):
        if isinstance(other_vector, Vector):

            if len(self.nums) == len(other_vector.nums):
                return Vector([a / b for a, b in zip(self.nums, other_vector.nums)])
            else:
                raise ValueError("Vectors have different dimensions")
            
        elif type(other_vector) == float or type(other_vector) == int:
            return Vector([a / other_vector for a in self.nums])
            
        else:
            raise TypeError("Addition with non-Vector type")

    def rotateX(self, angle: float):
        if len(self.nums) != 3:
            raise ValueError("Vektor není 3dimenzionální, nelze otočit ve 3D")
        
        x, y, z = self.nums[0], self.nums[1], self.nums[2]
        self.nums = [
            x,
            y * math.cos(angle) - z * math.sin(angle),
            y * math.sin(angle) + z * math.cos(angle)
        ]
        return self
    
    def rotateY(self, angle: float):
        if len(self.nums) != 3:
            raise ValueError("Vektor není 3dimenzionální, nelze otočit ve 3D")
        
        x, y, z = self.nums[0], self.nums[1], self.nums[2]
        self.nums = [
            x * math.cos(angle) + z * math.sin(angle), 
            y, 
            -x * math.sin(angle) + z * math.cos(angle)
        ]
        return self
    
    def rotateZ(self, angle: float):
        if len(self.nums) != 3:
            raise ValueError("Vektor není 3dimenzionální, nelze otočit ve 3D")
        
        x, y, z = self.nums[0], self.nums[1], self.nums[2]
        self.nums = [
            x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle),
            z
        ]
        return self

    def X_rotation(self):
        return math.atan2(self.nums[2], self.nums[1])
    
    def Y_rotation(self):
        return math.atan2(self.nums[2], self.nums[0])
    
    def Z_rotation(self):
        return math.atan2(self.nums[1], self.nums[0])
        

    def __str__(self):
        return f"[{' '.join(map(str, self.nums))}]"
    
    def __getitem__(self, index):
        return self.nums[index]
    

class Object:
    def __init__(self, vertex_table: list[Vector], edge_table: list[list[int]], origin: Vector, color, line_thickness: float) -> None:
        self.vertex_table = vertex_table
        self.edge_table = edge_table
        self.origin = origin
        self.color = color
        self.line_thickness = line_thickness
        self.scale_vector = Vector([1, 1, 1])
        self.position_vector = Vector([0, 0, 0])
        self.rotation_vector = Vector([0, 0, 0])
        self.mesh = copy.deepcopy(vertex_table)

    
    def compute_average_origin(self):
        num_vertices = len(self.vertex_table)
        dimension = 3
        origin = Vector([0] * dimension)

        for vertex in self.vertex_table:
            origin += vertex

        self.origin = origin / num_vertices

    def compute_mesh(self) -> None:
        translated_origin = self.origin + self.position_vector
        computed_mesh = [0] * len(self.mesh)

        # scale, rotation_vector, translation
        for i in range(len(computed_mesh)):
            # scale
            transformed_vertex = self.mesh[i] * self.scale_vector
            # rotation_vector
            transformed_vertex.rotateX(self.rotation_vector[0])
            transformed_vertex.rotateY(self.rotation_vector[1])
            transformed_vertex.rotateZ(self.rotation_vector[2])
            # translation
            computed_mesh[i] = (transformed_vertex + self.position_vector)
            
        self.computed_mesh = computed_mesh


class Camera:
    def __init__(self, focal_length: float, aspect_ratio: float, position_vector: Vector, rotation_vector: Vector, clip_start: float) -> None:
        self.focal_length = focal_length
        self.aspect_ratio = aspect_ratio
        self.position_vector = position_vector
        self.rotation_vector = rotation_vector
        self.clip_start = clip_start
        

class Scene:
    def __init__(self, objects: list[Object], camera: Camera, window) -> None:
        self.objects = objects
        self.camera = camera
        self.window = window

    def render(self):

        for object in self.objects:
            object.compute_mesh()

            world_space_mesh = []
            screen_space_vertex_list = []
            for vertex_index, vertex in enumerate(object.computed_mesh):
                is_visible = False
                # translate the scene by camera origin
                translated_vertex = vertex - self.camera.position_vector
                # rotate the scene by -camera rotation
                translated_vertex.rotateX(-self.camera.rotation_vector[0]).rotateY(-self.camera.rotation_vector[1]).rotateZ(-self.camera.rotation_vector[2])

                if 1: # check if vertex is far enough from camera
                    world_space_mesh.append(translated_vertex)

                    projected_vertex = Vector([
                        translated_vertex[0] * self.camera.focal_length / translated_vertex[1],
                        translated_vertex[2] * self.camera.focal_length / translated_vertex[1],
                    ])
                    screen_space_vertex_list.append(projected_vertex)
            
            # vertex draw
            # for index, screen_space_vertex in enumerate(screen_space_vertex_list):
            #     pygame.draw.circle(self.window, object.color, screenSpaceOrientation2D(screen_space_vertex), 2)

            # edge draw
            for index, edge in enumerate(object.edge_table):
                v1 = screen_space_vertex_list[edge[0]]
                v2 = screen_space_vertex_list[edge[1]]

                pygame.draw.aaline(self.window, object.color, screenSpaceOrientation2D(v1), screenSpaceOrientation2D(v2))



            



        
def screenSpaceOrientation2D(vec: Vector):
    return [
        vec[0] + window_size[0] / 2,
        window_size[1] / 2 - vec[1]
    ]


vertex_table = [
   Vector([-1, -1, -1]),
   Vector([1, -1, -1]),
   Vector([1, 1, -1]),
   Vector([-1, 1, -1]),
   Vector([-1, -1, 1]),
   Vector([1, -1, 1]),
   Vector([1, 1, 1]),
   Vector([-1, 1, 1]),
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


o = Object(vertex_table, edge_table, Vector([0, 0, 0]), "red", 4)
o.position_vector = Vector([0, 0, 0])
o.scale_vector *= 2
o.rotation_vector += Vector([0, 0, 1])
o.compute_mesh()
for i in o.computed_mesh:
    print(i)
camera = Camera(50, 1, Vector([0, -5, 0]), Vector([0, 0, 0]), 0.01)
scene = Scene([o], camera, win)

t = 0
speed = 0.01

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        camera.position_vector += Vector([0, speed, 0])

    if keys[pygame.K_s]:
        camera.position_vector += Vector([0, -speed, 0])

    if keys[pygame.K_a]:
        camera.position_vector += Vector([-speed, 0, 0])

    if keys[pygame.K_d]:
        camera.position_vector += Vector([speed, 0, 0])




    win.fill("black")
    o.rotation_vector += Vector([0.001, 0.001, 0.001])


    scene.render()

    pygame.display.flip()
    t += 0.001
