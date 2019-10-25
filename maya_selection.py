import maya


class Selection:
    
    @classmethod
    def get(cls):
        return maya.cmds.ls(selection=True)
    
    @classmethod
    def set(cls, *objs):
        maya.cmds.select(*objs, replace=True)
        
    @classmethod
    def add(cls, *objs):
        maya.cmds.select(*objs, add=True)
        
    @classmethod
    def is_empty(cls):
        return len(cls.get()) == 0
        
    @classmethod
    def clear(cls):
        cls.set([])
        
    @classmethod
    def first(cls):
        if cls.is_empty():
            return None
        else:
            return cls.get()[0]
