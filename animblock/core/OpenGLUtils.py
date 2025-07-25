import numpy as np
from OpenGL.GL import *
from PIL import Image


class OpenGLUtils:
    @staticmethod
    def initializeShader(shaderCode, shaderType):
        extension = "#extension GL_ARB_shading_language_420pack : require\n"
        shaderCode = "#version 130\n" + extension + shaderCode

        # create empty shader object and return reference value
        shaderID = glCreateShader(shaderType)
        # stores the source code in the shader
        glShaderSource(shaderID, shaderCode)
        # compiles source code previously stored in the shader object
        glCompileShader(shaderID)

        # queries whether shader compile was successful
        compileSuccess = glGetShaderiv(shaderID, GL_COMPILE_STATUS)
        if not compileSuccess:
            # retrieve error message
            errorMessage = glGetShaderInfoLog(shaderID)
            # free memory used to store shader program
            glDeleteShader(shaderID)
            # TODO: parse str(errorMessage) for better printing
            raise Exception(errorMessage)

        # compilation was successful; return shader reference value
        return shaderID

    @staticmethod
    def initializeShaderFromCode(vertexShaderCode, fragmentShaderCode):
        vertexShaderID = OpenGLUtils.initializeShader(vertexShaderCode, GL_VERTEX_SHADER)
        fragmentShaderID = OpenGLUtils.initializeShader(fragmentShaderCode, GL_FRAGMENT_SHADER)

        programID = glCreateProgram()
        glAttachShader(programID, vertexShaderID)
        glAttachShader(programID, fragmentShaderID)
        glLinkProgram(programID)

        return programID

    """
    @staticmethod
    def initializeShaderFromFiles(vertexShaderFileName, fragmentShaderFileName):

        vertexShaderFile = open(vertexShaderFileName, mode='r')
        vertexShaderCode = vertexShaderFile.read()
        vertexShaderFile.close()

        fragmentShaderFile = open(fragmentShaderFileName, mode='r')
        fragmentShaderCode = fragmentShaderFile.read()
        fragmentShaderFile.close()

        return OpenGLUtils.initializeShaderFromCode(vertexShaderCode, fragmentShaderCode)
    """

    @staticmethod
    def initializeTexture(imageFileName):
        # load image from file using Pillow
        image = Image.open(imageFileName)
        # Convert to RGBA if not already
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return OpenGLUtils.initializeSurface(image)

    @staticmethod
    def initializeSurface(image):
        # Flip image to match OpenGL's coordinate system
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Get dimensions and pixel data
        width, height = image.size
        textureData = np.array(image).tobytes()

        # Create texture
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)

        # send image data to texture buffer
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData
        )

        # generate a mipmap for use with 2d textures
        glGenerateMipmap(GL_TEXTURE_2D)

        # default: use smooth interpolated color sampling when textures magnified
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # use the mip map filter rather than standard filter
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        return texid

    @staticmethod
    def updateSurface(image, textureID):
        # Flip image to match OpenGL's coordinate system
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Get dimensions and pixel data
        width, height = image.size
        textureData = np.array(image).tobytes()

        glBindTexture(GL_TEXTURE_2D, textureID)
        # send image data to texture buffer
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData
        )

        # Generate mipmaps after updating
        glGenerateMipmap(GL_TEXTURE_2D)
