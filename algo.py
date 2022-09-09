from utils import Vertex, BowyerWatson, VisualizeTriangulation

size       = 1024
n_vertices = 128

vertices      = Vertex.samples(size, size, num=n_vertices)
triangulation = BowyerWatson(vertices)

VisualizeTriangulation(vertices, triangulation)