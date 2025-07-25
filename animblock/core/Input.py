import glfw

class Input(object):

    def __init__(self):
        self.keyDownList = set()
        self.keyPressedList = set()
        self.keyUpList = set()
        self.mouseButtonDown = False
        self.mouseButtonPressed = 0
        self.mouseButtonUp = False
        self.mouseWheelAmount = 0
        self.mousePosition = (0, 0)
        self.quitStatus = False
        self.windowResize = False
        self.windowWidth = None
        self.windowHeight = None

    def update(self):
        self.keyDownList.clear()
        self.keyUpList.clear()
        self.mouseButtonDown = False
        self.mouseButtonUp = False
        self.windowResize = False

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keyDownList.add(key)
            self.keyPressedList.add(key)
        elif action == glfw.RELEASE:
            self.keyUpList.add(key)
            self.keyPressedList.discard(key)

    def mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.mouseButtonDown = True
            self.mouseButtonPressed = button
        elif action == glfw.RELEASE:
            self.mouseButtonUp = True
            self.mouseButtonPressed = 0

    def cursor_position_callback(self, window, xpos, ypos):
        self.mousePosition = (xpos, ypos)

    def scroll_callback(self, window, xoffset, yoffset):
        self.mouseWheelAmount += yoffset

    def window_size_callback(self, window, width, height):
        self.windowResize = True
        self.windowWidth = width
        self.windowHeight = height

    def isKeyDown(self, keyCode):
        return keyCode in self.keyDownList

    def isKeyPressed(self, keyCode):
        return keyCode in self.keyPressedList

    def isKeyUp(self, keyCode):
        return keyCode in self.keyUpList

    def isMouseDown(self):
        return self.mouseButtonDown

    def isMousePressed(self):
        return self.mouseButtonPressed

    def isMouseUp(self):
        return self.mouseButtonUp

    def getMousePosition(self):
        return self.mousePosition

    def getMouseWheel(self):
        amount = self.mouseWheelAmount
        self.mouseWheelAmount = 0  # Reset after reading
        return amount

    def quit(self):
        return self.quitStatus

    def resize(self):
        return self.windowResize

    def getWindowSize(self):
        return {"width": self.windowWidth, "height": self.windowHeight}
