from flask import jsonify, session, request
from functools import wraps
from enum import IntFlag, auto
from log import log

import os
import time
import pyotp

class AuthScope(IntFlag):
	NONE = 0
	SELL = 1
	ITEMS_VIEW = 2
	ITEMS_EDIT = 4 # Relevant functionality unimplemented
	TAGS_VIEW = 8
	TAGS_TOPUP = 16
	TAGS_INIT = 32
	TAGS_EDIT = 64 # Relevant functionality unimplemented
	BAR =   SELL | ITEMS_VIEW | TAGS_VIEW
	TOPUP =        ITEMS_VIEW | TAGS_VIEW | TAGS_INIT | TAGS_TOPUP

totps = {
	pyotp.TOTP(os.environ.get('TOTP_BAR_SECRET')): AuthScope.BAR,
	pyotp.TOTP(os.environ.get('TOTP_TOPUP_SECRET')): AuthScope.TOPUP,
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
		if totp.verify(request.form['totp'], valid_window=1):
			session['exp'] = int(time.time() + 3600)
			session['p'] = int(authscope)
			log(f'Authenticated {ua=} as {authscope}')
			return jsonify({'message': 'Authenticated as ' + repr(authscope), 'authLevel': int(authscope)})
	else:
		log(f'Authenticate {ua=} failed')
		return jsonify({'error': 'Unauthenticated, invalid code', 'authLevel': 0})
