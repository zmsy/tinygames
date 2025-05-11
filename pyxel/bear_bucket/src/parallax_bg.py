import math
import random
import pyxel
from typing import List, Tuple, TypedDict

# Colors from main.pyxpal for moody, dark mountains (no red)
MOUNTAIN_COLORS = [1, 2, 5]  # darkest to lightest

# Each layer: (vertical offset, parallax factor, color index, roughness)
LAYERS: List[Tuple[int, float, int, int]] = [
    (90, 0.2, MOUNTAIN_COLORS[0], 18),  # farthest, darkest, smoothest
    (110, 0.4, MOUNTAIN_COLORS[1], 10),
    (135, 0.7, MOUNTAIN_COLORS[2], 3),  # closest, lightest, roughest
]


class StarsConfig(TypedDict):
    num_stars: int
    color: int
    twinkle_color: int
    area_top: int
    area_bottom_frac: float
    parallax_factor: float
    twinkle_mod: int
    twinkle_speed: float
    twinkle_min: float
    twinkle_max: float
    twinkle_phase_jitter: float


# Static config for stars
STARS_CONFIG: StarsConfig = {
    "num_stars": 40,
    "color": 7,  # white
    "twinkle_color": 6,  # light gray for twinkle
    "area_top": 0,  # y start
    "area_bottom_frac": 0.5,  # fraction of screen_height for y end
    "parallax_factor": 0.08,  # slower than mountains
    "twinkle_mod": 13,  # cross/star pattern
    "twinkle_speed": 0.08,  # radians per frame
    "twinkle_min": 0.3,  # min brightness (0-1)
    "twinkle_max": 1.0,  # max brightness (0-1)
    "twinkle_phase_jitter": 2.0,  # phase offset per star
}

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

        # Moon parameters
        random.seed(self.seed + 999)
        moon_radius = 16
        moon_x = random.randint(
            self.screen_width // 2, self.screen_width - moon_radius - 8
        )
        moon_y = random.randint(12, self.screen_height // 4)
        self.moon_pos = (moon_x, moon_y, moon_radius)

        # Star parameters
        random.seed(self.seed + 1234)
        self.stars: List[Tuple[int, int]] = []
        num_stars = STARS_CONFIG["num_stars"]
        area_top = STARS_CONFIG["area_top"]
        area_bottom = int(self.screen_height * STARS_CONFIG["area_bottom_frac"])
        for _ in range(num_stars):
            sx = random.randint(0, self.screen_width - 1)
            sy = random.randint(area_top, area_bottom)
            self.stars.append((sx, sy))

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
        # Draw moon (color 7: white, or 6: light gray)
        moon_x, moon_y, moon_radius = self.moon_pos
        pyxel.circ(moon_x, moon_y, moon_radius, 7)
        # Optionally, add a subtle crater
        pyxel.circ(
            moon_x + moon_radius // 3, moon_y + moon_radius // 4, moon_radius // 4, 6
        )

        # Draw stars with parallax and twinkle
        star_parallax = self.parallax_x * STARS_CONFIG["parallax_factor"]
        frame = pyxel.frame_count
        for i, (sx, sy) in enumerate(self.stars):
            # Parallax scroll
            px = (sx - int(star_parallax)) % self.screen_width
            # Twinkle: brightness modulated by time and star index
            phase = (
                frame * STARS_CONFIG["twinkle_speed"]
                + i * STARS_CONFIG["twinkle_phase_jitter"]
            )
            twinkle = (math.sin(phase) + 1) / 2  # 0..1
            brightness = (
                STARS_CONFIG["twinkle_min"]
                + (STARS_CONFIG["twinkle_max"] - STARS_CONFIG["twinkle_min"]) * twinkle
            )
            # Choose color based on brightness threshold
            color = (
                STARS_CONFIG["color"]
                if brightness > 0.5
                else STARS_CONFIG["twinkle_color"]
            )
            pyxel.pset(px, sy, color)
            # Optionally, make some stars crosses
            if (sx + sy) % STARS_CONFIG["twinkle_mod"] == 0 and brightness > 0.7:
                pyxel.pset(px, sy - 1, color)
                pyxel.pset(px, sy + 1, color)
                pyxel.pset(px - 1, sy, color)
                pyxel.pset(px + 1, sy, color)

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
