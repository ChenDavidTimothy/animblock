import numpy as np

from .MatrixFactory import *


# this class uses a numpy matrix to store data
# and contains methods to transform the matrix
class Matrix:
    LOCAL = 1
    GLOBAL = 2

    def __init__(self):
        self.matrix = MatrixFactory.makeIdentity().astype(
            float
        )  # set type, otherwise set values cast to ints
        self._objectRef = None  # Reference to the Object3D using this matrix

    def _notifyChange(self):
        """Notify Object3D when matrix changes."""
        if hasattr(self, "_objectRef") and self._objectRef is not None:
            self._objectRef._invalidateWorldMatrix()

    def translate(self, x=0, y=0, z=0, type=GLOBAL):
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeTranslation(x, y, z)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeTranslation(x, y, z) @ self.matrix
        self._notifyChange()

    def rotateZ(self, angle=0, type=GLOBAL):
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeRotationZ(angle)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeRotationZ(angle) @ self.matrix
        self._notifyChange()

    def rotateX(self, angle=0, type=GLOBAL):
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeRotationX(angle)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeRotationX(angle) @ self.matrix
        self._notifyChange()

    def rotateY(self, angle=0, type=GLOBAL):
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeRotationY(angle)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeRotationY(angle) @ self.matrix
        self._notifyChange()

    def translateAxisDistance(self, axis=None, distance=0, type=GLOBAL):
        if axis is None:
            axis = [1, 0, 0]
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeTranslationAxisDistance(axis, distance)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeTranslationAxisDistance(axis, distance) @ self.matrix
        self._notifyChange()

    def rotateAxisAngle(self, axis=None, angle=0, type=GLOBAL):
        if axis is None:
            axis = [1, 0, 0]
        if type == Matrix.LOCAL:
            self.matrix = self.matrix @ MatrixFactory.makeRotationAxisAngle(axis, angle)
        if type == Matrix.GLOBAL:
            self.matrix = MatrixFactory.makeRotationAxisAngle(axis, angle) @ self.matrix
        self._notifyChange()

    def scaleUniform(self, s=1, type=GLOBAL):
        self.matrix = self.matrix @ MatrixFactory.makeScaleUniform(s)
        self._notifyChange()

    # positions are global with respect to parent object
    def getPosition(self):
        return [self.matrix.item((0, 3)), self.matrix.item((1, 3)), self.matrix.item((2, 3))]

    def setPosition(self, x=0, y=0, z=0, type=LOCAL):
        self.matrix[0, 3] = x
        self.matrix[1, 3] = y
        self.matrix[2, 3] = z
        self._notifyChange()

    # returns 3x3 submatrix with rotation data (assumes no scale)
    def getRotationMatrix(self):
        return np.array([self.matrix[0][0:3], self.matrix[1][0:3], self.matrix[2][0:3]])

    # copies the upper 3x3 submatrix of M (which contains rotation data) into this matrix.
    def setRotationSubmatrix(self, M):
        self.matrix[0:3, 0:3] = M[0:3, 0:3]
        self._notifyChange()

    # rotate matrix to look at target=[x,y,z]
    def lookAt(self, x, y, z):
        self.matrix = MatrixFactory.makeLookAt(self.getPosition(), [x, y, z], [0, 1, 0])
        self._notifyChange()
