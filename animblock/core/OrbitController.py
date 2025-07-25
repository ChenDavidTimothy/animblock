from math import cos, pi, sin

import glfw
import numpy as np

from .Object3D import Object3D


class OrbitController(Object3D):
    """
    An optimized controller for orbiting a camera around a target point.

    This controller allows camera manipulation through mouse input, including:
    - Orbiting around a target (azimuth/elevation)
    - Zooming in/out (changing distance)
    - Panning (moving the target point)

    The controller uses efficient matrix operations and implements interpolation
    for smooth movement.
    """

    def __init__(
        self,
        input_manager,
        camera,
        target=(0, 0, 0),
        distance=5,
        initial_azimuth=0,
        initial_elevation=0,
        smooth_factor=0.2,
    ):
        """
        Initialize the orbit controller.

        Args:
            input_manager: Reference to the input system
            camera: The camera to be controlled
            target (tuple): Target position (x, y, z) to orbit around
            distance (float): Initial distance from target
            initial_azimuth (float): Initial horizontal rotation angle in radians
            initial_elevation (float): Initial vertical rotation angle in radians
            smooth_factor (float): Interpolation factor for smooth movement (0-1)
        """
        super().__init__()

        # Input and camera references
        self.input = input_manager
        self.camera = camera

        # Position state
        self.target_position = np.array(target, dtype=float)
        self.distance = float(distance)

        # Target state for interpolation
        self.target_distance = self.distance
        self.target_azimuth = float(initial_azimuth)
        self.target_elevation = float(initial_elevation)
        self.target_pan_offset = np.zeros(3, dtype=float)

        # Current state
        self.azimuth = self.target_azimuth
        self.elevation = self.target_elevation
        self.pan_offset = np.zeros(3, dtype=float)

        # Interaction settings
        self.mouse_sensitivity = 0.004
        self.zoom_sensitivity = 0.1
        self.pan_sensitivity = 0.005
        self.smooth_factor = smooth_factor

        # Mouse interaction state
        self.dragging = False
        self.last_mouse_pos = None

        # Cached vectors (calculated on demand)
        self._forward = None
        self._right = None
        self._up = None
        self._need_vector_update = True

        # Configure mouse buttons
        self.MOUSE_ROTATE = glfw.MOUSE_BUTTON_MIDDLE
        self.MOUSE_PAN = glfw.MOUSE_BUTTON_RIGHT

        # Set initial camera position
        self._update_camera_position(immediate=True)

    def setSensitivity(
        self,
        mouse_sensitivity=0.004,
        zoom_sensitivity=0.1,
        pan_sensitivity=0.005,
        smooth_factor=None,
    ):
        """
        Set the sensitivity parameters for the controller.

        Args:
            mouse_sensitivity (float): Sensitivity for rotation
            zoom_sensitivity (float): Sensitivity for zoom
            pan_sensitivity (float): Sensitivity for panning
            smooth_factor (float, optional): Smoothing factor (0-1)
        """
        self.mouse_sensitivity = mouse_sensitivity
        self.zoom_sensitivity = zoom_sensitivity
        self.pan_sensitivity = pan_sensitivity
        if smooth_factor is not None:
            self.smooth_factor = max(0.0, min(1.0, smooth_factor))

    def setTarget(self, target_position):
        """
        Set a new target position to orbit around.

        Args:
            target_position (tuple): New target position (x, y, z)
        """
        self.target_position = np.array(target_position, dtype=float)
        self._update_camera_position(immediate=True)

    def setDistance(self, distance, immediate=False):
        """
        Set the distance from the target.

        Args:
            distance (float): New distance
            immediate (bool): Whether to update immediately or smoothly
        """
        self.target_distance = max(0.1, float(distance))
        if immediate:
            self.distance = self.target_distance
            self._update_camera_position(immediate=True)

    def update(self):
        """Update the controller state and camera position."""
        # Handle user input
        self._handle_mouse_input()

        # Smoothly interpolate the state
        self._interpolate_state()

        # Update the camera position based on current state
        self._update_camera_position()

    def _handle_mouse_input(self):
        """Process mouse input for camera control."""
        mouse_pos = self.input.getMousePosition()

        # Check for start of dragging
        if not self.dragging:
            if (
                self.input.isMousePressed() == self.MOUSE_ROTATE
                or self.input.isMousePressed() == self.MOUSE_PAN
            ):
                self.dragging = True
                self.last_mouse_pos = mouse_pos

        # Check for end of dragging
        if self.dragging and self.input.isMouseUp():
            self.dragging = False
            self.last_mouse_pos = None

        # Handle dragging for rotation or panning
        if self.dragging and self.last_mouse_pos:
            dx = mouse_pos[0] - self.last_mouse_pos[0]
            dy = mouse_pos[1] - self.last_mouse_pos[1]
            self.last_mouse_pos = mouse_pos

            if self.input.isMousePressed() == self.MOUSE_ROTATE:
                # Update rotation targets
                self.target_azimuth -= dx * self.mouse_sensitivity
                self.target_elevation += dy * self.mouse_sensitivity

                # Clamp elevation to avoid gimbal lock
                self.target_elevation = max(
                    min(self.target_elevation, pi / 2 - 0.01), -pi / 2 + 0.01
                )

                # Mark vectors for recalculation
                self._need_vector_update = True

            elif self.input.isMousePressed() == self.MOUSE_PAN:
                # Calculate pan vectors
                self._ensure_vectors_updated()

                # Calculate pan amount
                pan_x = self._right * -dx * self.pan_sensitivity
                pan_y = self._up * -dy * self.pan_sensitivity

                # Update target pan offset
                self.target_pan_offset += pan_x + pan_y

        # Handle zooming with mouse wheel
        zoom = self.input.getMouseWheel()
        if zoom != 0:
            # Calculate zoom factor
            zoom_factor = 1 - zoom * self.zoom_sensitivity

            # Update target distance with zoom
            self.target_distance *= zoom_factor
            self.target_distance = max(0.1, min(self.target_distance, 100))

    def _interpolate_state(self):
        """Smoothly interpolate between current and target state."""
        # Calculate interpolation factor
        t = min(1.0, self.smooth_factor)

        # Interpolate distance
        self.distance += (self.target_distance - self.distance) * t

        # Interpolate rotation
        self.azimuth += (self.target_azimuth - self.azimuth) * t
        self.elevation += (self.target_elevation - self.elevation) * t

        # Interpolate pan offset
        self.pan_offset += (self.target_pan_offset - self.pan_offset) * t

        # Update vectors if needed
        if self._need_vector_update:
            self._forward = None
            self._right = None
            self._up = None
            self._need_vector_update = False

    def _ensure_vectors_updated(self):
        """Ensure the direction vectors are up-to-date."""
        if self._forward is None:
            self._forward = np.array(
                [
                    cos(self.elevation) * sin(self.azimuth),
                    sin(self.elevation),
                    cos(self.elevation) * cos(self.azimuth),
                ]
            )

            # Right is perpendicular to forward (in XZ plane)
            self._right = np.array([cos(self.azimuth), 0, -sin(self.azimuth)])

            # Up is perpendicular to both forward and right
            self._up = np.cross(self._right, self._forward)

            # Normalize vectors
            self._right = self._right / np.linalg.norm(self._right)
            self._up = self._up / np.linalg.norm(self._up)

    def _update_camera_position(self, immediate=False):
        """
        Update the camera position based on orbit parameters.

        Args:
            immediate (bool): Whether to update immediately or use the current state
        """
        # Calculate final position vector from target
        target_with_offset = self.target_position + self.pan_offset

        # Calculate the camera position using spherical coordinates
        x = self.distance * cos(self.elevation) * sin(self.azimuth)
        y = self.distance * sin(self.elevation)
        z = self.distance * cos(self.elevation) * cos(self.azimuth)

        # Set camera position
        camera_pos = target_with_offset + np.array([x, y, z])
        self.camera.transform.setPosition(camera_pos[0], camera_pos[1], camera_pos[2])

        # Point camera at target
        self.camera.transform.lookAt(
            target_with_offset[0], target_with_offset[1], target_with_offset[2]
        )
