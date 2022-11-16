from database import db_connection
from flask import jsonify, Response, make_response

def route_get_items():
	cur = db_connection.cursor()
	cur.execute('select id, name, cost from Items order by cost asc, name asc, id asc')

	items = []
	for (id, name, cost) in cur:
		items.append({'id': id, 'name': name, 'cost': cost})

	return jsonify({'items': items})

def route_get_item(id):
	cur = db_connection.cursor()
	cur.execute('select id, name, cost from Items where id = ? order by cost asc, name asc, id asc', [id])

	(id, name, cost) = cur.fetchone()

	return jsonify({'id': id, 'name': name, 'cost': cost})

def route_get_item_image(id):
	cur = db_connection.cursor()
	cur.execute('select image from Items where id = ?', [id])

	image = cur.fetchone()

	if image is None:
		return make_response('', 404)

	return Response(image, mimetype='image/jpeg')

def route_get_stock():
	cur = db_connection.cursor()
	cur.execute('select id, name, cost, coalesce(sum(quantity), 0) as \'sold\' from Items left join ReceiptItems on item_id = id group by id order by cost asc, name asc, id asc')

	items = []
	for (id, name, cost, sold) in cur:
		items.append({'id': id, 'name': name, 'cost': cost, 'sold': int(sold)})

	return jsonify({'items': items})
