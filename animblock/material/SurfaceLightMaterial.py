from .SurfaceBasicMaterial import SurfaceBasicMaterial


class SurfaceLightMaterial(SurfaceBasicMaterial):
    def __init__(
        self,
        color=None,
        alpha=1,
        texture=None,
        wireframe=False,
        lineWidth=1,
        useVertexColors=False,
        alphaTest=0,
    ):
        if color is None:
            color = [1, 1, 1]

        # Initialize with SurfaceBasicMaterial
        super().__init__(
            color=color,
            alpha=alpha,
            texture=texture,
            wireframe=wireframe,
            lineWidth=lineWidth,
            useVertexColors=useVertexColors,
            alphaTest=alphaTest,
        )

        # Enable lighting for this material
        self.setUniform("bool", "useLight", 1)
