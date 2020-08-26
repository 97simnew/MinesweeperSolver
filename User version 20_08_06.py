# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:33:52 2020

@author: 97simnew
"""

import numpy as np
from scipy.special import comb
import pygame
from copy import deepcopy

Dwidth=1065
Dheight=450

pygame.init()

window=pygame.display.set_mode((Dwidth,Dheight))
pygame.display.set_caption('Minesweeper')

class Button():
    def __init__(self,x,y,width,height,text=False,font_size=18):
        self.font_size=font_size
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.text=text
    def draw(self,win,color=(50,50,50)):
        pygame.draw.rect(win,(100,100,100),(self.x-2,self.y-2,self.width+4,self.height+4),0)
        pygame.draw.rect(win,color,(self.x,self.y,self.width,self.height),0)
        if self.text:
            font=pygame.font.SysFont('Sylfaen',self.font_size)
            text=font.render(self.text,True,(255,255,255))
            win.blit(text,((self.x+(self.width-text.get_width())/2),(self.y+(self.height-text.get_height())/2)))
    def is_over(self,pos):
        if pos[0]>self.x and pos[0]<(self.x+self.width):
            if pos[1]>self.y and pos[1]<(self.y+self.height):
                return True
        return False

class simple_sqr:
    def __init__(self,coord,num,adj_unk,adj_IDed):
        self.coord=coord
        self.num=num
        self.adj_unk=adj_unk
        self.adj_IDed=adj_IDed

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
        font=pygame.font.SysFont('timesnewroman',17)
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
    def count_adj(self,grid,known_mines):
        self.adj_unk=set()
        self.adj_IDed=0
        for i in range(self.grid_x-1,self.grid_x+2):
            for j in range(self.grid_y-1,self.grid_y+2):
                if -1<i<x and -1<j<y and (i,j) in known_mines:
                    self.adj_IDed=self.adj_IDed+1
                elif -1<i<x and -1<j<y and not grid[(i,j)].clicked:
                    self.adj_unk.add((i,j))


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
    np.random.shuffle(possible)
    mine_spaces=possible[0:mines]
    for i in mine_spaces:
        mine_grid[i].mine=True
    return mine_grid

def click(grid,coord):
    if not grid[coord].clicked:
        grid[coord].clicked=True
        global x, y, window, stage, front, known_mines, prob_dict
        grid[coord].count_adj(grid,known_mines)
        if coord in front: front.remove(coord)
        grid[coord].show_num(window)
        if grid[coord].num=='X':
            stage=9
            print('You lose')
            if coord in prob_dict:
                print(coord,'prob:',prob_dict[coord])
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
                        
                        
def solving(grid,known_mines,initial=False):
    global stage
    '''The first stage of this function (within the Done loop) looks for squares that can be
    identified as definitely or defiely not mines, and loops until it stops making progress.
    The second stage (within the completely_Done loop) runs a semi-local probability function
    which can identify squares as either definitely mines or definitely not mines, as well as
    listing possible local distributions. The third stage (within the perfectly_Done) loop
    combines these local distributions with the total number of mines and number of unseen
    squares remaining to obtain definitive probabilities for every unclicked square.'''
    perfectly_Done=False
    while not perfectly_Done:
        perfectly_Done=True
        completely_Done=False
        while not completely_Done:
            completely_Done=True
            Done=False
            while not Done:
                Done=True
                for key in grid:
                    if grid[key].clicked and len(grid[key].adj_unk)>0 and grid[key].num!='X':
                        grid[key].count_adj(grid,known_mines)
                        if solve_level>0:
                            if (grid[key].num)-(grid[key].adj_IDed)==0:
                                for i in range(key[0]-1,key[0]+2):
                                    for j in range(key[1]-1,key[1]+2):
                                        if -1<i<x and -1<j<y and not grid[(i,j)].clicked and (i,j) not in known_mines:
                                            Done=False
                                            click(grid,(i,j))
                            elif (grid[key].num)-(grid[key].adj_IDed)-len(grid[key].adj_unk)==0:
                                for i in range(key[0]-1,key[0]+2):
                                    for j in range(key[1]-1,key[1]+2):
                                        if -1<i<x and -1<j<y and not grid[(i,j)].clicked:
                                            Done=False
                                            known_mines.add((i,j))
                                            if (i,j) in front:
                                                front.remove((i,j))
                        elif prob_mapping or guess_use>0:
                            if (grid[key].num)-(grid[key].adj_IDed)-len(grid[key].adj_unk)==0:
                                for i in range(key[0]-1,key[0]+2):
                                    for j in range(key[1]-1,key[1]+2):
                                        if -1<i<x and -1<j<y and not grid[(i,j)].clicked:
                                            Done=False
                                            known_mines.add((i,j))
                                            if (i,j) in front:
                                                front.remove((i,j))
                            
            prob_dict,distributions,clumps=local_probs(grid,front,known_mines,mines)
            if solve_level>1:
                for sqr in prob_dict:
                    if prob_dict[sqr]==0:
                        click(grid,sqr)
                        completely_Done=False
                    if prob_dict[sqr]==1:
                        known_mines.add(sqr)
                        front.remove(sqr)
                        completely_Done=False
        background=set()
        ranges=[{} for i in range(len(distributions))]
        '''ranges lists a dictionary for each clump. These dictionaries have a total number of
        mines for that clump as key, and a number of ways consistant with that as contents.'''
        for key in grid:
            if not grid[key].clicked:
                background.add(key)
        for clump in clumps:
            for sqr in clump:
                background.remove(sqr)
        for sqr in known_mines:
            if sqr in background:
                background.remove(sqr)
        for i,dists in enumerate(distributions):
            for dist in dists:
                if len(dist) not in ranges[i]:
                    ranges[i][len(dist)]=1
                else:
                    ranges[i][len(dist)]=ranges[i][len(dist)]+1
        bg_range={}
        if len(background)>0:
            surround_range=clump_permutator(ranges.copy())
            for tup in surround_range:
                if (mines-len(known_mines)-tup[0])>=0:
                    if mines-len(known_mines)-tup[0] not in bg_range:
                        bg_range[mines-len(known_mines)-tup[0]]=tup[1]
                    else:
                        bg_range[mines-len(known_mines)-tup[0]]=bg_range[mines-len(known_mines)-tup[0]]+tup[1]
            if len(bg_range)==0:
                bg_range[mines-len(known_mines)]=1
            #Now use this dictionary to calcute probability for background squares.
            total_ways=0
            for num in bg_range:
                total_ways=total_ways+bg_range[num]
            prob=0
            for num in bg_range:
                prob=prob+((num*bg_range[num])/(len(background)*total_ways))
            for sqr in background:
                prob_dict[sqr]=prob
        #calculate new probabilities for each clump taking into account global mine distribution.
        for i,clump in enumerate(clumps):
            multipliers={}
            total_ways=0
            for num in ranges[i]:
                multipliers[num]=0
                if len(clumps)>1:
                    other_clumps=clump_permutator(ranges[:i]+ranges[i+1:])
                    if len(other_clumps)==0: print('Error: other_clumps empty.')
                    for possible in other_clumps:
                        if possible[0]+num<=mines-len(known_mines):
                            bg_mines=mines-len(known_mines)-possible[0]-num
                            multipliers[num]=multipliers[num]+possible[1]*int(comb(len(background),bg_mines))
                else:
                    bg_mines=mines-len(known_mines)-num
                    if bg_mines<0:
                        print(mines,'-',len(known_mines),'-',num,'<0')
                    multipliers[num]=multipliers[num]+int(comb(len(background),bg_mines))
                total_ways=total_ways+(ranges[i][num]*multipliers[num])
            if total_ways==0:
                print('Error:total_ways=0',clump,distributions[i])
                print('clump ',i,' of ',len(clumps))
                print('ranges',ranges[i])
                print('multipliers',multipliers)
                print('clumps:',clumps)
            for sqr in clump:
                prob_dict[sqr]=0
            for dist in distributions[i]:
                num=len(dist)
                prob=multipliers[num]/total_ways
                if not 0<=prob<=1:
                    print ('Error: prob ',prob,' out of range.')
                    print ('ways, total ways',multipliers[num],total_ways)
                    print (dist)
                    prob=0
                for sqr in dist:
                    prob_dict[sqr]=prob_dict[sqr]+prob
        if solve_level>2:
            for sqr in prob_dict:
                if prob_dict[sqr]==0:
                    click(grid,sqr)
                    perfectly_Done=False
                if prob_dict[sqr]==1:
                    known_mines.add(sqr)
                    perfectly_Done=False
        
    if len(known_mines)==mines:
        stage=8
        print('you win')
    return prob_dict
        
def clump_permutator(ranges):
    #The following calculates a ranges dictionary for squares within a local area from all other clumps
    calc_range1=[]
    for r_dict in ranges:
        if len(calc_range1)==0:
            for num in r_dict:
                calc_range1.append((num,r_dict[num]))
        else:
            calc_range2=[]
            for num in r_dict:
                for tup in calc_range1:
                    calc_range2.append((num+tup[0],r_dict[num]*tup[1]))
            calc_range1=calc_range2.copy()
    return calc_range1      #will contain tuples.(mines in clump,consistent permutations)

def find_clump(clear_new, clear_front, clump=[set(),set()]):
    '''This function will identify the set of simple squares in clear_front which belong to
    the same area clump. clear squares added to clump[0]. Unknowns added to clump[1]. Once
    added to clump, squares are removed from set clear_front.'''
    for clear in clear_new:
        clump[0].add(clear)
        for unk in clear.adj_unk:
            clump[1].add(unk)
    clear_new=set()
    for clear in clear_front:
        for unk in clear.adj_unk:
            if unk in clump[1]:
                clear_new.add(clear)
    if len(clear_new)>0:
        for clear in clear_new:
            clear_front.remove(clear)
        clump=find_clump(clear_new,clear_front,clump)
    return clump

def hypothetical_solve(clump,dist):
    '''A simplified solver designed to be called by the combinations function'''
    Done=False
    n=0
    while not Done and n<100:
        n=n+1
        if n==100: print('loop out')
        finish0=set()
        Done=True
        for sqr in clump[0]:
            if len(sqr.adj_unk)>0:
                if sqr.num-sqr.adj_IDed==0:
                    Done=False
                    finish0.add(sqr)
                    for unk in sqr.adj_unk:
                        for sqr2 in clump[0]:
                            if sqr2!=sqr:
                                if unk in sqr2.adj_unk:
                                    sqr2.adj_unk.remove(unk)
                        if unk in clump[1]:
                            clump[1].remove(unk)
                if sqr.num-sqr.adj_IDed==len(sqr.adj_unk):
                    Done=False
                    finish0.add(sqr)
                    for unk in sqr.adj_unk:
                        dist.add(unk)
                        for sqr2 in clump[0]:
                            if sqr2!=sqr:
                                if unk in sqr2.adj_unk:
                                    sqr2.adj_unk.remove(unk)
                                    sqr2.adj_IDed=sqr2.adj_IDed+1
                        if unk in clump[1]:
                            clump[1].remove(unk)
        for sqr in finish0:
            clump[0].remove(sqr)

def combinations(clump,distributions,dist,initial=False):
    '''This function takes a clump of visible unknowns, and the adjacent squares which show
    information about them, and returns a list of all possible mine distributionsin the clump.'''
    possible=True           #This section checks if considered clump arangement is possible
    for sqr in clump[0]:
        if sqr.adj_IDed>sqr.num:
            possible=False
        if sqr.num-sqr.adj_IDed>len(sqr.adj_unk):
            possible=False
    if possible:            #add distribution to list if it is complete
        if len(clump[1])==0:
            distributions.append(dist)
        else:
            finish0=set()       #forget squares with 0 adjacent unknowns
            for sqr in clump[0]:
                if len(sqr.adj_unk)==0:
                    finish0.add(sqr)
            for sqr in finish0:
                clump[0].remove(sqr)
            clump1=deepcopy(clump)
            trying=clump1[1].pop()
            clump2=deepcopy(clump1)
            #assume trying is mine
            dist1=dist.copy()
            dist1.add(trying)
            for sqr in clump1[0]:
                if trying in sqr.adj_unk:
                    sqr.adj_unk.remove(trying)
                    sqr.adj_IDed=sqr.adj_IDed+1
            hypothetical_solve(clump1,dist1)
            combinations(clump1,distributions,dist1)
            #assume trying is not a mine
            dist2=dist.copy()
            for sqr in clump2[0]:
                if trying in sqr.adj_unk:
                    sqr.adj_unk.remove(trying)
            hypothetical_solve(clump2,dist2)
            combinations(clump2,distributions,dist2)
        if initial:
            return distributions

def local_probs(grid,front,known_mines,mines):
    '''This function splits the grid into independant clumps, and then uses the combinations
    function to find all possible distributions of mines in these clumps. It returns these
    distributions as well as probabilities based on them.'''
    clear_front=set()
    prob_dict={}
    for key in grid:
        if grid[key].clicked and len(grid[key].adj_unk)>0:
            clear_front.add(simple_sqr(key,grid[key].num,grid[key].adj_unk,grid[key].adj_IDed))
    clear_front2=clear_front.copy()
    clumps=[]
    while len(clear_front2)>0:
        start=clear_front2.pop()
        clumps.append(find_clump({start},clear_front2,[set(),set()]))
    distributions=[0]*len(clumps)
    for i in range(0,len(clumps)):
        distributions[i]=combinations(clumps[i],[],set(),initial=True)
        ways=len(distributions[i])
        if ways==0: print ('ways==0 error')
        for sqr in clumps[i][1]:
            n=0
            for dist in distributions[i]:
                if sqr in dist:
                    n=n+1
            prob_dict[sqr]=float(n)/float(ways)
    unk_clumps=[]
    for clump in clumps:
        unk_clumps.append(clump[1])
    return prob_dict,distributions,unk_clumps

def start_game(x=30,y=16):
    global known_mines,front,prob_dict,stage,run,grid
    known_mines=set()
    front=set()
    prob_dict={}
    stage=0
    grid=blank_grid(x,y)

def simple_guess(prob_dict,first_guess):
    min_prob=prob_dict[min(prob_dict,key=prob_dict.get)]
    #Find options with minimum probability
    options=[]
    for sqr in prob_dict:
        if prob_dict[sqr]==min_prob:
            options.append(sqr)
    #Pick the option closest to the first square clicked
    if len(options)>1:
        sqr=min(options,key=lambda option:abs(option[0]-first_guess[0])+abs(option[1]-first_guess[1]))
    else:sqr=options[0]
    return sqr

#define grid paramaters
mines=99
x=30
y=16

hovering=None
run=True
move0=None
guess=None

start_game(x,y)

solve_level=1
prob_mapping=True
guess_func=1
guess_use=0

label_font=pygame.font.SysFont('timesnewroman',26)
readout_font=pygame.font.SysFont('timesnewroman',18)
solver_label=label_font.render('Deductive solver:',True,(255,255,255))
window.blit(solver_label,(785,185))
prob_label=label_font.render('Probability map:',True,(255,255,255))
window.blit(prob_label,(785,100))
guessing_label=label_font.render('Guessing function:',True,(255,255,255))
window.blit(guessing_label,(785,270))

new_game=Button(860,40,150,50,text='New Game',font_size=24)

solv_off=Button(995,220,65,35,text='Off')
solv_1=Button(785,220,65,35,text='Simple')
solv_2=Button(855,220,65,35,text='Complex')
solv_3=Button(925,220,65,35,text='Global')
solv_buttons=[solv_off,solv_1,solv_2,solv_3]

prob_off=Button(855,135,65,35,text='Off')
prob_on=Button(785,135,65,35,text='On')

min_risk=Button(785,305,135,35,text='Least risk')
guess_off=Button(995,355,65,35,text='Off')
guess_show=Button(785,355,65,35,text='Show')
guess_auto=Button(855,355,65,35,text='Auto')
guess_buttons=[guess_off,guess_show,guess_auto]

def redraw(hovering):
    global known_mines
    for i,button in enumerate(solv_buttons):
        if i==solve_level:
            button.draw(window,(0,150,0))
        else: button.draw(window)
    
    if prob_mapping:
        prob_on.draw(window,(0,150,0))
        prob_off.draw(window)
    else:
        prob_off.draw(window,(0,150,0))
        prob_on.draw(window)
    
    if guess_func==1 and guess_use>0: min_risk.draw(window,(0,150,0))
    else: min_risk.draw(window)

    for i,button in enumerate(guess_buttons):
        if i==guess_use:
            button.draw(window,(0,150,0))
        else: button.draw(window)
    
    if hovering=='new_game':
        new_game.draw(window,(100,100,100))
    else: new_game.draw(window)
    
    pygame.draw.rect(window,(0,0,0),(785,400,300,50),0)
    if type(hovering)==tuple and prob_mapping and stage<8:
        if hovering in known_mines:
            readout=readout_font.render('Chance of mine: 100%',True,(255,255,255))
            window.blit(readout,(785,400))
        elif hovering in prob_dict:
            num_string='%.2f' % (round(prob_dict[hovering],4)*100)
            readout=readout_font.render('Chance of mine: '+num_string+'%',True,(255,255,255))
            window.blit(readout,(785,400))
    elif stage==8:
        readout=readout_font.render('You win',True,(255,255,255))
        window.blit(readout,(785,400))
    elif stage==9:
        readout=readout_font.render('You lose',True,(255,255,255))
        window.blit(readout,(785,400))
    
    if stage==0:    
        for key in grid:
            if key==hovering:
                grid[key].draw(window,(150,150,255))
            else: grid[key].draw(window)
    elif stage==1 or stage==8:  
        for key in grid:
            if not grid[key].clicked:
                if key==guess and guess_use>0:
                    grid[key].draw(window,(0,255,255))
                elif key==hovering:
                    grid[key].draw(window,(150,150,255))
                elif key in known_mines and prob_mapping:
                    grid[key].draw(window,(100,100,100))
                elif key in prob_dict and prob_mapping:
                    if prob_dict[key]==0:
                        grid[key].draw(window,(100,255,100))
                    else:
                        grid[key].draw(window,(255,255-int(255*prob_dict[key]),255-int(255*prob_dict[key])))
                else: grid[key].draw(window)
                
while run:
    redraw(hovering)
    pygame.display.update()
    pygame.time.delay(25)
    pos=pygame.mouse.get_pos()
    
    if 0<stage<8 and not guess:
        if guess_func==1: guess=simple_guess(prob_dict,move0)
        else: print('Error: Selected guess_func not availible')
        if guess_use==2:
            click(grid,guess)
            if stage<8:
                prob_dict=solving(grid,known_mines)
                guess=None
    
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        
        if event.type==pygame.MOUSEMOTION:
            if on_grid(pos):
                for key in grid:
                    if grid[key].is_over(pos):
                        hovering=grid[key].coord
            elif new_game.is_over(pos):
                hovering='new_game'
            else: hovering=None

        if event.type==pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            if on_grid(pos):
                if stage==0:
                    for key in grid:
                        if grid[key].is_over(pos):
                            move0=key
                            grid=lay_mines(grid,mines,key)
                            stage=1
                            for key2 in grid:
                                grid[key2].get_number(grid)
                            click(grid,key)
                            prob_dict=solving(grid,known_mines)
                            guess=None
                if stage==1:
                    for key in grid:
                        if grid[key].is_over(pos):
                            if not grid[key].clicked:
                                click(grid,key)
                                if stage<8:
                                    prob_dict=solving(grid,known_mines)
                                    guess=None
            elif prob_on.is_over(pos): prob_mapping=True
            elif prob_off.is_over(pos): prob_mapping=False
            elif new_game.is_over(pos): start_game()
            elif min_risk.is_over(pos): guess_func=1
            else:
                for i,button in enumerate(guess_buttons):
                    if button.is_over(pos): guess_use=i
                for i,button in enumerate(solv_buttons):
                    if button.is_over(pos): solve_level=i

pygame.display.quit()
#quit()
