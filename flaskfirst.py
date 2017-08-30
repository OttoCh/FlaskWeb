from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import flash
from flask import jsonify
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
print __name__

#decorator
@app.route('/')
@app.route('/restaurant/')
def showRestaurantList():
	restaurant = session.query(Restaurant).all()
	return render_template('main.html',items=restaurant)

@app.route('/restaurant/<int:rest_id>/')
def restaurantMenu(rest_id):
	restaurant = session.query(Restaurant).first()
	items = session.query(MenuItem).filter_by(restaurant_id = rest_id)
	if items.count()==0:
		return render_template('404.html'), 404
	else: 
		return render_template('menu.html', restid=rest_id,items=items)

@app.route('/restaurant/<int:rest_id>/create', methods=['GET','POST'])
def createNewMenu(rest_id):
	newMenu = MenuItem()
	url = url_for('restaurantMenu',rest_id= rest_id)
	if request.method == 'POST':
		menu_name = request.form['menu_name']
		menu_price = request.form['menu_price']
		menu_desc = request.form['menu_desc']
		menu_course = request.form['menu_course']
		newMenu = MenuItem(name = menu_name, course=menu_course, description=menu_desc, price=menu_price, restaurant_id=rest_id)
		session.add(newMenu)
		session.commit()
		flash("new menu created")
		return render_template('create.html',restid=rest_id, url=url)
	else:
		#return output
		return render_template('create.html',restid=rest_id, url=url)


@app.route('/restaurant/<int:rest_id>/<int:menu_id>/edit', methods=['GET','POST'])
def editMenu(rest_id, menu_id):
	url = url_for('showRestaurantList')
	if request.method == 'POST':
		editted_menu = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=rest_id).first()
		editted_menu.name = request.form['menu_name']
		editted_menu.price = request.form['menu_price']
		editted_menu.description = request.form['menu_desc']
		editted_menu.course = request.form['menu_course']
		session.add(editted_menu)
		session.commit()
		editted_menu = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=rest_id).first()
		#return output
		flash("menu item has been editted")
		return render_template('edit.html',restid=rest_id,menuid=menu_id,url=url, editted_menu=editted_menu)
	else:
		#return output
		editted_menu = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=rest_id).first()
		return render_template('edit.html',restid=rest_id,menuid=menu_id, url=url, editted_menu=editted_menu)

@app.route('/restaurant/<int:rest_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenu(rest_id, menu_id):
	url = url_for('showRestaurantList')
	if request.method == 'POST':
		item = session.query(MenuItem).filter_by(restaurant_id = rest_id, id = menu_id).one()
		session.delete(item)
		session.commit()
		flash("Menu item has been deleted")
		return render_template('delete.html', restid=rest_id, menuid=menu_id, url=url)
	else:
		targetMenu = session.query(MenuItem).filter_by(restaurant_id = rest_id, id = menu_id).one()
		return render_template('delete.html', menuname=targetMenu.name, restid=rest_id, menuid=menu_id, url=url)

#API endpoint
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuOneJSON(restaurant_id, menu_id):
	#restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	#items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	menu = session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItem=menu.serialize)

@app.route('/location')
def findLocation():
	geoip_url = 'http://freegeoip.net/json/{}'.format(request.remote_addr)
	print format(request.remote_addr)
	client_location = requests.get(geoip_url).json()
	return render_template('location.html', client_location=client_location)

@app.errorhandler(404)
def not_found(error):
	output = "404, not found"
	return output

if __name__ == '__main__':
	app.secret_key = 'secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 1775)