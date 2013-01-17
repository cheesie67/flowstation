def secant(func, oldx, x, TOL=1e-5, MAXDX=10000000 ):
	oldf, f = func(oldx), func(x)
	if (abs(f) > abs(oldf)):
		oldx, x = x, oldx 
		oldf, f = f, oldf
	count = 0
	while 1:
		dx = f * (x - oldx) / float(f - oldf)	
		if abs( dx ) > MAXDX: dx = MAXDX*abs(dx)/dx
		if abs(dx) < TOL * (1 + abs(x)): return x - dx
		oldx, x = x, x - dx
		oldf, f = f, func(x) 
		count = count + 1
