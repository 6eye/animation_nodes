import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_NodeNetworkSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_NodeNetworkSocket"
    bl_label = "Node Network Socket"
    dataType = "Node Network"
    allowedInputTypes = ["all"]
    drawColor = (0.34, 0.25, 0.22, 1.0)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return None
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return None
