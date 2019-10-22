#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import copy

try:
    from local_config import DEBUG
except:
    DEBUG = False

class Error(BaseException):
    def __init__(self, mess, signal = False):
        self.message = 'Error: ' + mess
        self.signal = signal
        
class Polimino:
    var = 2
    def __init__(self, width, height, num, kind):
        self.width = width
        self.height = height          
        self.kind = kind    # 'R' - rectangular, 'L' - L-kind, 'S' - square
        self.num = num      # polimino power (number of them on the table)

        self.image = {}     # образ полимино, для добавления в table
        k = 0
        if(kind == 'R'):                     # прямоугольный
            if(height==width):kind = 'S'
            if self.height > self.width:
                self.width, self.height = self.height, self.width
            for i in range(self.height):
                for j in range(self.width):
                    self.image[k] = [i, j]
                    k += 1
        else:                               # L-образный
            self.image[k] = [0, 0]
            k=1
            for j in range(1, width):
                self.image[k] = [0, j]
                k += 1
            for i in range(1, height):
                self.image[k] = [i, 0]
                k += 1
    
    def print_image(self):
        '''
        Выводит образ полимино
        '''
        if self.kind == 'R':
            s = ('# '*self.width + '\n')*self.height
        else:
            s = '# '*self.width + '\n# '*(self.height-1) + '\n'
        print(s)
        
    def rotated(self, rotation):
        '''
        Возвращает повернутый образ полимини
        '''
        if not rotation:
            return self.image
        rot_image = copy.deepcopy(self.image)
        if rotation==1 :# 90
            for k in range(len(self.image)):
                # i_rot = -j + w - 1
                rot_image[k][0] = -self.image[k][1] + self.width - 1
                # j_rot = i
                rot_image[k][1] = self.image[k][0]
        elif rotation==2 :# 180
            for k in range(len(self.image)):
                # i_rot = -i + h - 1
                rot_image[k][0] = -self.image[k][0] + self.height - 1
                # j_rot = -j + w - 1
                rot_image[k][1] = -self.image[k][1] + self.width - 1
        elif rotation==3 :# 270
            for k in range(len(self.image)):
                # i_rot = j
                rot_image[k][0] = self.image[k][1]
                # j_rot = -i + h - 1
                rot_image[k][1] = -self.image[k][0] + self.height - 1
        else: 
            raise Error('Polimino.rotated: wrong rotation argument')
        return rot_image
    
class Table:
    def __init__(self, width=1, height=1, rows_involved=1, rows_packed=0):
        self.width = width                          # ширина стола
        self.height = height                        # высота стола   
        self.rows_involved = rows_involved    # сколько рядов затронуто при размещении
        self.rows_packed = rows_packed        # сколько рядов заполнено
        self.table = []                     # сетка стола
        self.ini_table(width, height)
        self.area = width*height
        self.track_list = []

    def ini_table(self, width, height):
        if width<0 or height<0:
             raise Error('Отрицательные размеры стола')
        self.table = [0]*height
        for i in range(height): 
            self.table[i] = [0]*width

    def quality_factor(self):
        '''
        Рассчитывает и возвращает фактор, характеризующий качество размещения полимино
        Чем меньше фактор, тем лучше
        '''
        factor = 0
        for i in range(self.rows_involved):
            row_factor = self.table[i][0]==0
            for j in range(1, self.width):
                row_factor += (self.table[i][j]==0)+((self.table[i][j]==1) & (self.table[i][j-1]==0))*0.5
            factor += row_factor * (1 + 0.25*(self.rows_involved - i - 1))
        return factor/self.rows_involved
    
    def print_table(self):
        '''
        Выводит сетку стола Table
        '''
        s = ''
        for i in range(self.rows_involved):
            for j in range(self.width): s += str(self.table[i][j])
            s += '\n'
        s += ('0'*self.width + '\n')*(self.height - self.rows_involved)
        print(s)

    def place_polimino(self, i, j, polim, rotation = 0):
        '''
        Размещает полимино
        '''
        # в пределах стола?
        if rotation in [0, 2]:
            if((i+polim.height)>self.height or (j+polim.width)>self.width):
                # print('outside the table')
                return  False
        else:
            if((i+polim.width)>self.height or (j+polim.height)>self.width):
                # print('outside the table')
                return  False

        # вставка образа в table
        image = polim.rotated(rotation)
        for k in range(len(image)): # image - это словарь
            # координаты клеток,  размещаемых на столе
            ii = i + image[k][0]   
            jj = j + image[k][1]
            if self.table[ii][jj]:
                self.undo(i, j, image, k)
                # print(str(ii)+' '+str(jj))
                return False
            self.table[ii][jj] = 1
            self.rows_involved = max(ii+1, self.rows_involved)
        polim.num -= 1
        # print('polimono placed num='+str(polim.num))
        self.track_list.append([polim, i, j, rotation, self.rows_involved])
        #print()
        debug_message('rows '+str(self.rows_involved),False)
        # self.print()
        return True
    
    def undo(self, i, j, image, k):
        for kk in range(k):
            ii = i + image[kk][0]
            jj = j + image[kk][1]
            self.table[ii][jj] = 0
    
    def undo_placement(self):
        '''
        Убирает последний размещенный полимино  
        '''
        [polim, i, j, rotation] = self.track_list.pop()[:4]
        self.rows_involved = self.track_list[-1][4]
        debug_message('undo:rows '+str(self.rows_involved),False)
        polim.num += 1
        self.undo(i, j, polim.rotated(rotation), len(polim.image))
        return i, j

def debug_message(s,wait = False):
    if(DEBUG):
        print(s)
        if(wait):
            input()