import maya

class Functions:

    @classmethod
    def delete(cls, obj):
        maya.cmds.delete(obj)
    
    @classmethod
    def duplicate(cls, obj, name=""):
        ret = maya.cmds.duplicate(obj)
        copied = ret[0]
        if name != "":
            maya.cmds.rename(copied, name)
            return name
        else:
            return copied
