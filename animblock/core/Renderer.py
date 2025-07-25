from OpenGL.GL import *

from ..lights import Light
from .Mesh import Mesh


class Renderer:
    def __init__(self, viewWidth=512, viewHeight=512, clearColor=None):
        if clearColor is None:
            clearColor = [0.75, 0.75, 0.75]
        glEnable(GL_DEPTH_TEST)

        # enable transparency
        glEnable(GL_BLEND)

        # needed for antialiasing; also need to configure in window settings
        glEnable(GL_MULTISAMPLE)

        # allow setting of point size from vertex shader
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)

        # set default screen dimensions
        self.setViewport(0, 0, viewWidth, viewHeight)

        self.clearColor = clearColor

        self.fog = None
        self.shadowMapEnabled = False

    # define the location/size of the rendered output in the window
    def setViewport(self, left=0, bottom=0, width=512, height=512):
        self.left = left
        self.bottom = bottom
        self.screenWidth = width
        self.screenHeight = height

    def setViewportSize(self, width, height):
        # define the location/size of the rendered output in the window
        self.screenWidth = width
        self.screenHeight = height

    # color(rgba) used for clearing the screen background
    def setClearColor(self, red, green, blue):
        self.clearColor = [red, green, blue]

    def setFog(self, fog):
        self.fog = fog
        fogColor = fog.uniformList.getUniformValue("fogColor")
        self.setClearColor(fogColor[0], fogColor[1], fogColor[2])

    def render(self, scene, camera, renderTarget=None, clearColor=True, clearDepth=True):
        # shadow rendering pass -------------------------------------------
        if self.shadowMapEnabled:
            # render objects in meshList from light's shadowCamera onto light's shadowMap

            # note: at present, only one shadow casting directional light is supported
            shadowCastLightList = scene.getObjectsByFilter(
                lambda x: isinstance(x, Light) and x.shadowCamera is not None
            )

            # only store depth data for objects which are set to cast a shadow on other objects
            shadowCastMeshList = scene.getObjectsByFilter(
                lambda x: isinstance(x, Mesh) and x.castShadow
            )

            for light in shadowCastLightList:
                # set render target properties
                glBindFramebuffer(GL_FRAMEBUFFER, light.shadowRenderTarget.framebufferID)
                glViewport(0, 0, light.shadowRenderTarget.width, light.shadowRenderTarget.height)

                glClearColor(1, 0, 1, 1)
                glClear(GL_COLOR_BUFFER_BIT)
                glClear(GL_DEPTH_BUFFER_BIT)

                # activate shader
                shadowProgramID = light.shadowMaterial.shaderProgramID
                glUseProgram(shadowProgramID)

                # reduce number of matrix inversions to improve performance
                light.shadowCamera.updateViewMatrix()
                light.shadowCamera.uniformList.setUniformValue(
                    "shadowProjectionMatrix", light.shadowCamera.getProjectionMatrix()
                )
                light.shadowCamera.uniformList.setUniformValue(
                    "shadowViewMatrix", light.shadowCamera.getViewMatrix()
                )
                light.shadowCamera.uniformList.update(shadowProgramID)

                for mesh in shadowCastMeshList:
                    mesh.render(shaderProgramID=shadowProgramID)

        # standard rendering pass -------------------------------------------
        glClearColor(self.clearColor[0], self.clearColor[1], self.clearColor[2], 1)

        # activate render target
        if renderTarget is None:
            # set render target to window
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(self.left, self.bottom, self.screenWidth, self.screenHeight)
        else:
            # set render target properties
            glBindFramebuffer(GL_FRAMEBUFFER, renderTarget.framebufferID)
            glViewport(0, 0, renderTarget.width, renderTarget.height)

        # clear specified buffers
        if clearColor:
            glClear(GL_COLOR_BUFFER_BIT)
        if clearDepth:
            glClear(GL_DEPTH_BUFFER_BIT)

        # Get objects to render
        meshList = scene.getObjectsByFilter(lambda x: isinstance(x, Mesh))
        lightList = scene.getObjectsByFilter(lambda x: isinstance(x, Light))

        # Reduce number of matrix calculations
        camera.updateViewMatrix()

        # Pre-calculate camera matrices once per frame
        viewMatrix = camera.getViewMatrix()
        projectionMatrix = camera.getProjectionMatrix()
        camera.uniformList.setUniformValue("projectionMatrix", projectionMatrix)
        camera.uniformList.setUniformValue("viewMatrix", viewMatrix)

        # Sort meshes by shader program to minimize program switches
        meshList.sort(key=lambda mesh: mesh.material.shaderProgramID)

        # Track current shader program to avoid redundant switching
        currentProgramID = None

        # Pre-calculate light data once per frame
        lightData = []
        for light in lightList:
            lightInfo = {
                "position": light.transform.getPosition(),
                "direction": light.getDirection(),
                "light": light,
            }
            lightData.append(lightInfo)

        # Render all meshes with optimized state changes
        for mesh in meshList:
            if not mesh.visible:
                continue

            # Only switch shader programs when necessary
            programID = mesh.material.shaderProgramID
            if programID != currentProgramID:
                glUseProgram(programID)
                currentProgramID = programID

                # Update uniforms that apply to all meshes with this shader
                if self.fog is not None:
                    self.fog.uniformList.update(programID)

                camera.uniformList.update(programID)

                # Update light uniforms once per shader program
                for lightInfo in lightData:
                    light = lightInfo["light"]
                    light.uniformList.setUniformValue("position", lightInfo["position"])
                    light.uniformList.setUniformValue("direction", lightInfo["direction"])
                    light.uniformList.update(programID)

                    if light.shadowCamera is not None:
                        light.shadowCamera.uniformList.setUniformValue(
                            "shadowLightDirection", lightInfo["direction"]
                        )
                        light.shadowCamera.uniformList.update(programID)

            # Update mesh-specific uniforms and render the mesh
            mesh.render(shaderProgramID=programID)
