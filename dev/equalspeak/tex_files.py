import re
from functools import reduce, partial

ENVS = {
	r'\$[^$]': (r'\$[^$]', 'math', 1),
	r'\$\$': (r'\$\$', 'math', 2),
	r'\\\(': (r'\\\)', 'math', 2),
	r'\\\[': (r'\\\]', 'math', 2),
	r'\\begin{': (r'}', 'envi', 7)
}

# Remove initial and ending whitespaces and replace tabs, new lines, and double
# whitespace with one whitespace.
def my_clean(s:str):
	subs = [			# All different forms of whitespace.
		('\t', ' '),
		('\n', ' '),
		('  ', ' '),
		('\v', ' '),
		('\f', ' '),
		('\r', ' '),
		('\ ', ' ')
	]
	for x, y in subs:
		s = s.replace(x, y)
	# Remove initial and ending whitespaces.
	pat = re.compile(r'[^\s]')
	x = list(pat.finditer(s))[0]
	y = list(pat.finditer(s[::-1]))[0]
	return s[x.span()[0]:len(s) - y.span()[0]]


# Merge dictionaries with the same set of keys, whose values are lists
def merge_dicts(d1:dict, d2:dict) -> dict:
	return {k: d1[k] + d2[k] for k in d1.keys()}

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


def search_doc(S:str, JUMP=1000, i=0) -> dict:
	collect = {'math': [], 'envi': []}
	all_pats = []
	for r in ENVS.keys():
		pattern = re.compile(r)
		all_pats += [
			(p.span()[0], r) for p in pattern.finditer(S, endpos=JUMP)
		]
	if len(all_pats) == 0: 
		return collect
	all_pats = sorted(all_pats)
	j, r = all_pats[0]
	end_pat = re.compile(ENVS[r][0])
	it = end_pat.finditer(S, pos=j + 1)
	try:
		k = next(it).span()[0]
	except StopIteration:
		print("Document provided does not compile!")
		k = len(S) - 1
	collect[ENVS[r][1]].append(
		(my_clean(S[j + ENVS[r][2]:k]), r, (i + j + ENVS[r][2], i + k))
	)
	shift = k + ENVS[r][2]
	return merge_dicts(collect, search_doc(S[shift:], i=shift))


# Main class
class latexparse:

	def __init__(self, lines=[], file=None) -> None:
		self.lines = lines
		self.file = file
		# Find 'begin document'
		i = 0
		while i < len(lines) and not r'\begin{document}' in lines[i]:
			i += 1
		j = i + 1
		while j < len(lines) and not r'\end{document}' in lines[j]:
			j += 1
		self.doclines = (i, j)
		self.packages = get_packages(lines[:i])
		
	def __repr__(self) -> str:
		head = f"A LaTeX parser for\n{self.file}" 
		packages = ""
		for p in self.packages:
			packages += f"\n\t{p} : Not supported"
		return head + packages

	def convert(self):
		S = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		d = search_doc(S)
		return d
	
	def document(self):
		return ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
	
	def preamble(self):
		return ''.join(self.lines[:self.doclines[0]])

def read_tex(file:str):
	with open(file, 'r') as f:
		return latexparse(lines=f.readlines(), file=file)

