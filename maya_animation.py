import maya


class Animation:

    @classmethod
    def clear_range(cls, attribute_index, start, end):
        maya.cmds.cutKey(attribute_index.key, time=(start, end))

    @classmethod
    def add_keyframe(cls, attribute_index, time, value):
        maya.cmds.setKeyframe(attribute_index.key, time=time, value=value)
    
    @classmethod
    def list_frames_that_have_keyframes(cls, attribute_index):
        res = maya.cmds.keyframe(attribute_index, query=True)
        if res is None:
            return []
        else:
            return res
        
    @classmethod
    def is_attribute_animated(cls, attribute_index):
        return len(cls.list_frames_that_have_keyframes(attribute_index)) != 0
        
    @classmethod
    def list_keyable_attributes(cls, obj):
        result = maya.cmds.listAttr(obj, shortNames=True, keyable=True)
        if result is None:
            return []
        else:
            return result
            
    @classmethod
    def list_animated_attributes(cls, obj):
        return [attr for attr in cls.list_keyable_attributes(obj) if cls.is_attribute_animated(attr)]
    
    @classmethod
    def evaluate_at_frame(cls, attribute_index, frame):
        return maya.cmds.getAttr(str(attribute_index), t=frame)
        
    @classmethod
    def evaluate_for_timeline(cls, attribute_index):
        return [
            cls.evaluate_at_frame(attribute_index, frame)
            for frame in range(
                int(Timeline.get_start()),
                int(Timeline.get_end()) + 1
            )
        ]
    
    @classmethod
    def convert_to_free_splines(cls, attribute_index):
        maya.cmds.keyTangent(attribute_index.key, outTangentType="linear", inTangentType="linear")
        maya.cmds.keyTangent(attribute_index.key, lock=False)
        maya.cmds.keyTangent(attribute_index.key, weightedTangents=True)
        maya.cmds.keyTangent(attribute_index.key, weightLock=False)

    @classmethod
    def set_keyframe_ingoing_tangent(cls, attribute_index, frame, weight, angle):
        maya.cmds.keyTangent(
            attribute_index.key, time=(frame, frame),
            edit=True, absolute=True,
            outWeight=weight, outAngle=angle
        )

    @classmethod
    def set_keyframe_outgoing_tangent(cls, attribute_index, frame, weight, angle):
        maya.cmds.keyTangent(
            attribute_index.key, time=(frame, frame),
            edit=True, absolute=True,
            inWeight=weight, inAngle=angle
        )

    @classmethod
    def ghost_keyframes(cls, keyframes):
        maya.mel.eval("unGhostAll")
        for o in Selection.get():
            obj_for_ghosting = o
            obj_is_transform = maya.cmds.objectType(o) == 'transform'
            if obj_is_transform: # Change the object to the shape if this is a transform
                obj_for_ghosting = maya.cmds.listRelatives(o, shapes=True)[0]
            maya.cmds.setAttr("%s.ghosting" % obj_for_ghosting, 1)
            maya.cmds.setAttr("%s.ghostingControl" % obj_for_ghosting, 1)
            maya.cmds.setAttr("%s.ghostFrames" % obj_for_ghosting, keyframes, type="Int32Array")

