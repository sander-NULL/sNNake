'''
Created on May 11, 2022

@author: sander
'''

import pygame
import itertools
import random
import numpy as np

'''
To do:
1. perfect game notification
2. order of drawing stuff
'''

pygame.init()
 
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
grey = (150,150,150)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

#dimension of unit block
snake_block = 10

#speed of the snake
snake_speed = 5

#offsets of playing field in pixels
offset_x = 20
offset_y = 35

#dimensions of playing field in blocks
field_width = 20
field_height = 20

#dimensions of display
dis_width = field_width * snake_block + 4 + 2 * offset_x + 400
dis_height = field_height * snake_block + 4 + offset_y + 10
 
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('SNNake')
 
clock = pygame.time.Clock()
 
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
block_font = pygame.font.SysFont("comicsansms", 13) 

def sigmoid(x):
    return 1/(1+np.exp(-x))

# create version of sigmoid for vectors and matrices
vsigmoid = np.vectorize(sigmoid)

def draw_score(score):
    value = score_font.render("Score: " + str(score), True, white)
    dis.blit(value, [offset_x, 0])


def draw_snake(snake_block, snake_list):
    i = 230
    sign = -1
    cnt = 0    
    for x in itertools.islice(reversed(snake_list), 1, None):
        pygame.draw.rect(dis, (i,i,i), [x[0], x[1], snake_block-1,snake_block-1])
        i += sign * 25
        if i <= 25 or i >= 230:
            sign *= -1
        cnt += 1
        foo = block_font.render(str(cnt), True, red)
        dis.blit(foo, [x[0],x[1]])
    for x in itertools.islice(reversed(snake_list),1):
        pygame.draw.rect(dis, white, [x[0], x[1], snake_block-1, snake_block-1]) 
 
def game():
    game_over = False
    game_close = False
 
    #create weight matrices
    #one input layer with 9 neurons
    #two hidden layers with 8 neurons
    #one output layer with 4 neurons
    '''W1 = np.random.uniform(-1, 1, (8,9))
    W2 = np.random.uniform(-1, 1, (8,8))
    W3 = np.random.uniform(-1, 1, (4,8))'''
    npzfile = np.load("test.npz")
    W1 = npzfile['W1']
    W2 = npzfile['W2']
    W3 = npzfile['W3']
    
    # set starting position and speed
    x1 = random.randrange(field_width) * snake_block + offset_x
    y1 = random.randrange(field_height) * snake_block + offset_y
    
    snake_Head = [x1, y1]
    x1_change = 0
    y1_change = 0
    usr_x1_change = 0
    usr_y1_change = 0
 
    snake_List = [snake_Head]
    Length_of_snake = 1
 
    # create random block for first food position and map it onto field blocks without snake blocks (which is just the head)
    # the following code enumerates <food_block> blocks excluding the ones belonging to the snake
    # starting from the top left corner
    food_block = random.randrange(field_width * field_height - Length_of_snake) + 1
    i = -1
    for j in range(food_block):
        i += 1
        while [offset_x + (i % field_width) * snake_block, offset_y + (i // field_width) * snake_block] in snake_List:
            i += 1
        foodx = offset_x + (i % field_width) * snake_block
        foody = offset_y + (i // field_width) * snake_block
    #foodx = random.randrange(field_width) * snake_block + offset_x
    #foody = random.randrange(field_height) * snake_block + offset_y
        
    #counter = 0
    while not game_close:
        #counter += 1
        while game_over == True:
            #dis.fill(blue)
            mesg = font_style.render("Game over! Press 'C' to play again or 'Q' to quit", True, white)
            draw_score(Length_of_snake - 1)
            pygame.display.update(dis.blit(mesg, [150, 0]))
 
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_close = True
                        game_over = False
                    if event.key == pygame.K_c:
                        game()

        #set input vector for ANN
        #(x1,y1) = coords of head
        #(snake_List[0][0], snake_List[0][1]) = coords of head
        #Length_of_snake = well...
        #(x1_change, y1_change) = direction of movement
        #(foodx, foody) = coords of food

        #first we normalize the inputvector
        #all points (x,y) are mapped in the square [-1, 1) x (-1, 1]
        #the asymmetry in the half open intervals is due to pyGame's coordinate system having the origin in the top left corner
        head_x_normalized = 2/field_width * (x1-offset_x)/snake_block - 1   #maps is to the range [-1, 1)
        head_y_normalized = 1 - 2/field_height * (y1-offset_y)/snake_block  #maps it to the range (-1, 1]
        tail_x_normalized = 2/field_width * (snake_List[0][0]-offset_x)/snake_block - 1     #maps is to the range [-1, 1)
        tail_y_normalized = 1 - 2/field_height * (snake_List[0][1]-offset_y)/snake_block    #maps it to the range (-1, 1]
        Los_normalized = Length_of_snake / (field_width*field_height)
        x1_change_normalized = x1_change/snake_block
        y1_change_normalized = y1_change/snake_block
        food_x_normalized = 2/field_width * (foodx-offset_x)/snake_block - 1    #maps is to the range [-1, 1)
        food_y_normalized = 1 - 2/field_height * (foody-offset_y)/snake_block   #maps it to the range (-1, 1]
        
        inputvector = np.array([head_x_normalized, head_y_normalized, tail_x_normalized, tail_y_normalized, Los_normalized, x1_change_normalized, y1_change_normalized, food_x_normalized, food_y_normalized, 1]).reshape(10,1)
        print("input = ")
        print(inputvector)
        
        #apply activation function to each entry
        layer1_output = np.tanh(np.matmul(W1, inputvector))

        #append a one to the vector for the bias
        layer1_output = np.append(layer1_output, 1)
        layer1_output = layer1_output.reshape(9,1)

        #apply activation function to each entry
        layer2_output = np.tanh(np.matmul(W2, layer1_output))

        #append a one to the vector for the bias
        layer2_output = np.append(layer2_output, 1)
        layer2_output = layer2_output.reshape(9,1)

        outputvector = vsigmoid(np.matmul(W3, layer2_output))

        #rescale outputvector to get probabilities
        total_sum = outputvector[0] + outputvector[1] + outputvector[2] + outputvector[3]
        outputvector = 1/total_sum * outputvector
        print("output = ")
        print(outputvector)
        
        #see what index contains maximal value
        key = np.argmax(outputvector)
        if (key == 0):
            #move left
            print('LEFT')
            if (x1_change == 0):
                usr_x1_change = -snake_block
                usr_y1_change = 0
        elif (key == 1):
            #move up
            print('UP')
            if (y1_change == 0):
                usr_y1_change = -snake_block
                usr_x1_change = 0
        elif (key == 2):
            #move right
            print('RIGHT')
            if (x1_change == 0):
                usr_x1_change = snake_block
                usr_y1_change = 0
        elif (key == 3):
            #move down
            print('DOWN')
            if (y1_change == 0):
                usr_y1_change = snake_block
                usr_x1_change = 0

       
        '''for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_close = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    #if snake moves vertically set user's request to move left
                    usr_x1_change = -snake_block
                    usr_y1_change = 0
                    #print("LEFT")
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    #if snake moves vertically set user's request to move right
                    usr_x1_change = snake_block
                    usr_y1_change = 0
                    #print("RIGHT")
                elif event.key == pygame.K_UP and y1_change == 0:
                    #if snake moves horizontally set user's request to move snake up
                    usr_y1_change = -snake_block
                    usr_x1_change = 0
                    #print("UP")
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    #if snake moves horizontally set user's request to move snake down
                    usr_y1_change = snake_block
                    usr_x1_change = 0
                    #print("DOWN")'''
        
        #change snake coordinates
        #change x1_change and y1_change only once per tick to prevent snake from instantly moving in opposite direction and hitting itself
        x1_change = usr_x1_change
        y1_change = usr_y1_change    
        x1 += x1_change
        y1 += y1_change

        #snake hits border check
        if x1 >= offset_x + field_width * snake_block or x1 < offset_x \
        or y1 >= offset_y + field_height * snake_block or y1 < offset_y:
            game_over = True
        
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]
 
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_over = True
                
        #draw background, border and food
        dis.fill(black)
        pygame.draw.rect(dis, white, [offset_x-3, offset_y-3, field_width * snake_block + 5, field_height * snake_block + 5] , 2)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block-1, snake_block-1])
 
        draw_snake(snake_block, snake_List)
        draw_score(Length_of_snake - 1)
 
        #update screen
        pygame.display.update()
        
        #check if snake ate food
        if x1 == foodx and y1 == foody:
            if field_width * field_height - Length_of_snake == 0:
                game_over = True
            else:
                #create random block for new food position and map it onto field blocks without snake blocks
                #the following code enumerates <food_block> blocks excluding the ones belonging to the snake
                #starting from the top left corner
                food_block = random.randrange(field_width * field_height - Length_of_snake) + 1
                i = -1
                for j in range(food_block):
                    i += 1
                    while [offset_x + (i % field_width) * snake_block, offset_y + (i // field_width) * snake_block] in snake_List:
                        i += 1
                foodx = offset_x + (i % field_width) * snake_block
                foody = offset_y + (i // field_width) * snake_block
                pygame.draw.rect(dis, green, [foodx, foody, snake_block-1, snake_block-1])
            Length_of_snake += 1
            draw_score(Length_of_snake - 1)
            pygame.display.update()      
        
        #pygame.image.save(dis, "SNNake" + str(counter) + ".jpg")
        clock.tick(snake_speed)
 
    pygame.quit()
    quit()

game()
