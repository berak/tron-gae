import sys
import random
import time
import logging

def parse_map( maptext ):
	lines = maptext.split('\n')
	r=0
	players = 0
	grid=[]
	for line in lines:
		if not line: continue
		if line[0] != '#': continue
		grid.append([])
		c=0
		for ch in line:
			grid[r].append(str(ch))
			if ch in "12345678":
				players += 1
			c += 1
		r += 1

	#~ logging.info( "map: " + str(r) + " " + str(c))
	return grid, r, c, players


def find_map( grid, h, w, id ):
	for r in range(h):
		for c in range(w):
			if grid[r][c] == str(id):
				return r, c
	return -1,-1


class Game(object):
	debug = False
	VALID=["N","E","S","W"]
	def __init__(self):
		self.width = 0
		self.height = 0
		self.grid=[]
		self.players=[]
		self.errors=[]
		self.turn = 0
		
	def readmapfile( self, name ):
		f=open(name,"rb")
		s=f.read()
		f.close()
		return self.readmap(s)

	def readmap( self, maptext ):
		self.grid, self.height, self.width, p = parse_map( maptext )


	def print_board( self ):
		print self.turn, self.alive()
		for line in self.grid:
			print "".join(line)


	def add_player(self, code, name):
		p = {}
		err = ""
		alive = 1
		try:			
			exec( compile(code, name, "exec") ) in p
		except Exception, e:		
			alive = 0
			err = " crashed on startup : " + str(e)
		p['id']    = str(1+len(self.players))
		p['hist']  = ""
		p['name']  = name
		p['score'] = 100 - alive*100
		p['alive'] = alive
		p['r'], p['c'] = find_map( self.grid, self.height, self.width, p['id'] )

		self.players.append(p)
		self.errors.append(err)

	def alive(self):
		al = 0
		for i,p in enumerate(self.players):
			if p['alive'] :
				al += 1
		return al


	def lost(self,p):
		p['alive'] = 0
		p['score'] = self.alive()
		if self.debug:
			print "LOST ", p['name'], p['id'], p['score'], p['alive']


	def doturn(self):
		for i,p in enumerate(self.players):
			if not p['alive']:
				continue
			r = p['r']
			c = p['c']
			t0 = time.time()
			try:
				p['step'] = p['turn'](self.grid,r,c) 
			except Exception, e:
				self.errors[i] = " crashed : " + str(e)
				self.lost(p)
				continue
			t1 = time.time()
			if t1 - t0 > 1:
				self.errors[i] = " timed out %d s." % (t1-t0)
				self.lost(p)
				continue
			if not ( p['step'] in self.VALID ):
				self.errors[i] = " invalid move " + str(p['step'])
				self.lost(p)
				
		for i,p in enumerate(self.players):
			if not p['alive']:
				continue
			r = p['r']
			c = p['c']
			step = p['step']
			p['hist'] += step
			#~ print self.turn, i, p['id'], p['r'], p['c'], step, p['hist']
			if step == 'N':
				if (r > 0) and (self.grid[r-1][c]) == ' ':
					p['r'] -= 1; self.grid[r-1][c] = str(i+1)
				else:
					self.lost(p)
			elif step == 'S':
				if (r < self.height-1) and (self.grid[r+1][c] == ' '):
					p['r'] += 1;  self.grid[r+1][c] = str(i+1)
				else:
					self.lost(p)
			elif step == 'E':
				if (c < self.width-1) and(self.grid[r][c+1] == ' '):
					p['c'] += 1;  self.grid[r][c+1] = str(i+1)
				else:
					self.lost(p)
			elif step == 'W':
				if (c > 0) and (self.grid[r][c-1] == ' '):
					p['c'] -= 1;  self.grid[r][c-1] = str(i+1)
				else:
					self.lost(p)
			
	def run(self, debug=False):
		self.debug = debug
		while(1):
			self.doturn()
			if debug:
				self.print_board()
			if self.alive() < 1:
				break
			self.turn += 1
		if debug: 
			for i,p in enumerate(self.players):	print p['score'], p['id'], p['name'], len(p['hist']), p['hist'], self.errors[i]



#~ north="""
#~ def turn( board, r,c ):
	#~ return "N"
#~ """
#~ south="""
#~ def turn( board, r,c ):
	#~ return "S"
#~ """
#~ ran="""
#~ import random,time
#~ random.seed(time.time())
#~ def turn( board, r,c ):
	#~ return random.choice(["N","S","E","W"])
#~ """
#~ free="""
#~ def turn( board, r,c ):
	#~ if board[r-1][c]==' ': return 'N'
	#~ if board[r+1][c]==' ': return 'S'
	#~ if board[r][c-1]==' ': return 'W'
	#~ return 'E'
#~ """
#~ err="""
#~ def turn( board, r,c ):
	#~ if bod[r-1][c]==' ': return 'N'
	#~ if board[r+1][c]==' ': return 'S'
	#~ if board[r][c-1]==' ': return 'W'
	#~ return 'E'
#~ """


#~ g = Game()
#~ g.readmapfile("maps\maze.txt")
#~ g.add_player(ran, "Randor")
#~ g.add_player(err, "Err")
#~ g.add_player(free, "Freon")
#~ # g.add_player(free, "Freebie")
#~ # g.add_player(ran, "Randex")
#~ g.run(True)
