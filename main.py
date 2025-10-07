import pygame
import time
from pygame.locals import *
import random

# Size of each block (snake segment / apple)
SIZE = 40



class Apple:
    def __init__(self, parent_screen, width, height):
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.parent_screen = parent_screen
        self.width = width
        self.height = height
        self.x = SIZE * 3
        self.y = SIZE * 3

    def draw(self):
        """Draw apple on the game window"""
        self.parent_screen.blit(self.image, (self.x, self.y))

    def move(self):
        """Move apple to a random position on the grid (dynamic for screen size)"""
        max_x = (self.width // SIZE) - 1
        max_y = (self.height // SIZE) - 1
        self.x = random.randint(0, max_x) * SIZE
        self.y = random.randint(0, max_y) * SIZE



class Snake:
    def __init__(self, parent_screen, length):
        self.length = length
        self.parent_screen = parent_screen
        self.block = pygame.image.load("resources/block.jpg").convert()
        self.x = [SIZE] * length
        self.y = [SIZE] * length
        self.direction = 'down'

    def increase_length(self):
        """Increase snake length by 1"""
        self.length += 1
        self.x.append(-1)  # Temporary offscreen position
        self.y.append(-1)

    # Direction change functions
    def move_left(self): self.direction = 'left'
    def move_right(self): self.direction = 'right'
    def move_up(self): self.direction = 'up'
    def move_down(self): self.direction = 'down'

    def walk(self):
        """Move the snake in the current direction"""
        # Update body segments to follow the head
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # Move the head
        if self.direction == 'left':
            self.x[0] -= SIZE
        if self.direction == 'right':
            self.x[0] += SIZE
        if self.direction == 'up':
            self.y[0] -= SIZE
        if self.direction == 'down':
            self.y[0] += SIZE

        self.draw()

    def draw(self):
        """Draw snake on the game window"""
        for i in range(self.length):
            self.parent_screen.blit(self.block, (self.x[i], self.y[i]))



class Game:
    def __init__(self):
        pygame.init()
        self.play_background_music()

        # Get full screen resolution dynamically
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h

        # Create fullscreen window
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.mixer.init()

        # Create snake and apple
        self.snake = Snake(self.surface, 1)
        self.snake.draw()
        self.apple = Apple(self.surface, self.width, self.height)
        self.apple.draw()

    def is_collision(self, x1, y1, x2, y2):
        """Check if two objects collide"""
        if x1 >= x2 and x1 < x2 + SIZE and y1 >= y2 and y1 < y2 + SIZE:
            return True
        return False

    def play_background_music(self):
        pygame.mixer.music.load("resources/bg_music.mp3")
        pygame.mixer.music.play()

    def play_sound(self, sound):
        sound = pygame.mixer.Sound(f"resources/{sound}.mp3")
        pygame.mixer.Sound.play(sound)

    def render_background(self):
        """Draw background image (scaled to fullscreen)"""
        bg = pygame.image.load("resources/background.jpg")
        bg = pygame.transform.scale(bg, (self.width, self.height))
        self.surface.blit(bg, (0, 0))

    def play(self):
        """Main gameplay loop (snake movement, apple, collision checks)"""
        self.render_background()
        self.snake.walk()
        self.apple.draw()
        self.display_score()
        pygame.display.flip()

        # Snake colliding with apple
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("ding")
            self.snake.increase_length()
            self.apple.move()

        # Snake colliding with itself
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.play_sound("crash")
                raise Exception("Game Over")

        # Snake colliding with wall (dynamic borders)
        if (self.snake.x[0] < 0 or self.snake.x[0] >= self.width or
            self.snake.y[0] < 0 or self.snake.y[0] >= self.height):
            self.play_sound("crash")
            raise Exception("Game Over")

    def show_game_over(self):
        """Display Game Over screen"""
        self.render_background()
        font = pygame.font.SysFont('arial', 30)
        line1 = font.render(f"Game is over! Your score is {self.snake.length}", True, (255, 255, 255))
        self.surface.blit(line1, (self.width // 4, self.height // 2 - 50))
        line2 = font.render("To play again press Enter. To exit press Escape!", True, (255, 255, 255))
        self.surface.blit(line2, (self.width // 4, self.height // 2))
        pygame.display.flip()
        pygame.mixer.music.pause()

    def display_score(self):
        """Show score in top-right corner"""
        font = pygame.font.SysFont('arial', 30)
        score = font.render(f"Score: {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(score, (self.width - 200, 10))

    def reset(self):
        """Reset snake and apple after Game Over"""
        self.snake = Snake(self.surface, 1)
        self.apple = Apple(self.surface, self.width, self.height)

    def run(self):
        """Main game loop"""
        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        pause = False
                        pygame.mixer.music.unpause()
                    if not pause:  # Only move when not paused
                        if event.key == K_UP:
                            self.snake.move_up()
                        if event.key == K_DOWN:
                            self.snake.move_down()
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        if event.key == K_RIGHT:
                            self.snake.move_right()

                elif event.type == QUIT:
                    running = False

            # Core gameplay
            try:
                if not pause:
                    self.play()
            except Exception as e:
                self.show_game_over()
                pause = True
                self.reset()

            # Speed increases with snake length
            delay = max(0.05, 0.15 - (self.snake.length * 0.005))
            time.sleep(delay)



if __name__ == "__main__":
    game = Game()
    game.run()
