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
clock = pygame.time.Clock()


class Vector:
    def __init__(self, nums: list):
        self.nums = nums  # Data vektoru, představující čísla ve vektoru

    def __add__(self, other_vector):
        if isinstance(other_vector, Vector):
            return Vector([a + b for a, b in zip(self.nums, other_vector.nums)])
        elif isinstance(other_vector, (float, int)):
            return Vector([a + other_vector for a in self.nums])
        else:
            raise TypeError("Addition with invalid type")

    def __sub__(self, other_vector):
        if isinstance(other_vector, Vector):
            return Vector([a - b for a, b in zip(self.nums, other_vector.nums)])
        elif isinstance(other_vector, (float, int)):
            return Vector([a - other_vector for a in self.nums])
        else:
            raise TypeError("Subtraction with invalid type")

    def __mul__(self, other_vector):
        if isinstance(other_vector, Vector):
            return Vector([a * b for a, b in zip(self.nums, other_vector.nums)])
        elif isinstance(other_vector, (float, int)):
            return Vector([a * other_vector for a in self.nums])
        else:
            raise TypeError("Multiplication with invalid type")

    def __truediv__(self, other_vector):
        if isinstance(other_vector, Vector):
            return Vector([a / b for a, b in zip(self.nums, other_vector.nums)])
        elif isinstance(other_vector, (float, int)):
            return Vector([a / other_vector for a in self.nums])
        else:
            raise TypeError("Division with invalid type")

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
    
    def lenght(self):
        square_sum = 0
        for num in self.nums:
            square_sum += num ** 2
        return math.sqrt(square_sum)
        

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
        self.screen_vertex_projection_list = []

    
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

    def read_obj_file(self, file_path):
        vertices = []
        edges = []

        with open(file_path, 'r') as file:
            lines = file.readlines()

            for line in lines:
                tokens = line.split()

                if not tokens:
                    continue

                if tokens[0] == 'v':
                    # Parse vertices
                    x, y, z = map(float, tokens[1:])
                    vertices.append(Vector([x, y, z]))

                elif tokens[0] == 'f':
                    # Parse faces (edges in this case)
                    face_indices = [int(token.split('/')[0]) - 1 for token in tokens[1:]]
                    for i in range(len(face_indices)):
                        edges.append([face_indices[i], face_indices[(i + 1) % len(face_indices)]])

        self.vertex_table = vertices
        self.edge_table = edges
        self.mesh = copy.deepcopy(self.vertex_table)


class Camera:
    def __init__(self, focal_length: float, aspect_ratio: float, position_vector: Vector, rotation_angles: Vector, clip_start: float) -> None:
        self.focal_length = focal_length
        self.aspect_ratio = aspect_ratio
        self.position_vector = position_vector
        self.rotation_angles = rotation_angles
        self.clip_start = clip_start
        self.look_vector = Vector

    def compute_look_vector_euler(self):
        pitch, yaw = self.rotation_angles[0], self.rotation_angles[2]
        
        y = math.cos(pitch) * math.cos(yaw)
        z = math.sin(pitch)
        x = -math.cos(pitch) * math.sin(yaw)
        self.look_vector = Vector([x, y, z])

class Scene:
    def __init__(self, objects: list[Object], camera: Camera, window) -> None:
        self.objects = objects
        self.camera = camera
        self.window = window

    def render(self):
        visible_objects = []
        camera.compute_look_vector_euler()

        for object in self.objects:
            is_visible = False
            object.compute_mesh()

            world_space_mesh = []
            screen_space_vertex_list = []
            for vertex_index, vertex in enumerate(object.computed_mesh):
                # translate the scene by camera origin
                translated_vertex = vertex - self.camera.position_vector
                # rotate the scene by -camera rotation
                # translated_vertex.rotateX(-self.camera.rotation_angles[0]).rotateY(-self.camera.rotation_angles[1]).rotateZ(-self.camera.rotation_angles[2])
                translated_vertex.rotateZ(-self.camera.rotation_angles[2]).rotateY(-self.camera.rotation_angles[1]).rotateX(-self.camera.rotation_angles[0])
                world_space_mesh.append(translated_vertex)


                if translated_vertex[1] == 0:
                    # projected_vertex = Vector([float("inf"), float("inf")]) 
                    projected_vertex = Vector([0, 0])

                else:
                    projected_vertex = Vector([
                        translated_vertex[0] * self.camera.focal_length / translated_vertex[1],
                        translated_vertex[2] * self.camera.focal_length / translated_vertex[1],
                    ])

                if translated_vertex[1] > self.camera.clip_start: # check if vertex is far enough from camera
                    is_visible = True
                    projected_vertex.nums.append(1) # in front of the camera
                    screen_space_vertex_list.append(projected_vertex)

                else:
                    projected_vertex *= -100 # to ensure the single vertex visible edge spans to the screen border and inverts the position
                    projected_vertex.nums.append(0) # behind the camera
                    screen_space_vertex_list.append(projected_vertex)


            object.screen_vertex_projection_list = screen_space_vertex_list
            
            if is_visible:
                visible_objects.append(object)
            # vertex draw
            # for index, screen_space_vertex in enumerate(screen_space_vertex_list):
            #     pygame.draw.circle(self.window, object.color, screenSpaceOrientation2D(screen_space_vertex), 2)

            # edge draw
            for index, edge in enumerate(object.edge_table):
                v1 = screen_space_vertex_list[edge[0]]
                v2 = screen_space_vertex_list[edge[1]]

                if v1[2] or v2[2]:
                    pygame.draw.aaline(self.window, object.color, screenSpaceOrientation2D(v1), screenSpaceOrientation2D(v2))


            for object in visible_objects:
                1


        
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
o.rotation_vector += Vector([0, 0, 0])
o.compute_mesh()

ico = Object(0, 0, Vector([0, 0, 0]), "blue", 4)
ico.read_obj_file("ico.obj")

nig = Object(0, 0, Vector([0, 0, 0]), "blue", 4)
nig.read_obj_file("nig.obj")

camera = Camera(500, 1, Vector([0, -2, 0]), Vector([0, 0, 0]), 0.01)
scene = Scene([nig], camera, win)

t = 0
speed = 0.03
FPS = 300
font = pygame.font.Font(None, 20)
running = True

# mouse movement setup
mouse_pos = Vector([])
pygame.event.set_grab(True)  # grab the mouse
pygame.mouse.set_visible(False)  # hide the cursor

while running:
    clock.tick(FPS)
    start_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        camera.position_vector += camera.look_vector * speed

    if keys[pygame.K_s]:
        camera.position_vector += camera.look_vector * -speed

    if keys[pygame.K_a]:
        strafe_vector = camera.look_vector.rotateZ(-math.pi / 2) * -speed
        strafe_vector = strafe_vector * Vector([1, 1, -1])
        camera.position_vector += strafe_vector

    if keys[pygame.K_d]:
        strafe_vector = camera.look_vector.rotateZ(math.pi / 2) * -speed
        strafe_vector = strafe_vector * Vector([1, 1, -1])
        camera.position_vector += strafe_vector

    if keys[pygame.K_q]:
        camera.position_vector += Vector([0, 0, -speed])

    if keys[pygame.K_e]:
        camera.position_vector += Vector([0, 0, speed])


    # mouse events
    mouse_delta = Vector(list(pygame.mouse.get_rel()))
    mouse_sensitivity = 0.002
    camera.rotation_angles += Vector([-mouse_delta[1], 0, -mouse_delta[0]]) * mouse_sensitivity


    win.fill("black")
   
    end_time = pygame.time.get_ticks()  # get the end time of the frame
    delta_time = end_time - start_time

    fps_text = font.render("FPS: {:.2f}".format(clock.get_fps()), True, (255, 255, 255) if clock.get_fps() > FPS else (255, 0, 0))
    win.blit(fps_text, (10, 10)) 

    single_frame_delay_time_text = font.render("Δt: {:.0f} ms".format(delta_time), True, (255, 255, 255))
    win.blit(single_frame_delay_time_text, (10, 30)) 


    nig.rotation_vector += Vector([0, 0.005, 0])


    scene.render()

    pygame.display.flip()
    t += 0.001
