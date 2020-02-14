import maya

class API:

    @classmethod
    def get_mobject(cls, name):
        dag_path = maya.OpenMaya.MDagPath()
        selection = maya.OpenMaya.MSelectionList()
        selection.add(name)
        selection.getDagPath(0, dag_path)
        return dag_path.node()
