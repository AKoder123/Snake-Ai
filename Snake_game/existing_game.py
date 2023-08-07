import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import time

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    NONE = 5

Point = namedtuple('Point', 'x, y')
# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (76, 187, 23)
BLUE2 = (57, 255, 20)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 18
#Vinay lost at 3 speed

class SnakeGameAI:
    #w = 640, h = 480 default
    def __init__(self, w=640, h=520):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake 2: Race to 15 Apples')
        self.clock = pygame.time.Clock()
        self.reset()
        self.h_reset()


    def reset(self):
        # init game state
        self.score = 0
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2//2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def h_reset(self):
        self.hscore = 0
        self.hdirection = Direction.NONE

        self.hhead = Point(self.w-(self.w/2//2), self.h/2)
        self.hsnake = [self.hhead,
                      Point(self.hhead.x-BLOCK_SIZE, self.hhead.y),
                      Point(self.hhead.x-(2*BLOCK_SIZE), self.hhead.y)]

        self.hscore = 0
        self.hfood = None
        self._place_h_food()
    
    def end(self):
        self.display.fill(BLACK)
        
        text4 = font.render("Human WINS, AI hit a wall!!", True, WHITE)
        

        text3 = font.render("GAME OVER", True, WHITE)
        text = font.render("AI Score: " + str(self.score), True, WHITE)
        text2 = font.render("Player Score: "+str(self.hscore), True, WHITE)
        self.display.blit(text, [0, 0])
        self.display.blit(text2, [self.w-200, 0])
        self.display.blit(text3, [self.w//2-100, self.h//2])
        self.display.blit(text4, [self.w//2-90, self.h//2-80])
        pygame.display.flip()
        time.sleep(5)


    def h_end(self):
        self.display.fill(BLACK)
        if (self.hscore == 15) and (self.score == 15):
            text4 = font.render("Draw, Well Done >:(", True, WHITE)
        elif self.hscore == 15:
            text4 = font.render("Human WINS, Well Done >:(", True, WHITE)
        else:
            if self.hscore > self.score:
                text4 = font.render("AI WINS, Human hit a wall :)", True, WHITE)
            else:
                text4 = font.render("AI WINS :)", True, WHITE)
    

        text3 = font.render("GAME OVER", True, WHITE)
        text = font.render("AI Score: " + str(self.score), True, WHITE)
        text2 = font.render("Player Score: "+str(self.hscore), True, WHITE)
        self.display.blit(text, [0, 0])
        self.display.blit(text2, [self.w-200, 0])
        self.display.blit(text3, [self.w//2-100, self.h//2])
        self.display.blit(text4, [self.w//2-90, self.h//2-80])
        pygame.display.flip()
        time.sleep(5)

        


    def _place_food(self):
        x = random.randint(0, (self.w//2-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if (self.food in self.snake):
            self._place_food()
    
    def _place_h_food(self):
        x = random.randint((self.w//2 + BLOCK_SIZE)//BLOCK_SIZE, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.hfood = Point(x, y)
        if (self.hfood in self.hsnake):
            self._place_h_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
                    self.hdirection = Direction.LEFT
                elif event.key == pygame.K_RIGHT or (event.key == pygame.K_d):
                    self.hdirection = Direction.RIGHT
                elif event.key == pygame.K_UP or (event.key == pygame.K_w):
                    self.hdirection = Direction.UP
                elif event.key == pygame.K_DOWN or (event.key == pygame.K_s):
                    self.hdirection = Direction.DOWN
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        self.clock.tick(SPEED)
        # 5. update ui and clock
        # self._update_ui()
        # self.clock.tick(SPEED)
        # 2. move
        self._hmove(self.hdirection) # update the head
        self.hsnake.insert(0, self.hhead)
        
        # 3. check if game over
        hgame_over = False
        if self.his_collision():
            hgame_over = True
            
        # 4. place new food or just move
        if self.hhead == self.hfood:
            self.hscore += 1
            self._place_h_food()
        else:
            self.hsnake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score
    
    def play_h_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
                    self.hdirection = Direction.LEFT
                elif event.key == pygame.K_RIGHT or (event.key == pygame.K_d):
                    self.hdirection = Direction.RIGHT
                elif event.key == pygame.K_UP or (event.key == pygame.K_w):
                    self.hdirection = Direction.UP
                elif event.key == pygame.K_DOWN or (event.key == pygame.K_s):
                    self.hdirection = Direction.DOWN

                    
        
        # 2. move
        self._hmove(self.hdirection) # update the head
        self.hsnake.insert(0, self.hhead)
        
        # 3. check if game over
        hgame_over = False
        if self.his_collision():
            hgame_over = True
            return hgame_over, self.hscore
        if self.score >= 15:
            hgame_over = True
        if self.hscore >= 15:
            hgame_over = True
            
        # 4. place new food or just move
        if self.hhead == self.hfood:
            self.hscore += 1
            self._place_h_food()
        else:
            self.hsnake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)      
        # 6. return game over and score
        return hgame_over, self.hscore


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w//2 - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False
    
    def his_collision(self, pt=None):
        if pt is None:
            pt = self.hhead
        # hits boundary
        if pt.x < self.w//2  + BLOCK_SIZE or pt.x < 0 or pt.x > self.w - BLOCK_SIZE or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        pygame.draw.rect(self.display, WHITE, pygame.Rect(self.w//2, 0, BLOCK_SIZE, self.h))

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        for pt in self.hsnake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.hfood.x, self.hfood.y, BLOCK_SIZE, BLOCK_SIZE))


        text = font.render("AI Score: " + str(self.score), True, WHITE)
        text2 = font.render("Player Score: "+str(self.hscore), True, WHITE)
        self.display.blit(text, [0, 0])
        self.display.blit(text2, [self.w-200, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _hmove(self, direction):
        x = self.hhead.x
        y = self.hhead.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.hhead = Point(x, y)