from core import *

from material import *


class LineSegmentMaterial(LineBasicMaterial):
    def __init__(self, color=None, alpha=1, lineWidth=4, useVertexColors=False):
        if color is None:
            color = [1, 1, 1]
        super().__init__(
            color=color, alpha=alpha, lineWidth=lineWidth, useVertexColors=useVertexColors
        )

        self.drawStyle = GL_LINES
