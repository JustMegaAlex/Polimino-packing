#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

from polimino_packing import Error, Polimino, Table

try:
    from local_config import ini_task_list, DEBUG
except:
    DEBUG = False
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
            # print(str(i)+' '+str(j)+' '+str(table_instance.table[i][j]))
            if table_instance.table[i][j]==0:
                i_place = i
                j_place = j
                # print('found '+str(i_place)+' '+str(j_place))
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
        
try:
    # создаем экземпляр стола
    table_instance = Table(width=ini_task_list[0][0], height=ini_task_list[0][1])
    table_instance.print_table() 

    # заполняем список POLIMINOS
    POLIMINOS = [Polimino(l[0][0], l[0][1], l[1], 'R') for l in ini_task_list[1]]
    # число прямоугольных полимино
    # rect_polim_number = len(ini_task_list[1])
    # L-poliminos
    POLIMINOS += [Polimino(l[0][0], l[0][1], l[1], 'L') for l in ini_task_list[2]]
    
    # общее количество полимино, размещаемых на столе
    unpacked_polims = 0 
    for poli in POLIMINOS:
        unpacked_polims += poli.num
    print('Poliminos total:'+str(unpacked_polims))

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
        print(area)
        if area > table_instance.area :
            raise Error('Total polimino area is larger than the table area!')
    print('Poliminos total area: '+str(area))

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
        #print('Trying poli№ '+str(ind)+': num ='+str(polimino.num))
        # запоминаем начальную клетку
        i_mem = i_place
        j_mem = j_place
        
        # перебираем все повороты одного полимино
        # в каждой клетке задействованных строк
        if polimino:
            for rotation in range(4):
                while not(i_place < 0):    # см search_free_cell()
                    # пробуем разместить
                    if table_instance.place_polimino(i_place, j_place, polimino, rotation):
                        new_factor = table_instance.quality_factor()    # новое значение фактора
                        #print('factor '+str(new_factor))
                        #table_instance.print_table()
                        #
                        # input()
                        if factor > new_factor:                 # стало лучше?
                            print('new best poli')
                            factor = new_factor                                 # запоминаем фактор
                            best_poli = [i_place, j_place, polimino, rotation]    # и полимино с параметрами размещения
                        # отменяем размещение для последующего перебора
                        table_instance.undo_placement()
                    # print('point('+str(i_place)+', '+str(j_place)+') factor '+str(factor))
                    # input()
                    # ищем следующую свободную ячейку
                    i_place, j_place = search_free_cell(i_place, j_place+1)
                    # else:print('placement faied')
                # вспоминаем, откуда начинали
                i_place = i_mem
                j_place = j_mem
        #print('factor ' + str(factor))
        #polimino.print_image()
        # переходим к следующему полимино
        polimino, ind = find_next_polim(ind+1)
        if not polimino:   # если все полимино проверены
            print('all polims checked')
            # если удалось разместить хотя бы один
            if best_poli:     
                # выводим образ выбранного полимино     
                print('poli choosed:')
                print('factor '+str(new_factor))
                best_poli[2].print_image()
                print()
                # размещаем его окончательно
                table_instance.place_polimino(best_poli[0], best_poli[1], best_poli[2], best_poli[3])
                unpacked_polims -= 1
                # выводим сетку стола
                table_instance.print_table()
                # ищем следующую свободную клетку
                i_place, j_place = search_free_cell(i_place, j_place)

                best_poli = []
                factor = factor_big_value
                ind = 0
                polimino,ind = find_next_polim()
                input()

            # в противном случае ищем следующую свободную клетку
            else:
                #print('next point')
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