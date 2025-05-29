# environment.py

from cmu_graphics import *
from PIL import Image as PILImage
import math

class Environment:
    """
    Handles environmental elements and helper drawing functions.
    """
    
    def openImage(fileName):
        """
        Opens an image file using PIL and returns the CMUImage object.
        Adjusted to avoid using __file__.
        """
        try:
            # Attempt to open the image file directly
            pilImage = PILImage.open(fileName)
            return CMUImage(pilImage)
        except FileNotFoundError:
            # If the file is not found, provide an error message
            print(f"Error: The image file '{fileName}' was not found.")
            print("Please ensure that the image is in the same directory as the script.")
            return None
    
    def drawTriangle(x1, y1, x2, y2, x3, y3, **kwargs):
        """
        Helper function to draw a triangle using drawPolygon.
        """
        drawPolygon(x1, y1, x2, y2, x3, y3, **kwargs)
        
    def drawHeart(xCenter, yCenter, size, fillColor):
        """
        Draws a heart shape at the specified location.
        """
        points = []
        for angle in range(0, 360, 10):
            angleRad = math.radians(angle)
            x = xCenter + size * 16 * math.sin(angleRad)**3
            y = yCenter - size * (13 * math.cos(angleRad) - 5 *\
                                   math.cos(2 * angleRad) - \
                                   2 * math.cos(3 * angleRad)\
                                   - math.cos(4 * angleRad))
            points.append((x, y))
        flatPoints = [coord for point in points for coord in point]
        drawPolygon(*flatPoints, fill=fillColor)
    
    def drawFish(x, y, size, fillColor):
        """
        Draws a fish at the specified location.
        """
        # Body
        drawOval(x, y, size * 2, size, fill=fillColor)
        # Tail
        drawPolygon(
            x - size, y,
            x - size * 1.5, y - size / 2,
            x - size * 1.5, y + size / 2,
            fill=fillColor
        )
        # Eye
        drawCircle(x + size / 2, y - size / 4, size / 8, fill="white")
        drawCircle(x + size / 2, y - size / 4, size / 16, fill="black")
    
    def drawPowerIcon(x, y, powerType):
        """
        Draws a realistic icon for the given power-up.
        """
        if powerType == 'doubleJump':
            # Draw wings for double jump
            drawArc(x - 10, y, 20, 20, 0, 180, fill='white', border='gray')
            drawArc(x + 10, y, 20, 20, 0, 180, fill='white', border='gray')
            drawLabel('2x', x, y + 5, size=10, fill='black')
        elif powerType == 'magnet':
            # Draw a magnet shape
            drawRect(x - 10, y - 10, 20, 20, fill='red')
            drawRect(x - 10, y - 10, 10, 20, fill='blue')
            drawCircle(x - 10, y - 10, 10, fill='blue')
            drawCircle(x + 10, y - 10, 10, fill='red')
        elif powerType == 'shield':
            # Draw a shield
            drawPolygon(
                x, y - 15,
                x - 12, y,
                x, y + 15,
                x + 12, y,
                fill='lightblue', border='blue', borderWidth=2
            )