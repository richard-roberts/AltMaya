import maya


class AttributeIndex:
    
    def __init__(self, node_name, attribute_name):
        self.obj = node_name
        self.attr = attribute_name
        self.key = "%s.%s" % (self.obj, self.attr)
    
    @staticmethod
    def from_key(key):
        node_name, attr_name = key.split(".")
        return AttributeIndex(node_name, attr_name)
        
    def __str__(self):
        return self.key
        
    def read(self):
        return maya.cmds.getAttr(self.key)
        
    def read_at_time(self, time):
        return maya.cmds.getAttr(self.key, time=time)
        
    def set(self, value):
        return maya.cmds.setAttr(self.key, value)
                
    def exists(self):
        return maya.cmds.objExists(self.key)
    
    def has_keyframes(self):
        ret = maya.cmds.keyframe(self.key, query=True)
        if ret is None:
            return False
        else:
            return len(ret) != 0
