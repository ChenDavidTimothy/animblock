from OpenGL.GL import *

from .LineBasicMaterial import LineBasicMaterial


class LineDashedMaterial(LineBasicMaterial):
    def __init__(
        self,
        color=None,
        alpha=1,
        lineWidth=4,
        dashLength=0.50,
        gapLength=0.25,
        useVertexColors=False,
    ):
        if color is None:
            color = [1, 1, 1]
        super().__init__(
            color=color, alpha=alpha, lineWidth=lineWidth, useVertexColors=useVertexColors
        )

        self.setUniform("bool", "useDashes", 1)
        self.setUniform("float", "dashLength", dashLength)
        self.setUniform("float", "gapLength", gapLength)
