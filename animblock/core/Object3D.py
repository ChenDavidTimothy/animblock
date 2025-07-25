import numpy as np
from OpenGL.GL import *

from ..mathutils import Matrix


class Object3D:
    def __init__(self):
        self.transform = Matrix()
        # Set reference back to this object for change notifications
        self.transform._objectRef = self
        self.parent = None
        self.children = []
        self.name = ""

        # Cache for world matrix calculation
        self._worldMatrix = None
        self._worldMatrixNeedsUpdate = True
        self._lastTransformMatrix = np.copy(self.transform.matrix)

    def add(self, child):
        self.children.append(child)
        child.parent = self
        # Force update of child world matrix
        child._invalidateWorldMatrix()

    def remove(self, child):
        self.children.remove(child)
        child.parent = None

    def _hasTransformChanged(self):
        """Check if transform has changed since last world matrix calculation."""
        if not np.array_equal(self._lastTransformMatrix, self.transform.matrix):
            self._lastTransformMatrix = np.copy(self.transform.matrix)
            return True
        return False

    def _invalidateWorldMatrix(self):
        """Mark world matrix as needing update and propagate to children."""
        self._worldMatrixNeedsUpdate = True
        for child in self.children:
            child._invalidateWorldMatrix()

    def getWorldMatrix(self):
        # Check if transform has changed
        if self._hasTransformChanged():
            self._worldMatrixNeedsUpdate = True

        # Recalculate only if needed
        if self._worldMatrixNeedsUpdate or self._worldMatrix is None:
            if self.parent is None:
                self._worldMatrix = np.copy(self.transform.matrix)
            else:
                self._worldMatrix = self.parent.getWorldMatrix() @ self.transform.matrix
            self._worldMatrixNeedsUpdate = False

        return self._worldMatrix

    # return a list of descendants in depth-first order
    def getDepthFirstList(self):
        # elements added to list as a stack for depth-first traversal
        unvisitedList = [self]
        visitedList = []
        while len(unvisitedList) > 0:
            item = unvisitedList.pop(0)
            visitedList.append(item)
            unvisitedList = item.children + unvisitedList
        return visitedList

    # return a list of descendants x with filterFunction(x) = True
    def getObjectsByFilter(self, filterFunction=None):
        return list(filter(filterFunction, self.getDepthFirstList()))

    # return first descendent with name parameter matching given value
    def getObjectByName(self, name):
        return self.getObjectsByFilter(lambda x: x.name == name)[0]
