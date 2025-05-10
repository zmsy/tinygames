import pyxel
from typing import List


class Const:
    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 128


class Player:
    def __init__(
        self,
        x: float,
        y: float,
        width: int = 8,
        height: int = 8,
        speed: float = 2.0,
        jump_strength: float = 5.0,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0
        self.speed: float = speed
        self.jump_strength: float = jump_strength
        self.is_jumping: bool = False
        self.is_on_ground: bool = False

    def move_left(self) -> None:
        self.velocity_x = -self.speed

    def move_right(self) -> None:
        self.velocity_x = self.speed

    def jump(self) -> None:
        if self.is_on_ground:
            self.velocity_y = -self.jump_strength
            self.is_jumping = True
            self.is_on_ground = False

    def update_position(self, tilemap: List[List[int]]) -> None:
        # Apply gravity
        self.velocity_y += 0.5  # Gravity constant

        # Update horizontal position
        self.x += self.velocity_x
        self.handle_collisions(tilemap, axis="x")

        # Update vertical position
        self.y += self.velocity_y
        self.handle_collisions(tilemap, axis="y")

        # Friction and reset horizontal velocity
        self.velocity_x = 0.0

    def handle_collisions(self, tilemap: List[List[int]], axis: str) -> None:
        map_width: int = len(tilemap[0])
        map_height: int = len(tilemap)

        # Calculate the tile indices the player occupies
        left: int = int(self.x // 8)
        right: int = int((self.x + self.width - 1) // 8)
        top: int = int(self.y // 8)
        bottom: int = int((self.y + self.height - 1) // 8)

        if axis == "x":
            for y in range(top, bottom + 1):
                if self.velocity_x > 0:  # Moving right
                    if right >= map_width or tilemap[y][right] == 1:
                        self.x = right * 8 - self.width
                        self.velocity_x = 0.0
                elif self.velocity_x < 0:  # Moving left
                    if left < 0 or tilemap[y][left] == 1:
                        self.x = (left + 1) * 8
                        self.velocity_x = 0.0
        elif axis == "y":
            self.is_on_ground = False
            for x in range(left, right + 1):
                if self.velocity_y > 0:  # Moving down
                    if bottom >= map_height or tilemap[bottom][x] == 1:
                        self.y = bottom * 8 - self.height
                        self.velocity_y = 0.0
                        self.is_on_ground = True
                elif self.velocity_y < 0:  # Moving up
                    if top < 0 or tilemap[top][x] == 1:
                        self.y = (top + 1) * 8
                        self.velocity_y = 0.0

    def draw(self) -> None:
        pyxel.rect(int(self.x), int(self.y), self.width, self.height, 9)


class App:
    def __init__(self) -> None:
        print("Initializing bucket o' bears...")

        pyxel.init(Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT, title="Bear Bucket")
        pyxel.load("./main.pyxres")

        self.tilemap: List[List[int]] = self.load_tilemap()
        self.player: Player = Player(x=32.0, y=32.0)

        pyxel.run(self.update, self.draw)

    def load_tilemap(self) -> List[List[int]]:
        # 32 tiles wide (256 px), 16 tiles high (128 px)
        width: int = 32
        height: int = 16
        tilemap: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]

        # Bottom row is all walls
        for x in range(width):
            tilemap[height - 1][x] = 1

        # Left and right walls up to y=11 (0-indexed)
        for y in range(4, height - 1):
            tilemap[y][0] = 1
            tilemap[y][width - 1] = 1

        # Left platform: 1 tile less wide, moved up 1 tile, leftmost at x=8
        for x in range(8, 12):  # 4 tiles wide: 8,9,10,11
            tilemap[height - 6][x] = 1  # height-6 is one tile above previous

        # Right platform: 1 tile less wide, leftmost at x=20, y=10
        for x in range(20, 24):  # 4 tiles wide: 20,21,22,23
            tilemap[10][x] = 1

        return tilemap

    def update(self) -> None:
        # Input handling
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player.move_left()
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player.move_right()
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.player.jump()

        self.player.update_position(self.tilemap)

    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 256, 128)
        self.draw_tilemap()
        self.player.draw()

    def draw_tilemap(self) -> None:
        for y, row in enumerate(self.tilemap):
            for x, tile in enumerate(row):
                if tile == 1:
                    pyxel.rect(
                        x * 8, y * 8, 8, 8, 7
                    )  # Draw walls/platforms as white squares


App()
