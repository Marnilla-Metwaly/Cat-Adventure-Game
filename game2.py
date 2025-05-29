# game.py

from cmu_graphics import *
from environment import Environment
from entities2 import *
import random
import math  

class Game:
    """
    Manages the overall game state, initialization, event handling, and the game loop.
    """
    def __init__(self):
        # Initialize game parameters
        self.stepsPerSecond = 30  # Game updates per second
        self.levelNumber = 1      # Starting level
        self.paused = False       # Game paused state
        self.difficulty = None    # Difficulty level
        self.mode = 'startScreen' # Start with the start screen
        self.cameraX = 0          # Initialize camera offset
        self.groundHeight = 0     # Will be set in reset
        self.pauseButton = {}
        self.exitButton = {}
        self.startScreenImage = None
        self.availableCharacters = ['Super Cat', 'Animation Cat']
        self.currentCharacterIndex = 0
        self.characterImages = {}
        self.heroImages = {}
        self.startScreenStage = 'characterSelection'
        self.startScreenImages = []
        self.currentStartScreenImageIndex = 0
        self.startScreenImageCounter = 0
        self.startScreenImageDelay = 10  # Steps before changing image
        self.easyButton = {}
        self.hardButton = {}
        self.superButton = {}
        self.animationButton = {}
        self.selectedHeroImages = None
        self.selectedCharacter = None    # Tracks the chosen character
        self.enemyImages = {}
        self.enemyImagesLoaded = {}
        self.selectedEnemyImages = None
        self.sounds = {}
        self.gameOverSoundPlayed = False  # Tracks if game over sound has been played

    def onAppStart(self):
        """
        Initializes the game when the app starts.
        """
        # Define pause button dimensions and position
        self.pauseButton = {
            'x': self.width - 50,
            'y': 30,
            'width': 30,
            'height': 30
        }
        # Define exit button dimensions and position
        self.exitButton = {
            'x': self.pauseButton['x'],
            'y': self.pauseButton['y'] + self.pauseButton['height'] + 10,
            'width': self.pauseButton['width'],
            'height': self.pauseButton['height']
        }

        # Load the start screen image
        # Created using Canva
        self.startScreenImage = Environment.openImage('starting.png')
        if self.startScreenImage is None:
            print("Error: The image file 'starting.png' was not found.")

        # Initialize character selection
        self.availableCharacters = ['Super Cat', 'Animation Cat']
        # Images from vecteezy
        self.characterImages = {
            'Super Cat': ['cat2.png', 'cat3.png'],
            'Animation Cat': []  # No images for Animation Cat; handled programmatically
        }
        # Load images for 'Super Cat'
        for character in self.characterImages:
            images = []
            for imageFile in self.characterImages[character]:
                img = Environment.openImage(imageFile)
                if img:
                    images.append(img)
                else:
                    print(f"Error: The image file '{imageFile}' was not found.")
            self.heroImages[character] = images
        
        self.availableEnemies = ['Walker', 'Chaser']
        # Images from vecteezy
        self.enemiesImages = {
            'Walker': ['dog11.png', 'dog12.png', 'dog13.png'],
            'Chaser': ['dog01.png', 'dog02.png']
        }
        if self.currentCharacterIndex == 0:
            # Load images for Walker and Chaser enemies
            for enemyType in self.enemiesImages:
                images = []
                for imageFile in self.enemiesImages[enemyType]:
                    img = Environment.openImage(imageFile)
                    if img:
                        images.append(img)
                    else:
                        print(f"Error: The image file '{imageFile}' was not found.")
                self.enemyImages[enemyType] = images

        # All sounds downloaded from pixabay
        self.sounds = {
            'jump': Sound('jump.mp3'),
            'gameBackground': Sound('game-start.mp3'),
            'gameOver': Sound('game-over.mp3'),
            'superPower': Sound('game-bonus.mp3')
        }

        # Play background music on the start screen
        if 'gameBackground' in self.sounds and self.sounds['gameBackground']:
            self.sounds['gameBackground'].play(loop=True)
        
        # Set start screen stage to 'characterSelection'
        self.startScreenStage = 'characterSelection'

        # Load the start screen images for difficulty selection
        # Created them using Canva
        imageFiles = ['design.png']
        for imageFile in imageFiles:
            img = Environment.openImage(imageFile)
            if img:
                self.startScreenImages.append(img)
            else:
                print(f"Error: The image file '{imageFile}' was not found.")

        # Define Easy button
        self.easyButton = {
            'x': self.width / 2 - 100,  # Centered horizontally
            'y': self.height / 2 + 160,  # Positioned slightly below vertical center
            'width': 200,             # Button width
            'height': 50,             # Button height
            'label': 'Easy'           # Button label
        }

        # Define Hard button
        self.hardButton = {
            'x': self.width / 2 - 100,  # Centered horizontally
            'y': self.height / 2 + 210, # Positioned further below vertical center
            'width': 200,             # Button width
            'height': 50,             # Button height
            'label': 'Hard'           # Button label
        }
        # Load background images for each character
        self.backgroundImages = {
            'Super Cat': Environment.openImage('backgroundSuperCat.png'),
            # No background image for Animation Cat
        }
        # Check if background images loaded successfully
        for character, bgImage in self.backgroundImages.items():
            if bgImage is None:
                print(f"Error: The background image for '{character}' was not found.")

    def onMousePress(self, x, y):
        """
        Handles mouse click events.
        """
        if self.mode == 'startScreen':
            if self.startScreenStage == 'difficultySelection':
                # Check if Easy button is clicked
                btn = self.easyButton
                if btn['x'] <= x <= btn['x'] + btn['width'] and \
                   btn['y'] <= y <= btn['y'] + btn['height']:
                    self.difficulty = 'Easy'
                    self.startGame()
                    return
                # Check if Hard button is clicked
                btn = self.hardButton
                if btn['x'] <= x <= btn['x'] + btn['width'] and \
                   btn['y'] <= y <= btn['y'] + btn['height']:
                    self.difficulty = 'Hard'
                    self.startGame()
                    return
        elif self.mode == 'game':
            # Check if the pause button was clicked
            btn = self.pauseButton
            if (btn['x'] <= x <= btn['x'] + btn['width'] and
                btn['y'] <= y <= btn['y'] + btn['height']):
                self.paused = not self.paused  # Toggle pause state
                if self.paused:
                    # Pause background music if it's playing
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                        self.sounds['gameBackground'].pause()
                else:
                    # Resume background music
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].pause():
                        self.sounds['gameBackground'].play(loop=True)
            # Check if the exit button was clicked
            exitBtn = self.exitButton
            if (exitBtn['x'] <= x <= exitBtn['x'] + exitBtn['width'] and
                exitBtn['y'] <= y <= exitBtn['y'] + exitBtn['height']):
                # Go back to main menu (start screen)
                self.mode = 'startScreen'
                self.startScreenStage = 'characterSelection'  # Reset to character selection
                self.onAppStart()  # Re-initialize the app
                # Stop background music
                if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                    self.sounds['gameBackground'].pause()
                # Play starting sound (using the same background music)
                if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].pause():
                    self.sounds['gameBackground'].play(loop=True)

    def onKeyHold(self, keys):
        """
        Handles key hold events for continuous movement.
        """
        if self.mode == 'game':
            if not self.gameOver and not self.levelComplete and not self.paused:
                # Reset horizontal velocity each frame
                self.hero.dx = 0
                if "right" in keys:
                    self.hero.dx += self.hero.speed
                if "left" in keys:
                    self.hero.dx -= self.hero.speed

    def onKeyPress(self, key):
        """
        Handles key press events.
        """
        if key.lower() == 'e':
            self.mode = 'startScreen'
            self.startScreenStage = 'characterSelection'  # Reset to character selection
            self.onAppStart()  # Re-initialize the app
            # Stop background music and play starting sound
            if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                self.sounds['gameBackground'].pause()
            # Play starting sound (using the same background music)
            if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].pause():
                self.sounds['gameBackground'].play(loop=True)
                    
        if self.mode == 'startScreen':
            if self.startScreenStage == 'characterSelection':
                if key == 'left':
                    self.currentCharacterIndex = (self.currentCharacterIndex - 1) % len(self.availableCharacters)
                elif key == 'right':
                    self.currentCharacterIndex = (self.currentCharacterIndex + 1) % len(self.availableCharacters)
                elif key == 'enter' or key == 'space':
                    # User confirms character selection
                    self.selectedCharacter = self.availableCharacters[self.currentCharacterIndex]
                    self.selectedHeroImages = self.heroImages.get(self.selectedCharacter, [])
                    self.startScreenStage = 'difficultySelection'
            elif self.startScreenStage == 'difficultySelection':
                # Handle difficulty selection via keyboard
                if key == 'up':
                    self.difficulty = 'Easy'
                elif key == 'down':
                    self.difficulty = 'Hard'
                elif self.difficulty and (key == 'enter' or key == 'space'):
                    self.startGame()
        elif self.mode == 'game':
            if key.lower() == 'p':
                self.paused = not self.paused  # Toggle pause state
                if self.paused:
                    # Pause background music if it's playing
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                        self.sounds['gameBackground'].pause()
                else:
                    # Resume background music
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].pause():
                        self.sounds['gameBackground'].play(loop=True)
            elif not self.gameOver and not self.levelComplete and not self.paused:
                if key == 'up':
                    # Handle jumping logic
                    if self.hero.onGround:
                        self.hero.dy = self.hero.jumpStrength
                    elif self.hero.doubleJumpCount > 0:
                        self.hero.dy = self.hero.jumpStrength
                        self.hero.doubleJumpCount -= 1
                    # Play jump sound
                    if 'jump' in self.sounds and self.sounds['jump']:
                        self.sounds['jump'].play()
            elif self.gameOver:
                if key.lower() == "r":
                    self.levelNumber = 1
                    self.reset(level=self.levelNumber, resetScore=True)
                    # Stop game over sound
                    if 'gameOver' in self.sounds and self.sounds['gameOver'] and self.sounds['gameOver'].play():
                        self.sounds['gameOver'].pause()
                    # Play background music
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground']:
                        self.sounds['gameBackground'].play(loop=True)
            elif self.levelComplete:
                if key.lower() == "n":
                    self.levelNumber += 1
                    self.reset(level=self.levelNumber, resetScore=False)
                    # Ensure background music is playing
                    if 'gameBackground' in self.sounds and self.sounds['gameBackground']:
                        self.sounds['gameBackground'].play(loop=True)

    def startGame(self):
        """
        Starts the game after selecting difficulty.
        """
        self.mode = 'game'
        self.reset(level=self.levelNumber)
        if self.difficulty == 'Easy':
            # Adjust game parameters for easy difficulty
            self.hero.lives = 5
            self.spawnRate = 6  # Enemies spawn less frequently
        else:
            # Hard difficulty settings
            self.hero.lives = 3
            self.spawnRate = 4  # Enemies spawn more frequently

    def onStep(self):
        """
        Updates the game state each frame.
        """
        if self.mode == 'startScreen':
            # Alternate start screen images if any
            self.startScreenImageCounter += 1
            if self.startScreenImageCounter >= self.startScreenImageDelay:
                self.startScreenImageCounter = 0
                if self.startScreenImages:
                    self.currentStartScreenImageIndex = (self.currentStartScreenImageIndex + 1) % len(self.startScreenImages)
        if self.mode == 'game':
            if not self.gameOver and not self.levelComplete and not self.paused:
                self.blips += 1  # Increment timer for enemy spawning
                # Spawn enemies periodically
                if self.blips % (self.spawnRate * self.stepsPerSecond) == 0:
                    # Spawn Walker or Chaser based on logic
                    enemyX = self.cameraX + self.width - 100
                    if random.random() < 0.7:  # 70% chance to spawn Walker
                        if self.currentCharacterIndex == 0:
                            self.enemies.append(Walker(enemyX, self.groundHeight - 25, self, images=self.enemyImages.get('Walker', [])))
                        else:
                            self.enemies.append(Walker(enemyX, self.groundHeight - 25, self))
                    else:
                        if self.currentCharacterIndex == 0:
                            self.enemies.append(Chaser(enemyX, self.groundHeight - 25, self, images=self.enemyImages.get('Chaser', [])))
                        else:
                            self.enemies.append(Chaser(enemyX, self.groundHeight - 25, self))

                # Update enemies
                for enemy in self.enemies:
                        enemy.onStep(self)

                # Update Hero
                self.hero.onStep(self)

                # Update Camera Position to Follow Hero
                if (self.hero.x - self.cameraX > self.width * 2 / 3 and
                    self.cameraX + self.width < self.worldWidth):
                    self.cameraX += self.hero.speed
                elif (self.hero.x - self.cameraX < self.width / 3 and
                      self.cameraX > 0):
                    self.cameraX -= self.hero.speed

                # Clamp cameraX within world boundaries
                self.cameraX = max(0, min(self.cameraX, self.worldWidth - self.width))

                # Update Enemies
                for enemy in self.enemies[:]:
                    enemy.onStep(self)
                    if enemy.lifeTimer <= 0:
                        if enemy.x + enemy.radius*2 < self.cameraX - 100:
                            self.enemies.remove(enemy)  # Enemy has been removed

                    # Check for collision with the hero
                    if self.hero.checkCollision(enemy):
                        if self.hero.shieldActive:
                            # Shield absorbs the damage
                            self.enemies.remove(enemy)
                        elif self.hero.dy > 0:
                            # Hero defeats the enemy by jumping on top
                            self.enemies.remove(enemy)
                            self.hero.dy = self.hero.jumpStrength / 2  # Bounce back
                            self.hero.score += 50
                        else:
                            # Enemy defeats the hero
                            self.hero.lives -= 1
                            # Play game over sound if hero has no lives left
                            if self.hero.lives <= 0:
                                self.gameOver = True
                                if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                                    self.sounds['gameBackground'].pause()
                                if 'gameOver' in self.sounds and self.sounds['gameOver']:
                                    self.sounds['gameOver'].play()
                            else:
                                # Reset hero position
                                self.hero.x = self.width / 5
                                self.hero.y = self.groundHeight - self.hero.radius
                                self.cameraX = 0
                                self.enemies.clear()

                # Remove enemies that have moved off-screen to the left
                self.enemies = [enemy for enemy in self.enemies
                               if enemy.x + enemy.radius >= self.cameraX - 100]

                # Update Collectibles
                for collectible in self.collectibles[:]:
                    if not collectible.collected:
                        collectible.moveTowardsHero(self.hero)
                        if collectible.checkCollection(self.hero):
                            self.hero.score += 10
                            self.collectibles.remove(collectible)
                    elif collectible.x + collectible.radius < self.cameraX - 100:
                        # Remove collectibles that are off-screen to the left
                        self.collectibles.remove(collectible)

                # Update Power-Ups
                for powerUp in self.powerUps[:]:
                    if (not powerUp.collected and
                        powerUp.checkCollection(self.hero, self)):
                        self.powerUps.remove(powerUp)
                        # Play super power sound
                        if 'superPower' in self.sounds and self.sounds['superPower']:
                            self.sounds['superPower'].play()
                    elif powerUp.x + powerUp.radius < self.cameraX - 100:
                        # Remove power-ups that are off-screen to the left
                        self.powerUps.remove(powerUp)

                # Update Moving Platforms
                for platform in self.platforms:
                    platform.onStep(self)

                # Check if hero fell into a hole
                if self.hero.y - self.hero.radius > self.groundHeight:
                    self.hero.lives -= 1
                    # Play game over sound if hero has no lives left
                    if self.hero.lives <= 0:
                        self.gameOver = True
                        if 'gameBackground' in self.sounds and self.sounds['gameBackground'] and self.sounds['gameBackground'].play():
                            self.sounds['gameBackground'].pause()
                        if 'gameOver' in self.sounds and self.sounds['gameOver']:
                            self.sounds['gameOver'].play()
                    else:
                        # Reset hero position
                        self.hero.x = self.width / 5
                        self.hero.y = self.groundHeight - self.hero.radius
                        self.cameraX = 0
                        self.enemies.clear()

                # Check for Level Completion
                if self.hero.x >= self.worldWidth - self.width / 2:
                    self.levelComplete = True

                # Prevent Hero from moving out of bounds
                if self.hero.x - self.hero.radius < 0:
                    self.hero.x = self.hero.radius
                elif self.hero.x + self.hero.radius > self.worldWidth:
                    self.hero.x = self.worldWidth - self.hero.radius

    def generatePlatforms(self, x, level):
        """
        Recursively generates platforms with varying sizes and positions.
        """
        if x >= self.worldWidth:
            return
        # Randomize platform attributes
        width = random.randint(100, 250)
        height = 20
        y = random.randint(int(self.groundHeight * 0.5),
                           int(self.groundHeight * 0.8))
        self.platforms.append(Platform(x, y, width, height))
        # Recursive call with increased x position
        gap = random.randint(75, 100)
        self.generatePlatforms(x + width + gap, level)

    def generateMovingPlatforms(self, x, level):
        """
        Generates moving platforms.
        """
        for _ in range(5):  # Number of moving platforms
            width = random.randint(100, 150)
            height = 20
            y = random.randint(int(self.groundHeight * 0.3),
                               int(self.groundHeight * 0.6))
            movingPlatform = Platform(x, y, width, height, moving=True)
            self.platforms.append(movingPlatform)
            x += random.randint(500, 800)

    def generateHoles(self, x, level):
        """
        Generates holes in the ground.
        """
        while x < self.worldWidth:
            width = random.randint(80, 150)
            self.holes.append(Hole(x, width))
            x += width + random.randint(200, 500)

    def generateCollectibles(self, x, level):
        """
        Recursively generates collectibles on platforms.
        """
        if x >= self.worldWidth:
            return
        # Find a platform near the x position
        platform = next((p for p in self.platforms
                         if p.x <= x <= p.x + p.width), None)
        if platform:
            collectibleY = platform.y - 20
        else:
            collectibleY = random.randint(int(self.groundHeight * 0.3),
                                          int(self.groundHeight * 0.6))
        self.collectibles.append(Collectible(x, collectibleY, color="orange"))
        # Recursive call with increased x position
        gap = random.randint(0, 250)
        self.generateCollectibles(x + gap, level)

    def generatePowerUps(self, x, level):
        """
        Recursively generates power-ups on platforms.
        """
        if x >= self.worldWidth:
            return
        # Find a platform near the x position
        platform = next((p for p in self.platforms
                         if p.x <= x <= p.x + p.width), None)
        if platform:
            powerUpY = platform.y - 30
        else:
            powerUpY = random.randint(int(self.groundHeight * 0.1),
                                      int(self.groundHeight * 0.5))
        powerTypes = ['doubleJump', 'magnet', 'shield']
        powerType = random.choice(powerTypes)
        self.powerUps.append(PowerUp(x, powerUpY, powerType))
        # Recursive call with increased x position
        gap = random.randint(500, 1000)
        self.generatePowerUps(x + gap, level)

    def generateClouds(self, x, level):
        """
        Generates clouds in the background.
        """
        cloudGap = 800
        while x < self.worldWidth + self.width:
            y = random.randint(50, int(self.groundHeight * 0.3))
            size = random.randint(60, 120)
            self.clouds.append(Cloud(x, y, size=size))
            x += cloudGap

    def reset(self, level=1, resetScore=True):
        """
        Resets the game state for a new level or restart.
        """
        self.blips = 0  # Timer for spawning enemies
        self.groundHeight = 2 * self.height / 3  # Height of the ground
        self.bushRadius = 50  # Not used but can be for decorations

        # Increase world width with each level
        self.worldWidth = 4000 * (1.5 ** (level - 1))

        # Generate platforms recursively
        self.platforms = []
        self.generatePlatforms(x=100, level=level)

        # Generate moving platforms
        self.generateMovingPlatforms(x=500, level=level)

        # Generate holes in the ground (only in hard mode)
        self.holes = []
        if self.difficulty != 'Easy':
            self.generateHoles(x=300, level=level)

        # Generate collectibles recursively
        self.collectibles = []
        self.generateCollectibles(x=500, level=level)

        # Generate power-ups recursively
        self.powerUps = []
        self.generatePowerUps(x=700, level=level)

        # Generate clouds
        self.clouds = []
        self.generateClouds(x=800, level=level)

        self.cameraX = 0  # Reset camera offset

        # Initialize Hero
        if not hasattr(self, 'hero'):
            self.hero = Hero(self.width / 5, self.groundHeight, images=self.selectedHeroImages)
        else:
            self.hero.x = self.width / 5
            self.hero.y = self.groundHeight - self.hero.radius
            self.hero.dx = 0
            self.hero.dy = 0
            self.hero.onGround = False
            if resetScore:
                self.hero.score = 0
                self.hero.lives = 3
                self.hero.doubleJumpCount = 0
                self.hero.magnetActive = False
                self.hero.shieldActive = False
                self.hero.powerUpTimers.clear()
            self.hero.images = self.selectedHeroImages  # Update hero's images

        # Initialize Enemies
        self.enemies = []

        # Game State Flags
        self.gameOver = False
        self.levelComplete = False

        # Initialize flags
        self.gameOverSoundPlayed = False

        # Set Current Level
        self.currentLevel = level

    def drawAnimationCatBackground(self):
        """
        Draws a programmatically created background for Animation Cat.
        """
        # Draw blue sky
        drawRect(0, 0, self.width, self.height, fill="skyBlue")
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self)
        
        # Drawing a sun
        drawCircle(700, 100, 40, fill="yellow", opacity=90)
        
        # Draw trees
        drawRect(100, self.groundHeight - 100, 20, 100, fill="sienna")  # Tree trunk
        drawOval(110, self.groundHeight - 130, 60, 40, fill="forestGreen")  # Tree foliage
        
        # Draw pyramids
        Environment.drawTriangle(0, self.groundHeight, 200, self.groundHeight - 150, 400,
                                 self.groundHeight, fill=gradient('orange', 'peru', 'chocolate', start='top'))
        Environment.drawTriangle(300, self.groundHeight, 500, self.groundHeight - 200, 700,
                                 self.groundHeight, fill=gradient('darkOrange', 'peru', 'chocolate', start='top'))
        Environment.drawTriangle(600, self.groundHeight, 800, self.groundHeight - 250, 1000,
                                 self.groundHeight, fill=gradient('orangeRed', 'peru', 'chocolate', start='top'))
        
        # Draw ground
        drawRect(0 - self.cameraX, self.groundHeight,
                         self.worldWidth, self.height - self.groundHeight,
                         fill="saddlebrown")
        
        # Draw holes
        for hole in self.holes:
                hole.draw(self)

    def drawAnimationCatStartScreen(app):
        """
        Draws the start screen background for Animation Cat.
        """
        # Draw sky background
        drawRect(0, 0, app.width, app.height, fill="skyBlue")
        
        # Drawing a sun
        drawCircle(20, 20, 60, fill="yellow", opacity=90)
        
        # Draw trees
        drawRect(100, app.height, 20, 100, fill="sienna")  # Tree trunk
        drawOval(110, app.height, 60, 40, fill="forestGreen")  # Tree foliage
        
        # Draw pyramids
        Environment.drawTriangle(-100, app.height, 200, app.height - 140, 400,
                                 app.height, fill=gradient('orange', 'peru', 'chocolate', start='top'))
        Environment.drawTriangle(300, app.height, 500, app.height - 190, 700,
                                 app.height, fill=gradient('darkOrange', 'peru', 'chocolate', start='top'))
        Environment.drawTriangle(600, app.height, 800, app.height - 240, 1000,
                                 app.height, fill=gradient('orangeRed', 'peru', 'chocolate', start='top'))
        
        x = app.width // 4
        y = app.height // 3
        cloud1 = Cloud(x, y, size=70)
        cloud1.draw(app)
        cloud2 = Cloud(app.width // 2, app.height // 6, size=250)
        cloud2.draw(app)
        cloud3 = Cloud(x*4, y, size=100)
        cloud3.draw(app)
        cloud4 = Cloud(x*0.8, y* 2, size=90)
        cloud4.draw(app)

        # Draw the game title
        drawLabel("Adventures of Hero Cat", app.width / 2, 100,
                  size=50, fill="fireBrick", bold=True)

        # Draw the hero character in the center
        heroX = app.width / 2
        heroY = app.height / 2 + 50
        tempHero = Hero(heroX, heroY)
        tempHero.draw(app)

        # Draw the buttons
        # Easy Button
        drawRect(app.width / 2 - 100, app.height / 2 + 160, 200, 50,
                 fill="green")
        drawLabel("Easy", app.width / 2, app.height / 2 + 185,
                  size=20, fill='lemonChiffon', align='center', bold= True)
        # Hard Button
        drawRect(app.width / 2 - 100, app.height / 2 + 215, 200, 50,
                 fill="red")
        drawLabel("Hard", app.width / 2, app.height / 2 + 240,
                  size=20, fill='lemonChiffon', align='center', bold= True)

    def redrawAll(self):
        """
        Draws all game elements on the screen.
        """
        if self.mode == 'startScreen':
            if self.startScreenStage == 'characterSelection':
                # Draw starting.png as background
                if self.startScreenImage is not None:
                    drawImage(self.startScreenImage, 0, 0, width=self.width, height=self.height)
                else:
                    drawRect(0, 0, self.width, self.height, fill="black")
                # Draw the selected character's name
                characterName = self.availableCharacters[self.currentCharacterIndex]
                if characterName == 'Super Cat':
                    drawLine(self.width / 2 -75, self.height - 100, self.width / 2 +75,
                             self.height - 100, fill= 'gold', lineWidth = 4)
                elif characterName == 'Animation Cat':
                    drawLine(self.width / 2 -75, self.height - 205, self.width / 2 +75,
                             self.height - 205, fill= 'gold', lineWidth = 4)
                # Provide instructions
                drawLabel("Use Left/Right Arrows to Choose, Enter to Confirm",
                          self.width / 2, self.height - 25, size=15,
                          fill='Black',bold = True)

            elif self.startScreenStage == 'difficultySelection':
                # Draw background based on selected character
                if self.selectedCharacter == 'Super Cat':
                    # Draw design.png as background
                    if self.startScreenImages:
                        currentImage = self.startScreenImages[self.currentStartScreenImageIndex]
                        drawImage(currentImage, 0, 0, width=self.width, height=self.height)
                        
                elif self.selectedCharacter == 'Animation Cat':
                    self.drawAnimationCatStartScreen()

                # Draw instructions
                massege = "Use Mouse or Up/Down Arrows to Choose,Enter to Confirm"
                drawLabel(massege, self.width / 2, self.height - 15, size=15,
                          fill="black", bold = True)
                if self.selectedCharacter == 'Super Cat':
                    if self.difficulty == 'Easy':
                        drawLine(self.width / 2 -65, self.height - 110, self.width / 2 +40,
                                 self.height - 110, fill= 'gold', lineWidth = 4)
                    elif self.difficulty == 'Hard':
                        drawLine(self.width / 2 -65, self.height - 40, self.width / 2 +40,
                                 self.height - 40, fill= 'gold', lineWidth = 4)
                elif self.selectedCharacter == 'Animation Cat':
                    if self.difficulty == 'Easy':
                        drawLine(self.width / 2 -75, self.height - 100, self.width / 2 +75,
                                 self.height - 100, fill= 'gold', lineWidth = 4)
                    elif self.difficulty == 'Hard':
                        drawLine(self.width / 2 -75, self.height - 40, self.width / 2 +75,
                                 self.height - 40, fill= 'gold', lineWidth = 4)

        elif self.mode == 'game':
            # Draw sky background first
            drawRect(0, 0, self.width, self.height, fill="skyBlue")

            # Draw clouds
            for cloud in self.clouds:
                cloud.draw(self)

            # Draw background based on selected character
            if self.selectedCharacter == 'Super Cat' and self.backgroundImages.get('Super Cat'):
                bgImage = self.backgroundImages['Super Cat']
                
                # Get the original width and height of the image
                imageWidth = 801
                imageHeight = 600

                # Calculate how many times the image needs to be repeated horizontally and vertically
                rows = math.ceil(self.height / imageHeight)
                cols = math.ceil(self.worldWidth / imageWidth)

                # Draw the image multiple times to tile it, without stretching
                for row in range(rows):
                    for col in range(cols):
                        drawImage(bgImage, col * imageWidth - self.cameraX, row * imageHeight, 
                                  width=imageWidth, height=imageHeight)
                 #Draw holes
                for hole in self.holes:
                    hole.draw(self, 'blue')

            elif self.selectedCharacter == 'Animation Cat':
                # Draw programmatically created background for Animation Cat
                self.drawAnimationCatBackground()
            else:
                # Default background if no character selected
                drawRect(0 - self.cameraX, 0, self.worldWidth, self.height, fill="skyBlue")

            # Draw platforms
            for platform in self.platforms:
                platform.draw(self)

            # Draw Collectibles
            for collectible in self.collectibles:
                collectible.draw(self)

            # Draw Power-Ups
            for powerUp in self.powerUps:
                powerUp.draw(self)

            # Draw Hero
            self.hero.draw(self)

            # Draw Enemies
            for enemy in self.enemies:
                enemy.draw(self)

            # Draw Score
            drawLabel(f"Score: {self.hero.score}", 70, 30, size=20, fill="white")

            # Display lives as hearts
            for i in range(self.hero.lives):
                x = 40 + i * 30
                y = 60
                Environment.drawHeart(x, y, 0.5, 'red') 

            # Display double jump count
            doubleJumpX = 40
            doubleJumpY = 90
            Environment.drawPowerIcon(doubleJumpX, doubleJumpY, 'doubleJump')
            drawLabel(f"x{self.hero.doubleJumpCount}", doubleJumpX + 20, doubleJumpY,
                      size=15, fill='black', bold =True)

            # Draw active power-up timers
            timerY = 30
            for powerUpName, timeLeft in self.hero.powerUpTimers.items():
                drawLabel(f"{powerUpName}: {timeLeft}s", self.width - 150, timerY,
                          size=15, fill="black", align="right", bold =True)
                timerY += 20

            # Draw pause button
            btn = self.pauseButton
            drawRect(btn['x'], btn['y'],
                     btn['width'], btn['height'],
                     fill='gray', border='black')
            # Draw '||' symbol on the pause button
            barWidth = btn['width'] / 5
            barHeight = btn['height'] * 0.8
            barY = btn['y'] + (btn['height'] - barHeight) / 2
            # Left bar
            drawRect(btn['x'] + barWidth, barY, barWidth, barHeight, fill='white')
            # Right bar
            drawRect(btn['x'] + 3 * barWidth, barY, barWidth,
                     barHeight, fill='white')

            # Draw exit button
            exitBtn = self.exitButton
            drawRect(exitBtn['x'], exitBtn['y'],
                     exitBtn['width'], exitBtn['height'],
                     fill='gray', border='black')
            # Draw 'X' symbol on the exit button
            drawLine(exitBtn['x'] + 5, exitBtn['y'] + 5,
                     exitBtn['x'] + exitBtn['width'] - 5,
                     exitBtn['y'] + exitBtn['height'] - 5,
                     fill='white', lineWidth=2)
            drawLine(exitBtn['x'] + exitBtn['width'] - 5, exitBtn['y'] + 5,
                     exitBtn['x'] + 5, exitBtn['y'] + exitBtn['height'] - 5,
                     fill='white', lineWidth=2)

            if self.paused:
                # Draw Pause Screen overlay
                drawRect(0, 0, self.width, self.height, fill="black", opacity=50)
                drawLabel("Paused", self.width / 2, self.height / 2 - 50,
                          size=40, fill="white")
                drawLabel("Press 'P' to Resume", self.width / 2, self.height / 2 + 20,
                          size=20, fill="white")
                drawLabel("Press 'E' to Exit", self.width / 2, self.height / 2 + 50,
                          size=20, fill="white")
            elif self.gameOver:
                # Draw Game Over Screen
                drawRect(0, 0, self.width, self.height, fill='salmon', opacity=70)
                drawLabel("Game Over!", self.width / 2, self.height / 2 - 50,
                          size=40, fill="red")
                drawLabel("Press 'R' to Restart", self.width / 2, self.height / 2 + 20,
                          size=20, fill="white")
            elif self.levelComplete:
                # Draw Level Complete Screen
                drawRect(0, 0, self.width, self.height, fill="black", opacity=70)
                drawLabel("Level Complete!", self.width / 2, self.height / 2 - 50,
                          size=40, fill="green")
                drawLabel("Press 'N' to Play Next Level",
                          self.width / 2, self.height / 2 + 20,
                          size=20, fill="white")
                