#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

from polimino_packing import Error, Polimino, Table, debug_message

try:
    from local_config import ini_task_list, DEBUG, SHOW
except:
    print('Warning: import ini_task_list failed, default one used')
    DEBUG = False
    SHOW = False
    ini_task_list = [
        [4, 5],             # размеры стола[w, h]    
        
        [                   # прямоугольные полимино[((w, h), N)...]
            ((2, 2), 1)
        ], 
                      
        [                   # L-полимино [((w, h), N)...]
            ((2, 3), 1), 
            ((2, 2), 1), 
            ((3, 2), 1), 
            ((3, 3), 1)
        ]    
    ]

def search_free_cell(i_begin=0, j_begin=0):
    # переход на следующую строку
    if j_begin >= len(table_instance.table[0]):
        j_begin = 0
        i_begin += 1
    # поиск свободной ячейки
    for i in range(i_begin, len(table_instance.table)):
        j_begin = j_begin*(i==i_begin)
        for j in range(j_begin, len(table_instance.table[0])):
            if table_instance.table[i][j]==0:
                i_place = i
                j_place = j
                return i_place, j_place
    return -1, -1

def undo_placement():
    global i_place, j_place 
    i_place, j_place = table_instance.undo_placement()

def find_next_polim(ind = 0):
    for k in range(ind,len(POLIMINOS)):
        if POLIMINOS[k].num:
            return POLIMINOS[k],k
    return None, 0
        
def wait():
    print('Enter any key to continue')
    input()

try:
    # создаем экземпляр стола
    table_instance = Table(width=ini_task_list[0][0], height=ini_task_list[0][1])
    table_instance.print_table() 

    # заполняем список POLIMINOS
    POLIMINOS = [Polimino(l[0][0], l[0][1], l[1], 'R') for l in ini_task_list[1]]
    # число прямоугольных полимино
    # L-poliminos
    POLIMINOS += [Polimino(l[0][0], l[0][1], l[1], 'L') for l in ini_task_list[2]]
    
    # общее количество полимино, размещаемых на столе
    unpacked_polims = 0 
    for poli in POLIMINOS:
        unpacked_polims += poli.num
    debug_message('Poliminos total:'+str(unpacked_polims))

    # проверка:
    area = 0        # площадь полимино
    for poli in POLIMINOS:
        # размеры полимино >= размеров стола
        if(poli.width>table_instance.width or poli.height>table_instance.height):
            raise Error('One of poliminos is larger than the table!')

        # общая площадь полимино >= площади стола
        if poli.kind == 'L':
            area += (poli.width + poli.height - 1)*poli.num
        else:
            area += (poli.width*poli.height)*poli.num
        debug_message('Poliminos total area: '+str(area))
        if area > table_instance.area :
            raise Error('Total polimino area is larger than the table area!')

    # сортируем полимино по наибольшему размеру: по убыванию 
    # сначала прямоугольные,  затем L
    # bubble sort
    swapped = True
    while(swapped):
        swapped = False
        for k in range(len(POLIMINOS)-1):
            if max(POLIMINOS[k].width, POLIMINOS[k].height)<max(POLIMINOS[k+1].width, POLIMINOS[k+1].height):
                POLIMINOS[k], POLIMINOS[k+1] = POLIMINOS[k+1], POLIMINOS[k]
                swapped = True
    # print sorting results
    print('Poliminos are sorted:')
    [print(el.kind + str(max(el.width, el.height))) for el in POLIMINOS]
    print('Poliminos total:'+str(unpacked_polims))

    # # # # # размещаем полимино
    ind = 0
    # первый полимино размещаем сразу
    table_instance.place_polimino(0, 0, POLIMINOS[ind], 0)
    # вывод сетки стола
    table_instance.print_table()
    input()
    unpacked_polims -= 1
    # начальная клетка
    i_place = 0
    j_place = POLIMINOS[ind].width
    # полимино, при котором фактор будет размещения наименьший
    best_poli = []      # в списке будет сам полимино и параметры размещения 
    # задаем начальное значение фактора размещения
    factor_big_value = table_instance.width * table_instance.height
    factor = factor_big_value           # заведомо большое значение
                                        # больше, чем Table.quality_factor может вернуть
                                        # далее при работе алгоритма чем он меньше, тем лучше 
    polimino,ind = find_next_polim()

    while unpacked_polims:
        # запоминаем начальную клетку
        i_mem = i_place
        j_mem = j_place
        
        # перебираем все повороты одного полимино
        # в каждой клетке задействованных строк
        if polimino:
            for rotation in range(4 - 3*(polimino.kind == 'S') - 2*(polimino.kind == 'R')):      # для квадрата только одна попытка
                while not(i_place < 0):    # см search_free_cell()  # для прямоугольника - две
                    # пробуем разместить
                    if table_instance.place_polimino(i_place, j_place, polimino, rotation):
                        new_factor = table_instance.quality_factor()    # новое значение фактора
                        #print('new_factor '+str(new_factor))
                        #print('factor '+str(factor))
                        #print('rows ' + str(table_instance.rows_involved))
                        #table_instance.print_table()
                        #wait()
                        if factor > new_factor:                 # стало лучше?
                            factor = new_factor                                 # запоминаем фактор
                            best_poli = [i_place, j_place, polimino, rotation]    # и полимино с параметрами размещения
                        # отменяем размещение для последующего перебора
                        table_instance.undo_placement()

                    # ищем следующую свободную ячейку
                    i_place, j_place = search_free_cell(i_place, j_place+1)

                # вспоминаем, откуда начинали
                i_place = i_mem
                j_place = j_mem

        # переходим к следующему полимино
        polimino, ind = find_next_polim(ind+1)
        if not polimino:   # если все полимино проверены
            # если удалось разместить хотя бы один
            if best_poli:     
                # размещаем полимино окончательно
                table_instance.place_polimino(best_poli[0], best_poli[1], best_poli[2], best_poli[3])
                unpacked_polims -= 1
                # ищем следующую свободную клетку
                i_place, j_place = search_free_cell(i_place, j_place)

                if SHOW:# показать пошаговое выполнение
                    debug_message('factor '+str(new_factor))
                    print('poli choosed:')
                    best_poli[2].print_image()
                    # выводим сетку стола
                    table_instance.print_table()
                    print()
                    wait()

                best_poli = []
                factor = factor_big_value
                ind = 0
                polimino,ind = find_next_polim()
            # в противном случае ищем следующую свободную клетку
            else:
                i_place, j_place = search_free_cell(i_place, j_place+1)
                if i_place < 0:
                    raise Error('Table is full',True)
                best_poli = []
                polimino,ind = find_next_polim()
    # конец алгоритма: успех
    print('True')
except Error as e:
    print(e.message)
    if e.signal:
        # конец алгоритма: не удалось
        print('False')