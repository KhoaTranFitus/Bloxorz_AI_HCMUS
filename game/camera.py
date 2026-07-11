from ursina import Entity, camera, mouse, Vec3


class CameraController(Entity):
    """Simple camera controller to orbit and zoom around a board center.

    Controls:
    - Q / E: rotate left / right
    - Scroll up / scroll down: zoom in / out
    """

    def __init__(self, center: Vec3, distance: float = 22.0, height: float = 16.0) -> None:
        super().__init__()

        self.center = center
        self.distance = distance
        self.height = height
        self.orbit_y = 45.0
        self.min_distance = 6.0
        self.max_distance = 60.0
        self.update_camera()

    def update_camera(self) -> None:
        import math

        rad = math.radians(self.orbit_y)
        x = self.center.x + self.distance * math.sin(rad)
        z = self.center.z + self.distance * math.cos(rad)

        camera.position = Vec3(x, self.height, z)
        camera.look_at(self.center)

    def update(self) -> None:
        if mouse.left:
            self.orbit_y += mouse.velocity.x * 30.0
            self.update_camera()

    def input(self, key: str) -> None:
        if key == 'q':
            self.orbit_y -= 5.0
            self.update_camera()

        if key == 'e':
            self.orbit_y += 5.0
            self.update_camera()

        if key == 'scroll up':
            self.distance = max(self.min_distance, self.distance - 2.0)
            self.update_camera()

        if key == 'scroll down':
            self.distance = min(self.max_distance, self.distance + 2.0)
            self.update_camera()
