import maya

import numpy


class Vertex:
    
    query_space = maya.OpenMaya.MSpace.kWorld
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        self.p = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(self.index, self.p, self.query_space)
    
    def as_array(self):
        return numpy.array([
            [self.p.x],
            [self.p.y], 
            [self.p.z]
        ])
        
    def set_by_xyz(self, x, y, z):
        m = maya.OpenMaya.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, m, maya.OpenMaya.MSpace.kWorld)
        
    def set_by_array(self, array):
        x = array[0]
        y = array[1]
        z = array[2]
        self.m_mesh.setPoint(self.index, maya.OpenMaya.MPoint(x, y, z), maya.OpenMaya.MSpace.kWorld)
        
    def __str__(self):
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, self.p.x, self.p.y, self.p.z)


class Triangle:
    
    def __init__(self, m_mesh, v1, v2, v3):
        self.m_mesh = m_mesh
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.update()
        
    def update(self):
        v1 = self.v1.as_array()
        v2 = self.v2.as_array()
        v3 = self.v3.as_array()
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        self.centroid = (v1 + v2 + v3) / 3
        self.edge_matrix = numpy.hstack([v2v1, v3v1])
        cp = numpy.cross(v2v1.T, v3v1.T)
        v4 = cp / numpy.linalg.norm(cp)
        self.simplex = numpy.hstack([v2v1, v3v1, v4.T])

class Mesh:
    
    @classmethod
    def compile_face_adjaceny_map(cls, name):
        
        face_to_edge = {}
        for f2e in maya.cmds.polyInfo(name, faceToEdge=True):
            f, es = f2e.split(":")
            face = int(f.split("FACE")[1].strip())
            edges = [int(v.strip()) for v in es.split(" ") if v.strip() != ""]
            face_to_edge[face] = edges
            
        edge_to_face = {}
        for e2f in maya.cmds.polyInfo(name, edgeToFace=True):
            e, fs = e2f.split(":")
            edge = int(e.split("EDGE")[1].strip())
            faces = [int(v.strip()) for v in fs.split(" ") if v.strip() != ""]
            edge_to_face[edge] = faces 
            
        adjaceny = {}
        for f in face_to_edge.keys():
            adj = []
            for e in face_to_edge[f]:
                adj += [v for v in edge_to_face[e] if v != f]
            adjaceny[f] = adj
        
        return adjaceny
    
    def __init__(self, name):
        self.name = name
        self.m_mesh = maya.OpenMaya.MFnMesh(ObjectIndex.get_path_from_name(name))
        
        s = time.time()
        self.adjaceny = self.compile_face_adjaceny_map(name)
        e = time.time()
        print("Adj map init took %2.2fs" % (e-s))
        
        s = time.time()
        self.vertices = [
            Vertex(self.m_mesh, i)
            for i in range(self.m_mesh.numVertices())
        ]
        e = time.time()
        print("Verts init took %2.2fs" % (e-s))
        
        s = time.time()
        inds = maya.OpenMaya.MIntArray()
        self.triangles = []
        for i in range(self.m_mesh.numPolygons()):
            self.m_mesh.getPolygonVertices(i, inds)
            if len(inds) != 3:
                raise ValueError("Can only process triangle meshes for now, sorry")
            t = Triangle(
                self.m_mesh,
                self.vertices[inds[0]],
                self.vertices[inds[1]],
                self.vertices[inds[2]]
            )    
            self.triangles.append(t)
        e = time.time()
        print("Triangles init took %2.2fs" % (e-s))
        
    def get_nearest_valid_point_fast(self, x, y, z):
        # maya.cmds.warning("Not using normal check for valid point (only distance)")
        query = maya.OpenMaya.MPoint(x, y, z)
        nearest = maya.OpenMaya.MPoint()
        self.m_mesh.getClosestPoint(query, nearest, maya.OpenMaya.MSpace.kWorld)
        return nearest.x, nearest.y, nearest.z
    
    def update(self):
        s = time.time()
        for t in self.triangles: t.update()
        e = time.time()
        print("Triangles update took %2.2fs" % (e-s))
