import pygame as pg
import os
from random import randint
from .. import tool
from .. import constants as c


class Zombie(pg.sprite.Sprite):
    def __init__(self, x, y, name, head_group=None, helmetHealth=0, helmetType2Health=0, bodyHealth=c.NORMAL_HEALTH, lostHeadHealth=c.LOSTHEAD_HEALTH, damage=c.ZOMBIE_ATTACK_DAMAGE, canSwim=False):
        pg.sprite.Sprite.__init__(self)

        self.name = name
        self.frames = []
        self.frame_index = 0
        self.loadImages()
        self.frame_num = len(self.frames)

        self.image = self.frames[self.frame_index]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.helmetHealth = helmetHealth
        self.helmetType2Health = helmetType2Health
        self.health = bodyHealth + lostHeadHealth
        self.lostHeadHealth = lostHeadHealth
        self.damage = damage
        self.dead = False
        self.lostHead = False
        self.canSwim = canSwim
        self.swimming = False
        self.helmet = (self.helmetHealth > 0)
        self.helmetType2 = (self.helmetType2Health > 0)
        self.head_group = head_group

        self.walk_timer = 0
        self.animate_timer = 0
        self.attack_timer = 0
        self.state = c.WALK
        self.animate_interval = 150
        self.walk_animate_interval = 180
        self.attack_animate_interval = 100
        self.lostHead_animate_interval = 180
        self.die_animate_interval = 50
        self.boomDie_animate_interval = 100
        self.ice_slow_ratio = 1
        self.ice_slow_timer = 0
        self.hit_timer = 0
        self.speed = 1
        self.freeze_timer = 0
        self.losthead_timer = 0
        self.is_hypno = False  # the zombie is hypo and attack other zombies when it ate a HypnoShroom

    def loadFrames(self, frames, name, colorkey=c.BLACK):
        frame_list = tool.GFX[name]
        rect = frame_list[0].get_rect()
        width, height = rect.w, rect.h
        if name in tool.ZOMBIE_RECT:
            data = tool.ZOMBIE_RECT[name]
            x, width = data['x'], data['width']
        else:
            x = 0
        for frame in frame_list:
            frames.append(tool.get_image(frame, x, 0, width, height, colorkey))

    def update(self, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handleState()
        self.updateIceSlow()
        self.animation()

    def handleState(self):
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.ATTACK:
            self.attacking()
        elif self.state == c.DIE:
            self.dying()
        elif self.state == c.FREEZE:
            self.freezing()

    # ?????????????????????
    def checkToDie(self, framesKind):
        if self.health <= 0:
            self.setDie()
            return True
        elif self.health <= self.lostHeadHealth:
            if not self.lostHead:
                self.changeFrames(framesKind)
                self.setLostHead()
                return True
            else:
                self.health -= (self.current_time - self.losthead_timer) / 40
                self.losthead_timer = self.current_time
                return False
        else:
            return False

    def walking(self):
        if self.checkToDie(self.losthead_walk_frames):
            return

        # ??????????????????
        if self.canSwim:
            # ??????????????????
            # ???????????????
            if self.rect.right <= c.MAP_POOL_FRONT_X:
                # ??????????????????????????????????????????
                if self.rect.right - 25 >= c.MAP_POOL_OFFSET_X:
                    # ????????????????????????
                    if not self.swimming:
                        self.swimming = True
                        self.changeFrames(self.swim_frames)
                        # ??????????????????
                        pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "zombieEnteringWater.ogg")).play()
                        # ???????????????????????????
                        if self.helmet:
                            if self.helmetHealth <= 0:
                                self.helmet = False
                            else:
                                self.changeFrames(self.helmet_swim_frames)
                        if self.helmetType2:
                            if self.helmetType2Health <= 0:
                                self.helmetType2 = False
                            else:
                                self.changeFrames(self.helmet_swim_frames)
                    # ????????????????????????
                    else:
                        if self.helmet:
                            if self.helmetHealth <= 0:
                                self.changeFrames(self.swim_frames)
                                self.helmet = False
                        if self.helmetType2:
                            if self.helmetType2Health <= 0:
                                self.changeFrames(self.swim_frames)
                                self.helmetType2 = False
                # ?????????????????????????????????????????????
                else:
                    if self.swimming:
                        self.changeFrames(self.walk_frames)
                        self.swimming = False
                        # ???????????????????????????
                        if self.helmet:
                            if self.helmetHealth <= 0:
                                self.helmet = False
                            else:
                                self.changeFrames(self.helmet_walk_frames)
                        if self.helmetType2:
                            if self.helmetType2Health <= 0:
                                self.helmetType2 = False
                            else:
                                self.changeFrames(self.helmet_walk_frames)
                    if self.helmet:
                        if self.helmetHealth <= 0:
                            self.helmet = False
                            self.changeFrames(self.walk_frames)
                    if self.helmetType2:
                        if self.helmetType2Health <= 0:
                            self.helmetType2 = False
                            self.changeFrames(self.walk_frames)
            elif self.is_hypno and self.rect.right > c.MAP_POOL_FRONT_X + 55:   # ??????????????????????????????
                if self.swimming:
                    self.changeFrames(self.walk_frames)
                if self.helmet:
                    if self.helmetHealth <= 0:
                        self.changeFrames(self.walk_frames)
                        self.helmet = False
                    elif self.swimming: # ??????????????????????????????
                        self.changeFrames(self.helmet_walk_frames)
                if self.helmetType2:
                    if self.helmetType2Health <= 0:
                        self.changeFrames(self.walk_frames)
                        self.helmetType2 = False
                    elif self.swimming: # ??????????????????????????????
                        self.changeFrames(self.helmet_walk_frames)
                self.swimming = False
            # ??????????????????
            else:
                if self.helmetHealth <= 0 and self.helmet:
                    self.changeFrames(self.walk_frames)
                    self.helmet = False
                if self.helmetType2Health <= 0 and self.helmetType2:
                    self.changeFrames(self.walk_frames)
                    self.helmetType2 = False
        # ???????????????????????????
        else:
            if self.helmetHealth <= 0 and self.helmet:
                self.changeFrames(self.walk_frames)
                self.helmet = False
            if self.helmetType2Health <= 0 and self.helmetType2:
                self.changeFrames(self.walk_frames)
                self.helmetType2 = False
        if (self.current_time - self.walk_timer) > (c.ZOMBIE_WALK_INTERVAL * self.getTimeRatio()):
            self.walk_timer = self.current_time
            if self.is_hypno:
                self.rect.x += 1
            else:
                self.rect.x -= 1

    def attacking(self):
        if self.checkToDie(self.losthead_attack_frames):
            return
        
        if self.helmetHealth <= 0 and self.helmet:
            self.changeFrames(self.attack_frames)
            self.helmet = False
        if self.helmetType2Health <= 0 and self.helmetType2:
            self.changeFrames(self.attack_frames)
            self.helmetType2 = False
            if self.name == c.NEWSPAPER_ZOMBIE:
                self.speed = 2.5
        if ((self.current_time - self.attack_timer) > (c.ATTACK_INTERVAL * self.getAttackTimeRatio())) and (not self.lostHead):
            if self.prey.health > 0:
                if self.prey_is_plant:
                    self.prey.setDamage(self.damage, self)
                else:
                    self.prey.setDamage(self.damage)
                
                # ??????????????????
                pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "zombieAttack.ogg")).play()
            self.attack_timer = self.current_time

        if self.prey.health <= 0:
            self.prey = None
            self.setWalk()

    def dying(self):
        pass

    def freezing(self):
        if self.old_state == c.WALK:
            if self.checkToDie(self.losthead_walk_frames):
                return
        else:
            if self.checkToDie(self.losthead_attack_frames):
                return

        if (self.current_time - self.freeze_timer) >= c.MIN_FREEZE_TIME + randint(0, 2000):
            self.setWalk()
            # ????????????????????????????????????
            self.ice_slow_timer = self.freeze_timer + 10000 # ?????????????????? + ???????????????20 s???????????????10 s??????????????????+10 s
            self.ice_slow_ratio = 2

    def setLostHead(self):
        self.losthead_timer = self.current_time
        self.lostHead = True
        self.animate_interval = self.lostHead_animate_interval
        if self.head_group is not None:
            self.head_group.add(ZombieHead(self.rect.centerx, self.rect.bottom))

    def changeFrames(self, frames):
        '''change image frames and modify rect position'''
        self.frames = frames
        self.frame_num = len(self.frames)
        self.frame_index = 0

        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def animation(self):
        if self.state == c.FREEZE:
            self.image.set_alpha(192)
            return

        if (self.current_time - self.animate_timer) > (self.animate_interval * self.getTimeRatio()):
            self.frame_index += 1
            if self.frame_index >= self.frame_num:
                if self.state == c.DIE:
                    self.kill()
                    return
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.image = self.frames[self.frame_index]
        if self.is_hypno:
            self.image = pg.transform.flip(self.image, True, False)
        self.mask = pg.mask.from_surface(self.image)
        if (self.current_time - self.hit_timer) >= 200:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(192)

    def getTimeRatio(self):
        return (self.ice_slow_ratio / self.speed)   # ???????????????????????????????????????????????????????????????????????????????????????

    def getAttackTimeRatio(self):
        return self.ice_slow_ratio  # ????????????????????????????????????

    def setIceSlow(self):
        # ????????????????????????????????????????????????
        if self.ice_slow_ratio == 1:
            pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "freeze.ogg")).play()

        # when get a ice bullet damage, slow the attack or walk speed of the zombie
        self.ice_slow_timer = self.current_time
        self.ice_slow_ratio = 2

    def updateIceSlow(self):
        if self.ice_slow_ratio > 1:
            if (self.current_time - self.ice_slow_timer) > c.ICE_SLOW_TIME:
                self.ice_slow_ratio = 1

    def setDamage(self, damage, effect=None, damageType=c.ZOMBIE_COMMON_DAMAGE):
        # ??????????????????
        if effect == c.BULLET_EFFECT_ICE:
            if damageType == c.ZOMBIE_DEAFULT_DAMAGE:   # ????????????????????????????????????????????????
                if not self.helmetType2:
                    self.setIceSlow()
            else:
                self.setIceSlow()
        # ??????
        elif effect == c.BULLET_EFFECT_UNICE:
            if damageType == c.ZOMBIE_DEAFULT_DAMAGE:   # ????????????????????????????????????????????????
                if not self.helmetType2:
                    self.ice_slow_ratio = 1
            else:
                self.ice_slow_ratio = 1

        if damageType == c.ZOMBIE_DEAFULT_DAMAGE:   # ??????????????????????????????
            # ????????????????????????????????????
            if self.helmetType2:
                self.helmetType2Health -= damage
                if self.helmetType2Health <= 0:
                    if self.helmet:
                        self.helmetHealth += self.helmetType2Health # ??????self.helmetType2Health??????????????????
                        self.helmetType2Health = 0  # ?????????????????????
                        if self.helmetHealth <= 0:
                            self.health += self.helmetHealth
                            self.helmetHealth = 0   # ?????????????????????
                    else:
                        self.health += self.helmetType2Health
                        self.helmetType2Health = 0
            elif self.helmet:   # ????????????????????????????????????????????????
                self.helmetHealth -= damage
                if self.helmetHealth <= 0:
                    self.health += self.helmetHealth
                    self.helmetHealth = 0   # ?????????????????????
            else:   # ????????????
                self.health -= damage
        elif damageType == c.ZOMBIE_COMMON_DAMAGE:  # ????????????????????????????????????????????????????????????????????????
            if self.helmet:   # ??????????????????
                self.helmetHealth -= damage
                if self.helmetHealth <= 0:
                    self.health += self.helmetHealth
                    self.helmetHealth = 0   # ?????????????????????
            else:   # ??????????????????
                self.health -= damage
        elif damageType == c.ZOMBIE_RANGE_DAMAGE:
            # ????????????????????????????????????
            if self.helmetType2:
                self.helmetType2Health -= damage
                if self.helmetType2Health <= 0:
                    if self.helmet:
                        self.helmetHealth -= damage # ?????????????????????????????????????????????
                        self.helmetHealth += self.helmetType2Health # ??????self.helmetType2Health??????????????????
                        self.helmetType2Health = 0  # ?????????????????????
                        if self.helmetHealth <= 0:
                            self.health += self.helmetHealth
                            self.helmetHealth = 0   # ?????????????????????
                    else:
                        self.health -= damage   # ?????????????????????????????????????????????
                        self.health += self.helmetType2Health
                        self.helmetType2Health = 0
                else:
                    if self.helmet:
                        self.helmetHealth -= damage
                        if self.helmetHealth <= 0:
                            self.health += self.helmetHealth
                            self.helmetHealth = 0   # ?????????????????????
                    else:
                        self.health -= damage
            elif self.helmet:   # ????????????????????????????????????????????????
                self.helmetHealth -= damage
                if self.helmetHealth <= 0:
                    self.health += self.helmetHealth
                    self.helmetHealth = 0   # ?????????????????????
            else:   # ????????????
                self.health -= damage
        elif damageType == c.ZOMBIE_ASH_DAMAGE:
            self.health -= damage   # ??????????????????
        elif damageType == c.ZOMBIE_WALLNUT_BOWLING_DANMAGE:
            # ??????????????????????????????????????????
            if self.helmetType2:
                # ???????????????????????????????????????????????????????????????3????????????
                self.helmetType2Health -= int(damage * 0.8)
            elif self.helmet:   # ????????????????????????????????????????????????
                self.helmetHealth -= damage
            else:   # ????????????
                self.health -= damage
        else:
            print('??????????????????????????????????????????????????????????????????????????????')
            setDamage(damage, effect=effect, damageType=c.ZOMBIE_DEAFULT_DAMAGE)
        
        # ??????????????????              
        self.hit_timer = self.current_time

    def setWalk(self):
        self.state = c.WALK
        self.animate_interval = self.walk_animate_interval

        if self.helmet or self.helmetType2: # ??????????????????????????????????????????????????????
            self.changeFrames(self.helmet_walk_frames)
        elif self.lostHead:
            self.changeFrames(self.losthead_walk_frames)
        else:
            self.changeFrames(self.walk_frames)

        if self.canSwim:
            if self.rect.right <= c.MAP_POOL_FRONT_X:
                self.swimming = True
                self.changeFrames(self.swim_frames)
                # ???????????????????????????
                if self.helmet:
                    if self.helmetHealth <= 0:
                        self.changeFrames(self.swim_frames)
                        self.helmet = False
                    else:
                        self.changeFrames(self.helmet_swim_frames)
                if self.helmetType2:
                    if self.helmetType2Health <= 0:
                        self.changeFrames(self.swim_frames)
                        self.helmetType2 = False
                    else:
                        self.changeFrames(self.helmet_swim_frames)

    def setAttack(self, prey, is_plant=True):
        self.prey = prey  # prey can be plant or other zombies
        self.prey_is_plant = is_plant
        self.state = c.ATTACK
        self.attack_timer = self.current_time
        self.animate_interval = self.attack_animate_interval

        if self.helmet or self.helmetType2: # ??????????????????????????????????????????????????????
            self.changeFrames(self.helmet_attack_frames)
        elif self.lostHead:
            self.changeFrames(self.losthead_attack_frames)
        else:
            self.changeFrames(self.attack_frames)

    def setDie(self):
        self.state = c.DIE
        self.animate_interval = self.die_animate_interval
        self.changeFrames(self.die_frames)

    def setBoomDie(self):
        self.health = 0
        self.state = c.DIE
        self.animate_interval = self.boomDie_animate_interval
        self.changeFrames(self.boomdie_frames)

    def setFreeze(self, ice_trap_image):
        self.old_state = self.state
        self.state = c.FREEZE
        self.freeze_timer = self.current_time
        self.ice_trap_image = ice_trap_image
        self.ice_trap_rect = ice_trap_image.get_rect()
        self.ice_trap_rect.centerx = self.rect.centerx
        self.ice_trap_rect.bottom = self.rect.bottom

    def drawFreezeTrap(self, surface):
        if self.state == c.FREEZE:
            surface.blit(self.ice_trap_image, self.ice_trap_rect)

    def setHypno(self):
        self.is_hypno = True
        self.setWalk()
        # ??????????????????
        pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "hypnoed.ogg")).play()


class ZombieHead(Zombie):
    def __init__(self, x, y):
        Zombie.__init__(self, x, y, c.ZOMBIE_HEAD, 0)
        self.state = c.DIE

    def loadImages(self):
        self.die_frames = []
        die_name = self.name
        self.loadFrames(self.die_frames, die_name)
        self.frames = self.die_frames

    def setWalk(self):
        self.animate_interval = 100


class NormalZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.NORMAL_ZOMBIE, head_group)

    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.walk_frames

# ????????????
class ConeHeadZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.CONEHEAD_ZOMBIE, head_group, helmetHealth=c.CONEHEAD_HEALTH)

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames


class BucketHeadZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.BUCKETHEAD_ZOMBIE, head_group, helmetHealth=c.BUCKETHEAD_HEALTH)

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames


class FlagZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.FLAG_ZOMBIE, head_group)
        self.speed = 1.25

    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.walk_frames


class NewspaperZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.NEWSPAPER_ZOMBIE, head_group, helmetType2Health=c.NEWSPAPER_HEALTH)
        self.speedUp = False

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.lostnewspaper_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = self.name + 'NoPaper'
        attack_name = self.name + 'NoPaperAttack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        lostnewspaper_name = self.name + 'LostNewspaper'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.lostnewspaper_frames,
                      self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, lostnewspaper_name,
                     die_name, boomdie_name]

        for i, name in enumerate(name_list):
            if name in {c.BOOMDIE, lostnewspaper_name}:
                color = c.BLACK
            else:
                color = c.WHITE
            self.loadFrames(frame_list[i], name, color)

        self.frames = self.helmet_walk_frames

    def walking(self):
        if self.checkToDie(self.losthead_walk_frames):
            return

        if self.helmetType2Health <= 0 and self.helmetType2:
            self.changeFrames(self.lostnewspaper_frames)
            self.helmetType2 = False
            # ????????????????????????
            pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "newspaperRip.ogg")).play()
        if (self.current_time - self.walk_timer) > (c.ZOMBIE_WALK_INTERVAL * self.getTimeRatio()):
            self.walk_timer = self.current_time
            if self.frames == self.lostnewspaper_frames:
                pass
            elif self.is_hypno:
                self.rect.x += 1
            else:
                self.rect.x -= 1

    def animation(self):
        if self.state == c.FREEZE:
            self.image.set_alpha(192)
            return

        if (self.current_time - self.animate_timer) > (self.animate_interval * self.getTimeRatio()):
            self.frame_index += 1
            if self.frame_index >= self.frame_num:
                if self.state == c.DIE:
                    self.kill()
                    return
                elif self.frames == self.lostnewspaper_frames and (not self.speedUp):
                    self.changeFrames(self.walk_frames)
                    self.speedUp = True
                    self.speed = 2.65
                    # ??????????????????????????????
                    pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "newspaperZombieAngry.ogg")).play()
                    return
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.image = self.frames[self.frame_index]
        if self.is_hypno:
            self.image = pg.transform.flip(self.image, True, False)
        self.mask = pg.mask.from_surface(self.image)
        if (self.current_time - self.hit_timer) >= 200:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(192)

class FootballZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.FOOTBALL_ZOMBIE, head_group, helmetHealth=c.FOOTBALL_HELMET_HEALTH)
        self.speed = 1.88
        self.animate_interval = 50
        self.walk_animate_interval = 50
        self.attack_animate_interval = 60
        self.lostHead_animate_interval = 180
        self.die_animate_interval = 150

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = self.name + 'LostHelmet'
        attack_name = self.name + 'LostHelmetAttack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames

class DuckyTubeZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.DUCKY_TUBE_ZOMBIE, head_group, canSwim=True)

    def loadImages(self):
        self.walk_frames = []
        self.swim_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        swim_name = self.name + 'Swim'
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHead'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.swim_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, swim_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.walk_frames

class ConeHeadDuckyTubeZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.CONEHEAD_DUCKY_TUBE_ZOMBIE, head_group, helmetHealth=c.CONEHEAD_HEALTH ,canSwim=True)
        
    def loadImages(self):
        self.helmet_walk_frames = []
        self.walk_frames = []
        self.helmet_swim_frames = []
        self.swim_frames = []
        self.helmet_attack_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_swim_name = self.name + 'Swim'
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.DUCKY_TUBE_ZOMBIE
        swim_name = c.DUCKY_TUBE_ZOMBIE + 'Swim'
        attack_name = c.DUCKY_TUBE_ZOMBIE + 'Attack'
        losthead_walk_name = c.DUCKY_TUBE_ZOMBIE + 'LostHead'
        losthead_attack_name = c.DUCKY_TUBE_ZOMBIE + 'LostHead'
        die_name = c.DUCKY_TUBE_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_swim_frames, self.helmet_attack_frames, self.walk_frames, self.swim_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_swim_name, helmet_attack_name, walk_name, swim_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames


class BucketHeadDuckyTubeZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.BUCKETHEAD_DUCKY_TUBE_ZOMBIE, head_group, helmetHealth=c.BUCKETHEAD_HEALTH ,canSwim=True)
        
    def loadImages(self):
        self.helmet_walk_frames = []
        self.walk_frames = []
        self.helmet_swim_frames = []
        self.swim_frames = []
        self.helmet_attack_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_swim_name = self.name + 'Swim'
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.DUCKY_TUBE_ZOMBIE
        swim_name = c.DUCKY_TUBE_ZOMBIE + 'Swim'
        attack_name = c.DUCKY_TUBE_ZOMBIE + 'Attack'
        losthead_walk_name = c.DUCKY_TUBE_ZOMBIE + 'LostHead'
        losthead_attack_name = c.DUCKY_TUBE_ZOMBIE + 'LostHead'
        die_name = c.DUCKY_TUBE_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_swim_frames, self.helmet_attack_frames, self.walk_frames, self.swim_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_swim_name, helmet_attack_name, walk_name, swim_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames


class ScreenDoorZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.SCREEN_DOOR_ZOMBIE, head_group, helmetType2Health=c.SCREEN_DOOR_HEALTH)

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.helmet_walk_frames


class PoleVaultingZombie(Zombie):
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.POLE_VAULTING_ZOMBIE, head_group=head_group, bodyHealth=c.POLE_VAULTING_HEALTH, lostHeadHealth=c.POLE_VAULTING_LOSTHEAD_HEALTH)
        self.speed = 1.88
        self.jumped = False
        self.jumping = False

    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []
        self.walk_before_jump_frames = []
        self.jump_frames = []

        walk_name = self.name + 'WalkAfterJump'
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE
        walk_before_jump_name = self.name
        jump_name = self.name + 'Jump'

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames,
                      self.walk_before_jump_frames, self.jump_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name,
                     walk_before_jump_name, jump_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.walk_before_jump_frames

    def setJump(self, successfullyJumped, jumpX):
        if not self.jumping:
            self.jumping = True
            self.changeFrames(self.jump_frames)
            self.successfullyJumped = successfullyJumped
            self.jumpX = jumpX
            # ??????????????????
            pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "polevaultjump.ogg")).play()

    def animation(self):
        if self.state == c.FREEZE:
            self.image.set_alpha(192)
            return

        if (self.current_time - self.animate_timer) > (self.animate_interval * self.getTimeRatio()):
            self.frame_index += 1
            if self.state == c.WALK:
                if self.jumping and (not self.jumped):
                    if self.successfullyJumped:
                        self.rect.x -= 5
                    else:
                        self.rect.x -= 1
            if self.frame_index >= self.frame_num:
                if self.state == c.DIE:
                    self.kill()
                    return
                self.frame_index = 0
                if self.jumping and (not self.jumped):
                    self.changeFrames(self.walk_frames)
                    if self.successfullyJumped:
                        self.rect.centerx = self.jumpX
                    self.jumped = True
                    self.speed = 1.04
            self.animate_timer = self.current_time

        self.image = self.frames[self.frame_index]
        if self.is_hypno:
            self.image = pg.transform.flip(self.image, True, False)
        self.mask = pg.mask.from_surface(self.image)
        if (self.current_time - self.hit_timer) >= 200:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(192)
    
    def setWalk(self):
        self.state = c.WALK
        self.animate_interval = self.walk_animate_interval
        if self.jumped:
            self.changeFrames(self.walk_frames)
        
    def setFreeze(self, ice_trap_image):
        # ??????????????????????????????????????????
        if (self.jumping and (not self.jumped)):
            self.ice_slow_timer = self.current_time
            self.ice_slow_ratio = 2
        else:
            self.freeze_timer = self.current_time
            self.old_state = self.state
            self.state = c.FREEZE
            self.ice_trap_image = ice_trap_image
            self.ice_trap_rect = ice_trap_image.get_rect()
            self.ice_trap_rect.centerx = self.rect.centerx
            self.ice_trap_rect.bottom = self.rect.bottom


# ?????????????????????????????????
class Zomboni(Zombie):
    def __init__(self, x, y, plant_group, map, IceFrozenPlot):
        Zombie.__init__(self, x, y, c.ZOMBONI, bodyHealth=c.ZOMBONI_HEALTH)
        self.plant_group = plant_group
        self.map = map
        self.IceFrozenPlot = IceFrozenPlot
        self.die_animate_interval = 70
        self.boomDie_animate_interval = 150
        # ????????????????????????
        pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "zomboni.ogg")).play()

    def loadImages(self):
        self.walk_frames = []
        self.walk_damaged1_frames = []
        self.walk_damaged2_frames = []
        self.losthead_walk_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        walk_damaged1_name = self.name + 'Damaged1'
        walk_damaged2_name = self.name + 'Damaged2'
        losthead_walk_name = self.name + 'Damaged2'
        die_name = self.name + 'Die'
        boomdie_name = self.name + 'BoomDie'

        frame_list = [  self.walk_frames, self.walk_damaged1_frames,
                        self.walk_damaged2_frames, self.losthead_walk_frames,
                        self.die_frames, self.boomdie_frames]
        name_list = [   walk_name, walk_damaged1_name,
                        walk_damaged2_name, losthead_walk_name,
                        die_name, boomdie_name]

        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name)

        self.frames = self.walk_frames

    def updateIceSlow(self):
        # ????????????????????????
        self.ice_slow_ratio = 1

    def setFreeze(self, ice_trap_image):
        pass

    def walking(self):
        if self.checkToDie(self.losthead_walk_frames):
            return

        if self.health <= c.ZOMBONI_DAMAGED2_HEALTH:
            self.changeFrames(self.walk_damaged2_frames)
        elif self.health <= c.ZOMBONI_DAMAGED1_HEALTH:
            self.changeFrames(self.walk_damaged1_frames)

        if (self.current_time - self.walk_timer) > (c.ZOMBIE_WALK_INTERVAL * self.getTimeRatio()) and (not self.lostHead):
            self.walk_timer = self.current_time
            if self.is_hypno:
                self.rect.x += 1
            else:
                self.rect.x -= 1

            # ???????????????
            for plant in self.plant_group:
                # ??????????????????????????????
                if ((plant.name not in {c.SPIKEWEED})
                and (self.rect.centerx <= plant.rect.right <= self.rect.right)):
                    # ????????????????????????????????????????????????
                    plant.health -= 8000

            # ??????
            mapX, mapY = self.map.getMapIndex(self.rect.right - 40, self.rect.bottom)
            if 0 <= mapX < c.GRID_X_LEN:
                if c.ICE_FROZEN_PLOT not in self.map.map[mapY][mapX]:
                    x, y = self.map.getMapGridPos(mapX, mapY)
                    self.plant_group.add(self.IceFrozenPlot(x, y))
                    self.map.map[mapY][mapX][c.MAP_PLANT].add(c.ICE_FROZEN_PLOT)

            self.speed = max(0.6, 1.5 - (c.GRID_X_LEN + 1 - mapX)*0.225)

    def setDie(self):
        self.state = c.DIE
        self.animate_interval = self.die_animate_interval
        self.changeFrames(self.die_frames)
        # ????????????????????????
        pg.mixer.Sound(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) ,"resources", "sound", "zomboniExplosion.ogg")).play()

