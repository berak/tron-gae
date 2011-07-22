#!/usr/bin/env python
#
# Copyright 2017 Noodle Dec.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app

import logging
import random
import time

import tron
import tron_db

from Header import header,footer, validate_form

class MapHandler(webapp.RequestHandler):
    def get(self):          
        s  = header( "maps" )
        s += validate_form(1)
        s += """
        <form action=/maps/up method=post enctype='multipart/form-data' onSubmit="return valid()">
        <table>
        <tr>
        <td width=20%>
        Map Author <br>
        <input type=text name='author' title='author'> <br><br>
        Map Name <br>
        <input type=text name='name' title='name'> <br><br><br><br><br>
        <input type=submit value='upload another map'>
        </td>
        <td halign=top>
        <textarea name='text' rows=10 cols=60 title='paste your map here'></textarea>
        </td>
        <td> 
        only the following chars are allowed:
        <pre>
        wall char  : '#' 
        free space : ' ' 
        players    : ['1','2','3','4'] 
        </pre>
        maps can have up to 500 walkable fields(the max size of the history for a player).<br>
        please come up with something symmetric, that gives equal chances for each player.<br>
        </td>
        </table >
        </form>
        <table border=0 width=90%>
        """
        for m in tron_db.Map.all():
            s += m.html()
        s += "</table>"
        s += footer()
        self.response.out.write( s )
        

class MapUploadHandler(webapp.RequestHandler):
    def post(self):          
        author = self.request.get("author")
        name = self.request.get("name")
        text = self.request.get("text")
        if author and name and text:
            m = tron_db.Map(key_name=name, text=text, author=author)
            m.put()
        self.redirect("/maps/")
        
class MapShHandler(webapp.RequestHandler):
    def get(self):          
        key = self.request.get("key")
        m = tron_db.Map.get_by_key_name( key )
        
        self.response.out.write( header(m.key().name() + " by " + m.author) )
        self.response.out.write( "<pre>" )
        self.response.out.write( "\n" + m.text )
        self.response.out.write( "</pre>" )
        self.response.out.write( footer() )
        
        
def main():
    random.seed(time.time())
    application = webapp.WSGIApplication([
        ('/maps/up', MapUploadHandler),
        ('/maps/sh', MapShHandler),
        ('/maps/', MapHandler),
        ], debug=True)
    util.run_wsgi_app(application)

    
if __name__ == '__main__':
    #~ profile_main()
    main()


