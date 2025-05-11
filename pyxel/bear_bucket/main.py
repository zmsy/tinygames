import pyxel
from dataclasses import dataclass
from typing import List
from src.parallax_bg import ParallaxBackground


class Const:
    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 128
    GRAVITY = 0.75
    TILE_LEN = 8


@dataclass
class BoundingBox:
    top: float
    left: float
    right: float
    bottom: float


class Player:
    def __init__(
        self,
        x: float,
        y: float,
        width: int = Const.TILE_LEN,
        height: int = Const.TILE_LEN,
        speed: float = 2.0,
        jump_strength: float = 10.0,
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

        # Platformer movement constants
        self.acceleration: float = 0.5
        self.max_speed: float = 2.5
        self.friction: float = 0.2

        # Track if input was given this frame
        self.input_x: int = 0

        # Jump buffer (frames)
        self.jump_buffer_timer: int = 0
        self.JUMP_BUFFER_MAX: int = 1  # ~0.1s at 60fps

        # Coyote time (frames)
        self.coyote_timer: int = 0
        self.COYOTE_TIME_MAX: int = 2  # ~0.07s at 60fps

    @property
    def box(self):
        return BoundingBox(
            self.y, self.x, self.x + self.width - 1, self.y + self.height - 1
        )

    def move_left(self) -> None:
        self.velocity_x -= self.acceleration
        self.input_x = -1

    def move_right(self) -> None:
        self.velocity_x += self.acceleration
        self.input_x = 1

    def jump(self) -> None:
        # Called on input: set jump buffer so jump will trigger as soon as on ground
        self.jump_buffer_timer = self.JUMP_BUFFER_MAX

    def update_jump(self, tilemap: List[List[int]]) -> None:
        # Try to jump if possible (buffered jump)
        if (self.is_on_ground or self.coyote_timer > 0) and self.jump_buffer_timer > 0:
            self.velocity_y = -self.jump_strength
            self.is_jumping = True
            self.is_on_ground = False
            self.jump_buffer_timer = 0
            self.coyote_timer = 0  # Reset coyote timer after jump

        # Decrement jump buffer timer
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # Set is_on_ground using terse helper
        self.is_on_ground = self._check_on_ground(tilemap)

        # Coyote time logic
        if self.is_on_ground:
            self.coyote_timer = self.COYOTE_TIME_MAX
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

    def update_position(self, tilemap: List[List[int]]) -> None:
        # Apply gravity
        self.velocity_y += Const.GRAVITY

        # Clamp velocity_x to max_speed
        if self.velocity_x > self.max_speed:
            self.velocity_x = self.max_speed
        elif self.velocity_x < -self.max_speed:
            self.velocity_x = -self.max_speed

        # Apply friction if no input
        if self.input_x == 0:
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
                if self.velocity_x < 0:
                    self.velocity_x = 0
            elif self.velocity_x < 0:
                self.velocity_x += self.friction
                if self.velocity_x > 0:
                    self.velocity_x = 0

        # Update horizontal position
        self.x += self.velocity_x
        self.handle_collisions(tilemap, axis="x")

        # Update vertical position
        self.y += self.velocity_y
        self.handle_collisions(tilemap, axis="y")

        # All jump/coyote/buffer logic colocated here
        self.update_jump(tilemap)

        # Reset input tracker for next frame
        self.input_x = 0

    def handle_collisions(self, tilemap: List[List[int]], axis: str) -> None:
        map_width: int = len(tilemap[0])
        map_height: int = len(tilemap)

        # Calculate the tile indices the player occupies
        left_tile: int = int(self.x // 8)
        right_tile: int = int((self.x + self.width - 1) // 8)
        top_tile: int = int(self.y // 8)
        bottom_tile: int = int((self.y + self.height - 1) // 8)

        if axis == "x":
            for y in range(top_tile, bottom_tile + 1):
                if self.velocity_x > 0:  # Moving right
                    if right_tile >= map_width or tilemap[y][right_tile] == 1:
                        self.x = right_tile * Const.TILE_LEN - self.width
                        self.velocity_x = 0.0
                elif self.velocity_x < 0:  # Moving left
                    if left_tile < 0 or tilemap[y][left_tile] == 1:
                        self.x = (left_tile + 1) * Const.TILE_LEN
                        self.velocity_x = 0.0
        elif axis == "y":
            self.is_on_ground = False
            for x in range(left_tile, right_tile + 1):
                if self.velocity_y > 0:  # Moving down
                    if bottom_tile >= map_height or tilemap[bottom_tile][x] == 1:
                        self.y = bottom_tile * Const.TILE_LEN - self.height
                        self.velocity_y = 0.0
                        self.is_on_ground = True
                elif self.velocity_y < 0:  # Moving up
                    if top_tile < 0 or tilemap[top_tile][x] == 1:
                        self.y = (top_tile + 1) * Const.TILE_LEN
                        self.velocity_y = 0.0

    def _check_on_ground(self, tilemap: List[List[int]]) -> bool:
        bottom_tile_row = int(self.box.bottom // Const.TILE_LEN) + 1
        if self.velocity_y < 0 or bottom_tile_row >= len(tilemap):
            return False
        final_y = self.box.bottom + 1
        tile_y = bottom_tile_row * Const.TILE_LEN
        left_tile = int(self.box.left // Const.TILE_LEN)
        right_tile = int(self.box.right // Const.TILE_LEN)
        return any(
            tilemap[bottom_tile_row][x] == 1 and 0 <= tile_y - final_y < 2
            for x in range(left_tile, right_tile + 1)
        )

    def draw(self) -> None:
        pyxel.rect(int(self.x), int(self.y), self.width, self.height, 9)


class App:
    def __init__(self) -> None:
        print("Initializing bucket o' bears...")

        pyxel.init(Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT, title="Bear Bucket")
        pyxel.load("./main.pyxres")

        self.tilemap: List[List[int]] = self.load_tilemap()
        self.player: Player = Player(x=32.0, y=32.0)
        self.parallax_bg = ParallaxBackground(Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT)

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
        # If neither left nor right pressed, input_x remains 0

        if pyxel.btn(pyxel.KEY_X):
            self.player.jump()

        self.player.update_position(self.tilemap)
        self.parallax_bg.update(self.player.x)

    def draw(self) -> None:
        pyxel.cls(0)
        # Draw parallax background before tilemap and player
        self.parallax_bg.draw()
        pyxel.bltm(0, 0, 0, 0, 0, 256, 128, 0)
        self.player.draw()


App()
