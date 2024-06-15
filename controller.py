import pygame 
import enum
import math

pygame.init()
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash(str(self.x) + ',' + str(self.y))
    
    def distance(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)
    
    
class Direction(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    def __int__(self):
        return self.value
    
class Controller:
    snake = None
    game = None
    
    def init(self, snake, game):
        self.snake = snake
        self.game = game
    
    def make_move(self):
        pass
    
    def update_state(self):
        pass
    
    def display_controller_gui(self):
        pass
    
class KeyBoardController(Controller):
    snake = None
    game = None
    train_flag = False
    
    def init(self, snake, game):
        self.snake = snake
        self.game = game
        
    def make_move(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        
        # if keys[pygame.K_RIGHT]:
        #     self.snake.turn_right()
        # elif keys[pygame.K_LEFT]:
        #     self.snake.turn_left()
        
        if keys[pygame.K_UP]:
            if self.snake.last_direction != Direction.DOWN:
                self.snake.go_up()
        elif keys[pygame.K_DOWN]:
            if self.snake.last_direction != Direction.UP:
                self.snake.go_down()
        elif keys[pygame.K_LEFT]:
            if self.snake.last_direction != Direction.RIGHT:
                self.snake.go_left()
        elif keys[pygame.K_RIGHT]:
            if self.snake.last_direction != Direction.LEFT:
                self.snake.go_right()
        
            
    def update_state(self):
        pass
    
    def display_controller_gui(self):
        pass
    
    def replay(self):
        pass
