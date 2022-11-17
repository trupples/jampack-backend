from database import get_db_connection
from flask import jsonify, Response, make_response

def route_get_items():
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('select id, name, cost from Items order by cost asc, name asc, id asc')

	items = []
	for (id, name, cost) in cur:
		items.append({'id': id, 'name': name, 'cost': cost})

	cur.close()
	db_connection.close()

	return jsonify({'items': items})

def route_get_item(id):
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('select id, name, cost from Items where id = %s order by cost asc, name asc, id asc', [id])

	(id, name, cost) = cur.fetchone()

	cur.close()
	db_connection.close()

	return jsonify({'id': id, 'name': name, 'cost': cost})

def route_get_item_image(id):
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	
	cur.execute('select image from Items where id = %s', [id])

	image = cur.fetchone()

	if image is None:
		return make_response('', 404)

	cur.close()
	db_connection.close()

	return Response(image, mimetype='image/jpeg')

def route_get_stock():
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('select id, name, cost, coalesce(sum(quantity), 0) as \'sold\' from Items left join ReceiptItems on item_id = id group by id order by cost asc, name asc, id asc')

	items = []
	for (id, name, cost, sold) in cur:
		items.append({'id': id, 'name': name, 'cost': cost, 'sold': int(sold)})

	cur.close()
	db_connection.close()

	return jsonify({'items': items})
