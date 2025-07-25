class Uniform:
    def __init__(self, type, name, value):
        # type: float | vec2 | vec3 | vec4 | mat4 | bool | sampler2D
        self.type = type

        # name of corresponding variable in shader program
        self.name = name

        # value to be sent to shader.
        #   float/vecN/matN: numeric data
        #   bool: 0 for False, 1 for True
        #   sampler2D: ModernGL texture object or texture ID
        self.value = value

        # only used for uniform sampler2D variables;
        #   used to track texture unit assignment
        self.textureNumber = None

    def update(self, program):
        """Update uniform in ModernGL program - simplified interface"""
        # For ModernGL, uniform updates are handled directly by the Material class
        # This method is kept for compatibility but doesn't need to do anything
        pass


class UniformList:
    """Helper class for managing collections of uniforms"""

    def __init__(self):
        self.data = {}

    def addUniform(self, uniform, indexName=None):
        """Add uniform to collection"""
        if indexName is None:
            indexName = uniform.name
        self.data[indexName] = uniform

    def getUniformValue(self, indexName):
        """Get uniform value by name"""
        return self.data[indexName].value

    def setUniformValue(self, indexName, value):
        """Set uniform value by name"""
        self.data[indexName].value = value

    def update(self, program):
        """Update all uniforms in ModernGL program"""
        textureUnit = 1  # Start at 1, unit 0 reserved for shadow maps

        for uniform in self.data.values():
            if uniform.name not in program:
                continue

            try:
                if uniform.type == "sampler2D":
                    # Handle texture uniforms
                    if uniform.value and hasattr(uniform.value, "use"):
                        # This is a ModernGL texture
                        uniform.value.use(location=textureUnit)
                        program[uniform.name].value = textureUnit
                        uniform.textureNumber = textureUnit
                        textureUnit += 1
                    elif isinstance(uniform.value, int) and uniform.value > 0:
                        # Legacy texture ID - assign texture unit
                        program[uniform.name].value = (
                            uniform.textureNumber if uniform.textureNumber else 0
                        )
                else:
                    # Handle other uniform types directly
                    if uniform.type == "bool":
                        program[uniform.name].value = bool(uniform.value)
                    elif uniform.type == "mat4":
                        # ModernGL expects matrices as bytes
                        import numpy as np

                        if isinstance(uniform.value, np.ndarray):
                            # Convert to float32 and transpose for column-major order
                            matrix_data = uniform.value.astype(np.float32).T
                            program[uniform.name].write(matrix_data.tobytes())
                        else:
                            program[uniform.name].value = uniform.value
                    else:
                        program[uniform.name].value = uniform.value
            except Exception:
                # Silently skip uniforms that don't exist in this program
                pass
