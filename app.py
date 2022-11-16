import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS

from authentication import *
from items import *
from tags import *

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
CORS(app, origins = [os.environ.get('FRONTEND_ORIGIN')], supports_credentials = True)

routes = {
	'/items': {'GET': route_get_items},
	'/item/<id>': {'GET': route_get_item},
	'/item/<id>.jpg': {'GET': route_get_item_image},
	
	'/stock': {'GET': authenticated(route_get_stock, AuthScope.ITEMS_VIEW)},

	'/tags': {'GET': authenticated(route_get_tags, AuthScope.TAGS_VIEW)},
	'/tag/<id>': {'GET': route_get_tag},
	'/tag/<id>/topUp': {'POST': authenticated(route_top_up, AuthScope.TAGS_TOPUP)},

	'/checkout': {'POST': authenticated(route_checkout, AuthScope.SELL)},

	'/authenticate': {'POST': route_authenticate},
}

print('Implemented routes:')
for route in routes:
	for (method, handler) in routes[route].items():
		print(method, route)
		app.route(route, methods=[method])(handler)
