![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/pygame-2.0%2B-green?logo=pygame&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-required-013243?logo=numpy&logoColor=white)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-yellow)


This is a multi-mode interactive visualizer built with Python, Pygame, and NumPy. It generates fluid trigonometric interference patterns that evolve continuously. Each mode features a unique flow pattern, color palette, and pace. In AUTO mode, the visualizer synchronizes with your system clock and smoothly crossfades between moods:

Sunrise from 05:00 to 08:00

Daylight from 08:00 to 17:00

Sunset from 17:00 to 20:00

Aurora Night from 20:00 to 05:00

Requirements

Python 3

pygame version 2.0 or higher

numpy

Installation and Running
Install dependencies:
pip install pygame numpy

Run the script:
python fluid_visualizer.py

Command Line Options

mode: Start in a specific mode and disable auto mode

no auto: Disable time-of-day synchronization

hour: Preview a specific hour from 0 to 23

scale: Render downscale factor for performance adjustment

fps: Target frame rate

Controls

RIGHT, LEFT, or SPACE: Switch to the next, previous, or next mode

Keys 1 through 7: Jump directly to a specific mode and turn auto mode off

A key: Toggle AUTO time-of-day mode

UP or DOWN: Speed up or slow down the animation pace

P key: Pause or resume the simulation

S key: Save a PNG screenshot of the current frame

H key: Toggle the heads-up display overlay

ESC key: Quit the application

Mouse movement: Create interactive wave ripples across the screen
