class Error(BaseException):
    def __init__(self,mess):
        self.message = 'Error: ' + mess
        pass

class Polimino:
    var = 2
    def __init__(self,w,h,num,type):
        self.w = w
        self.h = h          
        self.type = type    #'R' - rectangular, 'L' - L-type, 'S' - square
        self.num = num      #polimino power (number of them on the table)

        self.image = {}     #образ полимино
        k = 0
        if(type == 'R'):
            if(h==w):type = 'S'
            if(self.h > self.w):
                buf = self.h
                self.h = self.w
                self.w = buf
            for i in range(w):
                for j in range(h):
                    self.image[k] = [i,j]
                    k += 1
        else:
            self.image[k] = [0,0]
            k=1
            for i in range(1,w):
                self.image[k] = [i,0]
                k += 1
            for i in range(1,h):
                self.image[k] = [0,i]
                k += 1
        pass

    def printInfo(self):
        print('w='+str(self.w)+' h='+str(self.h)+' num='+str(self.num)+' type='+self.type)
        pass
    def printImage(self):
        listTemp = []
        for i in range(len(self.image)):
            listTemp[self.image[i][0]][self.image[i][1]] = '#'
        s = ''
        for i in range(len(self.image)):
            s += '\n'*self.image[i][1]+' '*self.image[i][0]+'#'
        print(s)
        pass
    
class Table:
    def __init__(self,w=1,h=1,whiteCells=0,rowsInvolved=0,rowsPacked=0):
        self.w = w                          #ширина стола
        self.h = h                          #высота стола
        self.whiteCells = whiteCells                  #пропуски клеток в рядах при размещении полимино
        self.rowsInvolved = rowsInvolved    #сколько рядов затронуто при размещении
        self.rowsPacked = rowsPacked        #сколько рядов заполнено
        self.table = []                     #сетка стола
        self.iniTable(w,h)
        pass

    def iniTable(self,w,h):
        if(w<0 or h<0): raise Error('Отрицательные размеры стола')
        row = []
        [row.append(0) for i in range(w)]
        [self.table.append(row) for j in range(h)]
        pass

    def qualityFactor(self):
        factor = 0
        for i in range(self.rowsInvolved):
            factor += self.table[i][0]==0
            for j in range(1,self.w):
                factor += (self.table[i][j]==0)+((self.table[i][j]==1) & (self.table[i][j-1]==0))*0.5
        return factor
        
def newFun():
    pass

try:
    # initialize task
    iniTaskList = [
        [4,4],                  #table size [w,h]
        [((1,1),2),((2,2),2)],  #square poliminos [((w,h),N)...]
        [((5,4),2)]                      #L-poliminos [((w,h),N)...]
    ]
    #создаем стол
    table = Table(w=iniTaskList[0][0],h=iniTaskList[0][1],rowsInvolved=3)
    '''table.table = [
        [1,1,1,1,1,0],
        [0,1,0,1,0,1],
        [0,0,1,0,0,0],
    ]
    table.w = 6
    table.h = 3
    print(table.qualityFactor())'''
    ###create list of polimino instances
    #square poliminos
    listPolim = [Polimino(l[0][0],l[0][1],l[1],'R') for l in iniTaskList[1]]
    #L-poliminos
    listPolim += [Polimino(l[0][0],l[0][1],l[1],'L') for l in iniTaskList[2]]
    listPolim[2].printImage()
    #check poliminos' sizes are valid
    for poli in listPolim:
        if(poli.w>table.w or poli.h>table.h):
            raise Error('one of poliminos is larger than the table!')
except Error as e:
    print(e.message)