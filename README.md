![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/pygame-2.0%2B-green?logo=pygame&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-required-013243?logo=numpy&logoColor=white)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-yellow)
<img width="1366" height="677" alt="fluid_neon_classic_1792192738" src="https://github.com/user-attachments/assets/2e2f5e54-e494-45e9-aea5-95cb0da2bb10" />
<img width="1366" height="677" alt="fluid_aurora_night_1792192687" src="https://github.com/user-attachments/assets/99b800ba-6381-4431-8af5-03da2aabd5fc" />


This is a multi-mode interactive visualizer built with Python, Pygame, and NumPy. It generates fluid trigonometric interference patterns that evolve continuously. Each mode features a unique flow pattern, color palette, and pace. In AUTO mode, the visualizer synchronizes with your system clock and smoothly crossfades between moods:
<img width="1366" height="677" alt="fluid_sunset_1792192719" src="https://github.com/user-attachments/assets/73536401-7b90-4c1c-aa09-70d89f83343b" />
<img width="1366" height="677" alt="fluid_ocean_1792192699" src="https://github.com/user-attachments/assets/b14f6474-5bed-4f9c-aebd-f3061d0e0e73" />



Sunrise from 05:00 to 08:00

Daylight from 08:00 to 17:00

Sunset from 17:00 to 20:00

Aurora Night from 20:00 to 05:00

Requirements

Python 3

pygame version 2.0 or higher

numpy

bash installation/run
git clone https://github.com/wifiknight45/fluid_motion.git
cd fluid_motion
pip install -r requirements.txt
python3 visualizer.py


Command Line Options

mode: Start in a specific mode and disable auto mode

no auto: Disable time-of-day synchronization

hour: Preview a specific hour from 0 to 23

scale: Render downscale factor for performance adjustment

fps: Target frame rate

Controls

RIGHT, LEFT, or SPACE: Switch to the next, previous, or next mode

Keys 1 through 7: Jump directly to a specific mode and turn auto mode off

A key: toggle AUTO time-of-day mode

UP or DOWN: speed up or slow down the animation pace

P key: pause or resume the simulation

S key: Save a PNG screenshot of the current frame

H key: Toggle the heads-up display overlay

ESC key: Quit the application

Mouse movement: Create interactive wave ripples across the screen
