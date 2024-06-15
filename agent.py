import pygame
from controller import *
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import numpy as np
from model import Linear_QNet, QTrainer
# from game import *


MODEL_FILEPATH = "model/model.pth"
MAX_MEMORY = 5000
MAX_TRAIN_SIZE = 1000
LEARNING_RATE = 0.001


FIRST_LAYER_SIZE = 256
SECOND_LAYER_SIZE = 36
THIRD_LAYER_SIZE = 36
OUTPUT_SIZE = 3

class CellItemType(enum.Enum):
    WALL = -1
    EMPTY = 0
    BODY = 1
    HEAD = 2
    FRUIT = 4
    
    def __int__(self):
        return self.value

class MemoryStore:
    def __init__(self, state, action, reward, next_state, done):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done

class Agent(Controller):
    
    def __init__(self, train_flag):
        self.train_flag = train_flag
        self.memory = deque(maxlen = MAX_MEMORY)
        self.neural_network = None
        self.discount = 0.9
        self.learning_rate = LEARNING_RATE
        self.epsilon = 0.8
        self.epsilon_decay_linear = 1/100
        
    def init(self, snake, game):
        self.snake = snake
        self.game = game
        self.reward = 0
        self.score = 0

        if self.train_flag:
            self.epsilon -= self.epsilon_decay_linear
            
        self.current_state = self.get_snake_nearby()
        self.last_action = None
        
        if not self.neural_network:
            if self.train_flag:
                self.neural_network = Linear_QNet(self.get_input_size(), FIRST_LAYER_SIZE, OUTPUT_SIZE)
                self.trainer = QTrainer(self.neural_network, self.learning_rate, self.discount)
            else:
                # check
                state_dict = torch.load(MODEL_FILEPATH)
                self.neural_network = Linear_QNet(self.get_input_size(), FIRST_LAYER_SIZE, OUTPUT_SIZE)
                self.neural_network.load_state_dict(state_dict)
                self.trainer = QTrainer(self.neural_network, self.learning_rate, self.discount)
                # self.neural_network.eval()
                
                
    def save_to_memory(self, state, action, reward, next_state, done):
        self.memory.append(MemoryStore(state, action, reward, next_state, done))
        
    def get_input_size(self):
        return len(self.current_state)
    
    # def board_to_state(self):
    #     board = []
    #     board.append(CellItemType.WALL.value)
    #     for col in range(self.game.board.left, self.game.board.right, self.snake.step):
    #         board.append(CellItemType.WALL.value)
    #     board.append(CellItemType.WALL.value)
        
        
    #     for row in range(self.game.board.top, self.game.board.bottom, self.snake.step):
    #         board.append(CellItemType.WALL.value)
    #         for col in range(self.game.board.left, self.game.board.right, self.snake.step):
    #             board.append(CellItemType.EMPTY.value)
    #         board.append(CellItemType.WALL.value)
                    
    #     board[self.game.snake.body[0].x + int(self.game.snake.body[0].y / self.snake.step_size)] = CellItemType.HEAD
        
    #     for pt in self.game.snake.body[1:]:
    #         board[pt.x + int(pt.y / self.snake.step_size)] = CellItemType.BODY
            
    #     board[self.game.food.position.x + int(self.game.food.position.y / self.snake.step_size)] = CellItemType.FRUIT
        
    #     return board
                
    def not_good(self, point):
        if point.x < self.game.board.left or point.x >= self.game.board.right:
            return True
        
        if point.y < self.game.board.top or point.y >= self.game.board.bottom:
            return True
        
        if point in self.game.snake.body[1:]:
            return True
        
        return False
        
    def get_snake_nearby(self):
        
        # board = self.board_to_state()
        
        head = self.snake.body[0]
        
        point_l = Position(head.x - self.snake.step_size, head.y)
        point_r = Position(head.x + self.snake.step_size, head.y)
        point_u = Position(head.x, head.y - self.snake.step_size)
        point_d = Position(head.x, head.y + self.snake.step_size)
        
        point_l_danger = self.not_good(point_l)
        point_d_danger = self.not_good(point_d)
        point_r_danger = self.not_good(point_r)
        point_u_danger = self.not_good(point_u)
        
        
        dir_l = self.snake.last_direction == Direction.LEFT
        dir_r = self.snake.last_direction == Direction.RIGHT
        dir_u = self.snake.last_direction == Direction.UP
        dir_d = self.snake.last_direction == Direction.DOWN
        
        betweenx = 0
        for pt in self.snake.body[1:]:
            if pt.x > head.x and pt.x < self.game.food.position.x:
                betweenx = 1
            elif pt.x < head.x and pt.x > self.game.food.position.x:
                betweenx = 1
                
        betweeny = 0
        for pt in self.snake.body[1:]:
            if pt.y > head.y and pt.y < self.game.food.position.y:
                betweeny = 1
            elif pt.y < head.y and pt.y > self.game.food.position.y:
                betweeny = 1
        
        
        state = [
            (dir_r and point_r_danger) or
            (dir_l and point_l_danger) or
            (dir_u and point_u_danger) or
            (dir_d and point_d_danger),
            
            (dir_u and point_r_danger) or
            (dir_d and point_l_danger) or
            (dir_l and point_u_danger) or
            (dir_r and point_d_danger),
            
            (dir_d and point_r_danger) or
            (dir_u and point_l_danger) or
            (dir_r and point_u_danger) or
            (dir_l and point_d_danger),
            
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            self.game.food.position.x < self.snake.body[0].x,
            self.game.food.position.x > self.snake.body[0].x,
            self.game.food.position.y < self.snake.body[0].y,
            self.game.food.position.y > self.snake.body[0].y,
            
            betweenx,
            betweeny
        ]
        
        return np.array(state, dtype=int)
    
    def make_move(self):
        self.current_state = torch.tensor(self.get_snake_nearby(), dtype=torch.float)
        
        final_move = [0, 0, 0]
        
        if random.random() < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(self.current_state, dtype=torch.float)
            prediction = self.neural_network(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        if final_move[0] == 1:
            self.snake.turn_left()
        elif final_move[1] == 1:
            self.snake.turn_right()
        elif final_move[2] == 1:
            pass
        
        self.last_action = final_move
        
    def get_reward(self):
        self.reward = 0
        if self.snake.get_score() > self.score:
            # print("Score: ", self.snake.get_score())
            # print("Last Score: ", self.score)
            self.score = self.snake.get_score()
            self.reward = 100
        elif self.game.is_over():
            self.reward = -100
        else:
            self.reward = -1
            
    def update_state(self):
        if self.train_flag:
            self.get_reward()
            # if self.reward != 0 and self.reward != -1:
            #     print("Reward: ", self.reward)
            
            self.trainer.train_step(self.current_state, self.last_action, self.reward, self.get_snake_nearby(), self.game.is_over())
            
            self.save_to_memory(self.current_state, self.last_action, self.reward, self.get_snake_nearby(), self.game.is_over())
            
    def replay(self):
        if len(self.memory) > MAX_TRAIN_SIZE:
            mini_sample = random.sample(self.memory, MAX_TRAIN_SIZE)
        else:
            mini_sample = self.memory
            
        # states, actions, rewards, next_states, dones = zip(*mini_sample)
        
        # states = torch.tensor(states, dtype=torch.float)
        # actions = torch.tensor(actions, dtype=torch.float)
        # rewards = torch.tensor(rewards, dtype=torch.float)
        # next_states = torch.tensor(next_states, dtype=torch.float)
        # dones = torch.tensor(dones, dtype=torch.float)
        
        # self.trainer.train_step(states, actions, rewards, next_states, dones)   
        # print("hehe")
        for current_item in mini_sample:
            self.trainer.train_step(current_item.state, current_item.action, current_item.reward, current_item.next_state, current_item.done)