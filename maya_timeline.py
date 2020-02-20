import maya


class Timeline:
    
    @classmethod
    def get_current_frame(cls):
        return maya.cmds.currentTime(query=True)
    
    @classmethod
    def get_start(cls):
        return maya.cmds.playbackOptions(query=True, minTime=True)
    
    @classmethod
    def get_end(cls):
        return maya.cmds.playbackOptions(query=True, maxTime=True)
        
    @classmethod
    def list_of_frames(cls):
        return list(range(int(cls.get_start()), int(cls.get_end()) + 1))
    
    @classmethod
    def set_start(cls, frame):
        return maya.cmds.playbackOptions(edit=True, minTime=frame)
    
    @classmethod
    def set_end(cls, frame):
        return maya.cmds.playbackOptions(edit=True, maxTime=frame)
