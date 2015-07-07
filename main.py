import Tkinter as tk
import random


NOMOVE = {
'Left': 'Right',
'Right': 'Left',
'Up': 'Down',
'Down': 'Up',
}

OFF = 0
PLACE = 1
DELETE = 2

# TODO
# 1. speed management
# 3. not empty field by default, additional borders
# 5. menu configure before start
# 6. levels and egg counter

class Snake(object):
    def __init__(self, field, color, fat, speed=0, flat_thorus=False):
        width, height = field.fieldsize
        assert not width % fat and not height % fat
        
        self.canvas = field
        self.fat = fat
        self.color = color
        self.flat_thorus = flat_thorus
        self.setspeed(speed)
        self.reset()
        self.canvas.bind('<Button-1>', self.b1)
        self.canvas.bind('<Button-3>', self.b3)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<ButtonRelease-3>', self.release)
        self.canvas.bind('<Motion>', self.borderProcessing)

    def b1(self, event):
        co = (event.x - event.x % self.fat, event.y - event.y % self.fat)
        self.mode = PLACE
        if co in self.borders:
            return
        id = self.canvas.drawSquare(co, self.fat, fill='red')
        self.borders[co] = id
        
    def b3(self, event):
        co = (event.x - event.x % self.fat, event.y - event.y % self.fat)
        self.mode = DELETE
        try:
            self.canvas.delete(self.borders[co])
            del self.borders[co]
        except KeyError:
            return
            
    def release(self, event=None):
        self.mode = OFF
        
    def borderProcessing(self, event):
        if self.mode is PLACE:
            self.b1(event)
        if self.mode is DELETE:
            self.b3(event)
        
    def setspeed(self, speed):
        assert 0 <= speed <= 9
        self.speed = range(200, 70, -14)[speed]
        
    def reset(self):
        self.idstack = []
        self.body = []
        self.borders = {}
        self.locked = False
        self.paused = False
        self.mode = OFF
        self.direction = 'Down' # Left Right Up Down
        self.canvas.master.bind('<KeyPress>', self.control)
        self.placeEgg()
        x, y = self.canvas.fieldsize
        point = y // 2 - self.fat * 3
        for i in range(point, y//2, self.fat):
            self.dsquare((point, i))
        self.headcoord = [point, i]
        self.move()
        
    def again(self):
        self.canvas.deletetext()
        for id in self.idstack:
            self.canvas.delete(id)
        for id in self.borders.values():
            self.canvas.delete(id)
        self.canvas.deleteEgg()
        self.canvas.deleteMenu()
        self.reset()
        
    def control(self, event):
        # While snake stay you may press two different 
        # direction keys twice and that will be reason for snake crash
        # because NOMOVE blocking don't happen.
        # self.locked boolean fixes that.

        if event.keysym in ('Pause', 'space'):
            if self.paused:
                self.paused = False
                self.canvas.deletetext()
                self.move()
            else:
                self.paused = True
                self.idpause = self.canvas.centertext('PAUSE')
            return
            
        if event.keysym == 's':
            d = {}
            d['FieldSize'] = self.canvas.fieldsize
            d['SnakeWidth'] = self.fat
            d['Borders'] = list(self.borders.keys())
            print(d)
            
        if self.locked or self.paused:
            return
        if event.keysym in ('Left', 'Right', 'Up', 'Down'):
            if NOMOVE[event.keysym] == self.direction: 
                # impossimble start moving to east when snake heads west
                return
            self.direction = event.keysym
        self.locked = True
        
    def dsquare(self, coords):
        id = self.canvas.drawSquare(coords, self.fat, fill=self.color)
        self.idstack.append(id)
        self.body.append(coords)
        
    def gameOverCondition(self):
        if self.flat_thorus:
            return (self.body.count(self.headcoord) == 2 or
                    tuple(self.headcoord) in self.borders)
        else:
            x, y = self.headcoord
            xmax, ymax = self.canvas.fieldsize
            condition = (
            y < 0 or x < 0 or 
            xmax == x or ymax == y or
            self.body.count(self.headcoord) == 2 or
            tuple(self.headcoord) in self.borders
            )
            return condition

    def move(self):
        if self.paused:
            return

        if self.gameOverCondition():
            self.canvas.centertext('CRASH')
            self.canvas.showMenu(self)
            self.canvas.master.unbind('<KeyPress>')
            return
        
        deletetail = True
        if self.headcoord == self.eggcoord: # egg eating
            self.canvas.deleteEgg()
            self.placeEgg()
            deletetail = False # growing
        if deletetail:
            self.canvas.delete(self.idstack.pop(0))
            self.body.pop(0)
            
        x, y = self.headcoord
        xmax, ymax = self.canvas.fieldsize
            
        f = self.fat
        if self.direction == 'Down':
            self.headcoord = [x, y+f]
        if self.direction == 'Up':
            self.headcoord = [x, y-f]
        if self.direction == 'Right':
            self.headcoord = [x+f, y]
        if self.direction == 'Left':
            self.headcoord = [x-f, y]
        
        if self.flat_thorus:
            if y < 0: self.headcoord[1] = ymax-self.fat
            if x < 0: self.headcoord[0] = xmax-self.fat
            if ymax == y: self.headcoord[1] = 0
            if xmax == x: self.headcoord[0] = 0
        
        self.locked = False
        self.dsquare(self.headcoord)
        self.canvas.master.after(self.speed, self.move)
        
    def placeEgg(self):
        xmax, ymax = self.canvas.fieldsize
        f = self.fat
        x = random.choice(range(0, xmax-f, f))
        y = random.choice(range(0, ymax-f, f))
        while ([x, y] in self.body or (x, y) in self.borders):
            x = random.choice(range(0, xmax-f, f))
            y = random.choice(range(0, ymax-f, f))
        self.canvas.drawEgg(x, y, f)
        self.eggcoord = [x, y]
         
         
class Field(tk.Canvas):
    @property
    def fieldsize(self):
        return (int(self['width']), int(self['height']))
        
    def centertext(self, text):
        x, y = self.fieldsize
        self.textid = self.create_text((x/2.0, y/2.0), 
            font='Arial 30 bold', text=text, fill='red')
            
    def drawSquare(self, dot, snakefat, **kw):
        f = snakefat
        x, y = dot
        id = self.create_polygon(dot, (x, y+f), (x+f, y+f), (x+f, y), **kw)
        return id
        
    def deletetext(self):
        self.delete(self.textid)
        
    def drawEgg(self, x, y, fat):
        self.eggid = self.create_oval((x, y), (x+fat, y+fat), fill='white')
        
    def deleteEgg(self):
        self.delete(self.eggid)
        
    def showMenu(self, snake):
        x, y = self.fieldsize
        frame = tk.Frame(self.master)
        qb = tk.Button(frame, text="Quit", command=exit, 
            activebackground='#dd0000', bg='red')
        qb.pack(fill=tk.X)
        ab = tk.Button(frame, text='Again', command=snake.again, 
            activebackground='#dd0000', bg='red')
        ab.pack(fill=tk.X)
        self.menuid = self.create_window((x/2.0, y/1.5), window=frame)
        
    def deleteMenu(self):
        self.delete(self.menuid)
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Snake')
    canvas = Field(root, height=450, width=450, bg='black')
    canvas.pack()
    Snake(canvas, color='green', fat=15, speed=7, flat_thorus=True)
    root.mainloop()
