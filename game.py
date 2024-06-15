import pygame 
import random
import numpy as np
from controller import *
from agent import *

ST_LENGTH = 1
MAX_MOVES = 150
BOXES = 30

class Food : 
    def __init__(self):
        self.position = Position(0, 0)
        self.image = pygame.image.load('food.png')   
        
    def get_rect(self):
        img_rect = self.image.get_rect()
        img_rect.x = self.position.x
        img_rect.y = self.position.y
        return img_rect
    
class Snake:
    def __init__(self):
        self.body = []
        
        for i in range(0, ST_LENGTH):
            self.body.append(Position(0, 0)) #check this
            
        self.last_direction = Direction.RIGHT
        self.image = pygame.image.load('snake.png')
        self.step = self.get_head().right - self.get_head().left
        
        
    def grow(self):
        self.body.append(Position(self.body[-1].x, self.body[-1].y))
        
    def get_head(self):
        return self.image.get_rect().move((self.body[0].x, self.body[0].y))
    
    def get_length(self):
        return len(self.body)
    
    def get_score(self):
        return self.get_length() - ST_LENGTH
    
    def go_left(self):
        self.last_direction = Direction((self.last_direction.value - 1) % 4)
        
    def go_right(self):
        self.last_direction = Direction((self.last_direction.value + 1) % 4)
    # def go_up(self):
    #     self.last_direction = Direction.UP
    
    # def go_down(self):
    #     self.last_direction = Direction.DOWN
    
    # def go_left(self):
    #     self.last_direction = Direction.LEFT
    
    # def go_right(self):
    #     self.last_direction = Direction.RIGHT
    
        
    def _set_direction(self, direction):
        self.last_direction = direction
        
    def update(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
            
        if self.last_direction == Direction.UP:
            self.body[0].y -= self.step
        elif self.last_direction == Direction.DOWN:
            self.body[0].y += self.step
        elif self.last_direction == Direction.LEFT:
            self.body[0].x -= self.step
        elif self.last_direction == Direction.RIGHT:
            self.body[0].x += self.step
            
class Game:
    snake = None
    food = None 
    
    def __init__(self, controller, speed):
        pygame.init()
        self._running = True
        self._display_surf = None
        self.board = None
        self.high_score = 0
        self.game_cnt = 0
        self.speed = speed
        self.controller = controller
        self.food = Food()
        
    def _start(self):
        self.snake.body[0].x = random.randint(self.board.left, self.board.right - 1)
        self.snake.body[0].y = random.randint(self.board.top, self.board.bottom - 1)
        
        self.snake.body[0].x -= self.snake.body[0].x % self.snake.step
        self.snake.body[0].y -= self.snake.body[0].y % self.snake.step
        
        self.snake._set_direction(Direction(random.randint(0, 3)))
        
        
    def init(self):
        pygame.display.set_caption('SNAKEEEEEEE')
        self.snake = Snake()
        self.border_width = 2 * self.snake.step
        self.window_height = BOXES * self.snake.step
        self.window_width = BOXES * self.snake.step 
        self._running = True
        # print(self._running)
        
        if isinstance(self.controller, Agent):
            self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 20), pygame.HWSURFACE)
        else:
            self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 150), pygame.HWSURFACE)
        
        self.board = pygame.Rect(self.border_width, self.border_width, self.window_width - 2 * self.border_width, self.window_height - 2 * self.border_width)
        
        self._start()
        self.place_food()
        self.controller.init(self.snake, self)
        self.moves_left = MAX_MOVES
        self._running = True
        # print("Game Initialized")
        
        
    def is_valid_position(self):
        return self.board.contains(self.snake.get_head())
    
    def get_score(self):
        return self.snake.get_score()
    
    def is_over(self):
        # print(self._running)
        return not self._running
    
    def draw_board(self):
        self._display_surf.fill((0, 0, 0))
        pygame.draw.rect(self._display_surf, (255, 255, 255), self.board)
        
        
    # def draw_ui(self):
    
    
    
    def draw_snake(self):
        for pos in self.snake.body:
            self._display_surf.blit(self.snake.image, (pos.x, pos.y))   
            
    def draw_food(self):
        self._display_surf.blit(self.food.image, (self.food.position.x, self.food.position.y)) #check this
        
    def place_food(self):
        x = random.randint(self.board.left, self.board.right - 1)
        y = random.randint(self.board.top, self.board.bottom - 1)
        
        x -= x % self.snake.step
        y -= y % self.snake.step
        
        self.food.position = Position(x, y)
        
        if self.food.position in self.snake.body:
            self.place_food()
            
    def render(self):
        self.draw_board()
        self.draw_snake()
        self.draw_food()
        # self.draw_ui()
        
        # self.controller.display_controller_gui()
        pygame.display.flip()
        
    def cleanup(self):
        pygame.quit()
        
    def read_direction(self):
        last_direction = self.snake.last_direction
        self.controller.make_move()
        if last_direction != self.snake.last_direction:
            self.moves_left -= 1
            
    def update_snake(self):
        self.snake.update()
        
    def check_collisions(self):
        if not self.is_valid_position():
            self._running = False
            
        if self.moves_left <= 0:
            self._running = False
            
        if self.snake.get_length() != len(set(self.snake.body)):
            self._running = False
            
        if self.food.position == self.snake.get_head():
            self.snake.grow()
            self.moves_left = MAX_MOVES + self.snake.get_length()
            self.place_food()
            
            if self.get_score() > self.high_score:
                self.high_score = self.get_score()
                
    def can_collide(self, pt = None):
        if pt is None:
            pt = self.snake.get_head()
            
        
        if pt.x < self.board.left or pt.x >= self.board.right:
            return True
        
        if pt.y < self.board.top or pt.y >= self.board.bottom:
            return True
        
        if pt in self.snake.body[1:]:
            return True
        
        return False
                
    def run(self):
        self.init()
        self.game_cnt += 1
        
        while not self.is_over():
            self.render()
            self.read_direction()
            
            self.update_snake()
            self.check_collisions()
            
            self.controller.update_state()
            pygame.time.wait(self.speed)
            
        self.controller.replay()
# def draw_plot




if __name__ == "__main__":
    controller = Agent(True)
    game = Game(controller, 100)
    
    score_in_game = []  
    highscore_in_game = [] 
    
    while game.game_cnt < 100:
        game.run()
        score_in_game.append(game.get_score())
        highscore_in_game.append(game.high_score)
        print("Game: ", game.game_cnt, "Score: ", game.get_score(), "High Score: ", game.high_score)
        
        
    print("Average Score: ", np.mean(score_in_game))
    print("High Score: ", np.max(highscore_in_game))
    game.cleanup()
    
    
# agent = Agent(True)
# game = Game(agent, 40)
# # agent.init(game.snake, game)
# game.init()
# print(game.controller.board_to_state())
# while game.game_cnt < 100:
#     print(game.game_cnt)
#     game.run()
# game.cleanup()