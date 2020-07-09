import maya


class Selection:
    
    @classmethod
    def get(cls):
        return maya.cmds.ls(orderedSelection=True, flatten=True)
    
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
            raise ValueError("selection is empty")
        else:
            return cls.get()[0]
            
    @classmethod
    def second(cls):
        if cls.is_empty():
            raise ValueError("selection is empty")
        else:
            sel = cls.get()
            if len(sel) < 2:
                raise ValueError("selection has less than two elements")
            else:
                return sel[1]
                
    @classmethod
    def third(cls):
        if cls.is_empty():
            raise ValueError("selection is empty")
        else:
            sel = cls.get()
            if len(sel) < 3:
                raise ValueError("selection has less than three elements")
            else:
                return sel[2]
