'''
Stmt_list   -> Stmt Stmt_list | .
Stmt        -> id equal Expr | print Expr.
Expr        -> Term Term_tail.
Term_tail   -> xor Term Term_tail | .
Term        -> Factor Factor_tail.
Factor_tail -> or Factor Factor_tail | .
Factor      -> Atom Atom_tail.
Atom_tail   -> and Atom Atom_tail | .
Atom        -> ( Expr ) | id | number.
'''

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
			self.match('id')
			self.match('=')
			self.Expr()
		elif self.la == 'print':
			self.match('print')
			self.Expr()
		else:
			raise ParseError("Stmt ERROR")

	def Expr(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			self.Term()
			self.Term_tail()
		else:
			raise ParseError("Expr ERROR")

	def Term_tail(self):
		if self.la == 'xor':
			self.match('xor')
			self.Term()
			self.Term_tail()
		elif self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			raise ParseError("Term_tail ERROR")

	def Term(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			self.Factor()
			self.Factor_tail()
		else:
			raise ParseError("Term ERROR")

	def Factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.Factor()
			self.Factor_tail()
		elif self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			raise ParseError("Factor_tail ERROR")

	def Factor(self):
		if self.la == '(' or self.la == 'id' or self.la == 'number':
			self.Atom()
			self.Atom_tail()
		else:
			raise ParseError("Factor ERROR")

	def Atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.Atom()
			self.Atom_tail()
		elif self.la == 'or' or self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == ')' or self.la == None:
			return
		else:
			raise ParseError("Atom_tail ERROR")

	def Atom(self):
		if self.la == '(':
			self.match('(')
			self.Expr()
			self.match(')')
		elif self.la == 'id':
			self.match('id')
		elif self.la == 'number':
			self.match('number')
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
