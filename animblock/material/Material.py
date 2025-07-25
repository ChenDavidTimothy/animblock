import moderngl

from ..core.OpenGLUtils import OpenGLUtils
from ..core.Uniform import Uniform


class Material:
    def __init__(self, vertexShaderCode, fragmentShaderCode, uniforms=None, name="Material"):
        self.program = OpenGLUtils.initializeShaderFromCode(vertexShaderCode, fragmentShaderCode)
        self.name = name

        # Store uniform objects for compatibility with existing code
        self.uniformList = {}

        if uniforms is not None:
            for uniform in uniforms:
                self.setUniform(uniform[0], uniform[1], uniform[2])

        # render settings - translated to ModernGL equivalents

        # options: moderngl.POINTS, moderngl.LINE_STRIP, moderngl.TRIANGLES
        self.drawStyle = moderngl.TRIANGLES

        # customize draw style moderngl.POINTS
        self.pointSize = 8

        # customize draw style moderngl.LINE_*
        self.lineWidth = 4

        # which sides of triangles should be rendered?
        self.renderFront = True
        self.renderBack = True

        self.additiveBlending = False
        self.linearFiltering = True

    @property
    def shaderProgramID(self):
        """Compatibility property - return the ModernGL program object"""
        return self.program

    def setUniform(self, type, name, value):
        """Set uniform value - compatible with existing interface"""
        self.uniformList[name] = Uniform(type, name, value)

    def updateRenderSettings(self):
        """Update ModernGL render settings"""
        ctx = OpenGLUtils.ctx

        # Point size (ModernGL doesn't have direct equivalent, handled in shader)
        # Line width (ModernGL doesn't have direct equivalent, handled in shader)

        # Face culling
        if self.renderFront and self.renderBack:
            ctx.disable(moderngl.CULL_FACE)
        else:
            ctx.enable(moderngl.CULL_FACE)
            # Note: ModernGL face culling is different from PyOpenGL
            # We'll keep it simple for now

        # Blending mode - ModernGL handles this differently
        # Blending is already enabled in the context, specific blend modes
        # would need to be set per-render call if needed
        pass

    def updateUniforms(self):
        """Update all uniforms in the program"""
        textureUnit = 1  # Start at 1, unit 0 reserved for shadow maps

        for uniform_name, uniform_obj in self.uniformList.items():
            if uniform_name not in self.program:
                continue

            try:
                if uniform_obj.type == "sampler2D":
                    # Handle texture uniforms
                    if uniform_obj.value and hasattr(uniform_obj.value, "use"):
                        # This is a ModernGL texture
                        uniform_obj.value.use(location=textureUnit)
                        self.program[uniform_name].value = textureUnit
                        textureUnit += 1
                    elif isinstance(uniform_obj.value, int) and uniform_obj.value > 0:
                        # Legacy texture ID handling
                        self.program[uniform_name].value = (
                            uniform_obj.textureNumber
                            if hasattr(uniform_obj, "textureNumber")
                            else 0
                        )
                else:
                    # Handle other uniform types
                    self.program[uniform_name].value = uniform_obj.value
            except Exception:
                # Silently skip uniforms that don't exist in this program
                pass
