import time

import numpy

import maya.cmds as cmds
import maya.api.OpenMaya as om

import AltMaya as altmaya


query_space = om.MSpace.kObject


class Vertex:
    
    
    def __init__(self, parent, m_mesh, index, existing=None):
        self.parent = parent
        self.m_mesh = m_mesh
        self.index = index
        
        if existing is None:
            self.setup_from_maya()
        else:
            self.setup_from_existing(existing)
           
        self.starting_p = om.MPoint(self.p)
        self.delta_p = self.read_delta()
        
    def update(self):
        self.p = self.m_mesh.getPoint(self.index, query_space)
        self.delta_p = self.read_delta()
        
    def setup_from_maya(self):
        self.p = self.m_mesh.getPoint(self.index, query_space)
        
    def setup_from_existing(self, existing):
        self.p = om.MPoint(existing.p)
        
    def as_array(self):
        return numpy.array([
            [self.p[0]],
            [self.p[1]], 
            [self.p[2]]
        ])
        
    def reset(self):
        self.m_mesh.setPoint(self.index, self.starting_p, query_space)
        
    def set_by_xyz(self, x, y, z):
        self.p = om.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, self.p, query_space)
        
    def set_by_array(self, array):
        x = array[0]
        y = array[1]
        z = array[2]
        self.set_by_xyz(x, y, z)
        
    def set_by_xyz_delta(self, x, y, z):
        self.set_by_xyz(
            x + self.starting_p[0],
            y + self.starting_p[1],
            z + self.starting_p[2]
        )
        
    def read_delta(self):
        return om.MPoint(
            self.starting_p[0] - self.p[0],
            self.starting_p[1] - self.p[1], 
            self.starting_p[2] - self.p[2])
        
    def __str__(self):
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, self.p[0], self.p[1], self.p[2])


class Triangle:
    
    def __init__(self, parent, m_mesh, v1, v2, v3, existing=None):
        self.parent = parent
        self.m_mesh = m_mesh
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        
        if existing is None:
            self.setup_from_maya()
        else:
            self.setup_from_existing(existing)
        
    def setup_from_existing(self, existing):
        self.original_centroid = existing.centroid
        self.original_edge_matrix = existing.edge_matrix
        self.original_r1qt = existing.r1qt
        self.original_simplex = existing.simplex

        self.centroid = self.original_centroid
        self.edge_matrix = self.original_edge_matrix
        self.r1qt = self.original_r1qt
        self.simplex = self.original_simplex
        
    def setup_from_maya(self):
        v1 = self.v1.as_array()
        v2 = self.v2.as_array()
        v3 = self.v3.as_array()
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        self.original_centroid = (v1 + v2 + v3) / 3
        self.original_edge_matrix = numpy.matrix(numpy.hstack([v2v1, v3v1]))
        q, r = numpy.linalg.qr(self.original_edge_matrix)
        self.original_r1qt = r.I * q.T    
        cp = numpy.cross(v2v1.T, v3v1.T)
        v4 = cp / numpy.linalg.norm(cp)
        # TODO - test getting maya normal here?!"
        self.original_simplex = numpy.matrix(numpy.hstack([v2v1, v3v1, v4.T]))

        self.centroid = self.original_centroid
        self.edge_matrix = self.original_edge_matrix
        self.r1qt = self.original_r1qt
        self.simplex = self.original_simplex
        
    def update(self, update_vertices=False):
        if update_vertices:
            self.v1.update()
            self.v2.update()
            self.v3.update()
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
        # TODO - test getting maya normal here?!"
        self.simplex = numpy.matrix(numpy.hstack([v2v1, v3v1, v4.T]))
        
    def as_key(self):
        index = self.parent.triangles.index(self)
        return "%s.f[%d]" % (self.parent.name, index)
        
    def select(self):
        altmaya.Selection.set([self.as_key()])


class Mesh:
    
    @classmethod
    def compile_face_adjaceny_map(cls, name):
        
        face_to_edge = {}
        for f2e in cmds.polyInfo(name, faceToEdge=True):
            f, es = f2e.split(":")
            face = int(f.split("FACE")[1].strip())
            edges = [int(v.strip()) for v in es.split(" ") if v.strip() != ""]
            face_to_edge[face] = edges
            
        edge_to_face = {}
        for e2f in cmds.polyInfo(name, edgeToFace=True):
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
        self.name = altmaya.Functions.duplicate(existing.name)
        self.m_mesh = altmaya.API.get_mesh_function_set_from_name(self.name)
        self.triangle_adjaceny_map = existing.triangle_adjaceny_map
        
        if verbose: s = time.time()
        self.vertices = [
            Vertex(self, self.m_mesh, i, existing=existing.vertices[i])
            for i in range(self.m_mesh.numVertices)
        ]
        if verbose: e = time.time()
        if verbose: print("Verts init took %2.2fs" % (e-s))
        
        if verbose: s = time.time()
        inds = om.MIntArray()
        self.triangles = []
        for i in range(self.m_mesh.numPolygons):
            inds = self.m_mesh.getPolygonVertices(i)
            if len(inds) != 3:
                raise ValueError("Can only process triangle meshes for now, sorry")
            t = Triangle(
                self,
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
        self.m_mesh = altmaya.API.get_mesh_function_set_from_name(self.name)
        
        if verbose: s = time.time()
        self.vertices = [
            Vertex(self, self.m_mesh, i)
            for i in range(self.m_mesh.numVertices)
        ]
        if verbose: e = time.time()
        if verbose: print("Verts init took %2.2fs" % (e-s))
        
        if verbose: s = time.time()
        self.triangles = []
        for i in range(self.m_mesh.numPolygons):
            inds = self.m_mesh.getPolygonVertices(i)
            if len(inds) != 3:
                raise ValueError("Can only process triangle meshes for now, sorry (face %d has %d verts)" % (i, len(inds)))
            t = Triangle(
                self,
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
        # cmds.warning("Not using normal check for valid point (only distance)")
        query = om.MPoint(x, y, z)
        n, ix = self.m_mesh.getClosestPoint(query, query_space)
        return n, ix
        
    def reset(self, verbose=False):
        if verbose: s = time.time()
        for v in self.vertices: v.reset()
        if verbose: e = time.time()
        if verbose: print("Triangles update took %2.2fs" % (e-s))
        
    def update(self, triangles=True, verts=True, verbose=False):
        if verbose: s = time.time()
        if verts:
            for v in self.vertices: v.update()
        if triangles:
            for t in self.triangles: t.update()
        if verbose: e = time.time()
        if verbose: print("Triangles update took %2.2fs" % (e-s))


class VertexList:

    def __init__(self, name):
        self.name = name
        self.m_mesh = om.MFnMesh(altmaya.API.get_dag_path_from_name(name))
        self.vertices = [
            Vertex(self, self.m_mesh, i)
            for i in range(self.m_mesh.numVertices)
        ]

    def set_positions(self, xyzs):
        for i in range(len(xyzs)):
            x = xyzs[i][0]
            y = xyzs[i][1]
            z = xyzs[i][2]
            self.vertices[i].set_by_xyz(x, y, z)
