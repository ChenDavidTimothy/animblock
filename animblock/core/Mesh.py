from .Object3D import Object3D
from .Uniform import Uniform, UniformList


class Mesh(Object3D):
    def __init__(self, geometry, material):
        super().__init__()
        self.geometry = geometry
        self.material = material
        self.visible = True

        self.uniformList = UniformList()
        self.uniformList.addUniform(Uniform("mat4", "modelMatrix", self.transform.matrix))

        # Shadow casting/receiving flags
        self.castShadow = False
        self.uniformList.addUniform(Uniform("bool", "receiveShadow", 0))

    def setCastShadow(self, state=True):
        self.castShadow = state

    def setReceiveShadow(self, state=True):
        if state:
            self.uniformList.setUniformValue("receiveShadow", 1)
        else:
            self.uniformList.setUniformValue("receiveShadow", 0)

    def render(self, program=None):
        """Render mesh using ModernGL"""
        if not self.visible:
            return

        # Use material's program if no program specified
        if program is None:
            program = self.material.program

        # Get VAO for this program
        vao = self.geometry.getVAO(program)

        # Update mesh-specific uniforms
        self.uniformList.setUniformValue("modelMatrix", self.getWorldMatrix())
        self.uniformList.update(program)

        # Update material uniforms
        self.material.updateUniforms()

        # Update material render settings
        self.material.updateRenderSettings()

        # Render the VAO
        if self.geometry.vertexCount > 0:
            vao.render(mode=self.material.drawStyle)
