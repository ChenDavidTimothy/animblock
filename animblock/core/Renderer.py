import moderngl

from ..lights import Light
from .Mesh import Mesh
from .OpenGLUtils import OpenGLUtils


class Renderer:
    def __init__(self, viewWidth=512, viewHeight=512, clearColor=None):
        if clearColor is None:
            clearColor = [0.75, 0.75, 0.75]

        self.ctx = OpenGLUtils.ctx

        # Enable standard 3D rendering features
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        # Note: Multisampling is handled by GLFW window hints, not ModernGL directly

        # Set default viewport
        self.setViewport(0, 0, viewWidth, viewHeight)

        self.clearColor = clearColor

        self.fog = None
        self.shadowMapEnabled = False

    def setViewport(self, left=0, bottom=0, width=512, height=512):
        """Set viewport dimensions"""
        self.left = left
        self.bottom = bottom
        self.screenWidth = width
        self.screenHeight = height
        self.ctx.viewport = (left, bottom, width, height)

    def setViewportSize(self, width, height):
        """Set viewport size"""
        self.screenWidth = width
        self.screenHeight = height
        self.ctx.viewport = (0, 0, width, height)

    def setClearColor(self, red, green, blue):
        """Set clear color"""
        self.clearColor = [red, green, blue]

    def setFog(self, fog):
        """Set fog parameters"""
        self.fog = fog
        fogColor = fog.uniformList.getUniformValue("fogColor")
        self.setClearColor(fogColor[0], fogColor[1], fogColor[2])

    def render(self, scene, camera, renderTarget=None, clearColor=True, clearDepth=True):
        """Main render method"""

        # Shadow rendering pass (if enabled)
        if self.shadowMapEnabled:
            self._renderShadowPass(scene)

        # Main rendering pass
        self._renderMainPass(scene, camera, renderTarget, clearColor, clearDepth)

    def _renderShadowPass(self, scene):
        """Render shadow map pass"""
        # Get shadow casting lights
        shadowCastLightList = scene.getObjectsByFilter(
            lambda x: isinstance(x, Light)
            and hasattr(x, "shadowCamera")
            and x.shadowCamera is not None
        )

        # Get shadow casting meshes
        shadowCastMeshList = scene.getObjectsByFilter(
            lambda x: isinstance(x, Mesh) and x.castShadow
        )

        for light in shadowCastLightList:
            if hasattr(light, "shadowRenderTarget") and light.shadowRenderTarget:
                # Bind shadow framebuffer
                light.shadowRenderTarget.framebuffer.use()

                # Clear shadow buffer
                self.ctx.clear(1.0, 0.0, 1.0, 1.0)  # Clear to magenta for debugging

                # Update shadow camera matrices
                light.shadowCamera.updateViewMatrix()
                light.shadowCamera.uniformList.setUniformValue(
                    "shadowProjectionMatrix", light.shadowCamera.getProjectionMatrix()
                )
                light.shadowCamera.uniformList.setUniformValue(
                    "shadowViewMatrix", light.shadowCamera.getViewMatrix()
                )

                # Render shadow casting meshes
                for mesh in shadowCastMeshList:
                    if hasattr(light, "shadowMaterial"):
                        # Update shadow material uniforms
                        light.shadowCamera.uniformList.update(light.shadowMaterial.program)
                        mesh.render(light.shadowMaterial.program)

    def _renderMainPass(self, scene, camera, renderTarget, clearColor, clearDepth):
        """Render main pass"""

        # Set render target
        if renderTarget is None:
            # Render to screen
            self.ctx.screen.use()
        else:
            # Render to custom framebuffer
            renderTarget.framebuffer.use()

        # Clear buffers
        if clearColor and clearDepth:
            self.ctx.clear(
                red=self.clearColor[0], green=self.clearColor[1], blue=self.clearColor[2], alpha=1.0
            )
        elif clearColor:
            # Clear only color - ModernGL approach
            self.ctx.clear(
                red=self.clearColor[0], green=self.clearColor[1], blue=self.clearColor[2], alpha=1.0
            )
        elif clearDepth:
            # Clear only depth - ModernGL approach
            self.ctx.clear(depth=1.0)

        # Get objects to render
        meshList = scene.getObjectsByFilter(lambda x: isinstance(x, Mesh))
        lightList = scene.getObjectsByFilter(lambda x: isinstance(x, Light))

        # Update camera matrices
        camera.updateViewMatrix()
        viewMatrix = camera.getViewMatrix()
        projectionMatrix = camera.getProjectionMatrix()
        camera.uniformList.setUniformValue("projectionMatrix", projectionMatrix)
        camera.uniformList.setUniformValue("viewMatrix", viewMatrix)

        # Group meshes by material to minimize program switches
        meshList.sort(key=lambda mesh: id(mesh.material.program))

        # Pre-calculate light data
        lightData = []
        for light in lightList:
            lightInfo = {
                "position": light.transform.getPosition(),
                "direction": light.getDirection() if hasattr(light, "getDirection") else [0, 0, 0],
                "light": light,
            }
            lightData.append(lightInfo)

        # Render meshes
        currentProgram = None
        for mesh in meshList:
            if not mesh.visible:
                continue

            program = mesh.material.program

            # Switch program only when necessary
            if program != currentProgram:
                currentProgram = program

                # Update camera uniforms for this program
                camera.uniformList.update(program)

                # Update fog uniforms
                if self.fog is not None:
                    self.fog.uniformList.update(program)

                # Update light uniforms
                for lightInfo in lightData:
                    light = lightInfo["light"]
                    light.uniformList.setUniformValue("position", lightInfo["position"])
                    light.uniformList.setUniformValue("direction", lightInfo["direction"])
                    light.uniformList.update(program)

                    # Update shadow uniforms if applicable
                    if hasattr(light, "shadowCamera") and light.shadowCamera is not None:
                        light.shadowCamera.uniformList.setUniformValue(
                            "shadowLightDirection", lightInfo["direction"]
                        )
                        light.shadowCamera.uniformList.update(program)

            # Render the mesh
            mesh.render(program)
