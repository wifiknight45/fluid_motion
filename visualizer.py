"""Interactive Evolving Fluid Visualizer - multi-mode edition.

Each mode has its own flow pattern, color palette and pace. In AUTO mode the
visualizer follows your computer's clock and crossfades between moods:

    05:00-08:00  Sunrise        08:00-17:00  Daylight
    17:00-20:00  Sunset         20:00-05:00  Aurora Night

Controls:
    RIGHT / LEFT / SPACE   next / previous / next mode
    1-7                    jump to a mode (turns AUTO off)
    A                      toggle AUTO (time-of-day) mode
    UP / DOWN              speed up / slow down
    P                      pause        S  save PNG screenshot
    H                      toggle HUD   ESC  quit
    Mouse                  move to create ripples

Requires: pygame>=2.0, numpy
Run:      python fluid_visualizer.py [--mode 2] [--no-auto] [--hour 19]
"""
import argparse
import sys
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pygame

WIDTH, HEIGHT = 800, 600
SPAN = 3 * np.pi            # spatial extent of the vertical axis
TAU = 2 * np.pi
BASE_SPEED = 1.2            # time units per second at 1.0x
MIN_SPEED, MAX_SPEED = 0.1, 5.0
FADE_SECONDS = 2.5          # crossfade length when the mode changes

sin, cos, abs_ = np.sin, np.cos, np.abs


# --- Palettes ----------------------------------------------------------------
def pal(a, b, c, d):
    """Cosine palette (Inigo Quilez): color = a + b*cos(2*pi*(c*t + d)), per RGB channel."""
    f = lambda v: np.array(v, dtype=np.float32)
    return {"a": f(a), "b": f(b), "c": f(c), "d": f(d)}


P_NEON    = pal((0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (1.0, 1.0, 1.0), (0.00, 0.33, 0.67))
P_OCEAN   = pal((0.06, 0.38, 0.52), (0.12, 0.28, 0.28), (0.5, 0.5, 0.5), (0.00, 0.05, 0.10))
P_SUNRISE = pal((0.85, 0.58, 0.50), (0.15, 0.25, 0.30), (0.6, 0.6, 0.6), (0.00, 0.10, 0.25))
P_DAY     = pal((0.55, 0.75, 0.85), (0.30, 0.20, 0.15), (0.8, 0.8, 0.8), (0.05, 0.10, 0.20))
P_SUNSET  = pal((0.60, 0.30, 0.40), (0.40, 0.30, 0.35), (0.45, 0.45, 0.45), (0.02, 0.10, 0.35))
P_AURORA  = pal((0.06, 0.20, 0.24), (0.10, 0.30, 0.22), (0.7, 0.6, 0.5), (0.65, 0.00, 0.15))
P_COSMIC  = pal((0.30, 0.12, 0.50), (0.28, 0.12, 0.38), (0.7, 0.7, 0.7), (0.00, 0.25, 0.10))


# --- Flow fields: (xx, yy, radius, t) -> array of roughly [-1, 1] -------------
def flow_neon(xx, yy, r, t):
    """The original interference pattern."""
    w1 = sin(xx + t) + cos(yy + t)
    w2 = sin(r - t * 1.5)
    w3 = cos(xx * 0.5 - t * 0.8) * sin(yy * 0.5 + t * 0.5)
    return (w1 + w2 + w3) / 4.5


def flow_ocean(xx, yy, r, t):
    """Domain-warped ridged waves: shimmering caustics like light on water."""
    u = xx + 0.5 * sin(yy * 1.2 + t * 0.6)
    v = yy + 0.5 * cos(xx * 1.0 - t * 0.5)
    c1 = 1 - abs_(sin(u * 1.6 + t * 0.9))
    c2 = 1 - abs_(sin(v * 1.9 - t * 0.7))
    c3 = 1 - abs_(sin((u + v) * 1.1 + t * 1.1))
    return (c1 * 0.4 + c2 * 0.35 + c3 * 0.25) * 2 - 1


def flow_sunrise(xx, yy, r, t):
    """Slow, soft horizontal bands drifting upward."""
    bands = sin(yy * 0.9 - t * 0.4 + 0.6 * sin(xx * 0.7 + t * 0.3))
    haze = sin(xx * 0.4 + yy * 0.3 - t * 0.25)
    return bands * 0.65 + haze * 0.35


def flow_daylight(xx, yy, r, t):
    """Crisp, brisk, higher-frequency waves."""
    return (sin(xx * 1.4 + t * 1.2) + sin(yy * 1.2 - t)
            + sin((xx + yy) * 0.9 + t * 0.8) + sin(r * 1.1 - t * 1.5)) / 4


def flow_sunset(xx, yy, r, t):
    """Long diagonal folds, like silk in wind."""
    p = xx * 0.8 + yy * 0.5
    return sin(p * 1.3 - t * 0.7 + 1.2 * sin(yy * 0.8 + t * 0.4)) * 0.7 + cos(r * 0.8 - t * 0.5) * 0.3


def flow_aurora(xx, yy, r, t):
    """Vertical curtains that sway and ripple."""
    a = sin(xx * 1.2 + 1.5 * sin(yy * 0.5 + t * 0.4) + t * 0.5)
    b = sin(xx * 2.3 - t * 0.6 + sin(yy * 0.9 - t * 0.3))
    return a * 0.6 + b * 0.4


@dataclass(frozen=True)
class Mode:
    name: str
    vibe: str
    field: Callable
    palette: dict
    speed: float = 1.0      # pace multiplier for this mode
    mouse: float = 1.0      # how strongly the mouse ripple shows


MODES = [
    Mode("Neon Classic", "electric",     flow_neon,     P_NEON,    1.0),
    Mode("Ocean",        "calm water",   flow_ocean,    P_OCEAN,   0.7, 0.8),
    Mode("Sunrise",      "gentle dawn",  flow_sunrise,  P_SUNRISE, 0.5, 0.7),
    Mode("Daylight",     "bright & busy", flow_daylight, P_DAY,    1.2),
    Mode("Sunset",       "warm flow",    flow_sunset,   P_SUNSET,  0.7),
    Mode("Aurora Night", "dark & dreamy", flow_aurora,  P_AURORA,  0.6, 1.2),
    Mode("Cosmic",       "deep space",   flow_neon,     P_COSMIC,  0.8),
]
MODE_INDEX = {m.name: i for i, m in enumerate(MODES)}


def mode_for_hour(hour):
    """Which mood fits this hour of the day (0-23)."""
    if 5 <= hour < 8:
        return MODE_INDEX["Sunrise"]
    if 8 <= hour < 17:
        return MODE_INDEX["Daylight"]
    if 17 <= hour < 20:
        return MODE_INDEX["Sunset"]
    return MODE_INDEX["Aurora Night"]


class Visualizer:
    def __init__(self, scale=2, fps=60, start_mode=None, auto=True, hour=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Interactive Evolving Fluid Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.scale, self.fps = max(1, scale), fps
        self.hour_override = hour

        self.auto = auto and start_mode is None
        self.mode_idx = start_mode if start_mode is not None else mode_for_hour(self._hour())
        self.prev_idx, self.fade = self.mode_idx, 1.0
        self._auto_timer = 0.0

        self.speed, self.t = 1.0, 0.0
        self.paused, self.show_hud, self.want_screenshot = False, True, False
        self._hud_key, self._hud_surf = None, None
        self.rebuild_grid()

    # --- Helpers --------------------------------------------------------------
    def _hour(self):
        return self.hour_override if self.hour_override is not None else time.localtime().tm_hour

    def set_mode(self, idx):
        if idx == self.mode_idx:
            return
        self.prev_idx, self.mode_idx, self.fade = self.mode_idx, idx, 0.0

    def rebuild_grid(self):
        """(Re)build coordinate grids at startup and on window resize."""
        w, h = self.screen.get_size()
        self.gw, self.gh = max(w // self.scale, 1), max(h // self.scale, 1)
        self.x_span = SPAN * self.gw / self.gh          # keep waves square
        x = np.linspace(0, self.x_span, self.gw, dtype=np.float32)
        y = np.linspace(0, SPAN, self.gh, dtype=np.float32)
        self.xx, self.yy = np.meshgrid(x, y, indexing="ij")   # (w, h) for surfarray
        self.radius = np.hypot(self.xx, self.yy)
        self.surf = pygame.Surface((self.gw, self.gh), 0, 24)

    # --- Simulation -----------------------------------------------------------
    def update(self, dt):
        if self.auto:
            self._auto_timer += dt
            if self._auto_timer >= 1.0:           # check the clock once a second
                self._auto_timer = 0.0
                self.set_mode(mode_for_hour(self._hour()))
        if self.fade < 1.0:
            self.fade = min(1.0, self.fade + dt / FADE_SECONDS)
        if not self.paused:
            s = self.fade * self.fade * (3 - 2 * self.fade)
            pace = MODES[self.prev_idx].speed + (MODES[self.mode_idx].speed - MODES[self.prev_idx].speed) * s
            self.t += BASE_SPEED * self.speed * pace * dt

    def _eval_mode(self, mode, mouse_term):
        f = mode.field(self.xx, self.yy, self.radius, self.t) + mouse_term * mode.mouse
        p = mode.palette
        return p["a"] + p["b"] * cos(TAU * (p["c"] * f[..., None] + p["d"]))

    def render_field(self, mouse_pos):
        w, h = self.screen.get_size()
        mxs = mouse_pos[0] / max(w, 1) * self.x_span
        mys = mouse_pos[1] / max(h, 1) * SPAN
        d = np.hypot(self.xx - mxs, self.yy - mys)
        mouse_term = sin(d * 3.5 - self.t * 5.0) / (d * 0.6 + 0.8) * 0.33

        rgb = self._eval_mode(MODES[self.mode_idx], mouse_term)
        if self.fade < 1.0:                        # crossfade from previous mode
            old = self._eval_mode(MODES[self.prev_idx], mouse_term)
            s = self.fade * self.fade * (3 - 2 * self.fade)
            rgb = old + (rgb - old) * s
        np.clip(rgb, 0.0, 1.0, out=rgb)
        pygame.surfarray.blit_array(self.surf, (rgb * 255).astype(np.uint8))

    # --- Drawing --------------------------------------------------------------
    def draw_hud(self):
        m = MODES[self.mode_idx]
        status = (f"{self.mode_idx + 1}. {m.name} - {m.vibe} | "
                  f"{'AUTO (time of day)' if self.auto else 'MANUAL'} | "
                  f"Speed {self.speed:.1f}x{' [PAUSED]' if self.paused else ''}")
        keys = "</>/SPACE: mode  1-7: pick  A: auto  UP/DOWN: speed  P: pause  S: save  H: hide  ESC: quit"
        if (status, keys) != self._hud_key:
            lines = [self.font.render(t, True, (255, 255, 255)) for t in (status, keys)]
            bg = pygame.Surface((max(l.get_width() for l in lines) + 16, 2 * lines[0].get_height() + 12),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            for i, l in enumerate(lines):
                bg.blit(l, (8, 4 + i * l.get_height()))
            self._hud_key, self._hud_surf = (status, keys), bg
        self.screen.blit(self._hud_surf, (10, 10))

    def draw(self):
        self.screen.blit(pygame.transform.smoothscale(self.surf, self.screen.get_size()), (0, 0))
        if self.want_screenshot:                   # saved before the HUD is drawn
            self.want_screenshot = False
            name = f"fluid_{MODES[self.mode_idx].name.replace(' ', '_').lower()}_{int(time.time())}.png"
            pygame.image.save(self.screen, name)
            print(f"Saved {name}")
        if self.show_hud:
            self.draw_hud()
        pygame.display.flip()

    # --- Input ----------------------------------------------------------------
    def handle_events(self):
        """Returns False when the app should quit."""
        n = len(MODES)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    return False
                elif k in (pygame.K_RIGHT, pygame.K_SPACE):
                    self.auto = False
                    self.set_mode((self.mode_idx + 1) % n)
                elif k == pygame.K_LEFT:
                    self.auto = False
                    self.set_mode((self.mode_idx - 1) % n)
                elif pygame.K_1 <= k < pygame.K_1 + n:
                    self.auto = False
                    self.set_mode(k - pygame.K_1)
                elif k == pygame.K_a:
                    self.auto = not self.auto
                    self._auto_timer = 1.0         # re-sync with the clock next frame
                elif k == pygame.K_UP:
                    self.speed = min(MAX_SPEED, self.speed + 0.2)
                elif k == pygame.K_DOWN:
                    self.speed = max(MIN_SPEED, self.speed - 0.2)
                elif k == pygame.K_p:
                    self.paused = not self.paused
                elif k == pygame.K_s:
                    self.want_screenshot = True
                elif k == pygame.K_h:
                    self.show_hud = not self.show_hud
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.get_surface()   # pygame 2 resizes the window itself
                self.rebuild_grid()
        return True

    # --- Main loop ------------------------------------------------------------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.fps) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.render_field(pygame.mouse.get_pos())
            self.draw()
        pygame.quit()


def main():
    ap = argparse.ArgumentParser(description="Interactive evolving fluid visualizer")
    ap.add_argument("--mode", type=int, choices=range(1, len(MODES) + 1), metavar=f"1-{len(MODES)}",
                    help="start in a specific mode (disables auto)")
    ap.add_argument("--no-auto", action="store_true", help="don't follow the time of day")
    ap.add_argument("--hour", type=int, choices=range(24), metavar="0-23",
                    help="pretend it is this hour (to preview time-of-day moods)")
    ap.add_argument("--scale", type=int, default=2, help="render downscale factor (higher = faster)")
    ap.add_argument("--fps", type=int, default=60)
    a = ap.parse_args()
    Visualizer(a.scale, a.fps, a.mode - 1 if a.mode else None, not a.no_auto, a.hour).run()
    sys.exit()


if __name__ == "__main__":
    main()
