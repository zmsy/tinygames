import math
import random
import pyxel
from typing import List, Tuple

# Colors from main.pyxpal for moody, dark mountains (no red)
MOUNTAIN_COLORS = [1, 2, 5]  # darkest to lightest

# Each layer: (vertical offset, parallax factor, color index, roughness)
LAYERS: List[Tuple[int, float, int, int]] = [
    (90, 0.2, MOUNTAIN_COLORS[0], 18),  # farthest, darkest, smoothest
    (110, 0.4, MOUNTAIN_COLORS[1], 10),
    (135, 0.7, MOUNTAIN_COLORS[2], 3),  # closest, lightest, roughest
]

type Point = Tuple[int, int]
type MountainProfile = Tuple[List[Point], float, int, int]


class ParallaxBackground:
    def __init__(self, screen_width: int, screen_height: int, seed: int = 42):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.seed = seed
        self.parallax_x = 0.0
        self.parallax_vx = 0.0
        self.last_player_x = None

        # Precompute static mountain profiles for each layer
        self.mountain_profiles: List[MountainProfile] = []
        for base_y, factor, color, roughness in LAYERS:
            points: List[Tuple[int, int]] = []
            # Make the profile wider than the screen for seamless scrolling
            profile_width = self.screen_width * 2
            for x in range(0, profile_width + 8, 8):
                local_seed = self.seed + color * 100 + x
                random.seed(local_seed)
                height = int(
                    math.sin((x) * 0.03 + color) * roughness
                    + random.randint(-roughness // 2, roughness // 2)
                )
                y = base_y - 20 - height  # Move mountains up by 20px
                points.append((x, y))
            self.mountain_profiles.append((points, factor, color, profile_width))

    def update(self, player_x: float):
        if self.last_player_x is None:
            self.last_player_x = player_x
        player_dx = player_x - self.last_player_x
        target_vx = player_dx
        self.parallax_vx += (target_vx - self.parallax_vx) * 0.2
        self.parallax_vx *= 0.92
        self.parallax_x += self.parallax_vx
        self.last_player_x = player_x

    def draw(self):
        for profile, factor, color, profile_width in self.mountain_profiles:
            # Calculate horizontal offset for parallax
            offset = int(self.parallax_x * factor) % profile_width
            # Build visible points by shifting and wrapping
            visible_points: List[Tuple[int, int]] = []
            for x, y in profile:
                sx = x - offset
                if 0 <= sx <= self.screen_width + 8:
                    visible_points.append((sx, y))
            # Ensure we have enough points to draw
            if len(visible_points) < 2:
                continue
            # Draw polygon (mountain silhouette)
            for i in range(len(visible_points) - 1):
                x1, y1 = visible_points[i]
                x2, y2 = visible_points[i + 1]
                pyxel.tri(x1, y1, x2, y2, x1, self.screen_height, color)
                pyxel.tri(x2, y2, x2, self.screen_height, x1, self.screen_height, color)
