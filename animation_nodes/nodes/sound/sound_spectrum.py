import bpy
import numpy
from math import expm1
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList

samplingItems = [
    ("EXP", "Exponential", "", "", 0),
    ("CUSTOM", "Custom", "", "", 1),
    ("SINGLE", "Single", "", "", 2),
    ("FULL", "Full", "", "", 3)
]
reductionItems = [
    ("MEAN", "Mean", "", "", 0),
    ("MAX", "Max", "", "", 1)
]
reductionFunctions = {
    "MEAN" : numpy.mean,
    "MAX" : numpy.max
}

class SoundSpectrumNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundSpectrumNode"
    bl_label = "Sound Spectrum"
    errorHandlingType = "EXCEPTION"

    reductionFunction: EnumProperty(name = "Reduction Function", default = "MAX",
        items = reductionItems)
    smoothingSamples: IntProperty(name = "Smoothing Samples", default = 5, min = 0)
    beta: FloatProperty(name = "Kaiser Beta", default = 6, min = 0)

    samplingMethod: EnumProperty(name = "Sampling Method", default = "EXP", items = samplingItems,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Sound", "Sound", "sound")
        self.newInput("Float", "Frame", "frame")
        self.newInput("Float", "Attack", "attack", value = 0.005, minValue = 0, maxValue = 1)
        self.newInput("Float", "Release", "release", value = 0.6, minValue = 0, maxValue = 1)
        self.newInput("Float", "Amplitude", "amplitude", value = 1)

        if self.samplingMethod == "EXP":
            self.newInput("Integer", "Count", "count", value = 20, minValue = 1)
            self.newInput("Float", "Low", "low", value = 0, minValue = 0, maxValue = 1, hide = True)
            self.newInput("Float", "High", "high", value = 1, minValue = 0, maxValue = 1, hide = True)
            self.newInput("Float", "K", "k", value = 5, minValue = 0.00001)
        elif self.samplingMethod == "CUSTOM":
            self.newInput("Float List", "Pins", "pins")
        elif self.samplingMethod == "SINGLE":
            self.newInput("Float", "Low", "low", value = 0, minValue = 0, maxValue = 1)
            self.newInput("Float", "High", "high", value = 0.1, minValue = 0, maxValue = 1)

        self.newInput("Scene", "Scene", "scene", hide = True)

        if self.samplingMethod in ("EXP", "CUSTOM", "FULL"):
            self.newOutput("Float List", "Spectrum", "spectrum")
        else:
            self.newOutput("Float", "Spectrum", "spectrum")

    def draw(self, layout):
        layout.prop(self, "samplingMethod", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "reductionFunction", text = "")
        layout.prop(self, "smoothingSamples")
        layout.prop(self, "beta")

    def getExecutionFunctionName(self):
        if self.samplingMethod == "EXP": return "executeExponential"
        elif self.samplingMethod == "CUSTOM": return "executeCustom"
        elif self.samplingMethod == "SINGLE": return "executeSingle"
        elif self.samplingMethod == "FULL": return "executeFull"

    def executeExponential(self, sound, frame, attack, release, amplitude, count, low, high, k, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        if not isValidRange(low, high): self.raiseErrorMessage("Invalid interval!")
        if count < 1: self.raiseErrorMessage("Invalid count!")

        fps = scene.render.fps
        spectrum = sound.computeTimeSmoothedSpectrum(frame / fps, (frame + 1) / fps,
            attack, release, self.smoothingSamples, self.beta)
        maxFrequency = len(spectrum) - 1

        scale = expm1(k) / (high - low)
        pins = [low + expm1(k * i / count) / scale for i in range(count + 1)]

        bars = DoubleList(count)
        reductionFunction = reductionFunctions[self.reductionFunction]
        for i in range(count):
            x, y = int(pins[i] * maxFrequency), int(pins[i + 1] * maxFrequency)
            if x == y: y = x + 1
            bars[i] = reductionFunction(spectrum[x:y]) * 300 * amplitude
        return bars

    def executeSingle(self, sound, frame, attack, release, amplitude, low, high, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        if not isValidRange(low, high): self.raiseErrorMessage("Invalid interval!")

        fps = scene.render.fps
        spectrum = sound.computeTimeSmoothedSpectrum(frame / fps, (frame + 1) / fps,
            attack, release, self.smoothingSamples, self.beta)
        maxFrequency = len(spectrum) - 1

        reductionFunction = reductionFunctions[self.reductionFunction]
        return reductionFunction(spectrum[int(low * maxFrequency):int(high * maxFrequency)]) * 300 * amplitude

    def executeCustom(self, sound, frame, attack, release, amplitude, pins, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        if not isValidCustomList(pins): self.raiseErrorMessage("Invalid pins list!")

        fps = scene.render.fps
        spectrum = sound.computeTimeSmoothedSpectrum(frame / fps, (frame + 1) / fps,
            attack, release, self.smoothingSamples, self.beta)
        maxFrequency = len(spectrum) - 1

        bars = DoubleList(len(pins) - 1)
        reductionFunction = reductionFunctions[self.reductionFunction]
        for i in range(len(pins) - 1):
            x, y = int(pins[i] * maxFrequency), int(pins[i + 1] * maxFrequency)
            bars[i] = reductionFunction(spectrum[x:y]) * 300 * amplitude
        return bars

    def executeFull(self, sound, frame, attack, release, amplitude, scene):
        if len(sound.soundSequences) == 0: self.raiseErrorMessage("Empty sound!")
        fps = scene.render.fps
        spectrum = sound.computeTimeSmoothedSpectrum(frame / fps, (frame + 1) / fps,
            attack, release, self.smoothingSamples, self.beta)
        return DoubleList.fromNumpyArray(spectrum) * (300 * amplitude)

def isValidCustomList(pins):
    if len(pins) < 3: return False
    for i in range(len(pins) - 1):
        if pins[i] < 0 or pins[i] > 1: return False
        if pins[i] >= pins[i + 1]: return False
    return pins[-1] >= 0 and pins[-1] <= 1

def isValidRange(low, high):
    if low >= high: return False
    if low < 0 or low > 1: return False
    if high < 0 or high > 1: return False
    return True
