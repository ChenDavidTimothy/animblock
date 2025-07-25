import time

import glfw
import moderngl
from PIL import Image

from .Input import Input
from .OpenGLUtils import OpenGLUtils


class Base:
    def __init__(self):
        # Initialize GLFW
        if not glfw.init():
            raise Exception("GLFW initialization failed")

        # Configure GLFW
        glfw.window_hint(glfw.SAMPLES, 4)  # 4x antialiasing
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)  # Don't use old OpenGL

        # Create a GLFW window
        self.window = glfw.create_window(640, 640, "   ", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window creation failed")

        # Make the window's context current
        glfw.make_context_current(self.window)

        # Create ModernGL context AFTER making window context current
        self.ctx = moderngl.create_context()

        # Set the global context in OpenGLUtils
        OpenGLUtils.ctx = self.ctx

        # Enable depth testing and blending (equivalent to PyOpenGL setup)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        # Note: MULTISAMPLE is enabled by default in ModernGL when creating context with samples

        # Set up input handling
        self.input = Input()
        glfw.set_key_callback(self.window, self.input.key_callback)
        glfw.set_mouse_button_callback(self.window, self.input.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.input.cursor_position_callback)
        glfw.set_scroll_callback(self.window, self.input.scroll_callback)
        glfw.set_window_size_callback(self.window, self.onWindowSizeChanged)

        self.clock = time.time()
        self.deltaTime = 0
        self.running = True

        # To store window dimensions
        self.window_width, self.window_height = glfw.get_window_size(self.window)

        # Renderer
        self.renderer = None
        self.camera = None
        self.scene = None

    def setWindowTitle(self, text):
        glfw.set_window_title(self.window, text)

    def setWindowSize(self, width, height):
        self.window_width = width
        self.window_height = height
        glfw.set_window_size(self.window, width, height)
        self.onWindowSizeChanged(self.window, width, height)

    def onWindowSizeChanged(self, window, width, height):
        self.window_width = width
        self.window_height = height

        # Get actual framebuffer size (important for high-DPI displays)
        fb_width, fb_height = glfw.get_framebuffer_size(window)

        # Set ModernGL viewport to match the framebuffer size
        self.ctx.viewport = (0, 0, fb_width, fb_height)

        if self.renderer:
            self.renderer.setViewportSize(fb_width, fb_height)

        if self.camera:
            aspect_ratio = width / float(height)  # Use window dimensions for aspect ratio
            self.camera.setPerspective(
                self.camera.fov, aspect_ratio, self.camera.near, self.camera.far
            )

    def initialize(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def run(self):
        self.initialize()

        while not glfw.window_should_close(self.window) and self.running:
            # Calculate delta time
            current_time = time.time()
            self.deltaTime = current_time - self.clock
            self.clock = current_time

            # Poll for and process events
            glfw.poll_events()
            self.input.update()

            # Update the scene
            self.update()

            # Render the scene
            self.render()

            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Check for quit
            if self.input.isKeyPressed(glfw.KEY_ESCAPE):
                self.running = False

        # Cleanup
        self.cleanup()
        glfw.terminate()

    def cleanup(self):
        pass

    def saveScreenshot(self, fileName):
        width, height = glfw.get_framebuffer_size(self.window)
        # Read from ModernGL default framebuffer
        data = self.ctx.screen.read(components=3)
        image = Image.frombytes("RGB", (width, height), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(fileName)
        print(f"Screenshot saved as {fileName}")
