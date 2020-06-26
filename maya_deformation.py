import numpy as np

import maya.cmds as cmds
import maya.api.OpenMaya as om

import AltMaya as altmaya


class VisualizeDeformation:
    
    def __init__(self, mesh):
        self.mesh = mesh
        self.update()

    def update(self):
        self.map_x = {}
        self.map_y = {}
        self.map_z = {}
        for v in self.mesh.vertices:
            d = v.read_delta()
            self.map_x[v.index] = d[0]
            self.map_y[v.index] = d[1]
            self.map_z[v.index] = d[2]
        self.vec_x = np.array(self.map_x.values())
        self.vec_y = np.array(self.map_y.values())
        self.vec_z = np.array(self.map_z.values())

    def value_range(self):
        min_v = min([min(self.vec_x), min(self.vec_y), min(self.vec_z)])
        max_v = max([max(self.vec_x), max(self.vec_y), max(self.vec_z)])
        return min_v, max_v
    
    def color_mesh_based_on_deformation(self, mesh_name, scaling):
        self.update()
        
        inds = []
        colors = []
        for i in range(len(self.mesh.vertices)):
            r = ((self.map_x[i] / scaling) + scaling) * 0.5
            g = ((self.map_y[i] / scaling) + scaling) * 0.5
            b = ((self.map_z[i] / scaling) + scaling) * 0.5
            c = om.MColor([r,g,b])
            colors.append(c)
            inds.append(i)

        cmds.polyColorPerVertex(mesh_name, colorDisplayOption=True)
        fs = altmaya.API.get_function_set_from_name(mesh_name)
        fs.setVertexColors(colors, inds)
    
    def value_range_to_other(self, mesh_name):
        o = altmaya.Mesh(mesh_name)
        
        map_x = {}
        map_y = {}
        map_z = {}
        for i in range(len(o.vertices)):
            ov = o.vertices[i]
            mv = self.mesh.vertices[i]
            map_x[ov.index] = ov.p[0] - mv.p[0] 
            map_y[ov.index] = ov.p[1] - mv.p[1]
            map_z[ov.index] = ov.p[2] - mv.p[2]
        vec_x = np.array(map_x.values())
        vec_y = np.array(map_y.values())
        vec_z = np.array(map_z.values())
        
        min_v = min([min(vec_x), min(vec_y), min(vec_z)])
        max_v = max([max(vec_x), max(vec_y), max(vec_z)])
        return min_v, max_v
        
    def apply_to_other(self, mesh_name, scaling):
        o = altmaya.Mesh(mesh_name)
        
        map_x = {}
        map_y = {}
        map_z = {}
        for i in range(len(o.vertices)):
            ov = o.vertices[i]
            mv = self.mesh.vertices[i]
            map_x[ov.index] = ov.p[0] - mv.p[0] 
            map_y[ov.index] = ov.p[1] - mv.p[1]
            map_z[ov.index] = ov.p[2] - mv.p[2]
        vec_x = np.array(map_x.values())
        vec_y = np.array(map_y.values())
        vec_z = np.array(map_z.values())
        
        min_v = min([min(vec_x), min(vec_y), min(vec_z)])
        max_v = max([max(vec_x), max(vec_y), max(vec_z)])
        normed = max([abs(min_v), abs(max_v)])
        inds = []
        colors = []
        for i in range(len(o.vertices)):
            r = ((map_x[i] / normed) / 2 + 0.5)
            g = ((map_y[i] / normed) / 2 + 0.5)
            b = ((map_z[i] / normed) / 2 + 0.5)
            c = om.MColor([r,g,b])
            colors.append(c)
            inds.append(i)

        cmds.polyColorPerVertex(mesh_name, colorDisplayOption=True)
        fs = altmaya.API.get_function_set_from_name(mesh_name)
        fs.setVertexColors(colors, inds)
