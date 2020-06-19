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
