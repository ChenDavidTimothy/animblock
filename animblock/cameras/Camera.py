import numpy as np

from ..core import Object3D, Uniform, UniformList
from ..mathutils import MatrixFactory


class Camera(Object3D):
    def __init__(self):
        super().__init__()
        self.projectionMatrix = MatrixFactory.makeIdentity()
        self.viewMatrix = MatrixFactory.makeIdentity()

        self.uniformList = UniformList()
        self.uniformList.addUniform(Uniform("mat4", "projectionMatrix", self.projectionMatrix))
        self.uniformList.addUniform(Uniform("mat4", "viewMatrix", self.viewMatrix))

        # Default perspective parameters
        self.fov = 60.0
        self.aspect = 1.0
        self.near = 0.1
        self.far = 1000.0

    def getProjectionMatrix(self):
        return self.projectionMatrix

    def updateViewMatrix(self):
        self.viewMatrix = np.linalg.inv(self.transform.matrix)

    def getViewMatrix(self):
        return self.viewMatrix

    def setPerspective(self, fov, aspect, near, far):
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
        self.updateProjectionMatrix()

    def updateProjectionMatrix(self):
        self.projectionMatrix = MatrixFactory.makePerspective(
            self.fov, self.aspect, self.near, self.far
        )
        self.uniformList.setUniformValue("projectionMatrix", self.projectionMatrix)

    def lookAt(self, target_position):
        self.viewMatrix = MatrixFactory.makeLookAt(self.getPosition(), target_position, [0, 0, 1])
