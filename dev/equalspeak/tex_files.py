from functools import reduce, partial

# Given strings key and s, find all occurrences of key in s and extract the
# contents of the braces in each instance.
def search_and_extract_braces(key:str, s:str) -> list[str]:
	extr = []
	while key in s:
		s = s[s.index(key) + len(key):]
		extr.append(s[s.index('{') + 1:s.index('}')])
	return extr

# Run the search_and_extract_braces on a list of lines. This can be made more
# general. Let's wait and see.
def bundle_saeb(key:str, lines:list[str]):
	saeb = partial(search_and_extract_braces, key)
	return reduce(lambda x, y: x + y, map(saeb, lines), [])

def get_packages(lines:list[str]) -> tuple[str]:
	packs = bundle_saeb('usepackage', lines)
	no_space = lambda s: s.replace(' ', '')
	packages = [no_space(s) for s in packs if not ',' in s]
	for s in [no_space(s) for s in packs if ',' in s]:
		packages += s.split(',')
	return tuple(sorted(packages))

# Main class
class latex_parse:

	def __init__(self, lines=[], file=None) -> None:
		self.lines = lines
		self.file = file
		docline = lambda l: r'\begin{document}' in l or r'\end{document}' in l
		self.doclines = tuple(
			map(lambda s: lines.index(s), filter(docline, lines))
		)
		self.packages = get_packages(lines[:self.doclines[0]])
		self._tree = None
		
	def __repr__(self) -> str:
		return f"A LaTeX parser for\n{self.file}" + ''.join(
			map(lambda p: f"\n\t{p} : Not supported", self.packages)
		)

	def get_tree(self) -> list[tuple]:
		"""
		Returns a speak-tree for the document.
		"""
		from .trees import speak_tree, grow_tree
		if self._tree:
			return self._tree
		S = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		T = speak_tree(S, 'document', (self.doclines[0] + 1, self.doclines[1]))
		self._tree = grow_tree(T)
		return self._tree
	
	def document(self, start=0, end=None):
		text = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		return text[start:end]
	
	def preamble(self):
		return ''.join(self.lines[:self.doclines[0]])

def read_tex(file:str):
	with open(file, 'r') as f:
		return latex_parse(lines=f.readlines(), file=file)