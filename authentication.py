from flask import jsonify, session, request
from functools import wraps
from enum import IntFlag, auto
from log import log

import os
import time
import pyotp

class AuthScope(IntFlag):
	NONE = 0
	SELL = auto()
	ITEMS_VIEW = auto()
	ITEMS_EDIT = auto() # Relevant functionality unimplemented
	TAGS_VIEW = auto()
	TAGS_TOPUP = auto()
	TAGS_EDIT = auto() # Relevant functionality unimplemented

	SELLER = SELL | ITEMS_VIEW | TAGS_VIEW
	MANAGER = SELL | ITEMS_VIEW | TAGS_VIEW | ITEMS_EDIT | TAGS_TOPUP | TAGS_EDIT

totps = {
	pyotp.TOTP(os.environ.get('TOTP_SELLER_SECRET')): AuthScope.SELLER,
	pyotp.TOTP(os.environ.get('TOTP_MANAGER_SECRET')): AuthScope.MANAGER,
}

def authenticated(handler, required_scope):
	@wraps(handler)
	def wrapped(*args, **kwargs):
		# Session cookie integrity is checked by flask beforehand
		# If the session has been tampered with, we get an empty session object

		if 'exp' not in session:
			return jsonify({'error': 'Unauthenticated'})

		if session['exp'] < time.time():
			return jsonify({'error': 'Session expired, please authenticate again'})

		if 'p' not in session:
			return jsonify({'error': 'Unauthenticated'})

		if required_scope & session['p'] != required_scope:
			return jsonify({'error': 'Unauthorized for this action'})

		session['exp'] = int(time.time() + 3600)

		return handler(*args, **kwargs)

	return wrapped

def route_authenticate():
	ua = request.headers['User-Agent']
	
	log(f'Authenticate {ua=}')

	for (totp, authscope) in totps.items():
		if totp.verify(request.form['totp']):
			session['exp'] = int(time.time() + 3600)
			session['p'] = int(authscope)
			log(f'Authenticated {ua=} as {authscope}')
			return jsonify({'message': 'Authenticated as ' + repr(authscope), 'authLevel': int(authscope)})
	else:
		log(f'Authenticate {ua=} failed')
		return jsonify({'error': 'Unauthenticated, invalid code', 'authLevel': 0})
