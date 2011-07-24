#!/usr/bin/env python

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
from Header import header,footer,sorry_404
from replay import drawNaked, drawReplay

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




def playgame(g,players,map_text,map_name ):          
    # get a map
    try:
        g.grid, g.height, g.width, nplayers = tron.parse_map(map_text)
    except:
        logging.warn("MAP " + str(map_name) + " borked!")
        return None

    for p in players:
        g.add_player( p.text, p.name )
        
    # dbg info
    s = "play: " + map_name + " : "
    for i,p in enumerate(g.players):
        s += p['name'] + " ";
    logging.info( s );   
    
    # play a game
    g.run()
        
class GamePlayHandler(webapp.RequestHandler):
    def get(self):          
        map_name = self.request.get("maps")
        player1 = self.request.get("player1")
        player2 = self.request.get("player2")
        player_code = self.request.get("code").replace('\r','')
        if not player_code: 
            player_code = "def turn(b,r,c):"+'\n'+"  return 'E'";
        self.response.out.write( header() )
        pl = tron_db.Program.all().fetch(50)
        mp = tron_db.Map.all().fetch(50)
        s = "<b>play an (unranked) match. it's you against the machine, or bot vs bot</b><p>"
        s += "<form action=/play>"
        s += "<textarea rows=10 cols=90 name=code>"+player_code+"</textarea><br>"
        s += "<select name=player1 title=player1>"
        if player1:
            s += "<option>" + player1 + "</option>\n"
        s += "<option> ME </option>\n"
        for p in pl:
            s += "<option>" + p.name + "</option>\n"
        s += "</select>"
        s += "<select name=player2 title=player2 >"
        if player2:
            s += "<option>" + player2 + "</option>\n"
        for p in pl:
            s += "<option>" + p.name + "</option>\n"
        s += "<option> ME </option>\n"
        s += "</select>"
        s += "<select name=maps title=map>"
        if map_name:
            s += "<option>" + map_name + "</option>\n"
        for m in mp:
            g,r,c,p = tron.parse_map(m.text)
            if p == 2:
                s += "<option>" + str(m.key().name()) + "</option>\n"
        s += "</select>&nbsp;&nbsp;"
        s += "<input type=submit value='play a game'>"
        s += "</form>"
        if map_name and player1 and player2:
            map = tron_db.Map.get_by_key_name(map_name)
            if player1=="ME" and player_code: 
                pl1 = tron_db.Program(text=player_code,name=player1)
            else: 
                pl1 = tron_db.Program.all().filter("name",player1).get()
                
            if player2=="ME" and player_code: 
                pl2 = tron_db.Program(text=player_code,name=player2)
            else: 
                pl2 = tron_db.Program.all().filter("name",player2).get()
            if map and pl1 and pl2:
                g = tron.Game()
                playgame(g,[pl1,pl2],map.text, map_name)
                plan = [player1,player2]
                hist = [g.players[0]['hist'],g.players[1]['hist']]
                rank = [g.players[0]['score'],g.players[1]['score']]
                s += drawReplay(42,plan,hist,g.errors,rank,map_name,map.text,g.turn )
            else:
                logging.warn("invalid setup " + str(map) + " " + str(pl1) + " " + str(pl2))
        self.response.out.write( s )
        self.response.out.write( footer() )
        
        
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
        if not user:
            self.response.out.write( sorry_404("user " + user) )
            return
        r = tron_db.Program.all().filter("name",user).get()
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
        
class UserSourceHandler(webapp.RequestHandler):
    def get(self):         
        user=self.request.get("name")
        p = tron_db.Program.all().filter("name",user).get()
        if not p:
            self.response.out.write( sorry_404("botcode for " + user) )
            return
        self.response.out.write( header("SourceCode for '" + user + "'") )
        self.response.out.write( "<br><p>" )
        self.response.out.write( "<pre>" )
        self.response.out.write( p.text )
        self.response.out.write( "</pre>" )
        self.response.out.write( "<br>" )
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
        game = tron_db.GameInfo.get_by_id(int(key))
        if not game:
            self.response.out.write( sorry_404( "game " + key ) )
            return
            
        s  = header()
        map = tron_db.Map.get_by_key_name(game.mapname)
        s += drawReplay(key,game.players,game.history,game.errors,game.rank,game.mapname,map.text,game.turn,w,h)
        s += footer()
        self.response.out.write( s )



class MainHandler(webapp.RequestHandler):
    def get(self):   
        s = header();
        s += """
        <br><p><h3>Welcome to <a href='https://github.com/berak/tron-gae/' title='da source'>Tron reloaded</a>!</h3>
        It's a small programming competition for bots written in <a href='http://python.org'>Python</a>,<br>
        inspired by the <a href ='http://csclub.uwaterloo.ca/contest'>google ai tron contest</a>,
        and the <a href='http://www.rpscontest.com'>rock-paper-scissors competition</a>.<p>
        Just <a href='/up/form'>submit your bot</a> to the competition, or <a href=/play> code live </a> against the bots on this server.<br>
        You can update (or submit another bot) as often as you like. <br>
        Bots that caused more than 50 crashes or timeouts will see their source code exposed.<p><br><br>
        Watch the latest game:&nbsp;
        """
        
        game = tron_db.GameInfo.all().order("-date").get()
        map = tron_db.Map.get_by_key_name(game.mapname)
        s += "<a href=/viz?key="+str(game.key().id())+">"+str(game.key().id()) +"</a><div  onBlur='javascript:stop()'>"
        s += drawNaked(game.players,game.history,map.text,game.turn,200,200 )
        s += "</div>"
        s += footer()
        self.response.out.write( s )



        
def main():
    random.seed(time.time())
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/bots/source', UserSourceHandler),
        ('/bots/search', UserSearchHandler),
        ('/bots/', UserAllHandler),
        ('/bots*.*', UserHandler),
        ('/play', GamePlayHandler),
        ('/games/', GameAllHandler),
        ('/viz*.*', ReplayVizHandler),
        ], debug=True)
    util.run_wsgi_app(application)

    
if __name__ == '__main__':
    main()


