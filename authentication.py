from flask import jsonify, session, request
from functools import wraps

import os
import time
import pyotp
totp = pyotp.TOTP(os.environ.get('TOTP_SECRET'))

from database import db_connection

def authenticated(handler):
	@wraps(handler)
	def wrapped(*args, **kwargs):
		if 'exp' not in session:
			return jsonify({'error': 'Unauthenticated'})

		if session['exp'] < time.time():
			return jsonify({'error': 'Session expired, please authenticate again'})

		session['exp'] = time.time() + 3600

		return handler(*args, **kwargs)

	return wrapped

def route_authenticate():
	if totp.verify(request.form['totp']):
		session['exp'] = time.time() + 3600
		return jsonify({'message': 'Authenticated'})
	else:
		return jsonify({'error': 'Unauthenticated, invalid code'})
