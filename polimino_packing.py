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
    def __init__(self, width = 0, height = 0, num = 0, kind = 'R'):
        self.width = width
        self.height = height          
        self.kind = kind    # 'R' - прямоуголные, 'L' - L-образные, 'S' - квадратные
        self.num = num      # число таких полимино на столе

        self.image = {}     # образ полимино, для добавления в table
        k = 0
        if(kind == 'R'):                     # прямоугольный
            if(height==width):
                self.kind = 'S'              # квадратный
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
        Возвращает образ полимино с учетом поворота
        '''
        if not rotation:
            return self.image
        rot_image = copy.deepcopy(self.image)
        if rotation==1 :# 90
            for k in range(len(self.image)):
                # i_rot = -j + w - 1
                rot_image[k][0] = -self.image[k][1]# + self.width - 1
                # j_rot = i
                rot_image[k][1] = self.image[k][0]
        elif rotation==2 :# 180
            for k in range(len(self.image)):
                # i_rot = -i + h - 1
                rot_image[k][0] = -self.image[k][0]
                # j_rot = -j + w - 1
                rot_image[k][1] = -self.image[k][1]
        elif rotation==3 :# 270
            for k in range(len(self.image)):
                # i_rot = j
                rot_image[k][0] = self.image[k][1]
                # j_rot = -i + h - 1
                rot_image[k][1] = -self.image[k][0]
        else: 
            raise Error('Polimino.rotated(): wrong rotation argument')
        return rot_image
    
class Table:
    '''
    Класс реализует стол и все необходимые функции 
    для поиска решения
    '''
    def __init__(self, width=1, height=1, rows_involved=1, rows_packed=0):
        self.width = width                          # ширина стола
        self.height = height                        # высота стола   
        self.rows_involved = rows_involved    # сколько рядов затронуто при размещении
        self.table = []                     # сетка стола
        self.polim_count = 1
        self.ini_table(width, height)
        self.area = width*height
        self.buffer_polim_set = []

        self.solution_tree = []               # дерево решения
        self.combinations_tryed = 0
        self._current = 0
        self._polim_set = 0
        self._children = 1
        self._parent = 2
        self._polim = 0
        self._i = 1
        self._j = 2
        self._rot = 3
        self._rows_inv = 4

    def ini_table(self, width, height):
        '''
        Задает таблицу стола с указанными размерами
        '''
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

    def place_polimino(self, i, j, polim, rotation = 0, add_to_tree = False):
        '''
        Размещает полимино
        '''
        # вставка образа в table
        image = polim.rotated(rotation)
        # запоминаем rows_involved
        rows_involved_mem = self.rows_involved
        for k in range(len(image)): # image - это словарь
            # координаты клеток,  размещаемых на столе
            ii = i + image[k][0]
            if (ii < 0) or (ii >= self.height):     # проверка выхода за пределы стола
                self.undo(i, j, image, k)
                self.rows_involved = rows_involved_mem
                return False

            jj = j + image[k][1]
            if (jj<0) or (jj>=self.width):
                self.undo(i, j, image, k)
                self.rows_involved = rows_involved_mem
                return False

            if self.table[ii][jj]:          # клетка свободна?
                self.undo(i, j, image, k)
                self.rows_involved = rows_involved_mem
                return False
            self.table[ii][jj] = self.polim_count
            self.rows_involved = max(ii+1, self.rows_involved)
        polim.num -= 1

        # если add_to_tree = True, добавить в дерево решения
        if add_to_tree:
            self.add_to_solution_tree(polim, i, j, rotation, rows_involved_mem)
            self.polim_count = self.polim_count*(self.polim_count < 9) + 1
        else:
        # если add_to_tree = False, просто записываем параметры в буфер    
            self.buffer_polim_set = [polim, i, j, rotation, rows_involved_mem]
        return True
    
    def undo(self, i, j, image, k):
        '''
        Удаляет полимино со стола
        '''
        for kk in range(k):
            ii = i + image[kk][0]
            jj = j + image[kk][1]
            self.table[ii][jj] = 0
    
    def undo_placement(self):
        '''
        Убирает последний размещенный полимино
        И создает новую ветку решения, если алгоритм зашел в тупик
        '''
        # параметры для удаления полимино со стола 
        if self.buffer_polim_set:   # если был заполнен buffer_polim_set, значит размещение пробное
            [polim, i, j, rotation, self.rows_involved] = self.buffer_polim_set
            self.buffer_polim_set.clear()
        else:                       # если buffer_polim_set пуст, значит нужна новая ветка
            # параметры из дерева
            [polim, i, j, rotation, self.rows_involved] = self.solution_tree[self._current][self._polim_set]
            # поднимаемся на предыдущий узел дерева 
            self.solution_tree_go_up()
            self.polim_count = 9*(self.polim_count < 2) + self.polim_count - 1
        # восстанавливаем значение rows_involved
        polim.num += 1
        self.undo(i, j, polim.rotated(rotation), len(polim.image))
        return i, j

    def check_solution_tree(self, polim, rotation):
        '''
        Обеспечивает неповторяемость веток решений
        '''
        if self.solution_tree:
            # убеждаемся, что указанной конфигурации нет в child-ах
            for child in self.solution_tree[self._current][self._children]:
                set = child[self._polim_set]
                if (polim == set[self._polim]) and (rotation == set[self._rot]):
                    return False
        return True
    
    def add_to_solution_tree(self, polim, i, j, rotation, rows_involved):
        '''
        добавляет новый узел в дерево решений
        '''
        self.solution_tree.append( 
                                    [
                                        [polim, i, j, rotation, rows_involved],
                                        [], 
                                        self._current
                                    ]                   
                                )
        new_index = len(self.solution_tree) - 1
        # добавляем child в текущий узел
        self.solution_tree[self._current][self._children].append(self.solution_tree[new_index])
        # обновляем текущий индекс
        self._current = new_index

    def show_tree(self):
        '''
        выводит дерево решений
        '''
        for joint in self.solution_tree:
            print(joint)

    def solution_tree_go_up(self):
        '''
        переводит _current-индекс на предыдущий узел дерева
        и удаляет потомков текущего узла - для оптимизации
        '''
        # конец всего, замощения нет
        if(self._current == 0):
            raise Error('All combinations used. Solution not found. ',True)
        # удаляем потомков дерева
        children = self.solution_tree[self._current][self._children]
        for child in children:
            self.solution_tree.remove(child)
        # переходим к верхнему узлу
        self._current = self.solution_tree[self._current][self._parent]
        # еще одна комбинация
        self.combinations_tryed += 1

def debug_message(s,wait = False):
    if(DEBUG):
        print('Debug message: '+s)
        if(wait):
            input()