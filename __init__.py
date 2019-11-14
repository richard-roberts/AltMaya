from .maya_animation import *
from .maya_attr_index import *
from .maya_gui import *
from .maya_history import *
from .maya_reporting import *
from .maya_selection import *
from .maya_timeline import *
from .maya_mesh import *







import maya

class ObjectIndex:
    
    @classmethod
    def get_path_from_name(cls, name):
        sel = maya.OpenMaya.MSelectionList()
        path = maya.OpenMaya.MDagPath()
        sel.add(name)
        sel.getDagPath(0, path)
        return path


import maya

class Vertex:
    
    def __str__(self):
        x, y, z = self.xyz()
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, x, y, z)
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
        self.m_point = maya.OpenMaya.MPoint()
        self.m_mesh.getPoint(self.index, self.m_point)
        
    def xyz(self):
        return self.m_point.x, self.m_point.y, self.m_point.z
        

class Face:
    
    def __init__(self, m_mesh, index):
        self.m_mesh = m_mesh
        self.index = index
    
    def get_vertex_indices(self):
        m_inds = maya.OpenMaya.MIntArray()
        self.m_mesh.getPolygonVertices(self.index, m_inds)
        return list(m_inds)
        
class Mesh:
    
    def __init__(self, name):
        self.m_mesh = maya.OpenMaya.MFnMesh(ObjectIndex.get_path_from_name(name))
        self.vertices = [Vertex(self.m_mesh, i) for i in range(self.m_mesh.numVertices())]
        self.faces = [Face(self.m_mesh, i) for i in range(self.m_mesh.numPolygons())]
        
        
        
m = Mesh("pSphere1")
for v in m.vertices:
    print(v)