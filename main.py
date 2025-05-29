# main.py

from cmu_graphics import *
from game2 import Game
import math

# Initialize the game instance
game = Game()

def onAppStart(app):
    game.width = app.width
    game.height = app.height
    game.onAppStart()

def onMousePress(app, x, y):
    game.onMousePress(x, y)

def onKeyHold(app, keys):
    game.onKeyHold(keys)

def onKeyPress(app, key):
    game.onKeyPress(key)

def onStep(app):
    game.onStep()

def redrawAll(app):
    game.redrawAll()

# Running the App
runApp(width=800, height=600)
