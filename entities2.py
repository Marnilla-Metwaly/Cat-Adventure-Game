# entities.py

from cmu_graphics import *
import math
import random
from environment import Environment  # Import the Environment class

class Sprite:
    """
    Base class for all moving objects in the game.
    Handles basic physics and collision detection.
    """
    def __init__(self, x, y, color="black"):
        self.radius = 25  # Radius for collision detection
        self.x = x  # Horizontal position
        self.y = y - self.radius  # Vertical position
        self.dx = 0  # Horizontal velocity
        self.dy = 0  # Vertical velocity
        self.gravity = 1  # Gravity acceleration
        self.color = color  # Color for drawing
        self.onGround = False  # Whether the sprite is on the ground

    def draw(self, app):
        # Placeholder for drawing; to be overridden by subclasses
        pass

    def onStep(self, app):
        """
        Updates the sprite's position and handles collisions.
        """
        # Apply gravity to vertical velocity
        self.dy += self.gravity
        # Update position based on velocities
        self.x += self.dx
        self.y += self.dy

        # Check for collision with the ground
        if self.y + self.radius >= app.groundHeight:
            # Check if the sprite is over a hole
            overHole = False
            for hole in app.holes:
                if hole.x <= self.x <= hole.x + hole.width:
                    overHole = True
                    break
            if not overHole:
                self.y = app.groundHeight - self.radius
                self.dy = 0
                self.onGround = True
            else:
                self.onGround = False
        else:
            self.onGround = False

        # Check for collision with platforms from above and below
        for platform in app.platforms:
            if (self.x + self.radius > platform.x and
                self.x - self.radius < platform.x + platform.width):
                if (self.y + self.radius >= platform.y and
                    self.y + self.radius - self.dy <= platform.y and
                    self.dy >= 0):
                    # Collision from above
                    self.y = platform.y - self.radius
                    self.dy = 0
                    self.onGround = True
                elif (self.y - self.radius <= platform.y + platform.height and
                      self.y - self.radius - self.dy >= platform.y + platform.height and
                      self.dy < 0):
                    # Collision from below
                    self.y = platform.y + platform.height + self.radius
                    self.dy = 0  # Stop vertical movement


    def checkCollision(self, other):
        """
        Checks if this sprite collides with another sprite.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        distanceSq = dx * dx + dy * dy
        # Collision occurs if the distance between centers is less than sum of radii
        return distanceSq <= (self.radius + other.radius) ** 2

    def getAngle(self, other):
        """
        Returns the angle between this sprite and another sprite.
        """
        return math.degrees(math.atan2(other.y - self.y, other.x - self.x))


class Hero(Sprite):
    """
    Represents the player's character.
    """
    def __init__(self, x, y, images=None):
        super().__init__(x, y, color="gray")
        self.speed = 6  # Movement speed
        self.jumpStrength = -15  # Jump velocity
        self.lives = 3  # Number of lives
        self.score = 0  # Player's score
        self.images = images  # List of images for animation
        self.currentImageIndex = 0  # For animation frames
        self.stepsPerImage = 5  # Controls animation speed
        self.stepsSinceLastImage = 0  # Counts steps for animation
        # Power-up attributes
        self.doubleJumpCount = 0  # Number of double jumps available
        self.magnetActive = False
        self.shieldActive = False
        self.shieldTimer = 0  # Timer for shield duration (in frames)
        self.magnetTimer = 0  # Timer for magnet duration (in frames)
        self.powerUpTimers = {}  # Dictionary to hold power-up timers

    def draw(self, app):
        x = self.x - app.cameraX
        y = self.y

        if self.images:
            # Draw the current image
            currentImage = self.images[self.currentImageIndex]
            drawImage(currentImage, x - self.radius, y - self.radius,
                      width=self.radius*2, height=self.radius*2)
        else:
            # Draw the head (face)
            drawCircle(x, y, self.radius,
                       fill="lightGray", border="darkGray", borderWidth=2)

            # Draw the ears
            earSize = self.radius / 2
            # Left ear coordinates
            leftEar = [
                (x - self.radius / 2, y - self.radius / 1.5),
                (x - self.radius / 1.2, y - self.radius * 1.2),
                (x - self.radius / 5, y - self.radius / 1.2)
            ]
            # Flatten the list of tuples into a list of coordinates
            leftEarCoords = [coord for point in leftEar for coord in point]
            # Draw left ear
            drawPolygon(*leftEarCoords, fill="lightGray",
                        border="darkGray", borderWidth=2)
            # Inner left ear coordinates
            innerLeftEar = [
                (x - self.radius / 2 + 4, y - self.radius / 1.5 + 4),
                (x - self.radius / 1.2 + 4, y - self.radius * 1.2 + 8),
                (x - self.radius / 5 - 2, y - self.radius / 1.2 + 4)
            ]
            innerLeftEarCoords = [coord for point in innerLeftEar\
                                  for coord in point]
            # Draw inner left ear
            drawPolygon(*innerLeftEarCoords, fill="pink")

            # Right ear coordinates
            rightEar = [
                (x + self.radius / 2, y - self.radius / 1.5),
                (x + self.radius / 1.2, y - self.radius * 1.2),
                (x + self.radius / 5, y - self.radius / 1.2)
            ]
            rightEarCoords = [coord for point in rightEar for coord in point]
            # Draw right ear
            drawPolygon(*rightEarCoords, fill="lightGray",
                        border="darkGray", borderWidth=2)
            # Inner right ear coordinates
            innerRightEar = [
                (x + self.radius / 2 - 4, y - self.radius / 1.5 + 4),
                (x + self.radius / 1.2 - 4, y - self.radius * 1.2 + 8),
                (x + self.radius / 5 + 2, y - self.radius / 1.2 + 4)
            ]
            innerRightEarCoords = [coord for point in innerRightEar\
                                   for coord in point]
            # Draw inner right ear
            drawPolygon(*innerRightEarCoords, fill="pink")

            # Draw the eyes
            eyeOffsetX = self.radius / 3
            eyeOffsetY = self.radius / 4
            eyeRadius = self.radius / 4
            # Left eye
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius,
                       fill="white")
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")
            # Right eye
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius,
                       fill="white")
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")

            # Draw the nose
            noseY = y
            noseSize = self.radius / 6
            drawCircle(x, noseY, noseSize, fill="pink", border="black")

            # Draw the mouth
            mouthWidth = self.radius / 2
            mouthHeight = self.radius / 6
            drawArc(x, y + self.radius / 4,
                    mouthWidth, mouthHeight,
                    200, 140, border="black")

            # Draw whiskers
            whiskerLength = self.radius
            whiskerY = noseY + self.radius / 8
            # Left whiskers
            drawLine(x - noseSize, whiskerY, x - whiskerLength, whiskerY - 5,
                     lineWidth=1, fill="black")
            drawLine(x - noseSize, whiskerY + 2.5, x - whiskerLength, whiskerY + 4,
                     lineWidth=1, fill="black")
            drawLine(x - noseSize, whiskerY + 5, x - whiskerLength, whiskerY + 10,
                     lineWidth=1, fill="black")
            # Right whiskers
            drawLine(x + noseSize, whiskerY, x + whiskerLength, whiskerY - 5,
                     lineWidth=1, fill="black")
            drawLine(x + noseSize, whiskerY + 2.5, x + whiskerLength, whiskerY + 4,
                     lineWidth=1, fill="black")
            drawLine(x + noseSize, whiskerY + 5, x + whiskerLength, whiskerY + 10,
                     lineWidth=1, fill="black")

            # Draw shield if active
            if self.shieldActive:
                drawCircle(x, y, self.radius + 5, fill=None,
                           border="blue", borderWidth=3)

    def updateAnimation(self):
        """
        Updates the hero's animation frame based on movement.
        """
        if self.images:
            self.stepsSinceLastImage += 1
            if self.stepsSinceLastImage >= self.stepsPerImage:
                self.currentImageIndex = (self.currentImageIndex + 1) % len(self.images)
                self.stepsSinceLastImage = 0
        else:
            if self.dx != 0 or not self.onGround:
                self.stepsSinceLastImage += 1
                if self.stepsSinceLastImage >= self.stepsPerImage:
                    # Toggle between 2 frames for walking animation
                    self.currentImageIndex = (self.currentImageIndex + 1) % 2
                    self.stepsSinceLastImage = 0
            else:
                # Reset to standing frame when not moving
                self.currentImageIndex = 0

    def onStep(self, app):
        # Update position and check collisions
        super().onStep(app)
        # Update animation frame
        self.updateAnimation()
        # Handle shield duration
        if self.shieldActive:
            self.shieldTimer -= 1
            self.powerUpTimers['Shield'] = self.shieldTimer // app.stepsPerSecond
            if self.shieldTimer <= 0:
                self.shieldActive = False
                self.powerUpTimers.pop('Shield', None)
        # Handle magnet duration
        if self.magnetActive:
            self.magnetTimer -= 1
            self.powerUpTimers['Magnet'] = self.magnetTimer // app.stepsPerSecond
            if self.magnetTimer <= 0:
                self.magnetActive = False
                self.powerUpTimers.pop('Magnet', None)

    def activateDoubleJump(self):
        """
        Increases the double jump count.
        """
        self.doubleJumpCount += 1

    def activateMagnet(self, app, duration=300):
        """
        Activates magnet ability.
        """
        self.magnetActive = True
        self.magnetTimer = duration
        self.powerUpTimers['Magnet'] = duration // app.stepsPerSecond

    def activateShield(self, app, duration=300):
        """
        Activates shield ability.
        """
        self.shieldActive = True
        self.shieldTimer = duration
        self.powerUpTimers['Shield'] = duration // app.stepsPerSecond


class Enemy(Sprite):
    """
    Base class for enemy sprites.
    """
    def __init__(self, x, y, app, color="brown"):
        super().__init__(x, y, color)
        self.dx = -2  # Moves left by default
        # Enemy lifetime in frames (random between 10s and 25s)
        self.lifeTimer = random.randint(25 * app.stepsPerSecond,
                                        35 * app.stepsPerSecond)

    def draw(self, app):
        # Placeholder for drawing; to be overridden by subclasses
        pass

    def onStep(self, app):
        """
        Updates the enemy's position and handles lifetime.
        """
        # Decrease life timer
        self.lifeTimer -= 1
        if self.lifeTimer <= 0:
            # Remove enemy from the game when time is up
            if self in app.enemies:
                app.enemies.remove(self)
            return  # Skip further updates for this enemy
        # Apply gravity and movement
        super().onStep(app)


class Walker(Enemy):
    """
    Enemy that walks horizontally and reverses direction at boundaries.
    """
    def __init__(self, x, y, app, color="sienna", images=None):
        super().__init__(x, y, app, color)
        self.images = images  # List of images for animation
        self.currentImageIndex = 0  # For animation frames
        self.stepsPerImage = 8  # Controls animation speed
        self.stepsSinceLastImage = 0  # Counts steps for animation

    def draw(self, app):
        x = self.x - app.cameraX
        y = self.y

        if self.images:
            # Draw the current image
            currentImage = self.images[self.currentImageIndex]
            drawImage(currentImage, x - self.radius, y - self.radius,
                      width=self.radius*2, height=self.radius*2)
        else :

            # Draw the dog's head
            drawCircle(x, y, self.radius, fill="sienna",
                       border="black", borderWidth=2)

            # Draw the floppy ears
            earWidth = self.radius / 1.5
            earHeight = self.radius 
            earOffsetX = self.radius / 1.5
            earOffsetY = self.radius / 1.5  # Increased to position ears higher

            # Left ear
            drawOval(x - earOffsetX, y - earOffsetY + self.radius / 10,  
                     earWidth, earHeight,fill="peru", border="black",
                     borderWidth=1, rotateAngle=45)
        
            # Right ear
            drawOval(x + earOffsetX, y - earOffsetY + self.radius / 10,  
                     earWidth, earHeight, fill="peru", border="black",
                     borderWidth=1, rotateAngle=-45)

            # Draw the eyes
            eyeOffsetX = self.radius / 4
            eyeOffsetY = self.radius / 4
            eyeRadius = self.radius / 5
            # Left eye
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius, fill="white")
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")
            # Right eye
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius, fill="white")
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")

            # Draw the nose
            noseY = y + self.radius / 6
            noseSize = self.radius / 6
            drawOval(x, noseY, noseSize, noseSize / 2, fill="black")

            # Draw the mouth
            mouthWidth = self.radius / 2
            mouthHeight = self.radius / 8
            drawArc(x, y + self.radius / 2,
                    mouthWidth, mouthHeight,
                    200, 140, border="black")

    
    def updateAnimation(self):
        """
        Updates the hero's animation frame based on movement.
        """
        if self.images:
            self.stepsSinceLastImage += 1
            if self.stepsSinceLastImage >= self.stepsPerImage:
                self.currentImageIndex = (self.currentImageIndex + 1) % len(self.images)
                self.stepsSinceLastImage = 0
        else:
            if self.dx != 0 or not self.onGround:
                self.stepsSinceLastImage += 1
                if self.stepsSinceLastImage >= self.stepsPerImage:
                    # Toggle between 2 frames for walking animation
                    self.currentImageIndex = (self.currentImageIndex + 1) % 2
                    self.stepsSinceLastImage = 0
            else:
                # Reset to standing frame when not moving
                self.currentImageIndex = 0

    def onStep(self, app):
        # Move horizontally
        self.x += self.dx

        # Reverse direction upon reaching world boundaries or holes
        if (self.x - self.radius <= 0 or
            self.x + self.radius >= app.worldWidth or
            self.checkForHole(app)):
            self.dx *= -1

        # Update position and handle lifetime
        super().onStep(app)
        self.updateAnimation()

    def checkForHole(self, app):
        """
        Checks if the enemy is about to walk into a hole.
        """
        nextX = self.x + self.dx
        for hole in app.holes:
            if (hole.x <= nextX <= hole.x + hole.width and
                self.y + self.radius >= app.groundHeight - 1):
                return True
        return False


class Chaser(Enemy):
    """
    Enemy that chases the hero when in range.
    """
    def __init__(self, x, y, app, color="darkred", images=None):
        super().__init__(x, y, app, color)
        self.speed = 2
        self.chaseRange = 300  # Distance at which the enemy starts chasing
        self.images = images  # List of images for animation
        self.currentImageIndex = 0  # For animation frames
        self.stepsPerImage = 8  # Controls animation speed
        self.stepsSinceLastImage = 0  # Counts steps for animation

    def draw(self, app):
        x = self.x - app.cameraX  # Adjust for camera offset
        y = self.y
        if self.images:
            # Draw the current image
            currentImage = self.images[self.currentImageIndex]
            drawImage(currentImage, x - self.radius, y - self.radius,
                      width=self.radius*4, height=self.radius*4)
        else : 
        # Draw the enemy as a wolf
            drawCircle(x, y, self.radius, fill="peru",
                       border="black", borderWidth=2)

            # Draw the floppy ears
            earWidth = self.radius / 1.5
            earHeight = self.radius 
            earOffsetX = self.radius / 1.5
            earOffsetY = self.radius / 1.5  # Increased to position ears higher

            # Left ear
            drawOval(x - earOffsetX, y - earOffsetY + self.radius / 10,  
                     earWidth, earHeight,fill="peru", border="black",
                     borderWidth=1, rotateAngle=45)
        
            # Right ear
            drawOval(x + earOffsetX, y - earOffsetY + self.radius / 10,  
                     earWidth, earHeight, fill="peru", border="black",
                     borderWidth=1, rotateAngle=-45)

            # Draw the eyes
            eyeOffsetX = self.radius / 4
            eyeOffsetY = self.radius / 4
            eyeRadius = self.radius / 5
            # Left eye
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius, fill="white")
            drawCircle(x - eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")
            # Right eye
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius, fill="white")
            drawCircle(x + eyeOffsetX, y - eyeOffsetY, eyeRadius / 2, fill="black")

            # Draw the nose
            noseY = y + self.radius / 6
            noseSize = self.radius / 6
            drawOval(x, noseY, noseSize, noseSize / 2, fill="black")

            # Draw the mouth
            mouthWidth = self.radius / 2
            mouthHeight = self.radius / 8
            drawArc(x, y + self.radius / 2,
                    mouthWidth, mouthHeight,
                    200, 140, border="black")
            
    def updateAnimation(self):
        """
        Updates the hero's animation frame based on movement.
        """
        if self.images:
            self.stepsSinceLastImage += 1
            if self.stepsSinceLastImage >= self.stepsPerImage:
                self.currentImageIndex = (self.currentImageIndex + 1) % len(self.images)
                self.stepsSinceLastImage = 0
        else:
            if self.dx != 0 or not self.onGround:
                self.stepsSinceLastImage += 1
                if self.stepsSinceLastImage >= self.stepsPerImage:
                    # Toggle between 2 frames for walking animation
                    self.currentImageIndex = (self.currentImageIndex + 1) % 2
                    self.stepsSinceLastImage = 0
            else:
                # Reset to standing frame when not moving
                self.currentImageIndex = 0
                
    def onStep(self, app):
        # Check distance to hero
        distance = math.hypot(self.x - app.hero.x, self.y - app.hero.y)
        if distance <= self.chaseRange:
            # Move towards the hero
            if self.x < app.hero.x:
                self.dx = self.speed
            else:
                self.dx = -self.speed
        else:
            self.dx = 0  # Stop moving if out of range

        self.x += self.dx

        # Update position and handle lifetime
        super().onStep(app)
        self.updateAnimation()

class Cloud:
    """
    Represents a cloud in the background.
    """
    def __init__(self, x, y, size=50, color="white"):
        self.x = x  # Horizontal position
        self.y = y  # Vertical position
        self.size = size  # Size of the cloud
        self.color = color  # Color for drawing

    def draw(self, app):
        # Only draw clouds within the current viewport
        if (self.x + self.size >= app.cameraX - 200 and
            self.x - self.size <= app.cameraX + app.width + 200):
            # Draw simple cloud using multiple overlapping ovals
            drawOval(
                self.x - app.cameraX, self.y,
                self.size, self.size / 2,
                fill=self.color, opacity=80
            )
            drawOval(
                self.x + self.size * 0.3 - app.cameraX,
                self.y - self.size * 0.2,
                self.size * 0.8, self.size * 0.4,
                fill=self.color, opacity=80
            )
            drawOval(
                self.x - self.size * 0.3 - app.cameraX,
                self.y - self.size * 0.2,
                self.size * 0.8, self.size * 0.4,
                fill=self.color, opacity=80
            )


class Platform:
    """
    Represents a platform that the hero can stand on.
    """
    def __init__(self, x, y, width, height, color="brown", moving=False):
        self.x = x  # Horizontal position
        self.y = y  # Vertical position
        self.width = width  # Platform width
        self.height = height  # Platform height
        self.color = color  # Color for drawing
        self.moving = moving  # Whether the platform moves
        self.direction = 1  # Direction of movement (1 or -1)
        self.range = 100  # Movement range
        self.startX = x  # Starting x position

    def draw(self, app):
        # Only draw platforms within the current viewport for efficiency
        if (self.x + self.width >= app.cameraX - 100 and
            self.x <= app.cameraX + app.width + 100):
            drawRect(self.x - app.cameraX, self.y,
                     self.width, self.height, fill=self.color)

    def onStep(self, app):
        """
        Updates the platform's position if it is moving.
        """
        if self.moving:
            self.x += self.direction * 2  # Speed of movement
            if abs(self.x - self.startX) >= self.range:
                self.direction *= -1  # Reverse direction


class Hole:
    """
    Represents a hole in the ground.
    """
    def __init__(self, x, width):
        self.x = x  # Horizontal position
        self.width = width  # Width of the hole

    def draw(self, app, color = 'black'):
        # Only draw holes within the current viewport
        if (self.x + self.width >= app.cameraX - 100 and
            self.x <= app.cameraX + app.width + 100):
            nextColor= 'skyBlue' if color == 'blue' else 'maroon'
            drawRect(self.x - app.cameraX, app.groundHeight,
                     self.width, app.height - app.groundHeight,
                     fill=gradient(color, nextColor, 'white', start='bottom'))


class PowerUp:
    """
    Represents a power-up item.
    """
    def __init__(self, x, y, powerType):
        self.radius = 15
        self.x = x
        self.y = y - self.radius
        self.collected = False
        self.powerType = powerType  # 'doubleJump', 'magnet', 'shield'

    def draw(self, app):
        if not self.collected:
            # Only draw power-ups within the current viewport
            if (self.x + self.radius >= app.cameraX - 100 and
                self.x - self.radius <= app.cameraX + app.width + 100):
                x = self.x - app.cameraX
                y = self.y
                Environment.drawPowerIcon(x, y, self.powerType)

    def checkCollection(self, hero, app):
        """
        Checks if the hero has collected this power-up.
        """
        if self.checkCollisionWith(hero):
            self.collected = True
            if self.powerType == 'doubleJump':
                hero.activateDoubleJump()
            elif self.powerType == 'magnet':
                hero.activateMagnet(app)
            elif self.powerType == 'shield':
                hero.activateShield(app)
            return True
        return False

    def checkCollisionWith(self, hero):
        """
        Checks collision with the hero.
        """
        dx = self.x - hero.x
        dy = self.y - hero.y
        distanceSq = dx * dx + dy * dy
        return distanceSq <= (self.radius + hero.radius) ** 2


class Collectible:
    """
    Represents a collectible item (fish) that the hero can collect.
    """
    def __init__(self, x, y, color="orange"):
        self.radius = 10  # Size of the collectible
        self.x = x  # Horizontal position
        self.y = y - self.radius  # Vertical position
        self.collected = False
        self.color = color  # Color for drawing

    def draw(self, app):
        if not self.collected:
            # Only draw collectibles within the current viewport
            if (self.x + self.radius >= app.cameraX - 100 and
                self.x - self.radius <= app.cameraX + app.width + 100):
                x = self.x - app.cameraX
                y = self.y
                Environment.drawFish(x, y, self.radius, self.color)

    def checkCollection(self, hero):
        """
        Checks if the hero has collected this item.
        """
        if self.checkCollisionWith(hero):
            self.collected = True
            return True
        return False

    def checkCollisionWith(self, hero):
        """
        Checks collision with the hero.
        """
        dx = self.x - hero.x
        dy = self.y - hero.y
        distanceSq = dx * dx + dy * dy
        return distanceSq <= (self.radius + hero.radius) ** 2

    def moveTowardsHero(self, hero):
        """
        Moves the collectible towards the hero if magnet is active.
        """
        if hero.magnetActive:
            dx = hero.x - self.x
            dy = hero.y - self.y
            distance = math.hypot(dx, dy)
            if distance < 250:  # Attraction range
                self.x += dx / distance * 10  # Speed towards hero
                self.y += dy / distance * 10