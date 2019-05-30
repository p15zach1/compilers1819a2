import plex

class ParseError(Exception):
	pass

class MyParser:
	def __init__(self):
		symbols = plex.Str('=', '(', ')')
		PRINT = plex.Str("print")
		AND = plex.Str('and')
		OR = plex.Str('or')
		XOR = plex.Str('xor')
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		ID = letter+plex.Rep(letter|digit)
		number = plex.Rep1(plex.Range('01'))
		space = plex.Any(' \n\t')

		self.lexicon = plex.Lexicon([
			(symbols, plex.TEXT),
			(PRINT, plex.TEXT),
			(AND, plex.TEXT),
			(OR, plex.TEXT),
			(XOR, plex.TEXT),
			(ID, 'id'),
			(number, 'number'),
			(space, plex.IGNORE)
		])

		self.st = {}

	def create_scanner(self, fp):
		self.scanner = plex.Scanner(self.lexicon, fp)
		self.la, self.text = self.next_token()

	def next_token(self):
		return self.scanner.read()

	def match(self, token):
		if self.la == token:
			self.la, self.text = self.next_token()
		else:
			raise ParseError("match error")

	def Stmt_list(self):
		if self.la == 'id' or self.la == 'print':
			self.Stmt()
			self.Stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("Stmt_list ERROR")

	def Stmt(self):
		if self.la == 'id':
			varname = self.text
			self.match('id')
			self.match('=')
			e = self.Expr()
			self.st[varname] = e
		elif self.la == 'print':
			self.match('print')
			e = self.Expr()
			print('{:b}'.format(e))
		else:
			raise ParseError("Stmt ERROR")

	def Expr(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			t = self.Term()
			tt = self.Term_tail()
			if tt is None:
				return t
			return t^tt[1]
		else:
			raise ParseError("Expr ERROR")

	def Term_tail(self):
		if self.la == 'xor':
			op = self.match('xor')
			f = self.Term()
			t = self.Term_tail()
			if t is None:
				return op, f
			return op, f^t[1]
		elif self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			raise ParseError("Term_tail ERROR")

	def Term(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			f = self.Factor()
			t = self.Factor_tail()
			if t is None:
				return f
			return f|t[1]
		else:
			raise ParseError("Term ERROR")

	def Factor_tail(self):
		if self.la == 'or':
			op = self.match('or')
			f = self.Factor()
			t = self.Factor_tail()
			if t is None:
				return op, f
			return op, f|t[1]
		elif self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			raise ParseError("Factor_tail ERROR")

	def Factor(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			f = self.Atom()
			t = self.Atom_tail()
			if t is None:
				return f
			return f&t[1]
			raise ParseError("Factor ERROR")

	def Atom_tail(self):
		if self.la == 'and':
			op = self.match('and')
			f = self.Atom()
			t = self.Atom_tail()
			if t is None:
				return op, f
			return op, f&t[1]
		elif self.la == 'or' or self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			print(self.la)
			raise ParseError("Atom_tail ERROR")

	def Atom(self):
		if self.la == '(':
			self.match('(')
			e = self.Expr()
			self.match(')')
			return e
		elif self.la == 'id':
			varname = self.text
			self.match('id')
			if varname in self.st:
				return self.st[varname]
			else:
				raise ParseError("id ERROR")
		elif self.la == 'number':
			value = int(self.text,2)
			self.match('number')
			return value
		else:
			raise ParseError("Atom ERROR")

	def parse(self, fp):
		self.create_scanner(fp)
		self.Stmt_list()
		#while self.la:
			#print(self.la, self.text)
			#self.la, self.text = self.next_token()

parser = MyParser()
with open('text.txt') as fp:
	scanner = parser.parse(fp)
