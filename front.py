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
from google.appengine.api import taskqueue

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson

import re
import logging
import time
import datetime
import random
import operator
from django.utils import simplejson


import tron
import tron_db
from Header import header,footer
TABSIZE = 40


def game_table( response, query ):
    response.out.write( "&nbsp;&nbsp;&nbsp;&nbsp;<div>" )
    response.out.write( "<table>" )
    response.out.write( "<th>game</th><th>map</th><th>turns</th><th> players </th>" )
    for r in query:
        response.out.write(  r.html() )
    response.out.write( "</table></div>" )


def get_offset( request ):
    try:
        return int(request.get('o'))
    except: 
        return 0
        
def table_pager( url, cnt=0 ):
    l = "page &nbsp;&nbsp;&nbsp;";
    for i in range((cnt+TABSIZE)/TABSIZE):
        #~ l += "<a href='/games/?o="+str(i*TABSIZE)+"'>["+str(i*TABSIZE)+"-"+str((i+1)*TABSIZE)+"]<a>&nbsp;&nbsp;&nbsp;"
        l += "<a href='"+url+"?o="+str(i*TABSIZE)+"'>"+str(i)+" <a>&nbsp;&nbsp;&nbsp;"
        if i >= 10: break
    return l

        
class GameAllHandler(webapp.RequestHandler):
    def get(self):          
        #~ keys =  tron_db.GameInfo.all(keys_only=True).order('-date').fetch(TABSIZE, offs)
        offs = get_offset(self.request)
        order = tron_db.GameInfo.all().order('-date')
        count = order.count()
            
        self.response.out.write(  header(title="latest games" ) )
        game_table(self.response, order.fetch(TABSIZE, offs) )

        self.response.out.write( "<p>" + table_pager( "/games/", count) + "<p>" )
        self.response.out.write( footer() )


class UserAllHandler(webapp.RequestHandler):
    def get(self):          
        offs = get_offset(self.request)
        query = tron_db.Program.all().order('rank')
        count = query.count()
        self.response.out.write(  header() )
        self.response.out.write( "<p><table>" )
        self.response.out.write( tron_db.Program_head )
        for i,r in enumerate(query.fetch(TABSIZE,offs)):
            self.response.out.write( r.html() )
        self.response.out.write( "</table>" + "<p>" + table_pager("/bots/",count) + "<p>" )
        self.response.out.write( footer() )


class UserHandler(webapp.RequestHandler):
    def get(self):         
        user=self.request.get("name")
        r = tron_db.Program.all().filter("name",user).get()
        #~ r = db.GqlQuery("select * from Program where name=:1",user).get()
        self.response.out.write( header("Profile for '" + user + "'") )
        self.response.out.write( "<table>" )
        self.response.out.write( tron_db.Program_head )
        self.response.out.write( r.html() )
        self.response.out.write( "</table></div>" )
        self.response.out.write( "<br>" )
        query = tron_db.GameInfo.all().filter("players in", [user])
        offs = get_offset(self.request)
        game_table( self.response, query.order('-date').fetch(TABSIZE,offs) )
        self.response.out.write( table_pager( "/games/",query.count()) + "<p>" )
        self.response.out.write( footer() )


class UserSearchHandler(webapp.RequestHandler):
    def get(self):           
        s = header();
        name = self.request.get("name")
        if not name : return
        res = tron_db.Program.all().filter("name >=",name).filter("name <", name + u'\ufffd')
        #~ res = tron_db.Program.all().filter("name =",name)
        nr = res.count()
        if nr == 1:
            z = res.get()
            self.redirect( "/bots?name="+z.name)
            return
        elif nr > 1:
            s += "found " + str(nr) + " bots named like '" + name + "'.<ul>"
            for z in res:
                s += "<li><a href=/bots?name="+z.name+"> " + z.name + " </a><br>"                
            s += "</ul>"
        else:
            s += "sorry, there is no bot named '" + name + "\'."
        s += footer()
        self.response.out.write( s )
            


def drawNaked(key, w, h):
    game = tron_db.GameInfo.get_by_id(int(key))
    map = tron_db.Map.get_by_key_name(game.mapname)
    rep = {}
    rep['id'] = key
    rep['turns'] = game.turn
    rep['players'] = game.players
    rep['history'] = game.history
    rep['board'],rep['h'],rep['w'],players = tron.parse_map(map.text)

    return """
    <canvas width="""  + str(w)+ " height="+str(h)+""" id='C'>
    <p>
    <div align=center>
    <a href='javascript:back()'>&lt;</a>&nbsp;
    <a href='javascript:stop()'>stop</a>&nbsp;
    <a href='javascript:forw()'>&gt;</a>&nbsp;
    </div>
    <script>
        replay = """ + simplejson.dumps(rep) + """;
        dirs={'N':[-1,0],'S':[1,0],'E':[0,1],'W':[0,-1]};
        colors = {
            '#':'rgb(100,100,100)',
            ' ':'rgb(70,70,70)',
            '1':'rgb(0,0,255)',
            '2':'rgb(0,255,0)',
            '3':'rgb(255,0,0)',
            '4':'rgb(255,255,0)',
            '5':'rgb(255,0,255)',
            };
        function drawboard(turn) {
            C = document.getElementById('C')
            V = C.getContext('2d');
            sw = """+str(w)+""" / replay['w']
            sh = """+str(h)+""" / replay['h']
            ppos = []
            for (r=0; r<replay['h']; r++) {
                for (c=0; c<replay['w']; c++) {
                    elm = replay['board'][r][c]
                    if ( elm in ['1','2','3','4'] ) {
                        ppos.push( [r,c,elm] )
                    }
                    V.fillStyle = colors[elm]
                    V.fillRect(c*sw,r*sh,sw,sh)
                    //V.fillStyle = 'rgb(100,0,100)'
                    //V.fillRect(c*sw+3,r*sh+3,sw-3,sh-3)
                }
            }
            for (t=0; t<turn; t++) {
                for (p=0; p<replay['players'].length; p++) {
                    hist = replay['history'][p]
                    if (hist.length > t) {
                        dr = dirs[hist[t]][0]
                        dc = dirs[hist[t]][1]
                        r  = dr + ppos[p][0] 
                        c  = dc + ppos[p][1] 
                        if (c<0) c=0; 
                        if (r<0) r=0; 
                        if (c>C.width)  c=C.width; 
                        if (r>C.height) r=C.height; 
                      //  alert(replay['players'][p] + " " + replay['history'][p][t] + " " + r + " " + c + " " + ppos[p] )
                        ppos[p][0] = r
                        ppos[p][1] = c                            
                        V.fillStyle = colors[ppos[p][2]]
                        V.fillRect(c*sw,r*sh,sw,sh)
                    }
                }
                //alert(t)
            }
        }
        function stop() {
            clearInterval(tick)
            tick=-1
        }
        the_turn = 0
        tick = setInterval( function() {
            if (the_turn <= replay['turns'])
            {
                drawboard(the_turn)
                the_turn += 1
            }
        },500)
    </script>"""



class ReplayVizHandler(webapp.RequestHandler):
    def get(self):           
        key = self.request.get("key")
        try:
            w = self.request.get("w")
            h = self.request.get("h")
        except:
            pass
        if not w : w=400
        if not h : h=400
        s  = header()
        s += "<table border=0 ><tr><td>"
        s += drawNaked( key, w, h )
        s += "</td><td>"
        game = tron_db.GameInfo.get_by_id(int(key))
        s += "game " + str(game.key().id()) + "<br><br>"
        s += "map  " + str(w) +  " " + str(h) + "<br><br>"
        s += "<table width=100%>"
        for i,p in enumerate(game.players):
            s += "<tr><td>" + p + "</td><td>" + str(game.rank[i])+ "</td><td>" + game.history[i] + "</td><td>" + game.errors[i] + "</td></tr>"
        s += "</table>"
        s += "</td></tr></table>"
        s += footer()
        self.response.out.write( s )



class MainHandler(webapp.RequestHandler):
    def get(self):   
        s = header();
        s += """
        <br><p><h3>Welcome to Tron reloaded!</h3>
        This is a programming competition for bots written in <a href='http://python.org'>Python</a>,<br>
        inspired by the <a href ='http://csclub.uwaterloo.ca/contest'>google ai tron contest</a>,
        and the <a href='http://www.rpscontest.com'>rock-paper-scissors competition</a>.<p>
        Just <a href='/up/form'>submit your code</a> and let your bot play on this server.<br>
        You can send in as many bots as you like (though it's more fun playing against other ppl..) <p><br><br>
        Watch the latest game:&nbsp;
        """
        
        gameid = tron_db.GameInfo.all().order("-date").get().key().id()
        s += str(gameid) +"<div>" + drawNaked( gameid,200,200 )+"</div>"
        s += footer()
        self.response.out.write( s )



        
def main():
    random.seed(time.time())
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/bots/search', UserSearchHandler),
        ('/bots/', UserAllHandler),
        ('/bots*.*', UserHandler),
        ('/games/', GameAllHandler),
        ('/viz*.*', ReplayVizHandler),
        ], debug=True)
    util.run_wsgi_app(application)

    
if __name__ == '__main__':
    #~ profile_main()
    main()


