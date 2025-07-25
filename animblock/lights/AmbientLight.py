from .Light import Light


class AmbientLight(Light):
    def __init__(self, position=None, color=None, strength=1):
        if color is None:
            color = [1, 1, 1]
        if position is None:
            position = [0, 0, 0]
        super().__init__(position=position, color=color, strength=strength)

        self.uniformList.setUniformValue("isAmbient", 1)
