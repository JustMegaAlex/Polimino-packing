from PoliminoPacking import Error,Polimino,Table

#Точка размещения полимино
iPack = 0
jPack = 0

ind = 0

listPolim=[]

def searchPlacementPoint(iBegin=0,jBegin=0):
    global iPack,jPack
    #переход на следующую строку
    if(jBegin >= len(table.table[0])):
        jBegin = 0
        iBegin += 1
    #поиск свободной ячейки
    for i in range(iBegin,len(table.table)):
        jBegin = jBegin*(i==iBegin)
        for j in range(jBegin,len(table.table[0])):
            #print(str(i)+' '+str(j)+' '+str(table.table[i][j]))
            if(table.table[i][j]==0):
                iPack = i
                jPack = j
                #print('found '+str(iPack)+' '+str(jPack))
                return
    raise Error('Table is full',True)

def undoPlacement():
    global iPack,jPack 
    iPack,jPack = table.placeUndo()
    pass

def findNextPoli():
    global ind,listPolim
    for i in range(ind+1,len(listPolim)):
        if(listPolim[i].num):
            ind = i
            return True
    return False
        
try:
    # initialize task
    iniTaskList = [
        [4,5],                  #table size [w,h]
        [((2,2),1)],  #square poliminos [((w,h),N)...]
        [((2,3),1),((2,2),1),((3,2),1),((3,3),1)]             #L-poliminos [((w,h),N)...]
    ]
    #создаем стол
    table = Table(w=iniTaskList[0][0],h=iniTaskList[0][1])
    table.print()
    ###create list of polimino instances
    #square poliminos
    rectPolimNumber = len(iniTaskList[1])
    listPolim = [Polimino(l[0][0],l[0][1],l[1],'R') for l in iniTaskList[1]]
    #L-poliminos
    listPolim += [Polimino(l[0][0],l[0][1],l[1],'L') for l in iniTaskList[2]]
    #количество неразмещенных полимино
    unpackedPolims = 0 
    for poli in listPolim:
        unpackedPolims += poli.num
    #проверка размеров полимино и общей площади полимино
    area = 0
    for poli in listPolim:
        if(poli.w>table.w or poli.h>table.h):
            raise Error('one of poliminos is larger than the table!')

        if(poli.type == 'L'): area += (poli.w + poli.h - 1)*poli.num
        else: area += (poli.w*poli.h)*poli.num
        if(area > table.area):
            raise Error('Total polimino area is larger than the table area!')
    print('Area: '+str(area))
    #сортируем полимино: от больших к мальеньким, 
    #сначала прямоугольные, затем L
    #bubble
    swapped = True
    while(swapped):
        swapped = False
        for k in range(len(listPolim)-1):
            if(max(listPolim[k].w,listPolim[k].h)<max(listPolim[k+1].w,listPolim[k+1].h)):
                listPolim[k],listPolim[k+1] = listPolim[k+1],listPolim[k]
                swapped = True
    #print sorting results
    print('Poliminos are sorted:')
    [print(el.type + str(max(el.w,el.h))) for el in listPolim]
    print('Poliminos total:'+str(unpackedPolims))
    #packing poliminos
    ind = 0
    table.placePolimino(0,0,listPolim[ind],0)
    table.print()
    input()
    unpackedPolims -= 1
    iPack = 0
    jPack = listPolim[ind].w
    factor = table.w*table.h #очень большое значение

    while(unpackedPolims):
        findNextPoli()
        polimino = listPolim[ind]
        #print('Trying poli№ '+str(ind)+': num ='+str(polimino.num))
        iMem,jMem = iPack,jPack
        for rot in range(4):
            #print('rotation '+str(rot))
            while(iPack<table.rowsInvolved):
                if(table.placePolimino(iPack,jPack,polimino,rot)):
                    newFactor = table.qualityFactor()
                    #print('factor '+str(newFactor))
                    if(factor>newFactor):
                        #print('new best poli')
                        factor = newFactor
                        bestPoli = [iPack,jPack,polimino,rot]
                    table.placeUndo()
                #print('point('+str(iPack)+','+str(jPack)+') factor '+str(factor))
                #input()
                searchPlacementPoint(iPack,jPack+1)
                #else:print('placement faied')
            iPack,jPack = iMem,jMem
        print('factor ' + str(factor))
        polimino.printImage()
        #ind += 1
        if(not findNextPoli()):
            #print('all polims checked')
            if(bestPoli):
                print('poli choosed:')
                bestPoli[2].printImage()
                print()
                table.placePolimino(bestPoli[0],bestPoli[1],bestPoli[2],bestPoli[3])
                unpackedPolims -= 1
                table.print()
                searchPlacementPoint(iPack,jPack)
                bestPoli = []
                factor = table.w*table.h
                ind = 0
                input()
                #break
            else:
                print('next point')
                searchPlacementPoint(iPack,jPack+1)
                bestPoli = []
    print('True')
except Error as e:
    print(e.message)
    if(e.signal): print('False')