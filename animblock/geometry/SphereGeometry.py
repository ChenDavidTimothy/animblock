from math import cos, pi, sin

from .SurfaceGeometry import SurfaceGeometry


class SphereGeometry(SurfaceGeometry):
    def __init__(self, radius=1, xResolution=32, yResolution=16):
        super().__init__(
            0,
            2 * pi,
            xResolution,
            -pi / 2,
            pi / 2,
            yResolution,
            lambda u, v: [radius * sin(u) * cos(v), radius * sin(v), radius * cos(u) * cos(v)],
        )
