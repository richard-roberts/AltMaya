import time

import maya
import numpy

import AltMaya as alt_maya

class Vertex:
    
    query_space = maya.OpenMaya.MSpace.kWorld
    
    def __init__(self, m_mesh, index, existing=None):
        self.m_mesh = m_mesh
        self.index = index
        
        if existing is None:
            self.setup_from_maya()
        else:
            self.setup_from_existing(existing)
            
        self.starting_p = maya.OpenMaya.MPoint(self.p.x, self.p.y, self.p.z)
        self.delta_p = self.read_delta()
        
    def setup_from_maya(self):
        self.p = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(self.index, self.p, self.query_space)
        
    def setup_from_existing(self, existing):
        self.p = maya.OpenMaya.MPoint(existing.p.x, existing.p.y, existing.p.z)
        
    def as_array(self):
        return numpy.array([
            [self.p.x],
            [self.p.y], 
            [self.p.z]
        ])
        
    def set_by_xyz(self, x, y, z):
        self.p.x = x
        self.p.y = y
        self.p.z = z
        # m = maya.OpenMaya.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, self.p, self.query_space)
        
    def set_by_array(self, array):
        x = array[0]
        y = array[1]
        z = array[2]
        self.set_by_xyz(x, y, z)
        
    def set_by_xyz_delta(self, x, y, z):
        self.set_by_xyz(
            x + self.starting_p.x,
            y + self.starting_p.y,
            z + self.starting_p.z
        )
        
    def read_delta(self):
        return maya.OpenMaya.MPoint(
            self.starting_p.x - self.p.x,
            self.starting_p.y - self.p.y, 
            self.starting_p.z - self.p.z)
        
    def __str__(self):
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, self.p.x, self.p.y, self.p.z)


class Triangle:
    
    def __init__(self, m_mesh, v1, v2, v3, existing=None):
        self.m_mesh = m_mesh
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        
        if existing is None:
            self.setup_from_maya()
        else:
            self.setup_from_existing(existing)
        
    def setup_from_existing(self, existing):
        self.centroid = existing.centroid
        self.edge_matrix = existing.edge_matrix
        self.simplex = existing.simplex
        self.r1qt = existing.r1qt
        
    def setup_from_maya(self):
        self.update()
        
    def update(self):
        v1 = self.v1.as_array()
        v2 = self.v2.as_array()
        v3 = self.v3.as_array()
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        self.centroid = (v1 + v2 + v3) / 3
        self.edge_matrix = numpy.matrix(numpy.hstack([v2v1, v3v1]))
        q, r = numpy.linalg.qr(self.edge_matrix)
        self.r1qt = r.I * q.T    
        cp = numpy.cross(v2v1.T, v3v1.T)
        v4 = cp / numpy.linalg.norm(cp)
        self.simplex = numpy.matrix(numpy.hstack([v2v1, v3v1, v4.T]))


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
    
    def __init__(self, name, existing=None, verbose=False):
        if existing is None:
            self.setup_from_maya(name, verbose)
        else:
            self.setup_from_existing(name, existing, verbose)
    
    def as_copy(self, verbose=False):
        return Mesh(self.name, existing=self, verbose=verbose)
        
    def setup_from_existing(self, name, existing, verbose):
        self.name = alt_maya.Functions.duplicate(existing.name)
        self.m_mesh = maya.OpenMaya.MFnMesh(alt_maya.ObjectIndex.get_path_from_name(self.name))
        self.triangle_adjaceny_map = existing.triangle_adjaceny_map
        
        if verbose: s = time.time()
        self.vertices = [
            Vertex(self.m_mesh, i, existing=existing.vertices[i])
            for i in range(self.m_mesh.numVertices())
        ]
        if verbose: e = time.time()
        if verbose: print("Verts init took %2.2fs" % (e-s))
        
        if verbose: s = time.time()
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
                self.vertices[inds[2]],
                existing=existing.triangles[i]
            )    
            self.triangles.append(t)
        if verbose: e = time.time()
        if verbose: print("Triangles init took %2.2fs" % (e-s))
        
    def setup_from_maya(self, name, verbose):        
        self.name = name
        self.m_mesh = maya.OpenMaya.MFnMesh(alt_maya.ObjectIndex.get_path_from_name(name))
        
        if verbose: s = time.time()
        self.vertices = [
            Vertex(self.m_mesh, i)
            for i in range(self.m_mesh.numVertices())
        ]
        if verbose: e = time.time()
        if verbose: print("Verts init took %2.2fs" % (e-s))
        
        if verbose: s = time.time()
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
        if verbose: e = time.time()
        if verbose: print("Triangles init took %2.2fs" % (e-s))        

        if verbose: s = time.time()
        self.triangle_adjaceny_map = self.compile_face_adjaceny_map(name)
        if verbose: e = time.time()
        if verbose: print("Adj map init took %2.2fs" % (e-s))
        
    def get_nearest_valid_point_fast(self, x, y, z):
        # maya.cmds.warning("Not using normal check for valid point (only distance)")
        query = maya.OpenMaya.MPoint(x, y, z)
        nearest = maya.OpenMaya.MPoint()
        self.m_mesh.getClosestPoint(query, nearest, maya.OpenMaya.MSpace.kWorld)
        return nearest.x, nearest.y, nearest.z
    
    def update(self, verbose=False):
        if verbose: s = time.time()
        for t in self.triangles: t.update()
        if verbose: e = time.time()
        if verbose: print("Triangles update took %2.2fs" % (e-s))
