import maya

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def maya_main_window():
    # Return the Maya main window widget as a Python object
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class StandardMayaWindow(QtWidgets.QDialog):

    def __init__(self, title, parent=None):
        super(StandardMayaWindow, self).__init__(
            maya_main_window() if parent is None else parent
        )
        self.setWindowTitle(title)
        
        # Remove `?` thing on windows
        if maya.cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
          
        # Note sure what this does
        if maya.cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
