from ..core import Mesh
from ..geometry import LineGeometry
from ..material import LineSegmentMaterial


class GridHelper(Mesh):
    def __init__(self, size=10, divisions=10, gridColor=None, centerColor=None, lineWidth=1):
        if centerColor is None:
            centerColor = [1, 0, 0]
        if gridColor is None:
            gridColor = [0, 0, 0]
        vertexPositionData = []
        vertexColorData = []

        # create range of values
        values = []
        deltaSize = size / divisions
        for n in range(divisions + 1):
            values.append(-size / 2 + n * deltaSize)

        # add vertical lines
        for x in values:
            vertexPositionData.append([x, -size / 2, 0])
            vertexPositionData.append([x, size / 2, 0])
            if x == 0:
                vertexColorData.append(centerColor)
                vertexColorData.append(centerColor)
            else:
                vertexColorData.append(gridColor)
                vertexColorData.append(gridColor)
        # add horizontal lines
        for y in values:
            vertexPositionData.append([-size / 2, y, 0])
            vertexPositionData.append([size / 2, y, 0])
            if y == 0:
                vertexColorData.append(centerColor)
                vertexColorData.append(centerColor)
            else:
                vertexColorData.append(gridColor)
                vertexColorData.append(gridColor)

        geo = LineGeometry(vertexPositionData)
        geo.setAttribute("vec3", "vertexColor", vertexColorData)

        mat = LineSegmentMaterial(lineWidth=lineWidth, useVertexColors=True)

        # initialize the mesh
        super().__init__(geo, mat)
