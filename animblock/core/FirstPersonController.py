from math import cos, sin

import glfw
import numpy as np

from ..mathutils import Matrix


class FirstPersonController:
    def __init__(self, input, target):
        super().__init__()

        self.input = input
        self.target = target

        # forward vector stays level with horizontal plane
        self.forward = np.array([0, 0, -1])
        # up vector is constant
        self.up = np.array([0, 1, 0])
        # recalculate right vector whenever forward vector changes
        self.right = np.cross(self.forward, self.up)

        # control rate of movement
        self.deltaTime = 1.0 / 60.0  # TODO: get actual number from input?
        self.unitsPerSecond = 1
        self.moveAmount = self.unitsPerSecond * self.deltaTime
        self.degreesPerSecond = 60
        self.turnAmount = self.degreesPerSecond * (3.1415926 / 180) * self.deltaTime

        # customizable key mappings - using GLFW key constants
        # standard controls (WASDRF, QETG)
        self.KEY_MOVE_FORWARDS = glfw.KEY_W
        self.KEY_MOVE_BACKWARDS = glfw.KEY_S
        self.KEY_MOVE_LEFT = glfw.KEY_A
        self.KEY_MOVE_RIGHT = glfw.KEY_D
        self.KEY_MOVE_UP = glfw.KEY_R
        self.KEY_MOVE_DOWN = glfw.KEY_F
        self.KEY_TURN_LEFT = glfw.KEY_Q
        self.KEY_TURN_RIGHT = glfw.KEY_E
        self.KEY_LOOK_UP = glfw.KEY_T
        self.KEY_LOOK_DOWN = glfw.KEY_G

    def setSpeed(self, unitsPerSecond=1, degreesPerSecond=60):
        self.unitsPerSecond = unitsPerSecond
        self.moveAmount = self.unitsPerSecond * self.deltaTime
        self.degreesPerSecond = degreesPerSecond
        self.turnAmount = self.degreesPerSecond * (3.1415926 / 180) * self.deltaTime

    def update(self):
        totalTurn = 0

        if self.input.isKeyPressed(self.KEY_MOVE_FORWARDS):
            self.target.transform.translateAxisDistance(
                self.forward, self.moveAmount, Matrix.GLOBAL
            )

        if self.input.isKeyPressed(self.KEY_MOVE_LEFT):
            self.target.transform.translateAxisDistance(self.right, -self.moveAmount, Matrix.GLOBAL)

        if self.input.isKeyPressed(self.KEY_MOVE_BACKWARDS):
            self.target.transform.translateAxisDistance(
                self.forward, -self.moveAmount, Matrix.GLOBAL
            )

        if self.input.isKeyPressed(self.KEY_MOVE_RIGHT):
            self.target.transform.translateAxisDistance(self.right, self.moveAmount, Matrix.GLOBAL)

        if self.input.isKeyPressed(self.KEY_MOVE_UP):
            self.target.transform.translateAxisDistance(self.up, self.moveAmount, Matrix.GLOBAL)

        if self.input.isKeyPressed(self.KEY_MOVE_DOWN):
            self.target.transform.translateAxisDistance(self.up, -self.moveAmount, Matrix.GLOBAL)

        if self.input.isKeyPressed(self.KEY_TURN_RIGHT):
            totalTurn -= self.turnAmount

        if self.input.isKeyPressed(self.KEY_TURN_LEFT):
            totalTurn += self.turnAmount

        # be consistent, swap to rotateAxisAngle(lookAxis=[1,0,0], totalLookAngle, Matrix.LOCAL)
        if self.input.isKeyPressed(self.KEY_LOOK_UP):
            self.target.transform.rotateX(self.turnAmount, Matrix.LOCAL)

        if self.input.isKeyPressed(self.KEY_LOOK_DOWN):
            self.target.transform.rotateX(-self.turnAmount, Matrix.LOCAL)

        # check if any turn happened, in which case, update direction vectors
        if totalTurn != 0:
            # convert global up direction into local coordinates
            v = np.linalg.inv(self.target.transform.getRotationMatrix()) @ self.up
            # local rotation around v
            self.target.transform.rotateAxisAngle(v, totalTurn, Matrix.LOCAL)

            # create 3x3 rotation matrix to update direction vectors
            s, c = sin(totalTurn), cos(totalTurn)
            rotation = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            self.forward = np.dot(rotation, self.forward)
            self.right = np.cross(self.forward, self.up)
