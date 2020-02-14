import maya

import AltMaya as altmaya


class IdleCallback:

    ids = []

    def __init__(self, callback):
        self.callback = callback
        self.id = maya.cmds.scriptJob(idleEvent=self.callback)
        IdleCallback.ids.append(self.id)

    def kill(self):
        IdleCallback.ids.remove(self.id)
        maya.cmds.scriptJob(kill=self.id)

    @staticmethod
    def clear():
        for cid in IdleCallback.ids:
            maya.cmds.scriptJob(kill=cid)
        IdleCallback.ids = []

class AttributeChangeCallback:

    jobs = {}

    def __init__(self, attribute_index, callback):
        self.name = attribute_index.obj
        self.callback = callback
        m_object = altmaya.API.get_mobject(self.name)
        job = maya.OpenMaya.MNodeMessage.addAttributeChangedCallback(m_object, self.callback)
        AttributeChangeCallback.jobs[self.name] = job

    def kill(self):
        job = AttributeChangeCallback.jobs[self.name]
        maya.OpenMaya.MMessage.removeCallback(job)
        del AttributeChangeCallback.jobs[self.name]

    @staticmethod
    def is_already_registered(attribute_index):
        name = attribute_index.obj
        return name in AttributeChangeCallback.jobs.keys()

    @staticmethod
    def clear():
        for key in AttributeChangeCallback.jobs.keys():
            job_ids = om.MCallbackIdArray()
            m_object = altmaya.API.get_mobject(key)
            maya.OpenMaya.MNodeMessage.nodeCallbacks(m_object, job_ids)
            maya.OpenMaya.MNodeMessage.removeCallbacks(job_ids)
            # job = AttributeChangeCallback.jobs[key]
            # maya.OpenMaya.MMessage.removeCallback(job)
        AttributeChangeCallback.jobs = {}

    