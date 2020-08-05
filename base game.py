# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:33:52 2020

@author: Talmar
"""

import numpy as np
from scipy.special import comb
import pygame
import math

Dwidth=800
Dheight=450

pygame.init()

window=pygame.display.set_mode((Dwidth,Dheight))
pygame.display.set_caption('Minesweeper')

class square():
    def __init__(self, x,y,width=25,height=25):
        self.width=width
        self.height=height
        self.grid_x=x
        self.grid_y=y
        self.pos_x=25+width*x
        self.pos_y=25+height*y
        self.mine=False
        self.clicked=False
        self.coord=(self.grid_x,self.grid_y)
        self.adj_unk=9
        self.adj_IDed=0
    def draw(self,win,color=(100,100,255)):
        if not self.clicked:
            pygame.draw.rect(win,color,(self.pos_x+1,self.pos_y+1,self.width-2,self.height-2),0)
    def get_number(self,grid):
        global x,y
        if self.mine:
            self.num='X'
        else:
            self.num=0
            for i in range(self.grid_x-1,self.grid_x+2):
                for j in range(self.grid_y-1,self.grid_y+2):
                    if -1<i<x and -1<j<y:
                        if grid[(i,j)].mine:
                            self.num=self.num+1
        font=pygame.font.SysFont('timesnewroman',16)
        self.surf=pygame.Surface([self.width-2,self.height-2])
        self.surf.fill((255,255,255))
        if self.num!=0:
            num_surf=font.render(str(self.num),0,(0,0,0))
            pos_x=int((self.width-2-num_surf.get_width())/2)
            pos_y=int((self.height-2-num_surf.get_height())/2)
            self.surf.blit(num_surf,(pos_x,pos_y))
    def show_num(self,win):
        win.blit(self.surf,(self.pos_x+1,self.pos_y+1))
    def is_over (self,pos):
        if pos[0]>self.pos_x and pos[0]<(self.pos_x+self.width):
            if pos[1]>self.pos_y and pos[1]<(self.pos_y+self.height):
                return True
        return False

def blank_grid(x,y):
    '''Creates a dictionary of possible positions. All false.'''
        #create space lables
    keys=list()
    for i in range(0,x):
        for j in range (0,y):
            keys.append((i,j))
    #create empty grid
    mine_grid={}
    for i in keys:
        mine_grid[i]=square(i[0],i[1])
    return mine_grid

def on_grid(pos):
    global x,y
    if pos[0]<25 or pos[0]>25*(x+1):
        return False
    elif pos[1]<25 or pos[1]>25*(y+1):
        return False
    else: return True

def lay_mines(mine_grid,mines,click):
    '''Randomly lays mines within grid. Leaves space surrounding first click.'''
    #identify safe squares around first click
    safes=list()
    for i in range(click[0]-1,click[0]+2):
        for j in range(click[1]-1,click[1]+2):
            safes.append((i,j))
    #select random set from grid spaces not in safes
    possible=list(mine_grid.keys())
    for i in safes:
        if i in possible:
            possible.remove(i)
        else: print(i)
    np.random.shuffle(possible)
    mine_spaces=possible[0:mines]
    for i in mine_spaces:
        mine_grid[i].mine=True
    return mine_grid

def click(grid,coord):
    if not grid[coord].clicked:
        grid[coord].clicked=True
        global x, y, run, window, stage, front, known_mines
        if coord in front: front.remove(coord)
        grid[coord].show_num(window)
        if grid[coord].num=='X':
            stage=9
            print('You lose')
            for key in grid:
                if grid[key].mine:
                    grid[key].show_num(window)
        elif grid[coord].num==0:
            for i in range(coord[0]-1,coord[0]+2):
                for j in range(coord[1]-1,coord[1]+2):
                    if -1<i<x and -1<j<y and not grid[(i,j)].clicked:
                        click(grid,(i,j))
        else:
            for i in range(coord[0]-1,coord[0]+2):
                for j in range(coord[1]-1,coord[1]+2):
                    if -1<i<x and -1<j<y and not grid[(i,j)].clicked and (i,j) not in known_mines:
                        front.add((i,j))
                        
                        
#define grid paramaters
x=30
y=16
mines=99

known_mines=set()
front=set()

grid=blank_grid(x,y)

#mine_grid=lay_mines(mine_grid,mines,first_click)

def redraw(hovering):
    global known_mines
    if stage==0:    
        for key in grid:
            if key==hovering:
                grid[key].draw(window,(150,150,255))
            else: grid[key].draw(window)
    elif stage==1 or stage==8:  
        for key in grid:
            if not grid[key].clicked:
                if key==hovering:
                    grid[key].draw(window,(150,150,255))
                elif key in known_mines:
                    grid[key].draw(window,(255,100,100))
                else: grid[key].draw(window)
                
                
                
hovering=None
stage=0
run=True
while run:
    redraw(hovering)
    pygame.display.update()
    pygame.time.delay(25)
    pos=pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        
        if event.type==pygame.MOUSEMOTION:
            if on_grid(pos):
                for key in grid:
                    if grid[key].is_over(pos):
                        hovering=grid[key].coord
            else: hovering=None

        if event.type==pygame.MOUSEBUTTONDOWN:
            if on_grid(pos):
                if stage==0:
                    for key in grid:
                        if grid[key].is_over(pos):
                            grid=lay_mines(grid,mines,key)
                            stage=1
                            for key2 in grid:
                                grid[key2].get_number(grid)
                            click(grid,key)
                if stage==1:
                    for key in grid:
                        if grid[key].is_over(pos):
                            if not grid[key].clicked:
                                click(grid,key)


pygame.quit()
#quit()








