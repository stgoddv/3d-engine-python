from typing import List, Tuple
from dataclasses import dataclass

import math
import tkinter
import re

# Canvas global variables
HEIGHT = 240 * 2
WIDTH = 256 * 2

# Canvas intialization
top = tkinter.Tk()
top.title('Ejemplo de aplicación 3d')
C = tkinter.Canvas(top, bg="black", height=HEIGHT, width=WIDTH)

# Some preliminary classes and data structures
@dataclass
class vec3d:
    x: float
    y: float
    z: float

@dataclass
class color:
    r: int
    g: int
    b: int

@dataclass
class triangle:
    def __init__(self, p: Tuple[vec3d, vec3d, vec3d], c: color = color(255, 255, 255)):
        self.c = c
        self.p = p

    def get_hexcolor(self):
        _rgb = (self.c.r, self.c.g, self.c.b)
        hex_color = '#%02x%02x%02x' % _rgb
        return hex_color

@dataclass
class mesh:
    tris: List[triangle]

@dataclass
class matrix:
    matrix: List[List[float]]

# Linear algebra basic operations
def DotProduct(v1: vec3d, v2: vec3d) -> float:
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

def MultiplyMatrix(v: vec3d, m: matrix) -> vec3d:
    x = v.x * m.matrix[0][0] + v.y * m.matrix[1][0] + \
        v.z * m.matrix[2][0] + m.matrix[3][0]

    y = v.x * m.matrix[0][1] + v.y * m.matrix[1][1] + \
        v.z * m.matrix[2][1] + m.matrix[3][1]

    z = v.x * m.matrix[0][2] + v.y * m.matrix[1][2] + \
        v.z * m.matrix[2][2] + m.matrix[3][2]

    w = v.x * m.matrix[0][3] + v.y * m.matrix[1][3] + \
        v.z * m.matrix[2][3] + m.matrix[3][3]

    if w != 0:
        x /= (w * 1.)
        y /= (w * 1.)
        z /= (w * 1.)

    return vec3d(x, y, z)

# Load models
filename = 'cat.obj'

# Load vertex from model
def load_from_obj_file(filename, tag='v'):
    vertex_pool = []
    with open(filename) as f:
        line = f.readline()
        count = 0
        while line:
            line = f.readline()
            p = re.compile(f'{tag} ([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+)')
            res = p.search(line)
            if res:
                vertex_pool.append((count, (res[1], res[2], res[3])))
                count += 1
    return vertex_pool

# load triangles from model
def load_from_obj_file_f(filename, tag='f'):
    vertex_pool = []
    with open(filename) as f:
        line = f.readline()
        count = 0
        while line:
            line = f.readline()
            p = re.compile(
                f'{tag} ([-+]?[0-9]*\.?[0-9]+)/[0-9]* ([-+]?[0-9]*\.?[0-9]+)/[0-9]* ([-+]?[0-9]*\.?[0-9]+)/[0-9]*')
            res = p.search(line)
            if res:
                vertex_pool.append((count, (res[1], res[2], res[3])))
                count += 1
    return vertex_pool

# Explanation:
# vertex_pool stores a pool of rows of 3d points ordered by an index.
# f_pool stores rows of 3 indices: one index (of vertex_pool) for each point of a triangle.
vertex_pool = load_from_obj_file(filename, 'v')
f_pool = load_from_obj_file_f(filename, 'f')

# Generate the pool of triangles of the model
def generate_mesh(vertex_pool, f_pool, scale=1.0):
    _mesh = []
    for f in f_pool:
        indices = f[1]
        p = []
        for i in range(3):
            p_x = float(vertex_pool[int(indices[i]) - 1][1][0]) * scale
            p_y = float(vertex_pool[int(indices[i]) - 1][1][1]) * scale
            p_z = float(vertex_pool[int(indices[i]) - 1][1][2]) * scale
            p.append(vec3d(p_x,p_y,p_z))
        _tri = triangle(p=p)
        _mesh.append(_tri)
    return mesh(_mesh)

meshCube = generate_mesh(vertex_pool, f_pool, scale=1)

# Projection Matrix
fNear = 0.1
fFar = 1000.
fFov = 90
fAspectRatio = HEIGHT / WIDTH
fFovRad = 1 / math.tan(fFov * 0.5 / 180. * 3.14159)

# Ray theory transformations for field of vision and perspective
matProj = matrix([
    [fAspectRatio * fFovRad, 0, 0, 0],
    [0, fFovRad, 0, 0],
    [0, 0, fFar / (fFar - fNear), 1],
    [0, 0, (-fFar * fNear) / (fFar - fNear), 0]
])

def draw_triangle(x1, y1, x2, y2, x3, y3, *options):
    drawed_triangle = C.create_polygon(x1, y1, x2, y2, x3, y3, *options)
    return drawed_triangle

matRotZ = matrix([
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
])

matRotX = matrix([
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
])

# Initialize variables
fTheta = 0
fElapsedTime = 0.01

# Initialize camera
vCamera = vec3d(0, 0, 0)

def timeChanged():
    C.delete("all")
    global fTheta
    fTheta += 1 * fElapsedTime

    # Rotation Z
    matRotZ.matrix[0][0] = math.cos(fTheta)
    matRotZ.matrix[0][1] = math.sin(fTheta)
    matRotZ.matrix[1][0] = -math.sin(fTheta)
    matRotZ.matrix[1][1] = math.cos(fTheta)
    matRotZ.matrix[2][2] = 1
    matRotZ.matrix[3][3] = 1

    # Rotation X
    matRotX.matrix[0][0] = 1
    matRotX.matrix[1][1] = math.cos(fTheta * 0.5)
    matRotX.matrix[1][2] = math.sin(fTheta * 0.5)
    matRotX.matrix[2][1] = -math.sin(fTheta * 0.5)
    matRotX.matrix[2][2] = math.cos(fTheta * 0.5)
    matRotX.matrix[3][3] = 1

    # Draw Triangles
    for tri in meshCube.tris:
        # Rotate in Z axis
        v_1 = MultiplyMatrix(tri.p[0], matRotZ)
        v_2 = MultiplyMatrix(tri.p[1], matRotZ)
        v_3 = MultiplyMatrix(tri.p[2], matRotZ)
        triRotatedZ = triangle((v_1, v_2, v_3))
        # Rotate in X axis
        v_1 = MultiplyMatrix(triRotatedZ.p[0], matRotX)
        v_2 = MultiplyMatrix(triRotatedZ.p[1], matRotX)
        v_3 = MultiplyMatrix(triRotatedZ.p[2], matRotX)
        triRotatedX = triangle((v_1, v_2, v_3))
        # Offset into screen
        triTranslated = triRotatedX
        triTranslated.p[0].z = triRotatedX.p[0].z + 600.
        triTranslated.p[1].z = triRotatedX.p[1].z + 600.
        triTranslated.p[2].z = triRotatedX.p[2].z + 600.
        # Normal derivation
        l_x = triTranslated.p[1].x - triTranslated.p[0].x
        l_y = triTranslated.p[1].y - triTranslated.p[0].y
        l_z = triTranslated.p[1].z - triTranslated.p[0].z
        line_1 = vec3d(l_x, l_y, l_z)
        l_x = triTranslated.p[2].x - triTranslated.p[0].x
        l_y = triTranslated.p[2].y - triTranslated.p[0].y
        l_z = triTranslated.p[2].z - triTranslated.p[0].z
        line_2 = vec3d(l_x, l_y, l_z)
        normal_x = line_1.y * line_2.z - line_1.z * line_2.y
        normal_y = line_1.z * line_2.x - line_1.x * line_2.z
        normal_z = line_1.x * line_2.y - line_1.y * line_2.x
        normal = vec3d(normal_x, normal_y, normal_z)
        l = math.sqrt(normal_x * normal_x + normal_y * normal_y + normal_z * normal_z)
        normal.x /= l
        normal.y /= l
        normal.z /= l
        # Camera definition
        cameraDiff = vec3d(triTranslated.p[0].x - vCamera.x, triTranslated.p[0].y - vCamera.y,
                           triTranslated.p[0].z - vCamera.z)
        dot = DotProduct(normal, cameraDiff)
        # Draw if visible
        if (dot < 0):
            # Illumination #
            light = vec3d(0, 0, -1)
            l = math.sqrt(light.x * light.x + light.y * light.y + light.z * light.z)
            light.x /= l
            light.y /= l
            light.z /= l
            dp = abs(DotProduct(normal, light))
            base_color = color(int(0 * dp), int(128 * dp), int(50 * dp))
            # Project from 3d -> 2d
            v_1 = MultiplyMatrix(triTranslated.p[0], matProj)
            v_2 = MultiplyMatrix(triTranslated.p[1], matProj)
            v_3 = MultiplyMatrix(triTranslated.p[2], matProj)
            triProjected = triangle(p=(v_1, v_2, v_3), c=base_color)
            # Scale into view
            triProjected.p[0].x += 1
            triProjected.p[0].y += 1
            triProjected.p[1].x += 1
            triProjected.p[1].y += 1
            triProjected.p[2].x += 1
            triProjected.p[2].y += 1
            triProjected.p[0].x *= 0.5 * WIDTH
            triProjected.p[0].y *= 0.5 * HEIGHT
            triProjected.p[1].x *= 0.5 * WIDTH
            triProjected.p[1].y *= 0.5 * HEIGHT
            triProjected.p[2].x *= 0.5 * WIDTH
            triProjected.p[2].y *= 0.5 * HEIGHT
            # Draw
            coords = (triProjected.p[0].x, triProjected.p[0].y, triProjected.p[1].x,
                      triProjected.p[1].y, triProjected.p[2].x, triProjected.p[2].y)
            draw_triangle(*coords, {'fill': triProjected.get_hexcolor(), 'outline': ''})

    C.pack()
    top.after(10, timeChanged)

timeChanged()
top.mainloop()
