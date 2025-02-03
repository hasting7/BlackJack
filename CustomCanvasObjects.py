from tkinter import Button, Frame, Label
from includes.StatusCodes import *
from includes.VisualConstants import *

class BetModifier(Frame):
	def __init__(self,delta, update_func, *args,**kwargs):
		super().__init__(*args,**kwargs)

		self.delta = delta

		self.chip_count = 0
		self.on_update = update_func

		self.font_size = 16

		self.inc = Button(self, text='+%d'%self.delta, command=lambda : self.edit_chips(1),highlightbackground=self['bg'], bg=self['bg'], font=('Arial',self.font_size))
		self.dec = Button(self, text='-%d'%self.delta, command=lambda : self.edit_chips(-1),highlightbackground=self['bg'], bg=self['bg'], font=('Arial',self.font_size))
		self.label = Label(self,text='0',width=3,height=1,font=('Arial', self.font_size))

		self.inc.pack(side='top',fill='both',expand=True)
		self.label.pack(side='top',fill='both',expand=True,padx=4)
		self.dec.pack(side='top',fill='both',expand=True)


	def edit_chips(self, count):
		if self.chip_count + count < 0: return

		self.chip_count += count

		self.label.config(text='%d'%self.chip_count)

		self.on_update()

	def get_total(self):
		return self.delta * self.chip_count

class Chip():
	def __init__(self, drawer_manager, x, y, r):
		self.drawer = drawer_manager
		self.x = x 
		self.y = y 
		self.r = r

		self.chip = self.drawer.create_oval(x-r,y-r,x+r,y+r,fill=WHITE,outline=BLACK,width=2,state='hidden')
		self.value_tag = self.drawer.create_text(x,y, text='', fill=BLACK,font=('Arial',16))

	def reset(self):
		self.render_updates(0)

	def render_updates(self,amount):
		chip_bg = WHITE
		chip_fg = BLACK
		state = 'hidden'
		bet_text = ''

		if amount > 0:
			chip_index = -1
			for i in range(len(CHIP_DENOMINATIONS)-1, -1, -1):
				if amount - CHIP_DENOMINATIONS[i] >= 0:
					chip_index = i
					break

			if chip_index != -1:
				chip_bg = CHIP_COLORS[chip_index]
				chip_fg = CHIP_FG[chip_index]
				state = 'normal'
				bet_text = "${:,}".format(amount)

		self.drawer.itemconfigure(self.chip, state=state, fill=chip_bg)

		self.drawer.itemconfigure(self.value_tag, text=bet_text,fill=chip_fg)
		self.drawer.tag_raise(self.value_tag)


class SmartLabel():
	def __init__(self, drawer_manager, x, y, font, fg, bg=None):
		self.drawer = drawer_manager
		self.x, self.y = x,y
		self.font_data = font
		self.fg = fg
		self.bg = bg
		self.active = False
		self.message = ''
		self.padding = 5

		self.text = self.drawer.create_text(x,y,font=font, fill=self.fg, text=self.message, state='hidden')

		self.components = [self.text]
		if self.bg:
			self.bbox = self.drawer.create_rectangle(x,y,x,y,fill=self.bg,outline=self.bg, state='hidden')
			self.components.insert(0,self.bbox)		

	def update(self,message=None):
		self.active = True
		if message:
			self.message = message

		for component in self.components:
			self.drawer.tag_raise(component)
			self.drawer.itemconfigure(component, state='normal')

		self.drawer.itemconfigure(self.text,text=self.message)

		if self.bg:
			x1, y1, x2, y2 = self.drawer.bbox(self.text)
			self.drawer.coords(self.bbox, x1-self.padding, y1-self.padding, x2+self.padding, y2+self.padding)

	def hide(self):
		self.active = False
		for component in self.components:
			self.drawer.itemconfigure(component, state='hidden')