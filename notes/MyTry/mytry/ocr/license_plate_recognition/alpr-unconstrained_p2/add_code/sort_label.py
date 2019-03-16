def analysis(location):
	al, at, ar, ab = location
	aw, ah = ar - al, ab - at
	acx, acy = (ar + al)//2, (ab + at)//2
	return (aw, ah), (acx, acy)


def is_bottom(b_pair, a_pair):
	a, b = a_pair[0], b_pair[0]
	width, height = a_pair[1]
	bl, bt, br, bb = b.tl()[0]*width, b.tl()[1]*height, b.br()[0]*width, b.br()[1]*height
	al, at, ar, ab = a.tl()[0]*width, a.tl()[1]*height, a.br()[0]*width, a.br()[1]*height
	(aw, ah), (acx, acy) = analysis((al, at, ar, ab))
	(bw, bh), (bcx, bcy) = analysis((bl, bt, br, bb))
	bs = (bb - max(ab, bt)) / bh 
	if bs > 0.5:
		return True
	return False


def is_top(b_pair, a_pair):
	a, b = a_pair[0], b_pair[0]
	width, height = a_pair[1]
	bl, bt, br, bb = b.tl()[0]*width, b.tl()[1]*height, b.br()[0]*width, b.br()[1]*height
	al, at, ar, ab = a.tl()[0]*width, a.tl()[1]*height, a.br()[0]*width, a.br()[1]*height
	(aw, ah), (acx, acy) = analysis((al, at, ar, ab))
	(bw, bh), (bcx, bcy) = analysis((bl, bt, br, bb))
	ts = (min(at, bb) - bt) / bh 
	if ts > 0.5:
		return True
	return False


def numeric_compare(a_pair, b_pair):
	# print('a_pair, b_pair = ', a_pair, b_pair)
	a, b = a_pair[0], b_pair[0]
	width, height = a_pair[1]
	if is_bottom(b_pair, a_pair):
		return -1 # a < b
	if not is_top(b_pair, a_pair):
		bl, bt, br, bb = b.tl()[0]*width, b.tl()[1]*height, b.br()[0]*width, b.br()[1]*height
		al, at, ar, ab = a.tl()[0]*width, a.tl()[1]*height, a.br()[0]*width, a.br()[1]*height
		(aw, ah), (acx, acy) = analysis((al, at, ar, ab))
		(bw, bh), (bcx, bcy) = analysis((bl, bt, br, bb))
		if bcx > acx:
			return -1 # a < b
	return 1 # a > b