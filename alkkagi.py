import pygame, sys, os, json, win32api, math
from pygame import gfxdraw

pygame.init()

window = pygame.display.set_mode((960, 960))
pygame.display.set_caption("Alkkagi")
clock = pygame.time.Clock()
settings = json.load(open(".\\data\\settings.json", "r", encoding="utf8"))

# ==================================================
# ==================================================

def font(fontname, size):
    return pygame.font.Font(f".\\data\\fonts\\{fontname}.ttf",size)

lastleft1 = 0
lastleft2 = 0
lastright2 = 0
lastright1 = 0
lastmiddle1 = 0
class mouse:
    def middlebtdown():
        global lastmiddle1
        middle = win32api.GetKeyState(0x04)
        if int(lastmiddle1) >=0 and middle <0:
            lastmiddle1 = middle
            return True
        else:
            lastmiddle1 = middle
            return False
    def rightbtdown():
        global lastright1
        right = win32api.GetKeyState(0x02)
        if int(lastright1) >= 0 and right <0:
            lastright1 = right
            return True
        else:
            lastright1=right
            return False
    def rightbtup():
        global lastright2
        right = win32api.GetKeyState(0x02)
        if int(lastright2) < 0 and right >=0:
            lastright2 = right
            return True
        else:
            lastright2=right
            return False
    def leftbtdown():
        global lastleft1
        left = win32api.GetKeyState(0x01)
        if int(lastleft1) >=0 and left <0:
            lastleft1 = left
            return True
        else:
            lastleft1 = left
            return False
    def leftbtup():
        global lastleft2
        left = win32api.GetKeyState(0x01)
        if int(lastleft2) < 0 and left >= 0:
            lastleft2 = left
            return True
        
        else:
            lastleft2 = left
            return False

# ==================================================
# ==================================================

def texload(path:str):
    return pygame.image.load(path).convert_alpha()

class textures:
    background = texload(".\\data\\background.png")
    white = texload(".\\data\\white.png")
    black = texload(".\\data\\black.png")

class al:
    def __init__(self, pos:tuple[int, int], team:bool, friction:float=1.) -> None:
        system.objects.append(self)

        self.pos = pos
        self.team = team # 0 is black, 1 is white
        self.friction = friction
        self.texture = textures.white if team else textures.black
        self.size = int(self.texture.get_size()[0]/2)
        self.radius = 20
        self.hovering = False
        self.activated = False
        self.moving = False
        self.speed = (0, 0)
        self.SpeedMultiplier = 2.5
        self.cos = 0
        self.sin = 0
        self.collide = 5

        pass

    def draw(self, **settings):
        mpos = settings.get("mpos", (0, 0))
        fps = settings.get("fps", 120)

        # ====================== Calc ======================
        distance = system.distance(mpos, self.pos)
        cos = -(mpos[0]-self.pos[0])/distance
        sin = (self.pos[1]-mpos[1])/distance
        multiplier = min(distance, 150)

        if (fps>0 and self.moving):
            self.speed = (self.speed[0]-self.cos*self.friction*150/fps, self.speed[1]-self.sin*self.friction*150/fps)
            self.pos = (self.pos[0]+self.speed[0]/fps*self.SpeedMultiplier, self.pos[1]+self.speed[1]/fps*self.SpeedMultiplier)
        # ==================================================

        # ===================== Detect =====================
        if (distance <= 20):
            self.hovering = True
            if (mouse.leftbtdown()): self.activated = True
        else: self.hovering = False
        if (pygame.mouse.get_pressed()[0] == 0):
            if (self.activated):
                self.speed = (multiplier*cos*self.SpeedMultiplier, multiplier*sin*self.SpeedMultiplier)
                self.cos, self.sin = cos, sin
                self.moving = True

            self.activated = False

        if (self.moving and (abs(self.speed[0]) <= 10 and abs(self.speed[1])<=10)): self.moving = False

        # if( not self.moving): self.cos, self.sin = 0, 0

        #check if die
        if (self.pos[0] <= 48 or self.pos[0]>= 912 or self.pos[1]<= 48 or self.pos[1]>= 912):
            system.objects.remove(self)


        # ==================================================

        if (self.activated): pygame.draw.aaline(window, (255, 0, 0), self.pos, (self.pos[0]-cos*multiplier,self.pos[1]-sin*multiplier))
        window.blit(self.texture, (self.pos[0]-self.size, self.pos[1]-self.size))
        if (self.hovering and not self.activated): gfxdraw.aacircle(window, int(self.pos[0]), int(self.pos[1]), 20, (0, 255, 0))

        if (self in system.calculated or self.collide < 5):
            self.collide += 1
            return
        for object in system.objects:
            if (object == self): continue

            d = system.distance(self.pos, object.pos)
            if (d <= self.size * 2):
                system.calculated.append(object)
                self.collide = 0
                object.collide = 0

                # collide!
                momentom = (abs(self.speed[0])+abs(self.speed[1]))/self.SpeedMultiplier
                self.speed = (0, 0)
                tan = (self.pos[1]-object.pos[1])/(self.pos[0]-object.pos[0]+0.1**10)
                ObjectAngle = math.atan(tan) * (180/math.pi) - 90

                cos = math.cos(ObjectAngle*(math.pi/180))
                sin = math.sin(ObjectAngle*(math.pi/180))

                if (sin > 0 and cos > 0): ObjectAngle = 360 - ObjectAngle
                elif (sin > 0 and cos < 0): ObjectAngle = 180 - ObjectAngle
                elif (sin < 0 and cos < 0): ObjectAngle = 180 - ObjectAngle
                elif (sin < 0 and cos > 0): ObjectAngle = 0 - ObjectAngle

                movingangle = math.atan(self.sin/(self.cos+0.1**10)) * (180/math.pi)

                # adjust
                sinm = 1
                cosm = 1
                if (self.sin > 0 and self.cos > 0): movingangle = 360 - movingangle
                elif (self.sin > 0 and self.cos < 0): movingangle = 180 - movingangle; sinm = -1
                elif (self.sin < 0 and self.cos < 0): movingangle = 180 - movingangle
                elif (self.sin < 0 and self.cos > 0): movingangle = 0 - movingangle; cosm = -1; sinm = -1

                difference = (movingangle - ObjectAngle)
                NewAngle = ObjectAngle - difference
                NewRadian = NewAngle*(math.pi/180)
                Ncos = math.cos(NewRadian)
                Nsin = math.sin(NewRadian)

                NewObjectAngle = movingangle + difference
                NewObjectRadian = NewObjectAngle*(math.pi/180)
                NOcos = math.cos(NewObjectRadian)
                NOsin = math.sin(NewObjectRadian)

                # pygame.draw.aaline(window, (0, 255, 0), self.pos, (self.pos[0]-100*cos, self.pos[1]-100*sin))
                # pygame.draw.aaline(window, (255, 0, 0), self.pos, (self.pos[0]+100*self.cos, self.pos[1]+100*self.sin))
                # pygame.draw.aaline(window, (0, 255, 255), self.pos, (self.pos[0]+100*Ncos, self.pos[1]+100*Nsin))
                # pygame.draw.aaline(window, (0, 255, 255), object.pos, (object.pos[0]+100*NOcos, object.pos[1]+100*NOsin))

                self.cos = Ncos
                self.sin = -1*Nsin



                object.cos = NOcos*cosm
                object.sin = -1*NOsin*sinm
                object.moving = True
                object.speed = (momentom*object.cos*object.SpeedMultiplier/2, momentom*object.sin*object.SpeedMultiplier/2)
                object.pos = (object.pos[0]+object.speed[0]/fps*object.SpeedMultiplier, object.pos[1]+object.speed[1]/fps*object.SpeedMultiplier)
                self.moving = True
                self.speed = (momentom*self.cos*self.SpeedMultiplier/2, momentom*self.sin*self.SpeedMultiplier/2)
                self.pos = (self.pos[0]+self.speed[0]/fps*self.SpeedMultiplier, self.pos[1]+self.speed[1]/fps*self.SpeedMultiplier)
        return

class system:
    fps = settings.get("fps", 120)
    objects= []
    calculated = []

    class draw:

        def rrect(surface,rect,color,radius=0.4):
            rect         = pygame.Rect(rect)
            color        = pygame.Color(*color)
            alpha        = color.a
            color.a      = 0
            pos          = rect.topleft
            rect.topleft = 0,0
            rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)
            circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
            pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
            circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)
            radius              = rectangle.blit(circle,(0,0))
            radius.bottomright  = rect.bottomright
            rectangle.blit(circle,radius)
            radius.topright     = rect.topright
            rectangle.blit(circle,radius)
            radius.bottomleft   = rect.bottomleft
            rectangle.blit(circle,radius)

            rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
            rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

            rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
            rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
            return surface.blit(rectangle,pos)
        
        def aacircle(surface, x, y, radius, color):
            gfxdraw.aacircle(surface, x, y, radius, color)
            gfxdraw.filled_circle(surface, x, y, radius, color)

        def text(text, font, window, x, y, cenleft="center", color=(0,0,0)):
            text_obj = font.render(text, True, color)
            text_rect=text_obj.get_rect()
            if(cenleft == "center"):
                text_rect.centerx = x
                text_rect.centery = y
            elif(cenleft == "left"):
                text_rect.left=x
                text_rect.top=y
            elif(cenleft == "right"):
                text_rect.right=x
                text_rect.top=y
            elif(cenleft == "cenleft"):
                text_rect.left=x
                text_rect.centery=y
            elif(cenleft == "cenright"):
                text_rect.right=x
                text_rect.centery=y
            window.blit(text_obj, text_rect)

        def gettsize(text,font):
            return font.render(text,True,(0,0,0)).get_rect().size
    def distance(pos1:tuple[int, int], pos2:tuple[int, int]) -> tuple[int, int]:
        return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)**0.5 + 0.1**5
    
    def reset():
        for object in system.objects: del object
        system.objects = []
        al((240, 720), 0)
        al((480, 720), 0)
        al((720, 720), 0)
        al((240, 240), 1)
        al((480, 240), 1)
        al((720, 240), 1)

    def event():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    system.reset()

    def display():
        mpos = pygame.mouse.get_pos()

        window.blit(textures.background, (0, 0))
        system.calculated = []
        for object in system.objects:
            object.draw(
                mpos=mpos,
                fps = clock.get_fps()
            )

    def run():
        while __name__ == "__main__":
            system.event()
            system.display()
            clock.tick(system.fps)
            pygame.display.update()


pygame.display.set_icon(textures.black)
system.reset()
system.run()