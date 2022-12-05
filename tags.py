from database import get_db_connection
from flask import jsonify, request
from log import log

def route_get_tags():
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('select id, name, balance from Tags')

	tags = []
	for (id, name, balance) in cur:
		tags.append({'id': id, 'name': name, 'balance': balance})

	cur.close()
	db_connection.close()

	return jsonify({'tags': tags})

def route_get_tag(id):
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('select id, name, balance from Tags where id = %s', [id])

	tag = cur.fetchone()

	if tag is None:
		cur.close()
		db_connection.close()
		return jsonify({})

	(id, name, balance) = tag

	cur.close()
	db_connection.close()

	return jsonify({'id': id, 'name': name, 'balance': balance})

def route_top_up(id):
	if 'amount' not in request.form:
		return jsonify({'error': 'Invalid request'})

	db_connection = get_db_connection()
	cur = db_connection.cursor()
	amount = int(request.form['amount'])

	log(f'Top up {id=} {amount=}')

	try:
		cur.execute('update Tags set balance = balance + %s where id = %s', [amount, id])
	except:
		cur.close()
		db_connection.commit()
		db_connection.close()
		log(f'Top up {id=} {amount=} failed')
		return jsonify({'error': 'An error occured'})

	cur.close()
	db_connection.commit()
	db_connection.close()

	log(f'Top up {id=} {amount=} succeeded')
	return jsonify({'message': 'ok'})

def route_checkout():
	user_id = request.form['user']
	iids = [int(q) for q in request.form.getlist('iids[]')]
	qtys = [int(q) for q in request.form.getlist('qtys[]')]

	if len(iids) != len(qtys) or any(q <= 0 for q in qtys):
		return jsonify({'error': 'Invalid item list'})

	total = 0
	db_connection = get_db_connection()
	cur = db_connection.cursor()

	cur.execute('insert into Receipts(buyer) values (%s)', [user_id]);
	receipt_id = cur.lastrowid

	for iid, qty in zip(iids, qtys):
		cur.execute('select cost from Items where id = %s', [iid])
		item = cur.fetchone()
		total += qty * item[0]

	log(f'Checkout {user_id=} {total=}')

	cur.execute('select balance from Tags where id = %s', [user_id])
	prev_balance = cur.fetchone()[0]

	if total > prev_balance:
		cur.close()
		db_connection.rollback()
		db_connection.close()
		log(f'Checkout {user_id=} {total=} Insufficient funds')
		return jsonify({'error': 'Insufficient funds', 'prev_balance': prev_balance, 'current_balance': prev_balance})

	for iid, qty in zip(iids, qtys):
		cur.execute('insert into ReceiptItems(receipt_id, item_id, quantity) values (%s, %s, %s)', [receipt_id, iid, qty])

	cur.execute('update Tags set balance = balance - %s where id = %s', [total, user_id])

	cur.close()
	db_connection.commit()
	db_connection.close()

	log(f'Checkout {user_id=} {total=} Sold')
	return jsonify({'message': 'ok', 'prev_balance': prev_balance, 'current_balance': prev_balance-total})
