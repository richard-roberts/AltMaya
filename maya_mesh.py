import maya

import numpy


class Vertex:
    
    def __str__(self):
        x, y, z = self.get_xyz()
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, x, y, z)
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        self.m_point = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(self.index, self.m_point, maya.OpenMaya.MSpace.kWorld)
        self.array = numpy.array(self.get_xyz())
        
    def get_xyz(self):
        return self.m_point.x, self.m_point.y, self.m_point.z
        
    def set_xyz(self, x, y, z):
        m_point = maya.OpenMaya.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, m_point, maya.OpenMaya.MSpace.kWorld)
        

class Face:
    
    def __str__(self):
        return "Face[%s]" % str(self.get_vertex_indices())[1:-1]
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        
        i, j, k = self.get_vertex_indices()
        m_v1 = maya.OpenMaya.MPoint()
        m_v2 = maya.OpenMaya.MPoint()
        m_v3 = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(i, m_v1, maya.OpenMaya.MSpace.kWorld)
        self.m_mesh.getPoint(j, m_v2, maya.OpenMaya.MSpace.kWorld)
        self.m_mesh.getPoint(k, m_v3, maya.OpenMaya.MSpace.kWorld)
        self.v1 = numpy.matrix([m_v1.x, m_v1.y, m_v1.z])
        self.v2 = numpy.matrix([m_v2.x, m_v2.y, m_v2.z])
        self.v3 = numpy.matrix([m_v3.x, m_v3.y, m_v3.z])
    
    def get_vertex_indices(self):
        m_inds = maya.OpenMaya.MIntArray()
        self.m_mesh.getPolygonVertices(self.index, m_inds)
        return list(m_inds)
        
    def get_edge_matrix(self):
        return numpy.hstack([self.v2.T-self.v1.T, self.v3.T-self.v1.T])
        
    def get_simplex(self):
        cp = numpy.cross(self.v2 - self.v1, self.v3 - self.v1)
        v4 = v1 + cp / numpy.linalg.norm(cp)
        return numpy.hstack([self.v2.T-self.v1.T, self.v3.T-self.v1.T, v4.T-self.v1.T])


class Mesh:
    
    def __init__(self, name):
        self.m_mesh = maya.OpenMaya.MFnMesh(ObjectIndex.get_path_from_name(name))
        self.vertices = [Vertex(self.m_mesh, i) for i in range(self.m_mesh.numVertices())]
        self.faces = [Face(self.m_mesh, i) for i in range(self.m_mesh.numPolygons())]
        
        