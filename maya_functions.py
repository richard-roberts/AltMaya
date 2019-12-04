import maya

class Functions:
    
    @classmethod
    def duplicate(cls, obj, name=""):
        ret = maya.cmds.duplicate(obj)
        copied = ret[0]
        maya.cmds.setAttr(copied + ".tx", 0)
        maya.cmds.setAttr(copied + ".ty", 0)
        maya.cmds.setAttr(copied + ".tz", 0)
        if name != "":
            maya.cmds.rename(copied, name)
            return name
        else:
            return copied
