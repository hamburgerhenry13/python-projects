import pygame
import os
import sys
import random

class image:
    def __init__(self, name, x, y, width, height):  # 檔名、X座標、Y座標、寬度、高度
        image = pygame.image.load(os.path.join('Assets', name))
        location = [x, y]
        size = [width, height]
        self.image = pygame.transform.scale(image, size)
        self.location = location
        self.rect = pygame.Rect(x, y, width, height)

    def rotate(self, angle):
        pygame.transform.rotate(self.image, angle)

    def resize(self, new_size):
        self.image = pygame.transform.scale(self.image, new_size)

    def relocate(self, new_location):
        self.location = new_location

    def draw(self):
        WIN.blit(self.image, self.location)

class background(image):
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)
        
class button(image):
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)

    def button_click(self, event):
        botton_clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_position = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_position[0], mouse_position[1]):
                botton_clicked = True  
            else:
                botton_clicked = False
        return botton_clicked

class character(image):  #
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)

    def movement_unlimited(self, keys_pressed):
        VEL = 5  # 按一次移五格
        if keys_pressed[pygame.K_LEFT] and self.location[0] - VEL > 0:  # left
            self.location[0] -= VEL
        if keys_pressed[pygame.K_RIGHT] and self.location[0] + VEL + self.rect.width < WIDTH:
            self.location[0] += VEL
        if keys_pressed[pygame.K_UP] and self.location[1] - VEL > 0:
            self.location[1] -= VEL
        if keys_pressed[pygame.K_DOWN] and self.location[1] + VEL + self.rect.height < HEIGHT:
            self.location[1] += VEL

    def movement_limited(self, event, walls, boxes, border, traps, bad_guys):  # 角色移動
        VEL = 50
        global ll
        global rr  
        global uu
        global dd
        global target_loc
        global pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                _ = [self.location[0] - VEL, self.location[1]]
                now = pygame.time.get_ticks()
                if now - pressed[1] > 1000 and self.cannot_move_left(walls, boxes, border, traps, bad_guys) is False:
                    target_loc = self.location[0] - VEL
                    ll = True
                    pressed[0] = pressed[1]
                    pressed[1] = now

            if event.key == pygame.K_RIGHT:
                now = pygame.time.get_ticks()
                _ = [self.location[0] + VEL, self.location[1]]
                if now - pressed[1] > 1000 and self.cannot_move_right(walls, boxes, border, traps, bad_guys) is False:
                    target_loc = self.location[0] + VEL
                    rr = True
                    pressed[0] = pressed[1]
                    pressed[1] = now
                    
            if event.key == pygame.K_UP:
                
                _ = [self.location[0], self.location[1] - VEL]
                now = pygame.time.get_ticks()
                if now - pressed[1] > 1000 and self.cannot_move_up(walls, boxes, border, traps, bad_guys) is False:
                    target_loc = self.location[1] - VEL
                    uu = True
                    pressed[0] = pressed[1]
                    pressed[1] = now
                    
            if event.key == pygame.K_DOWN:
                now = pygame.time.get_ticks()
               
                _ = [self.location[0], self.location[1] + VEL]
                if now - pressed[1] > 1000 and self.cannot_move_down(walls, boxes, border, traps, bad_guys) is False:
                    target_loc = self.location[1] + VEL
                    dd = True
                    pressed[0] = pressed[1]
                    pressed[1] = now

    def moving(self):
        global ll
        global rr
        global uu
        global dd
        global target_loc
        now = pygame.time.get_ticks()
        dis = now - pressed[1]
        if ll:
            a = dis//16
            _ = (-(300)/(30**3)*a*(a - 30))
            if _ >= 0:
                self.location[0] -= _
            else:
                self.location[0] = target_loc
                ll = False
                target_loc = 0
        if rr:
            a = dis//16
            _ = (-(300)/(30**3)*a*(a - 30))
            if _ >= 0:
                self.location[0] += _
            else:
                self.location[0] = target_loc
                rr = False
                target_loc = 0
        if uu:
            a = dis//16
            _ = (-(300)/(30**3)*a*(a - 30))
            if _ >= 0:
                self.location[1] -= _
            else:
                self.location[1] = target_loc
                uu = False
                target_loc = 0
        if dd:
            a = dis//16
            _ = (-(300)/(30**3)*a*(a - 30))
            if _ >= 0:
                self.location[1] += _
            else:
                self.location[1] = target_loc
                dd = False
                target_loc = 0

    def cannot_move_left(self, walls, boxes, border, traps, bad_guys):
        VEL = 50
        for x in walls.locations:
            if self.location[0] - VEL == x.location[0] and self.location[1] == x.location[1]:
                return True
        for x in boxes.locations:
            if self.location[0] - VEL == x.location[0] and self.location[1] == x.location[1]:
                for y in boxes.locations:
                    if self.location[0] - 2*VEL == y.location[0] and self.location[1] == y.location[1]:
                        return True
                for z in walls.locations:
                    if self.location[0] - 2*VEL == z.location[0] and self.location[1] == z.location[1]:
                        return True
                for m in traps.locations:
                    if self.location[0] - 2*VEL == m.location[0] and self.location[1] == m.location[1]:
                        return True
                for n in bad_guys.locations:
                    if self.location[0] - 2*VEL == n.location[0] and self.location[1] == n.location[1]:
                        return True 
                if self.location[0] - 2*VEL < border.left:
                    return True
        if self.location[0] - VEL < border.left:
            return True
        
        return False

    def cannot_move_right(self, walls, boxes, border, traps, bad_guys):
        VEL = 50
        for x in walls.locations:
            if self.location[0] + VEL == x.location[0] and self.location[1] == x.location[1]:
                return True
        for x in boxes.locations:
            if self.location[0] + VEL == x.location[0] and self.location[1] == x.location[1]:
                for y in boxes.locations:
                    if self.location[0] + 2*VEL == y.location[0] and self.location[1] == y.location[1]:
                        return True
                for z in walls.locations:
                    if self.location[0] + 2*VEL == z.location[0] and self.location[1] == z.location[1]:
                        return True
                for m in traps.locations:
                    if self.location[0] - 2*VEL == m.location[0] and self.location[1] == m.location[1]:
                        return True
                for n in bad_guys.locations:
                    if self.location[0] - 2*VEL == n.location[0] and self.location[1] == n.location[1]:
                        return True 
                if self.location[0] + 2*VEL >= border.right:
                    return True
        if self.location[0] + VEL >= border.right:
            return True
        return False

    def cannot_move_up(self, walls, boxes, border, traps, bad_guys):
        VEL = 50
        for x in walls.locations:
            if self.location[1] - VEL == x.location[1] and self.location[0] == x.location[0]:
                return True
        for x in boxes.locations:
            if self.location[1] - VEL == x.location[1] and self.location[0] == x.location[0]:
                for y in boxes.locations:
                    if self.location[1] - 2*VEL == y.location[1] and self.location[0] == y.location[0]:
                        return True
                for z in walls.locations:
                    if self.location[1] - 2*VEL == z.location[1] and self.location[0] == z.location[0]:
                        return True
                if self.location[1] - 2*VEL < border.top:
                    return True
                for m in traps.locations:
                    if self.location[0] - 2*VEL == m.location[0] and self.location[1] == m.location[1]:
                        return True
                for n in bad_guys.locations:
                    if self.location[0] - 2*VEL == n.location[0] and self.location[1] == n.location[1]:
                        return True 
        if self.location[1] - VEL < border.top:
            return True
        return False

    def cannot_move_down(self, walls, boxes, border, traps, bad_guys):
        VEL = 50
        for x in walls.locations:
            if self.location[1] + VEL == x.location[1] and self.location[0] == x.location[0]:
                return True
        for x in boxes.locations:
            if self.location[1] + VEL == x.location[1] and self.location[0] == x.location[0]:
                for y in boxes.locations:
                    if self.location[1] + 2*VEL == y.location[1] and self.location[0] == y.location[0]:
                        return True
                for z in walls.locations:
                    if self.location[1] + 2*VEL == z.location[1] and self.location[0] == z.location[0]:
                        return True
                for m in traps.locations:
                    if self.location[0] - 2*VEL == m.location[0] and self.location[1] == m.location[1]:
                        return True
                for n in bad_guys.locations:
                    if self.location[0] - 2*VEL == n.location[0] and self.location[1] == n.location[1]:
                        return True 
                if self.location[1] - 2*VEL >= border.bottom - VEL:
                    return True
        if self.location[1] - VEL >= border.bottom - 2*VEL:
            return True
        return False


class trap(image):
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)
    
    def trapped(self, Character):
        if Character.location == self.location:
            return True

class traps:
    def __init__(self, locations):
        for i in range(len(locations)):
            locations[i] = trap('trap.png', locations[i][0], locations[i][1], 50, 50)
        self.locations = locations

    def get_trapped(self, Character):
        for trap in self.locations:
            if trap.trapped(Character) is True:
                return True
        return False

    def draw_traps(self):
        for x in self.locations:
            x.draw()
            
class box(image):  
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)

    def box_moving(self, Character):
        VEL = 50
        _ = Character.location[0] - self.location[0]
        __ = Character.location[1] - self.location[1]
        if ll:
            if 0 < _ < 50 and __ == 0:
                self.location[0] -= 50 - _
                
        elif rr:
            if 0 < -_ < 50 and __ == 0:
                self.location[0] += 50 + _
                
        elif uu:
            if 0 < __ < 50 and _ == 0:
                self.location[1] -= 50 - __

        elif dd:
            if 0 < -__ < 50 and _ == 0:
                self.location[1] += 50 + __

        elif self.location[0] % 50 != 25:
            a = (self.location[0] // 50)*50 + 25
            b = (self.location[0] // 50 + 1)*50 + 25
            if b - self.location[0] > self.location[0] - a:
                self.location[0] = a
            else:
                self.location[0] = b
        elif self.location[1] % 50 != 25:
            a = (self.location[1] // 50)*50 + 25
            b = (self.location[1] // 50 + 1)*50 + 25
            if b - self.location[1] > self.location[1] - a:
                self.location[1] = a
            else:
                self.location[1] = b

class boxes:
    def __init__(self, locations):
        for i in range(len(locations)):
            _ = box('boxes.png', locations[i][0], locations[i][1], 50, 50)
            locations[i] = _
        self.locations = locations

    def draw_boxes(self):
        for x in self.locations:
            x.draw()

    def moving_boxes(self, Character):
        for x in self.locations:
            x.box_moving(Character)

class bad_guy(trap):
    def __init__(self, name, x, y, width, height):
        trap.__init__(self, name, x, y, width, height)
        self.alpha = 255

    def bad_guy_caught(self, Character):
        if self.location == Character.location:
            return True
        return False
            
        
class bad_guys:
    def __init__(self, locations):
        status = []
        for i in range(len(locations)):
            locations[i] = bad_guy('bad_guy.png', locations[i][0], locations[i][1], 50, 50)
            status.append([False, False])
        self.locations = locations
        self.status = status

    def draw_bad_guys(self):
        for x in self.locations:
            x.draw()

    def update_status(self, Character):
        result = -1
        for i in range(len(self.locations)):
            self.status[i][0] = self.status[i][1]
            self.status[i][1] = self.locations[i].bad_guy_caught(Character)
            if self.status[i] == [False, True] or self.status[i] == [True, True]:
                result = i
        return result

    def fading(self, Character): 
        _ = self.update_status(Character)
        if _ != -1:
            self.locations[_].alpha -= 10
            __ = self.locations[_].alpha
            self.locations[_].image.set_alpha(__)
            if __ <= 0:
                self.locations.pop(_)
                self.status.pop(_)

class wall(image):
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)

    def collide_with_wall(self, Target_location):
        if self.location == Target_location:
            return True
        return False

class walls:
    def __init__(self, locations):
        for i in range(len(locations)):
            locations[i] = wall('wall.png', locations[i][0], locations[i][1], 50, 50)
        self.locations = locations

    def draw_walls(self):
        for x in self.locations:
            x.draw()

class hearts:
    def __init__(self, number):
        self.number = number
        _ = pygame.font.SysFont('georgia', 40)
        self.font = _.render(str(self.number), 1, WHITE)

    def draw(self):
        _ = pygame.font.SysFont('georgia', 40)
        self.font = _.render(str(self.number), 1, WHITE)
        WIN.blit(self.font, (50, 540))

    def deducting(self, Traps, Character):
        global refer
        refer['ll'][0] = refer['ll'][1]
        refer['rr'][0] = refer['rr'][1]
        refer['uu'][0] = refer['uu'][1]
        refer['dd'][0] = refer['dd'][1]
        refer['traps'][0] = refer['traps'][1]
        refer['ll'][1] = ll
        refer['rr'][1] = rr
        refer['uu'][1] = uu
        refer['dd'][1] = dd
        refer['traps'][1] = Traps.get_trapped(Character)
        _ = list(refer.values())
        for i in range(len(_)-1):
            if _[i] == [False, True]:
                return True
        for j in _[-1]:
            if j == [False, True]:
                return True
        return False

    def deducting_heart(self, Traps, Character):
        if self.deducting(Traps, Character) is True:
            self.number -= 1

class level_fonts:
    def __init__(self, which_level):
        self.level = which_level
        _ = pygame.font.SysFont('georgia', 40)
        self.font = _.render('LEVEL ' + str(which_level), 1, WHITE)

    def draw(self, acc_fps):
        _ = pygame.font.SysFont('georgia', 40)
        self.font = _.render('LEVEL ' + str(self.level), 1, WHITE)
        WIN.blit(self.font, (210, -40 + acc_fps*3))

class girl(image):  #
    def __init__(self, name, x, y, width, height):
        image.__init__(self, name, x, y, width, height)

    def winning(self, Character, number_of_hearts):
        VEL = 50

        
        
        _ = [self.location[0] - Character.location[0], self.location[1] - Character.location[1]]
        for i in range(2):
            if _[i] < 0:
                _[i] = -_[i]
        if number_of_hearts > 0 and _ == [VEL, 0] or _ == [0, VEL]:
            return True
        return False

def fader(next_background, which_level=-1):
    clock = pygame.time.Clock()
    run = True
    alpha = 0
    alpha2 = 0
    sr = WIN.get_rect()
    veil = pygame.Surface(sr.size)
    next_veil = pygame.Surface(sr.size)
    veil.fill(BLACK)
    next_veil.blit(next_background.image, next_background.location)
    acc_fps = 0
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
        if alpha <= 120 and alpha2 <= 120:
            veil.set_alpha(alpha)
            next_veil.set_alpha(alpha2)
            alpha += 1
        elif alpha > 120 and alpha2 <= 120:
            next_veil.set_alpha(alpha2)
            alpha2 += 1
        else:
            if acc_fps <= 60 and which_level != -1:
                level_fonts(which_level).draw(acc_fps)
                acc_fps += 1
            else:
                run = False
        WIN.blit(veil, (0, 0))
        WIN.blit(next_veil, (0, 0))
        pygame.display.update()


def winning_screen(question, wrong_choice1, wrong_choice2, wrong_choice3, \
                   correct_choice, wrong_choice1_white, wrong_choice2_white, \
                   wrong_choice3_white, correct_choice_white):
    global not_passed
    global losing
    clock = pygame.time.Clock()
    run = True
    acc_fps = 0
    not_passed = True
    while run:
        acc_fps += 1
        clock.tick(FPS)  # 設定螢幕幀率為60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
            
            if wrong_choice1.button_click(event) or wrong_choice2.button_click(event)\
               or wrong_choice3.button_click(event):
                run = False
                print(111)
                gameover_screen()
            if correct_choice.button_click(event):
                run = False
                not_passed = False
            pause_screen(event)
        GIRL.relocate([450, 450])
        GIRL.resize([150, 150])
        mouse_position = pygame.mouse.get_pos()  # 找到滑鼠位置
        WIN.fill(WHITE)
        WINNING_SCREEN_BACKGROUND.draw()
        question.draw()
        if wrong_choice1.rect.collidepoint(mouse_position[0], mouse_position[1]):
           wrong_choice1_white.draw()
        else:
            wrong_choice1.draw()
        if wrong_choice2.rect.collidepoint(mouse_position[0], mouse_position[1]):
           wrong_choice2_white.draw()
        else:
            wrong_choice2.draw()
        if wrong_choice3.rect.collidepoint(mouse_position[0], mouse_position[1]):
           wrong_choice3_white.draw()
        else:
            wrong_choice3.draw()
        if correct_choice.rect.collidepoint(mouse_position[0], mouse_position[1]):
           correct_choice_white.draw()
        else:
            correct_choice.draw()
        GIRL.draw()
        
        pygame.display.update()

def gameover_screen():
    
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
            if RESTART_BUTTON.button_click(event):
                run = False
            if BACK_BUTTON.button_click(event):
                main()
                
        GAMEOVER_BACKGROUND.draw()
        mouse_position = pygame.mouse.get_pos()
              
        if BACK_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            BACK_BUTTON_WHITE.draw()
        else:
            BACK_BUTTON.draw()
        if RESTART_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            RESTART_BUTTON_WHITE.draw()
        else:
            RESTART_BUTTON.draw()
        pygame.display.update()

def congrats():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
                
        GAMEOVER_BACKGROUND.draw()
        mouse_position = pygame.mouse.get_pos()
              
        if BACK_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            BACK_BUTTON_WHITE.draw()
        else:
            BACK_BUTTON.draw()
        if RESTART_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            RESTART_BUTTON_WHITE.draw()
        else:
            RESTART_BUTTON.draw()
        pygame.display.update()    

pygame.init()

WIDTH, HEIGHT = 600, 600
FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PBCtaker")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

MAIN_SCREEN_BACKGROUND = background('main_screen.png', 0, 0, WIDTH, HEIGHT)
LEVEL1_BACKGROUND = background('lv1_background.png', 0, 0, WIDTH, HEIGHT)
PAUSE_BACKGROUND = background('pause_screen.png', 0, 0, WIDTH, HEIGHT)
WINNING_SCREEN_BACKGROUND = background('question box.png', 0, 0, WIDTH, HEIGHT)
GAMEOVER_BACKGROUND = background('game over.png', 0, 0, WIDTH, HEIGHT)
CONGRATS_BACKGROUND = background('congrats.png')

KNIGHT = character('knight.png', 375, 175, 50, 50)
GIRL = girl('girl.png', 425, 425, 50, 50)

START_BUTTON = button('Game Start.png', 210, 310, 180, 75)
QUIT_BUTTON = button('Quit.png', 210, 400, 180, 75)
START_BUTTON_WHITE = button('Game Start White.png', 210, 310, 180, 75)
QUIT_BUTTON_WHITE = button('Quit White.png', 210, 400, 180, 75)
CONTINUE_BUTTON = button('continue.png', 315, 323, 72, 72)
CONTINUE_BUTTON_WHITE = button('continue white.png', 315, 323, 72, 72)
BACK_BUTTON = button('back.png', 223, 323, 72, 72)
BACK_BUTTON_WHITE = button('back white.png', 223, 323, 72, 72)
RESTART_BUTTON = button('restart.png', 315, 323, 72, 72)
RESTART_BUTTON_WHITE = button('restart white.png', 315, 323, 72, 72)

HEALTH = hearts(20)
HEALTH_BAR = image('heart_bar.png', 25, 525, 100, 100)

SCOPE = pygame.Rect(100, 200, 400, 300)

L1_Q = image('Q1.png', 120, 150, 450, 80)
L1_A1 = button('Q1-1.png', 150, 280, 170, 65)
L1_A1W = button('Q1-1W.png', 150, 280, 170, 65)
L1_A2 = button('Q1-2.png', 215, 345, 170, 65)
L1_A2W = button('Q1-2W.png',  215, 345, 170, 65)
L1_A3 = button('Q1-3.png', 150, 410, 170, 65)
L1_A3W = button('Q1-3W.png', 150, 410, 170, 65)
L1_A4 = button('Q1-4.png', 215, 475, 170, 65)
L1_A4W = button('Q1-4W.png', 215, 475, 170, 65)

L2_Q = image('Q2.png', 120, 150, 450, 80)
L2_A1 = button('Q2-1.png', 150, 280, 170, 65)
L2_A1W = button('Q2-1W.png', 150, 280, 170, 65)
L2_A2 = button('Q2-2.png', 215, 345, 170, 65)
L2_A2W = button('Q2-2W.png',  215, 345, 170, 65)
L2_A3 = button('Q2-3.png', 150, 410, 170, 65)
L2_A3W = button('Q2-3W.png', 150, 410, 170, 65)
L2_A4 = button('Q2-4.png', 215, 475, 170, 65)
L2_A4W = button('Q2-4W.png', 215, 475, 170, 65)

L3_Q = image('Q3.png', 120, 150, 450, 80)
L3_A1 = button('Q3-1.png', 150, 280, 170, 65)
L3_A1W = button('Q3-1W.png', 150, 280, 170, 65)
L3_A2 = button('Q3-2.png', 215, 345, 170, 65)
L3_A2W = button('Q3-2W.png',  215, 345, 170, 65)
L3_A3 = button('Q3-3.png', 150, 410, 170, 65)
L3_A3W = button('Q3-3W.png', 150, 410, 170, 65)
L3_A4 = button('Q3-4.png', 215, 475, 170, 65)
L3_A4W = button('Q3-4W.png', 215, 475, 170, 65)

def draw_main_screen():
    clock = pygame.time.Clock()
    KNIGHT.relocate([375, 175])
    run = True
    while run:
        clock.tick(FPS)  # 設定螢幕幀率為60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
            if QUIT_BUTTON.button_click(event):
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()
            if START_BUTTON.button_click(event):
                run = False
        mouse_position = pygame.mouse.get_pos()  # 找到滑鼠位置
        WIN.fill(WHITE)
        MAIN_SCREEN_BACKGROUND.draw()
        if QUIT_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            QUIT_BUTTON_WHITE.draw()
        else:
            QUIT_BUTTON.draw()

        if START_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
            START_BUTTON_WHITE.draw()
        else:
            START_BUTTON.draw()
            
        pygame.display.update()

def pause_screen(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            clock = pygame.time.Clock()
            run = True
            while run:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()  # 按叉叉會把視窗關掉
                        sys.exit()
                    if CONTINUE_BUTTON.button_click(event):
                        run = False
                    if BACK_BUTTON.button_click(event):
                        main()
                
                PAUSE_BACKGROUND.draw()
                mouse_position = pygame.mouse.get_pos()
              
                if BACK_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
                    BACK_BUTTON_WHITE.draw()
                else:
                    BACK_BUTTON.draw()
                if CONTINUE_BUTTON.rect.collidepoint(mouse_position[0], mouse_position[1]):
                    CONTINUE_BUTTON_WHITE.draw()
                else:
                    CONTINUE_BUTTON.draw()
                pygame.display.update()
            
def draw_level1():
    global losing
    global pressed
    global refer
    global ll
    global uu
    global dd
    global rr
    L1_WALLS = walls([[175,125],[275,125],[325,125],[375,125],[425,125],[175,175],[225,175],[275,175],[425,175],
                  [125,225],[425,225],[125,275],[375,275],[75,325],[225,325],[275,325],[325,325],[375,325],
                  [425,325],[75,375],[425,375], [475,375],[75,425],[475,425]])
    L1_BOXES = boxes([[175,375],[175,425],[275,425],[325,375]])
    L1_BAD_GUYS = bad_guys([[225,275],[375,375],[325,275]])
    L1_BORDER = pygame.Rect(75, 125, 450, 400)
    clock = pygame.time.Clock()
    run = True
    pressed = [0, 0]
    KNIGHT.relocate([375, 175])
    GIRL.relocate([425, 425])
    GIRL.resize([50, 50])
    refer = {'ll':[False, False], 'rr':[False, False], 'uu':[False, False], 'dd':[False, False], \
             'traps':[False, False], 'bad_guys':L1_BAD_GUYS.status}
    ll = False
    rr = False
    uu = False
    dd = False
    target_loc = 0
    HEALTH.number = 23
    acc_fps = 0
    losing = False
    while run:
        acc_fps += 1
        clock.tick(FPS)  # 設定螢幕幀率為60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()

            KNIGHT.movement_limited(event, L1_WALLS, L1_BOXES, L1_BORDER, traps([]), L1_BAD_GUYS)
            pause_screen(event)

        if GIRL.winning(KNIGHT, HEALTH.number) is True:
            run = False

        if HEALTH.number <= 0:
            run = False
            losing = True
            gameover_screen()
            
        KNIGHT.moving()

        L1_BOXES.moving_boxes(KNIGHT)
        L1_BAD_GUYS.fading(KNIGHT) 
        
        HEALTH.deducting_heart(traps([]), KNIGHT)

        WIN.fill(WHITE)
        LEVEL1_BACKGROUND.draw()
        HEALTH_BAR.draw()
        
        L1_WALLS.draw_walls()
        L1_BOXES.draw_boxes()
        L1_BAD_GUYS.draw_bad_guys()
        HEALTH.draw()
        KNIGHT.draw()
        GIRL.draw()
        
        keys_pressed = pygame.key.get_pressed()  # knowing in every fps that what key's been pressed
        pygame.display.update()

def draw_level2():
    global losing
    global pressed
    global refer
    global ll
    global uu
    global dd
    global rr
    L2_WALLS = walls([[125,125],[175,125],[225,125],[275,125],[325,125],[375,125],[125,175],[375,175],[425,175],[475,175], \
    [75,225],[125,225],[225,225],[475,225],[75,275],[225,275],[275,275],[475,275],[75,325],[225,325],[275,325],[475,325], \
    [75,375],[225,375],[275,375],[475,375],[75,425],[125,425],[175,425],[225,425],[275,425],[475,425]])
    L2_BOXES = boxes([[325,275],[375,275],[425,275]])
    L2_TRAPS = traps([[275,225],[325,225],[175,275],[325,275],[375,275],[375,325]])
    L2_BAD_GUYS = bad_guys([[175,225],[375,375],[425,425]])
    L2_BORDER = pygame.Rect(75, 125, 450, 400)
    clock = pygame.time.Clock()
    run = True
    pressed = [0, 0]
    refer = {'ll':[False, False], 'rr':[False, False], 'uu':[False, False], 'dd':[False, False], \
             'traps':[False, False], 'bad_guys':L2_BAD_GUYS.status}
    ll = False
    rr = False
    uu = False
    dd = False
    target_loc = 0
    HEALTH.number = 20
    acc_fps = 0
    losing = False
    KNIGHT.relocate([125, 375])
    GIRL.relocate([325, 425])
    GIRL.resize([50, 50])
    while run:
        acc_fps += 1
        clock.tick(FPS)  # 設定螢幕幀率為60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()

            KNIGHT.movement_limited(event, L2_WALLS, L2_BOXES, L2_BORDER, L2_TRAPS, L2_BAD_GUYS)
            pause_screen(event)
            
        if GIRL.winning(KNIGHT, HEALTH.number) is True:
            run = False

        if HEALTH.number <= 0:
            run = False
            losing = True
            gameover_screen()
            
        KNIGHT.moving()

        L2_BOXES.moving_boxes(KNIGHT)
        L2_BAD_GUYS.fading(KNIGHT) 
        
        HEALTH.deducting_heart(traps([]), KNIGHT)

        WIN.fill(WHITE)
        LEVEL1_BACKGROUND.draw()
        HEALTH_BAR.draw()
        
        L2_WALLS.draw_walls()
        L2_BOXES.draw_boxes()
        L2_BAD_GUYS.draw_bad_guys()
        HEALTH.draw()
        KNIGHT.draw()
        GIRL.draw()
        
        keys_pressed = pygame.key.get_pressed()  # knowing in every fps that what key's been pressed
        pygame.display.update()    

def draw_level3():
    global losing
    global pressed
    global refer
    global ll
    global uu
    global dd
    global rr
    L3_WALLS = walls([[225,100],[275,100],[325,100],[375,100],[175,150],[425,150],
    [175,200],[225,200],[275,200],[325,200],[425,200],[125,250],[475,250],[125,300],[225,300],[325,300],[475,300],
    [75,350],[125,350],[425,350],[125,400],[225,400],[325,400],[25,400],[25,450],[75,500],
    [125,500],[175,500],[225,500],[275,500],[325,500],[375,500],[425,400],[425,450]])
    L3_TRAPS = traps([[175,300],[175,400],[225,250],[275,250],[275,300],[275,400],[325,350],[375,350]])
    L3_BAD_GUYS = bad_guys([[275,350],[325,450]])
    L3_BOXES = boxes([])
    L3_BORDER = pygame.Rect(75, 125, 450, 400)
    clock = pygame.time.Clock()
    run = True
    pressed = [0, 0]
    refer = {'ll':[False, False], 'rr':[False, False], 'uu':[False, False], 'dd':[False, False], \
             'traps':[False, False], 'bad_guys':L3_BAD_GUYS.status}
    ll = False
    rr = False
    uu = False
    dd = False
    target_loc = 0
    HEALTH.number = 20
    acc_fps = 0
    losing = False
    KNIGHT.relocate([425,250])
    GIRL.relocate([325,150])
    GIRL.resize([50, 50])
    while run:
        acc_fps += 1
        clock.tick(FPS)  # 設定螢幕幀率為60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # 按叉叉會把視窗關掉
                sys.exit()

            KNIGHT.movement_limited(event, L3_WALLS, L3_BOXES, L3_BORDER, L3_TRAPS, L3_BAD_GUYS)
            pause_screen(event)
            
        if GIRL.winning(KNIGHT, HEALTH.number) is True:
            run = False

        if HEALTH.number <= 0:
            run = False
            losing = True
            gameover_screen()
            
        KNIGHT.moving()

        L3_BOXES.moving_boxes(KNIGHT)
        L3_BAD_GUYS.fading(KNIGHT) 
        
        HEALTH.deducting_heart(L3_TRAPS, KNIGHT)

        WIN.fill(WHITE)
        LEVEL1_BACKGROUND.draw()
        HEALTH_BAR.draw()
        
        L3_WALLS.draw_walls()
        L3_BOXES.draw_boxes()
        L3_BAD_GUYS.draw_bad_guys()
        HEALTH.draw()
        KNIGHT.draw()
        GIRL.draw()
        
        keys_pressed = pygame.key.get_pressed()  # knowing in every fps that what key's been pressed
        pygame.display.update()    


def main():
    global not_passed
    not_passed = True
    draw_main_screen()

    while not_passed:
        fader(LEVEL1_BACKGROUND, 1)
        draw_level1()
        if losing is False:
            winning_screen(L1_Q, L1_A1, L1_A3, \
                       L1_A4, L1_A2, L1_A1W, \
                       L1_A3W, L1_A4W, L1_A2W)
    not_passed = True
    while not_passed:
        fader(LEVEL1_BACKGROUND, 2)
        draw_level2()
        fader(WINNING_SCREEN_BACKGROUND)
        if losing is False:
            winning_screen(L2_Q, L2_A2, L2_A3, \
                       L2_A4, L2_A1, L2_A2W, \
                       L2_A3W, L2_A4W, L2_A1W)
    not_passed = True

    while not_passed:
        fader(LEVEL1_BACKGROUND, 3)
        draw_level3()
        fader(WINNING_SCREEN_BACKGROUND)
        if losing is False:
            winning_screen(L3_Q, L3_A2, L3_A3, \
                       L3_A4, L3_A1, L3_A2W, \
                       L3_A3W, L3_A4W, L3_A1W)

if __name__ == "__main__":
    main()
