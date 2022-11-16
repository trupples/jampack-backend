from database import db_connection
from flask import jsonify, request

def route_get_tags():
	cur = db_connection.cursor()
	cur.execute('select id, name, balance from Tags')

	tags = []
	for (id, name, balance) in cur:
		tags.append({'id': id, 'name': name, 'balance': balance})

	return jsonify({'tags': tags})

def route_get_tag(id):
	cur = db_connection.cursor()
	cur.execute('select id, name, balance from Tags where id = ?', [id])

	tag = cur.fetchone()

	if tag is None:
		return jsonify({})

	(id, name, balance) = tag

	return jsonify({'id': id, 'name': name, 'balance': balance})

def route_top_up(id):
	try:
		amount = int(request.form['amount'])
		if amount < 0:
			raise ValueError()
	except:
		return jsonify({'error': 'Invalid amount'})

	cur = db_connection.cursor()
	cur.execute('update Tags set balance = balance + ? where id = ?', [amount, id])
	cur.close()
	db_connection.commit()

	return jsonify({'message': 'ok'})

def route_checkout():
	user_id = request.form['user']
	iids = [int(q) for q in request.form.getlist('iids[]')]
	qtys = [int(q) for q in request.form.getlist('qtys[]')]

	if len(iids) != len(qtys) or any(q <= 0 for q in qtys):
		return jsonify({'error': 'Invalid item list'})

	total = 0
	cur = db_connection.cursor()

	cur.execute('insert into Receipts(buyer) values (?)', [user_id]);
	receipt_id = cur.lastrowid

	for iid, qty in zip(iids, qtys):
		cur.execute('select cost from Items where id = ?', [iid])
		item = cur.fetchone()
		total += qty * item[0]

	cur.execute('select balance from Tags where id = ?', [user_id])
	balance = cur.fetchone()[0]

	if total > balance:
		cur.close()
		db_connection.rollback()
		return jsonify({'error': 'Insufficient funds'})

	for iid, qty in zip(iids, qtys):
		cur.execute('insert into ReceiptItems(receipt_id, item_id, quantity) values (?, ?, ?)', [receipt_id, iid, qty])

	cur.execute('update Tags set balance = balance - ? where id = ?', [total, user_id])

	cur.close()
	db_connection.commit()

	return jsonify({'message': 'ok'})
