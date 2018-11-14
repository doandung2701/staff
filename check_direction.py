def is_satify_direction(indir, direction):
	require_directions = get_require_direction(indir)
	if direction in require_directions:
		return False
	else:
		return True
