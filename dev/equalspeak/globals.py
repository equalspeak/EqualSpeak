ENVS = {
	r'\$[^$]': (r'\$[^$]', 'inline math', 1),
	r'\$\$': (r'\$\$', 'displayed math', 2),
	r'\\\(': (r'\\\)', 'inline math', 2),
	r'\\\[': (r'\\\]', 'displayed math', 2),
	r'\\begin{': (r'}', 'envi', 7), 
}

OPS = [
	'=', '\\+', '\\-', '\\\\cdot', '\\\\times', '/', '\\sim', '\\\\leq', '\\\\leqslant', 
	'\\\\geq', '\\\\geqslant', '<', '>', '\\\\neq', '\\\\approx', '\\\\equiv', '\\\\cong', 
	'\\\\simeq', '\\\\propto', '\\\\parallel', '\\\\nparallel', '\\\\perp', '\\\\nperp', 
	'\\\\subset', '\\\\subseteq', '\\\\supset', '\\\\supseteq', '\\\\in', '\\\\ni', 
	'\\\\notin', '\\\\cup', '\\\\cap', '\\\\setminus', '\\\\oplus', '\\\\otimes', '\\\\odot'
]

GRPS = {
	r'\(' : (r'\)', 'parenthesis', 1),
	r'\[' : (r'\]', 'bracket', 1),
	r'\\\{' : (r'\\\}', 'braces', 2)
}