from pathlib import Path

import moderngl
from PIL import Image


class OpenGLUtils:
    ctx = None  # ModernGL context, set by Base class

    @staticmethod
    def initializeShaderFromCode(vertexShaderCode, fragmentShaderCode):
        """Create shader program using ModernGL"""
        try:
            # Fix GLSL syntax for ModernGL compatibility
            vertexShaderCode = OpenGLUtils._fixVertexShaderSyntax(vertexShaderCode)
            fragmentShaderCode = OpenGLUtils._fixFragmentShaderSyntax(fragmentShaderCode)

            program = OpenGLUtils.ctx.program(
                vertex_shader=vertexShaderCode, fragment_shader=fragmentShaderCode
            )
            return program
        except Exception as e:
            print("=== VERTEX SHADER ===")
            print(vertexShaderCode)
            print("\n=== FRAGMENT SHADER ===")
            print(fragmentShaderCode)
            print("=====================")
            raise Exception(f"Shader compilation failed: {e}")

    @staticmethod
    def _fixVertexShaderSyntax(code):
        """Fix vertex shader syntax for GLSL 330 core"""
        if "#version" not in code:
            code = "#version 330 core\n" + code
        return code

    @staticmethod
    def _fixFragmentShaderSyntax(code):
        """Fix fragment shader syntax for GLSL 330 core"""
        if "#version" not in code:
            code = "#version 330 core\nout vec4 fragColor;\n" + code

        # Fix deprecated gl_FragColor
        code = code.replace("gl_FragColor", "fragColor")

        # Fix deprecated texture2D
        code = code.replace("texture2D(", "texture(")

        # Fix C-style array initializers
        if "Light lightArray[4] = {light0, light1, light2, light3};" in code:
            code = code.replace(
                "Light lightArray[4] = {light0, light1, light2, light3};",
                """Light lightArray[4];
                lightArray[0] = light0;
                lightArray[1] = light1;
                lightArray[2] = light2;
                lightArray[3] = light3;""",
            )

        return code

    @staticmethod
    def initializeTexture(imageFileName):
        """Load texture using ModernGL"""
        # Convert to Path object
        image_path = Path(imageFileName)

        # If file doesn't exist, try relative to package
        if not image_path.exists():
            package_dir = Path(__file__).parent.parent  # animblock/core/ -> animblock/
            image_path = package_dir / imageFileName

        # Load image from file using Pillow
        image = Image.open(image_path)
        # Convert to RGBA if not already
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return OpenGLUtils.initializeSurface(image)

    @staticmethod
    def initializeSurface(image):
        """Create ModernGL texture from PIL image"""
        # Flip image to match OpenGL's coordinate system
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Get dimensions and pixel data
        width, height = image.size
        textureData = image.tobytes()

        # Create ModernGL texture
        texture = OpenGLUtils.ctx.texture((width, height), 4, textureData)

        # Set filtering (equivalent to PyOpenGL settings)
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        # Note: ModernGL texture repeat is the default behavior

        return texture

    @staticmethod
    def updateSurface(image, texture):
        """Update ModernGL texture with new image data"""
        # Flip image to match OpenGL's coordinate system
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Get pixel data
        textureData = image.tobytes()

        # Update texture data
        texture.write(textureData)
