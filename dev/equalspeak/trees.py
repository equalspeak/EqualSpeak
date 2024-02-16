import re

class speak_vertex:

	def __init__(self, data, name, loc, parent_tree) -> None:
		self.data = data
		self.name = name
		self.location = loc
		self.parent = parent_tree
		self.children = []

	def __repr__(self) -> str:
		return f"{self.name} {self.location}"

class speak_tree:

	def __init__(self, root, name, loc) -> None:
		self.root = speak_vertex(root, name, loc, self)
		self.vertices = {self.root}

	def __repr__(self) -> str:
		head = f"Speak tree:\n"
		verts = self._dfs()
		return head + ''.join(["\t"*(t[1]) + f"{t[0]}\n" for t in verts])
	
	def _dfs(self) -> list[speak_vertex]:
		tov = []
		current = [(self.root, 0)]
		while current:
			v, r = current.pop()
			tov.append((v, r))
			current += list(map(lambda c: (c, r + 1), v.children))
		return tov

	def add_children(self, v:speak_vertex, L:list[tuple]):
		kids = list(map(lambda t: speak_vertex(t[0], t[1], t[2], v.parent), L))
		v.children = kids[::-1]
		self.vertices = self.vertices.union(set(kids))
		return self

	def get_vertex(self, s:str):
		L = list(filter(lambda v: v.data == s, self.vertices))
		if L:
			return L[0]
		return None
		

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

def search(S:str, JUMP=1000, i=0) -> list[tuple]:
	from .globals import ENVS
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
	try:
		k = next(it).span()[0]
	except StopIteration:
		# Getting here means we couldn't find a 'closing' statement.
		# Therefore the document provided probably does not compile.
		raise ValueError("File provided does not compile.")
	# Now we know the first relevant pattern occurs between j and k.
	env = ENVS[r][1]
	if env == 'envi':
		# If the relevant pattern brings us into a specialized environment, then
		# we do additional things.
		env = S[j:k]
		end_env = fr"\end{{{env}}}"
		j = k + 1
		try:
			k = S.index(end_env)
		except ValueError:
			# Getting here means we couldn't find a 'closing' statement.
			# Therefore the document provided probably does not compile.
			raise ValueError("File provided does not compile.")
		shift = k + len(end_env)
	else:
		shift = k + ENVS[r][2]
	vertex = (S[j:k], env, (i + j, i + k))
	return [vertex] + search(S[shift:], i=i + shift)

def plant_tree(S:str, a:int, b:int) -> speak_tree:
	kids = search(S)
	T = speak_tree(S, 'document', (a, b))
	return T.add_children(T.root, kids)

def deep_search(S:str, env=None, shift=0):
	from .globals import OPS, GRPS, ENVS
	regexpr = '|'.join(OPS + list(GRPS.keys()) + list(ENVS.keys()))
	l_str_to_iter = lambda X: re.compile(regexpr).finditer(S)
	try:
		first = next(l_str_to_iter(OPS))
	except StopIteration:
		return []
	if first.group() in OPS:
		i, j = first.span()
		return [
			(S[:i], env, (shift, shift + i)),
			(S[i:j], first.group(), (shift + i, shift + j)),
			(S[j:], env, (shift + j, shift + len(S)))
		]
	


def grow_tree(T:speak_tree, leaves=None) -> speak_tree:
	print(leaves)
	if leaves:
		v = leaves.pop()
	else:
		v = T.root
		leaves = []
	kids = deep_search(v.data, env=v.name, shift=v.location[0])
	if kids:
		T = T.add_children(v, kids)
		# leaves += list(map(lambda k: T.get_vertex(k[0]), kids))
	if leaves:
		return grow_tree(T, leaves=leaves)
	return T
	
