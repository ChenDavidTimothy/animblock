import moderngl

from .OpenGLUtils import OpenGLUtils


class RenderTarget:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height

        ctx = OpenGLUtils.ctx

        # Create color texture
        self.texture = ctx.texture((width, height), 4)  # RGBA texture
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Create depth texture
        self.depthTexture = ctx.depth_texture((width, height))

        # Create framebuffer with color and depth attachments
        self.framebuffer = ctx.framebuffer(
            color_attachments=[self.texture], depth_attachment=self.depthTexture
        )

        # For compatibility with existing code
        self.textureID = self.texture
        self.framebufferID = self.framebuffer
