from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import random
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback
#DB engine creating
db_engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = db_engine
Session = sessionmaker(bind=db_engine)
session = Session()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Create new restaurants</h1>"
                output += '''<form method='POST' enctype='multipart/form-data'><input name="restaurant_name" type="text" ><input type="submit" value="Submit"> </form>'''
                restaurants = session.query(Restaurant).all()
                for i in restaurants:
                    output += "%s<br>" %(i.name)
                    output += '''<a href="/%s/edit">Edit</a><br>''' %i.id
                    output += '''<a href="/%s/delete">Delete</a><br>''' %i.id
                    output += "<hr>"
                    output += "</body></html>"
                self.wfile.write(output)
                return
            elif self.path.endswith("/edit"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ID = int(self.path.split('/')[-2])
                #print ID
                output = ""
                output += "<html><body>"
                restaurant = session.query(Restaurant).filter_by(id=ID).all()[0]
                output += "<h1>%s</h1>" %restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data'><input name="restaurant_name" type="text" >'''
                output += '''<input type="hidden" name="name_to_be_edited" type="text" value = "%s">'''%restaurant.name
                output += '''<input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                session.commit()
            elif self.path.endswith("/delete"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ID = int(self.path.split('/')[-2])
                #print ID
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete<br></h1>"
                restaurant = session.query(Restaurant).filter_by(id=ID).all()[0]
                output += "<h1>%s</h1>" %restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data'>'''
                output += '''<input name="restaurant_name" type="hidden" >'''
                output += '''<input type="hidden" name="name_to_be_deleted" value = "%s">'''%restaurant.name
                output += '''<input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                session.commit()
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('restaurant_name')
                restaurant_edit = fields.get('name_to_be_edited')
                restaurant_delete = fields.get('name_to_be_deleted')
                name = messagecontent[0]
                
                if restaurant_delete is not None:
                    name_delete = restaurant_delete[0]
                    print "++++++++++++"
                    print name_delete
                    print "++++++++++++"
                    if name_delete:
                        print "deleting section"
                        restaurant_delete_query = session.query(Restaurant).filter_by(name='%s' %name_delete).all()[0]
                        session.delete(restaurant_delete_query)
                        session.commit()
                if restaurant_edit is not None:
                    name2 = restaurant_edit[0]
                    restaurant = session.query(Restaurant).filter_by(name='%s' %name2).all()
                    newrestaurant = restaurant[0]
                else:
                    newrestaurant = Restaurant()
                    newrestaurant.id = random.randint(1,10000)
                    print newrestaurant.name
                    print newrestaurant.id
                    print messagecontent
                newrestaurant.name = messagecontent[0]
                session.add(newrestaurant)
                session.commit()
        except:
            print(traceback.print_exc())


def main():
    try:
        port = 5000
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()