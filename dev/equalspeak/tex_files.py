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
		from .trees import plant_tree, grow_tree
		if self._tree:
			return self._tree
		S = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		T = plant_tree(S, self.doclines[0] + 1, self.doclines[1])
		L = list(v for v in T.vertices if v.name != 'document')
		self._tree = grow_tree(T, leaves=L)
		return self._tree
	
	def document(self, start=0, end=None):
		text = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		return text[start:end]
	
	def preamble(self):
		return ''.join(self.lines[:self.doclines[0]])
	
	def no_dollars(self, output_file=None):
		"""
		Converts all $ and $$ math modes to \\( and \\[, respectively.

		The default output file is the same as the input file, but with the suffix _nd.
		"""
		from .trees import plant_tree
		if self._tree:
			return self._tree
		S = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		T = plant_tree(S, self.doclines[0] + 1, self.doclines[1])
		L1 = [v for v in T.vertices if v.name == 'inline math $']
		L2 = [v for v in T.vertices if v.name == 'displayed math $$']
		for v in L2:
			a, b = v.location 
			# print(f"Replacing:\n{S[a - 2:b + 2]}\n")
			S = S[:a - 2] + f'\\[{v.data}\\]' + S[b + 2:]
		for v in sorted(L1, reverse=True):
			a, b = v.location 
			# print(f"Replacing:\n{S[a - 1:b + 1]}\n")
			S = S[:a - 1] + f'\\({v.data}\\)' + S[b + 1:]
		if output_file is None:
			output_file = self.file[:self.file.index('.tex')] + '_nd.tex'
		with open(output_file, 'w') as f:
			f.write(self.preamble())
			f.write("\\begin{document}\n")
			f.write(S)
			f.write("\\end{document}\n")
		print(f"Saved to {output_file}.")



def read_tex(file:str):
	with open(file, 'r') as f:
		return latex_parse(lines=f.readlines(), file=file)