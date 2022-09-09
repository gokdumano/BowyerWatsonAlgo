from matplotlib import pyplot as plt
from collections import Counter
from operator import attrgetter
from random import randrange
import numpy as np

class Vertex:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return (self.x == other.x) and\
               (self.y == other.y)
    
    def __repr__(self):
        return f'V(X:{self.x:.03f}, Y:{self.y:.03f})'
    
    @staticmethod
    def samples(xMax, yMax, xMin=0, yMin=0, num=1):
        return [ Vertex(randrange(xMin, xMax), randrange(yMin, yMax)) for i in range(num) ]
        
class Edge:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
    
    def __eq__(self, other):
        return (self.v1 == other.v1) and (self.v2 == other.v2) or\
               (self.v1 == other.v2) and (self.v2 == other.v1)
    
    def __contains__(self, v):
        return v in (self.v1, self.v2)
    
    def __repr__(self):
        return f'E({self.v1}, {self.v2})'
    
    def __hash__(self):
        v1, v2 = sorted((self.v1, self.v2), key=attrgetter('x'))
        return hash((v1.x, v1.y, v2.x, v2.y))

class Circle:
    def __init__(self, v1, v2, v3):
        self.center, self.radius = Circle.__calcCircle(v1, v2, v3)
        
    def __contains__(self, v):
        dxx  = np.square(self.center.x - v.x)
        dyy  = np.square(self.center.y - v.y)
        dist = np.sqrt(dxx + dyy)
        return dist < self.radius
        
    def __repr__(self):
        return f'C({self.center}, R:{self.radius:.03f})'
    
    @staticmethod
    def __calcCircle(v1, v2, v3):
        A = np.array([[2*v1.x, 2*v1.y, 1],
                      [2*v2.x, 2*v2.y, 1],
                      [2*v3.x, 2*v3.y, 1]])
        
        B = np.array([[-(v1.x ** 2 + v1.y ** 2)],
                      [-(v2.x ** 2 + v2.y ** 2)],
                      [-(v3.x ** 2 + v3.y ** 2)]])
        
        a, b, c = np.ravel(np.linalg.inv(A) @ B)
        xc, yc  = -a, -b
        radius  = np.sqrt(xc ** 2 + yc ** 2 - c)
        center  = Vertex(xc, yc)
        return center, radius        

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.circumCirc = Circle(v1, v2, v3)
        self.edges = (Edge(v1, v2), Edge(v1, v3), Edge(v2, v3))
        
    def __contains__(self, v):
        return v in (self.v1, self.v2, self.v3)
        
    def __repr__(self):
        return f'T({self.v1}, {self.v2}, {self.v3})'
            
    def __hash__(self):
        v1, v2, v3 = sorted((self.v1, self.v2, self.v3), key=attrgetter('x'))
        return hash((v1.x, v1.y, v2.x, v2.y, v3.x, v3.y))
    
    def __iter__(self):
        for v in (self.v1, self.v2, self.v3):
            yield v
    
    @staticmethod
    def createSuperTriangle(*vs):
        xMin = min(*vs, key=attrgetter('x')).x
        xMax = max(*vs, key=attrgetter('x')).x
        yMin = min(*vs, key=attrgetter('y')).y
        yMax = max(*vs, key=attrgetter('y')).y
        
        dx = (xMax - xMin) * 10
        dy = (yMax - yMin) * 10
        
        v1 = Vertex(xMin - dx    , yMin - dy * 3)
        v2 = Vertex(xMin - dx    , yMax + dy    )
        v3 = Vertex(xMax + dx * 3, yMax + dy    )
        return Triangle(v1, v2, v3)
    
def BowyerWatson(vertices):
    # https://gorillasun.de/blog/bowyer-watson-algorithm-for-delaunay-triangulation
    superTriangle = Triangle.createSuperTriangle(*vertices)
    triangulation = { superTriangle }

    for vertex in vertices:    
        badTriangles  = { triangle for triangle in triangulation if vertex in triangle.circumCirc }
        edges         = Counter(edge for triangle in badTriangles for edge in triangle.edges)
        polygon       = { edge for edge, count in edges.items() if count < 2 }
        triangulation = { triangle for triangle in triangulation if triangle not in badTriangles }
        
        for edge in polygon:
            newTri    = Triangle(edge.v1, edge.v2, vertex)
            triangulation.add(newTri)
            
    triangulation = { triangle for triangle in triangulation if all(v not in superTriangle for v in triangle)}
    return triangulation

def VisualizeTriangulation(vertices, triangulation):
    for triangle in triangulation:
        xs = [ v.x for v in (triangle.v1, triangle.v2, triangle.v3, triangle.v1) ]
        ys = [ v.y for v in (triangle.v1, triangle.v2, triangle.v3, triangle.v1) ]
        plt.plot(xs, ys, color='k', linewidth=1, zorder=1)
        
    xs = [ vertex.x for vertex in vertices ]
    ys = [ vertex.y for vertex in vertices ]
    
    plt.title(f'Delaunay triangulation\nnum_vertices:{len(vertices)}')
    plt.scatter(xs, ys, s=40, fc='white', ec='black', zorder=2)
    plt.show()
    
