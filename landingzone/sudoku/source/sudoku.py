# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.widgets import Button
from pylab import mpl
class sudoku(object):
    def __init__(self):
        self.digits   = '123456789'
        self.rows     = 'ABCDEFGHI'
        self.cols     = self.digits
        global button
        # resolve Chinese characters problem.
        mpl.rcParams['font.sans-serif'] = ['microsoft Yahei']
        mpl.rcParams['axes.unicode_minus'] = False
    def cross(self,A, B):
        "Cross product of elements in A and elements in B."
        return [a+b for a in A for b in B]
    def setPuzzle(self):
        self.squares  = self.cross(self.rows, self.cols)
        self.unitlist = ([self.cross(self.rows, c) for c in self.cols] +
                    [self.cross(r, self.cols) for r in self.rows] +
                    [self.cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
        self.units = dict((s, [u for u in self.unitlist if s in u]) 
                     for s in self.squares)
        self.peers = dict((s, set(sum(self.units[s],[]))-set([s]))
                     for s in self.squares)
    def valueformater(self,values):
        vs = [[] for i in range(9)]
        for k,v in values.items():
            vs[ord(k[0])+int(k[-1])//10-65].append(v)
        return vs
    def fetchpuzzle(self,grid):
        self.puzzle = { }
        grid = { k:v if v.isnumeric() else '' for k,v in self.grid_values(grid).items() }
        for k,v in grid.items():
            self.puzzle[k]=v if len(v) == 1 else ''
        return self.puzzle
    def parse_grid(self,grid):
        """
        Convert grid to a dict of possible values, {square: digits}, or
        return False if a contradiction is detected.
        """
        ## To start, every square can be any digit; then assign values from the grid.
        values = dict((s, self.digits) for s in self.squares)
        for s,d in self.grid_values(grid).items():
            if d in self.digits and not self.assign(values, s, d):
                return False ## (Fail if we can't assign d to square s.)
        return values
    
    def grid_values(self,grid):
        #Convert grid into a dict of {square: char} with '0' or '.' for empties.
        chars = [c for c in grid if c in self.digits or c in '0.*']
        assert len(chars) == 81
        return dict(zip(self.squares, chars))
    def assign(self,values, s, d):
        """Eliminate all the other values (except d) from values[s] and propagate.
        Return values, except return False if a contradiction is detected."""
        other_values = values[s].replace(d, '')
        if all(self.eliminate(values, s, d2) for d2 in other_values):
            #print ("No contradiction, s=%s,d=%s,values=%s"%(s,d,values))
            return values
        else:
            #print ("there is a contradiction occurred for s=%s,d=%s,values=%s"%(s,d,values))
            return False    
    def eliminate(self,values, s, d):
        """Eliminate d from values[s]; propagate when values or places <= 2.
        Return values, except return False if a contradiction is detected."""
        if d not in values[s]:
            return values ## Already eliminated
        values[s] = values[s].replace(d,'')
        ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
        if len(values[s]) == 0:
            return False ## Contradiction: removed last value
        elif len(values[s]) == 1:
            d2 = values[s]
            if not all(self.eliminate(values, s2, d2) for s2 in self.peers[s]):
                return False
        ## (2) If a unit u is reduced to only one place for a value d, then put it there.
        for u in self.units[s]:
            dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
                if not self.assign(values, dplaces[0], d):
                    return False
        return values
    def genverify(self,seq):
        "Return some element of seq that is true."
        for e in seq:
            if e:
                return e
        return False
    def depthfirstsearch(self,values):
        "Using depth-first search and propagation, try all possible values."
        if values is False:
            #print ("rs = false,failed earlier")
            return False ## Failed earlier
        if all(len(values[s]) == 1 for s in self.squares): 
            return values ## Solved!
        ## Chose the unfilled square s with the fewest possibilities
        n,s = min((len(values[s]), s) for s in self.squares if len(values[s]) > 1)
        rs = self.genverify(self.depthfirstsearch(self.assign(values.copy(), s, d)) for d in values[s])
        return rs

    def solve(self,grid):
        self.grid = grid
        self.setPuzzle()        
        self.display(self.fetchpuzzle(grid),True,True)
    def display(self,d,format=True,showbutton=True):
        """
        display the puzzle or solution.
        """
        self.clust_data = self.valueformater(d) if format else d
        colours = [[] for x in range(9)]
        for m in range(9):
            for n in range(9):
                if m//3 in (0,2) and n//3 in (0,2) or m//3 == n//3:
                    colours[m].append('#C0C0C0')
                else:
                    colours[m].append('#F8F8FF')
        fig=plt.figure(figsize=(6, 6.2))
        ax = fig.add_subplot(1,1,1)
        ax.axis('off')
        msfont = font_manager.FontProperties(size=20,weight='bold')
        fig.suptitle('数独题（困难模式）', fontproperties=msfont)
        mngr = plt.get_current_fig_manager()
        mngr.window.wm_geometry("+380+10")
        sudokutable = ax.table(cellText=self.clust_data,cellColours=colours,cellLoc='center',loc='center right')
        sudokutable.auto_set_font_size(False)  
        cellDict = sudokutable.get_celld()  
        if showbutton:
            point = plt.axes([0.4,0.01,0.2,0.06])
            button = Button(point,label="resolve it. 解题", color="green",hovercolor="yellow")
            button.on_clicked(lambda event:self.buttonpress(event))
        for i in range(9):
            for j in range(9):
                cellDict[(j,i)].set_height(.118)
                if len(self.clust_data[i][j]) == 1:
                    cellDict[(i,j)].set_text_props(fontsize=30)
                else:
                    cellDict[(i,j)].set_text_props(fontsize=10)
        #plt.savefig("sudoku.png")
        plt.show()
    def buttonpress(self,event):
        plt.close()
        d = self.depthfirstsearch(self.parse_grid(self.grid))
        print ("resolved.")
        self.display(d,True,False)
if __name__ == '__main__':
    import time
    t1 = time.time()
    s = sudoku()
    d = s.solve('4*****8*5*3**********7******2*****6*****8*4******1*******6*3*7*5**2*****1*4******')
    #d = s.solve('..79.48...9...2..1...1....78.....4.2..3...5..9.2.....85....9...1..8...3...93.12..')
    deltat = time.time() - t1
    print ("All done, It took %.2f ms."%deltat)
