import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ParticleSystemListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ParticleSystemListSocket"
    bl_label = "Particle System List Socket"
    dataType = "Particle System List"
    allowedInputTypes = ["Particle System List"]
    drawColor = (1.0, 0.55, 0.55, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
