from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if(self.path.endswith('/restaurant') or self.path.endswith('/restaurant/')):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				items = session.query(Restaurant).all()
				for item in items:
					output += item.name + "<br>"

					output += "<a href='"
					output += "/restaurant/" + str(item.id) + "/edit"
					output += "'>edit</a><br>"

					output += "<a href='"
					output += "/restaurant/" + str(item.id) + "/delete"
					output += "'>delete</a><br>"

				output += "<a href='/restaurant/new'>Make a new restaurant</a>"
				output += "</body></html>"

				self.wfile.write(output)
				#print output
				return

			elif self.path.endswith('/restaurant/new'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/new'>	\
				<h2>Make a new Restaurant!</h2><input name='restaurantName' type='/text'>	\
				<input type='submit' value='Submit'></form>"
				output += "<a href='/restaurant'></href>return to list"
				output += "</body></html>"
				self.wfile.write(output)
				#print output
				return

			elif self.path.endswith('/edit'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				#get id
				idNumb = int(self.path.split('/')[2])

				targetRestaurantName = session.query(Restaurant).filter_by(id=idNumb).one()

				output = ""
				output += "<html><body>"
				#name resto
				#form
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit'>	\
				<h2>Edit %s!</h2><input name='restaurantName' type='/text'>	\
				<input type='submit' value='Submit'></form>" % (str(idNumb), targetRestaurantName.name)
				output += "<a href='/restaurant'></href>Back to Menu</a>"
				output += "</body></html>"

				self.wfile.write(output)
				#print output
				return

			elif self.path.endswith('/delete'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				idNumb = int(self.path.split('/')[2])

				targetRestaurant = session.query(Restaurant).filter_by(id=idNumb).one()

				output = ""
				output += "<html><body>"
				output += "Are you sure you want to delete %s?" % targetRestaurant.name
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>" % idNumb
				output += "<input type='submit' value='Delete'>"
				output += "</form>"
				output += "</body></html>"

				self.wfile.write(output)
				#print output
				return

		except IOError:
			self.send_error(404, "%s File not found" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith('/new'):
				self.send_response(301)
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newRestaurantName = fields.get('restaurantName')
					newName = Restaurant(name=str(newRestaurantName[0]))
					session.add(newName)
					session.commit()

				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/new'>	\
				<h2>Make a new Restaurant!</h2><input name='restaurantName' type='/text'>	\
				<input type='submit' value='Submit'></form><br>"
				output += "<a href='/restaurant'></href>return to list"
				output += "</body></html>"

				self.wfile.write(output)
				#print output
				return

			elif self.path.endswith('/edit'):
				self.send_response(301)
				self.end_headers()

				restaurantId = 0
				targetRestaurantName = ""
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newRestaurantName = fields.get('restaurantName')[0]
					restaurantId = int(self.path.split('/')[2])
					targetRestaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
					targetRestaurant.name = newRestaurantName
					targetRestaurantName = targetRestaurant.name
					session.add(targetRestaurant)
					session.commit()

				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit'>	\
				<h2>Edit %s!</h2><input name='restaurantName' type='/text'>	\
				<input type='submit' value='Submit'></form>" % (str(restaurantId), targetRestaurantName)
				output += "<a href='/restaurant'></href>Back to Menu</a>"
				output += "</body></html>"

				self.wfile.write(output)
				#print output
				return

			elif self.path.endswith('/delete'):
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurant')
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurantId = int(self.path.split('/')[2])
					targetRestaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
					session.delete(targetRestaurant)
					session.commit()


				return
		except:
			pass

def main():
	try:
		port = 1775
		server = HTTPServer(('', port), webServerHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		print "^C interrupt"
		server.socket.close()

if __name__ == '__main__':
	print __name__
	main()