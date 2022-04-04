from functools import wraps
from flask import session, redirect

def admin_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
        
		if 'isAdmin' in session and 'isLogin' in session:
			if session['isAdmin'] == True:
				return f(*args, **kwargs)
			else:
				return redirect('/content/ads-scheduler')
		else:
			return redirect('/login')

	return wrap

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
        
		if 'isLogin' in session:
			if session['isLogin'] == True:
				return f(*args, **kwargs)
			return redirect('/')
		else:
			return redirect('/')

	return wrap

def not_login(f):
	@wraps(f)
	def wrap(*args, **kwargs):
        
		if 'isLogin' not in session:
			return f(*args, **kwargs)
		else:
			return redirect('/admin')

	return wrap