import maya

import numpy


class Vertex:
    
    def __str__(self):
        x, y, z = self.get_xyz()
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, x, y, z)
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        p = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(self.index, p, maya.OpenMaya.MSpace.kWorld)
        self.array = numpy.array([p.x, p.y, p.z])
        
    def set_xyz(self, x, y, z):
        m = maya.OpenMaya.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, m, maya.OpenMaya.MSpace.kWorld)
        self.array = numpy.array([x, y, z])
        

class Face:
    
    def __str__(self):
        return "Face[%s]" % str(self.get_vertex_indices())[1:-1]
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        
        m_inds = maya.OpenMaya.MIntArray()
        self.m_mesh.getPolygonVertices(self.index, m_inds)
        self.vertex_indices = list(m_inds)
        self.vertex_index_set = set(self.vertex_indices)
        
        if not len(self.vertex_indices) == 3:
            raise ValueError("Only know how to deal with triangle faces for now!")
      
        self.update()
        
    def update(self):  
        i, j, k = self.vertex_indices
        m_v1 = maya.OpenMaya.MPoint()
        m_v2 = maya.OpenMaya.MPoint()
        m_v3 = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(i, m_v1, maya.OpenMaya.MSpace.kWorld)
        self.m_mesh.getPoint(j, m_v2, maya.OpenMaya.MSpace.kWorld)
        self.m_mesh.getPoint(k, m_v3, maya.OpenMaya.MSpace.kWorld)
        self.v1a = numpy.array([m_v1.x, m_v1.y, m_v1.z])
        self.v2a = numpy.array([m_v2.x, m_v2.y, m_v2.z])
        self.v3a = numpy.array([m_v3.x, m_v3.y, m_v3.z])
        self.v1m = numpy.matrix(self.v1a)
        self.v2m = numpy.matrix(self.v2a)
        self.v3m = numpy.matrix(self.v3a)
        self.centroid = (self.v1a + self.v2a + self.v3a) / 3
        self.edge_matrix = numpy.hstack([self.v2m.T-self.v1m.T, self.v3m.T-self.v1m.T])
        cp = numpy.cross(self.v2m - self.v1m, self.v3m - self.v1m)
        v4 = self.v1m + cp / numpy.linalg.norm(cp)
        self.simplex = numpy.hstack([self.v2m.T-self.v1m.T, self.v3m.T-self.v1m.T, v4.T-self.v1m.T])
    
    def get_nearest_valid_point(self, queried_point):
        print("MISSING ANGLE CHECK IN Face.get_nearest_valid_point")
        # https://stackoverflow.com/questions/32252735/c-find-the-closest-point-on-a-mesh-to-a-query-point
        edge_1 = self.v2a - self.v1a
        edge_2 = self.v3a - self.v1a
        v_0 = self.v1a - queried_point

        a = numpy.dot(edge_1, edge_1)
        b = numpy.dot(edge_1, edge_2)
        c = numpy.dot(edge_2, edge_2)
        d = numpy.dot(edge_1, v_0)
        e = numpy.dot(edge_2, v_0)

        det = a * c - b * b
        s = b * e - c * d
        t = b * d - a * e

        if s + t < det:
            if s < 0.0:
                if t < 0.0:
                    if d < 0.0:
                        s = numpy.clip(-d/a, 0.0, 1.0)
                        t = 0.0
                    else:
                        s = 0.0
                        t = numpy.clip(-e/c, 0.0, 1.0)          
                else:
                    s = 0.0
                    t = numpy.clip(-e/c, 0.0, 1.0) 
            elif t < 0.0:
                s = numpy.clip(-d/a, 0.0, 1.0)
                t = 0.0
            else:
                invDet = 1.0 / det
                s *= invDet
                t *= invDet
        else:
            if s < 0.0:
                tmp0 = b+d
                tmp1 = c+e
                if tmp1 > tmp0:
                    numer = tmp1 - tmp0
                    denom = a-2*b+c
                    s = numpy.clip(numer/denom, 0.0, 1.0)
                    t = 1-s
                else:
                    t = numpy.clip(-e/c, 0.0, 1.0)
                    s = 0.0
            elif t < 0.0:
                if a+d > b+e:
                    numer = c+e-b-d
                    denom = a-2*b+c
                    s = numpy.clip(numer/denom, 0.0, 1.0)
                    t = 1-s
                else:
                    s = numpy.clip(-e/c, 0.0, 1.0)
                    t = 0.0
            else:
                numer = c+e-b-d
                denom = a-2*b+c
                s = numpy.clip(numer/denom, 0.0, 1.0)
                t = 1.0 - s

        nearest = self.v1a + s * edge_1 + t * edge_2
        return nearest
        

class Mesh:
    
    def __init__(self, name):
        self.m_mesh = maya.OpenMaya.MFnMesh(ObjectIndex.get_path_from_name(name))
        self.vertices = [Vertex(self.m_mesh, i) for i in range(self.m_mesh.numVertices())]
        self.faces = [Face(self.m_mesh, i) for i in range(self.m_mesh.numPolygons())]
        
        self.adjacent_faces = {}
        for f in self.faces:
            self.adjacent_faces[f] = []    
        for i in range(len(self.faces) - 1):
            for j in range(i + 1, len(self.faces)):
                f_a = self.faces[i]
                f_b = self.faces[j]
                if len(f_a.vertex_index_set & f_b.vertex_index_set) == 2:
                    self.adjacent_faces[f_a].append(f_b)
                    self.adjacent_faces[f_b].append(f_a)
                        
    def get_nearest_valid_point(self, point):
        print("WARNING - Mesh.get_nearest_valid_point() SLOW")
        nearest_point = None
        nearest_distance = float('inf')
        for f in self.faces:
            nearest = f.get_nearest_valid_point(point)
            distance = numpy.linalg.norm(nearest - point)
            if distance < nearest_distance:
                nearest_point = nearest
                nearest_distance = distance
        return nearest_point
    
    def update(self):
        for f in self.faces:
            f.update()
            