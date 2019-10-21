import copy

class Error(BaseException):
    def __init__(self,mess,signal = False):
        self.message = 'Error: ' + mess
        self.signal = signal
        pass

class Polimino:
    var = 2
    def __init__(self,w,h,num,type):
        self.w = w
        self.h = h          
        self.type = type    #'R' - rectangular, 'L' - L-type, 'S' - square
        self.num = num      #polimino power (number of them on the table)

        self.image = {}     #образ полимино
        self.listImage = []  #образ как лист
        k = 0
        if(type == 'R'):        #прямоугольный
            if(h==w):type = 'S'
            if(self.h > self.w):
                self.w,self.h = self.h,self.w
            for i in range(self.h):
                self.listImage.append([])
                for j in range(self.w):
                    self.image[k] = [i,j]
                    self.listImage[i].append(1)
                    k += 1
        #L-образный
        else:  
            self.image[k] = [0,0]
            self.listImage.append([1])
            k=1
            for j in range(1,w):
                self.image[k] = [0,j]
                self.listImage[0].append(1)
                k += 1
            for i in range(1,h):
                self.image[k] = [i,0]
                self.listImage.append([1])
                k += 1
        pass

    def printInfo(self):
        print('w='+str(self.w)+' h='+str(self.h)+' num='+str(self.num)+' type='+self.type)
        pass
    def printImage(self):
        if(self.type == 'R'):
            s = ('#'*self.w + '\n')*self.h
        else:
            s = '#'*self.w + '\n#'*(self.h-1) + '\n'
        print(s)
        pass
    def rotated(self,rot):
        if(not rot):return self.image
        rotImage = copy.deepcopy(self.image)
        if(rot==1):
            for k in range(len(self.image)):
                #i_rot = -j + w - 1
                rotImage[k][0] = -self.image[k][1] + self.w - 1
                #j_rot = i
                rotImage[k][1] = self.image[k][0]
        elif(rot==2):
            for k in range(len(self.image)):
                #i_rot = -i + h - 1
                rotImage[k][0] = -self.image[k][0] + self.h - 1
                #j_rot = -j + w - 1
                rotImage[k][1] = -self.image[k][1] + self.w - 1
        elif(rot==3):
            for k in range(len(self.image)):
                #i_rot = j
                rotImage[k][0] = self.image[k][1]
                #j_rot = -i + h - 1
                rotImage[k][1] = -self.image[k][0] + self.h - 1
        else: raise Error('Polimino.rotated: wrong rot argument')
        return rotImage
    
class Table:
    def __init__(self,w=1,h=1,whiteCells=0,rowsInvolved=1,rowsPacked=0):
        self.w = w                          #ширина стола
        self.h = h                          #высота стола
        self.whiteCells = whiteCells                  #пропуски клеток в рядах при размещении полимино
        self.rowsInvolved = rowsInvolved    #сколько рядов затронуто при размещении
        self.rowsPacked = rowsPacked        #сколько рядов заполнено
        self.table = []                     #сетка стола
        self.iniTable(w,h)
        self.area = w*h
        self.trackList = []
        pass

    def iniTable(self,w,h):
        if(w<0 or h<0): raise Error('Отрицательные размеры стола')
        self.table = [0]*h
        for i in range(h): self.table[i] = [0]*w
        pass

    def qualityFactor(self):
        factor = 0
        for i in range(self.rowsInvolved):
            factor += self.table[i][0]==0
            for j in range(1,self.w):
                factor += (self.table[i][j]==0)+((self.table[i][j]==1) & (self.table[i][j-1]==0))*0.5
        return factor/self.rowsInvolved
    
    def print(self):
        s = ''
        for i in range(self.rowsInvolved):
            for j in range(self.w): s += str(self.table[i][j])
            s += '\n'
        s += ('0'*self.w + '\n')*(self.h - self.rowsInvolved)
        print(s)
        pass

    def placePolimino(self,i,j,polim,rot = 0):
        #в пределах стола?
        if(rot in [0,2]):
            if((i+polim.h)>self.h or (j+polim.w)>self.w):
                #print('outside the table')
                return  False
        else:
            if((i+polim.w)>self.h or (j+polim.h)>self.w):
                #print('outside the table')
                return  False
        #копируем образ
        image = polim.rotated(rot)
        for k in range(len(image)): #image - это словарь
            #координаты клеток, размещаемых на столе
            ii = i + image[k][0]   
            jj = j + image[k][1]
            if(self.table[ii][jj]):
                self.undo(i,j,image,k)
                #print(str(ii)+' '+str(jj))
                return False
            self.table[ii][jj] = 1
            self.rowsInvolved = max(ii+1,self.rowsInvolved)
        polim.num -= 1
        #print('polimono placed num='+str(polim.num))
        self.trackList.append([polim,i,j,rot,self.rowsInvolved])
        print()
        print('rows '+str(self.rowsInvolved))
        #self.print()
        input()
        return True
    
    def undo(self,i,j,image,k):
        for kk in range(k):
            ii = i + image[kk][0]
            jj = j + image[kk][1]
            self.table[ii][jj] = 0
        pass
    def placeUndo(self):
        [polim,i,j,rot] = self.trackList.pop()[:4]
        self.rowsInvolved = self.trackList[-1][4]
        print('undo:rows '+str(self.rowsInvolved))
        polim.num += 1
        self.undo(i,j,polim.rotated(rot),len(polim.image))
        return i,j