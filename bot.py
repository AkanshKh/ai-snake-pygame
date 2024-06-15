import pygame 
import random
import numpy as np
from controller import *
from agent import *
import argparse

ST_LENGTH = 3
MAX_MOVES = 150
BOXES = 30
BOX_SIZE = 20

# class CellItemType(enum.Enum):
#     WALL = -1
#     EMPTY = 0
#     BODY = 1
#     HEAD = 2
#     FRUIT = 4
    
#     def __int__(self):
#         return self.value

WHITE = (255, 255, 255)
class Food:
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
        head = Position((BOXES * BOX_SIZE) // 2, (BOXES * BOX_SIZE) // 2)
        self.body = [head, Position(head.x - BOX_SIZE, head.y), Position(head.x - 2 * BOX_SIZE, head.y)]
        
        self.last_direction = Direction.RIGHT
        self.image = pygame.image.load('snake.png')
        self.step_size = BOX_SIZE
        
    def grow(self):
        self.body.append(Position(self.body[-1].x, self.body[-1].y))
        
    def get_head(self):
        return self.image.get_rect().move((self.body[0].x, self.body[0].y))
    
    def get_length(self):
        return len(self.body)
    
    def get_length(self):
        return len(self.body)
    
    def get_score(self):
        return self.get_length() - ST_LENGTH
    
    def turn_left(self):
        self.last_direction = Direction((self.last_direction.value - 1) % 4)
        
    def turn_right(self):
        self.last_direction = Direction((self.last_direction.value + 1) % 4)
        
    def go_up(self):
        self.last_direction = Direction.UP
    
    def go_down(self):
        self.last_direction = Direction.DOWN
    
    def go_left(self):
        self.last_direction = Direction.LEFT
    
    def go_right(self):
        self.last_direction = Direction.RIGHT
    
    def _set_direction(self, direction):
        self.last_direction = direction
        
    def update(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
            
        if self.last_direction == Direction.UP:
            self.body[0].y -= self.step_size
        elif self.last_direction == Direction.DOWN:
            self.body[0].y += self.step_size
        elif self.last_direction == Direction.LEFT:
            self.body[0].x -= self.step_size
        elif self.last_direction == Direction.RIGHT:
            self.body[0].x += self.step_size
         
         
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
        self.boxes = BOXES
        self.food = Food()
        
        
    def init(self):
        pygame.display.set_caption('SNAKEEEEEEE')
        self.snake = Snake()
        self._running = True
        self.border_width = BOX_SIZE * 2
        self.window_height = BOXES * BOX_SIZE + self.border_width * 2
        self.window_width = BOXES * BOX_SIZE + self.border_width * 2
        
        # change isinstance
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 120))
        
        self.board = pygame.Rect(self.border_width, self.border_width, self.window_width - 2 * self.border_width, self.window_height - 2 * self.border_width)
        
        self.place_food()
        self.controller.init(self.snake, self)
        self.moves_left = MAX_MOVES
        self._running = True
        
    def is_valid_position(self):
        return self.board.contains(self.snake.get_head())
    
    def get_score(self):
        return self.snake.get_score()
    
    def is_over(self):
        return not self._running
    
    def draw_board(self):
        self._display_surf.fill((0, 0, 0))
        pygame.draw.rect(self._display_surf, WHITE, self.board)
        
    def draw_snake(self):
        for pos in self.snake.body:
            self._display_surf.blit(self.snake.image, (pos.x, pos.y))   
            
    def draw_food(self):
        self._display_surf.blit(self.food.image, (self.food.position.x, self.food.position.y)) #check this
        
    def place_food(self):
        x = random.randint(self.board.left, self.board.right - 1)
        y = random.randint(self.board.top, self.board.bottom - 1)
        
        x -= x % self.snake.step_size
        y -= y % self.snake.step_size
        
        self.food.position = Position(x, y)
        
        if self.food.position in self.snake.body:
            self.place_food()
            
    def draw_ui(self):
        font = pygame.font.SysFont('Segoe UI', 24)
        
        bottom = self._display_surf.get_rect().bottom
        
        game_number = font.render('Game: ' + str(self.game_cnt), True, WHITE)
        self._display_surf.blit(game_number, (40, bottom - 140))
        
        moves_left = font.render('Moves Left: ' + str(self.moves_left), True, WHITE)
        self._display_surf.blit(moves_left, (40, bottom - 90))
        
        score = font.render('Score: ' + str(self.get_score()), True, WHITE)
        self._display_surf.blit(score, (300, bottom - 140))
        
        highscore = font.render('High Score: ' + str(self.high_score), True, WHITE)
        self._display_surf.blit(highscore, (300, bottom - 90))
        
        
            
    def render(self):
        self.draw_board()
        self.draw_snake()
        self.draw_food()
        self.draw_ui()
        
        # self.controller.display_controller_gui()
        pygame.display.flip()
        
    def cleanup(self):
        pygame.quit()
        
    def read_direction(self):
        lst_drn = self.snake.last_direction
        self.controller.make_move()
        
        if lst_drn != self.snake.last_direction:
            self.moves_left -= 1
            
    def update_snake(self):
        self.snake.update() 
        
    def can_collide(self, pt = None):
        if pt is None:
            pt = self.snake.body[0]
            
        
        if pt.x < self.board.left or pt.x >= self.board.right:
            return True
        
        if pt.y < self.board.top or pt.y >= self.board.bottom:
            return True
        
        if pt in self.snake.body[1:]:
            return True
    
        return False
            
    def check_is_valid(self):
        if self.moves_left <= 0:
            self._running = False
        
        if self.can_collide(self.snake.body[0]):
            self._running = False
        
        if self.food.position == self.snake.get_head():
            self.snake.grow()
            self.moves_left = MAX_MOVES + self.snake.get_length()
            self.place_food()
            
            if self.get_score() > self.high_score:
                self.high_score = self.get_score()
                
    # def board_to_state(self):
    #     board = []
        
    #     board.append(CellItemType.WALL)
    #     for col in range(game.board.left, game.board.right, game.snake.step_size):
    #         board.append(CellItemType.WALL)
    #     board.append(CellItemType.WALL)
        
        
    #     for row in range(game.board.top, game.board.bottom, game.snake.step_size):
    #         board.append(CellItemType.WALL)
    #         for col in range(game.board.left, game.board.right, game.snake.step_size):
    #             board.append(CellItemType.EMPTY)
    #         board.append(CellItemType.WALL)
                    
    #     board[game.snake.body[0].x + int(game.snake.body[0].y / BOX_SIZE)] = CellItemType.HEAD
        
    #     for pt in game.snake.body[1:]:
    #         board[pt.x + int(pt.y / BOX_SIZE)] = CellItemType.BODY
            
    #     board[game.food.position.x + int(game.food.position.y / BOX_SIZE)] = CellItemType.FRUIT
        
    #     return board
        
    def run(self):
        self.init()
        self.game_cnt += 1
        
        while not self.is_over():
            self.render()
            self.read_direction()
            # board = self.board_to_state()
            # print(board)
            # print(len(board))
            # print(self.snake.body[0].x, self.snake.body[0].y)
            # print(board[self.snake.body[0].x + int((self.snake.body[0].y - BOX_SIZE) / BOX_SIZE)])
            # if board[self.snake.body[0].x + int((self.snake.body[0].y - BOX_SIZE) / BOX_SIZE)] is not CellItemType.EMPTY:
            #     print(board[self.snake.body[0].x + int((self.snake.body[0].y - BOX_SIZE) / BOX_SIZE)])
                
            self.update_snake()
            
            self.check_is_valid()
            
            self.controller.update_state()
            
            pygame.time.delay(self.speed)
        
        if game.controller.train_flag:
            self.controller.replay()
        
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--speed", type = int, default = 100, help = "Speed of the game. Default set to 100")
    parser.add_argument("--count", type = int, default = 100, help = "Number of games to play. Default set to 100")
    parser.add_argument("--ai",action = 'store_true', help = "Flag to set AI. Default set to True")
    parser.add_argument("--train",action = 'store_true', help = "Flag to set training. Default set to True")
    
    args = parser.parse_args()
    
    controller = KeyBoardController()
    
    if args.ai:
        controller = Agent(args.train)
    game = Game(controller, args.speed)
    
    score_in_game = []  
    highscore_in_game = [] 
    
    while game.game_cnt < args.count:
        game.run()
        
        if game.get_score() == game.high_score and game.controller.train_flag:
            print("Saving model")
            game.controller.neural_network.save()
           
        score_in_game.append(game.get_score())
        highscore_in_game.append(game.high_score)
           
        print("Game: ", game.game_cnt, "Score: ", game.get_score(), "High Score: ", game.high_score)
        
        
    print("Average Score: ", np.mean(score_in_game))
    print("High Score: ", np.max(highscore_in_game))
    game.cleanup()
    
    