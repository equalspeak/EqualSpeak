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
		('\\ ', ' ')
	]
	for x, y in subs:
		s = s.replace(x, y)
	# Remove initial and ending whitespaces.
	pat = re.compile(r'[^\s]')
	x = list(pat.finditer(s))[0]
	y = list(pat.finditer(s[::-1]))[0]
	return s[x.span()[0]:len(s) - y.span()[0]]


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

def get_top(re_it, i) -> int:
	try:
		return next(re_it).span()[i]
	except StopIteration:
		# Getting here means we couldn't find a 'closing' statement.
		# Therefore the document provided probably does not compile.
		raise ValueError("File provided does not compile.")

def search(S:str, JUMP=100, i=0) -> list[tuple]:
	# A function that takes a string r, compiles it with regex, and returns the
	# iterable from 'finditer'.
	str_to_iter = lambda r, a, b: re.compile(r).finditer(S, pos=a, endpos=b)
	all_pats = [
		(p.span()[0], r) for r in ENVS for p in str_to_iter(r, 0, JUMP)
	]
	if len(all_pats) == 0:
		# If we found no relevant patterns, push forward or stop entirely.
		if len(S) > JUMP:
			return search(S[JUMP:], i=i + JUMP)
		return []
	all_pats = sorted(all_pats)
	j, r = all_pats[0]
	j += ENVS[r][2]
	# At this stage, we know the first relevant pattern occurs at index j. 
	it = str_to_iter(ENVS[r][0], j, len(S))
	k = get_top(it, 0)
	# Now we know the first relevant pattern occurs between j and k.
	env = ENVS[r][1]
	if env == 'envi':
		# If the relevant pattern brings us into a specialized environment, then
		# we do additional things.
		env = S[j:k]
		end_env = fr"\\end{{{env}}}"
		end_env_pat = re.compile(end_env)
		it_env = end_env_pat.finditer(S, pos=k)
		j = k + 1
		k = get_top(it_env, 0)
		shift = k + len(end_env)
	else:
		shift = k + ENVS[r][2]
	vertex = ((i + j, i + k), env, my_clean(S[j:k]))
	return [vertex] + search(S[shift:], i=i + shift)

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
		self._forest = None
		
	def __repr__(self) -> str:
		return f"A LaTeX parser for\n{self.file}" + ''.join(
			map(lambda p: f"\n\t{p} : Not supported", self.packages)
		)

	def get_forest(self) -> list[tuple]:
		"""
		Returns a forest of parsing trees.
		"""
		if self._forest:
			return self._forest
		S = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		self._forest = search(S)
		return self._forest
	
	def document(self, start=0, end=None):
		text = ''.join(self.lines[self.doclines[0] + 1:self.doclines[1]])
		return text[start:end]
	
	def preamble(self):
		return ''.join(self.lines[:self.doclines[0]])

def read_tex(file:str):
	with open(file, 'r') as f:
		return latex_parse(lines=f.readlines(), file=file)