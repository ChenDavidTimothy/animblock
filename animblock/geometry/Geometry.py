import numpy as np

from ..core.OpenGLUtils import OpenGLUtils


class Geometry:
    def __init__(self, name="Geometry"):
        self.attributeData = {}
        self.vertexCount = None  # must be set by extending class
        self.name = name

        # store vertex array objects for different programs
        # index by program object id
        self.vaoData = {}

        # Store ModernGL buffers
        self.buffers = {}

    def setAttribute(self, type, name, value):
        """Set attribute data and create ModernGL buffer"""
        data = {"type": type, "name": name, "value": value, "buffer": None}
        self.attributeData[name] = data
        self.processAttribute(name)

    def processAttribute(self, name):
        """Create ModernGL buffer for attribute data"""
        data = self.attributeData[name]

        # Convert to numpy array and create ModernGL buffer
        array = np.array(data["value"], dtype=np.float32)
        buffer = OpenGLUtils.ctx.buffer(array.tobytes())

        data["buffer"] = buffer
        self.buffers[name] = buffer

    def updateAttribute(self, name, value):
        """Update attribute data and ModernGL buffer"""
        self.attributeData[name]["value"] = value
        self.processAttribute(name)

    def setupVAO(self, program):
        """Setup ModernGL VertexArray for given program"""
        # Build content list for ModernGL vertex array
        vao_content = []

        for name, data in self.attributeData.items():
            if data["buffer"] is None:
                continue

            # Convert type to ModernGL format string
            if data["type"] == "float":
                format_str = "1f"
            elif data["type"] == "vec2":
                format_str = "2f"
            elif data["type"] == "vec3":
                format_str = "3f"
            elif data["type"] == "vec4":
                format_str = "4f"
            else:
                raise Exception(f"Unknown attribute type: {data['type']}")

            # Check if this attribute exists in the program
            if data["name"] in program:
                vao_content.append((data["buffer"], format_str, data["name"]))

        # Create ModernGL VertexArray
        if vao_content:
            vao = OpenGLUtils.ctx.vertex_array(program, vao_content)
        else:
            # Create empty VAO if no valid attributes
            vao = OpenGLUtils.ctx.vertex_array(program, [])

        # Store VAO using program object as key
        self.vaoData[id(program)] = vao
        return vao

    def getVAO(self, program):
        """Get ModernGL VertexArray for given program"""
        program_id = id(program)

        if program_id not in self.vaoData:
            self.setupVAO(program)

        return self.vaoData[program_id]
