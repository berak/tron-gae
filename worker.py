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
import trueskill
from django.utils import simplejson

import tron
import tron_db
from Header import header,footer
TS_MU = 38.0
MGAMES = 5
TIMEOUT_RANK = 200
TIMEOUT_WORK = 60



def run_game():
    
    # get a map
    g = tron.Game()
    maps = tron_db.Map.all(keys_only=True).fetch(1000)
    mkey = random.choice(maps)
    map  = tron_db.Map.get(mkey)
    try:
        g.grid, g.height, g.width, players = tron.parse_map(map.text)
    except:
        logging.warn("MAP " + str(map.key().name()) + " borked!")
        return
    # get players
    keys = tron_db.Program.all(keys_only=True).fetch(1000)
    rnk  = random.sample(keys, players)

    prog = []
    for k in rnk:
        p = tron_db.Program.get(k)
        g.add_player( p.text, p.name )
        prog.append(p)
        
    # dbg info
    s = map.key().name() + " : "
    for i,p in enumerate(g.players):
        s += p['name'] + " ";
    logging.info( s );   
    
    # play a game
    g.run()
    
    #serialize it
    sav = tron_db.GameInfo( mapname=map.key().name(), turn=g.turn )
    for i,p in enumerate(g.players):
        if g.errors[i]:
            logging.info(p['name'] + " : " + g.errors[i])
        sav.errors.append(g.errors[i])
        sav.players.append(p['name'])
        sav.history.append(p['hist'][:500])
        sav.rank.append(p['score'])
        if p['score'] == 0:
            prog[i].won += 1
        if g.errors[i]:
            prog[i].errors += 1
        prog[i].ngames += 1
        #~ prog[i].put()
    sav.put()

    # update ranking
    calc_ranks( prog, sav.rank )


def calc_ranks( progs, ranks ):
    class TrueSkillPlayer(object):
        def __init__(self, name, skill, rank):
            self.name = name
            self.old_skill = skill
            self.skill = skill
            self.rank = rank

    ts_players = []
    for i, p in enumerate(progs):
        ts_players.append( TrueSkillPlayer(i, (p.mu,p.sigma), ranks[i] ) )
        
    trueskill.AdjustPlayers(ts_players)
    
    for i, p in enumerate(progs):
        p.mu    = ts_players[i].skill[0]
        p.sigma = ts_players[i].skill[1]
        p.skill = p.mu - p.sigma * 3
        p.put()
 

def recalcRanking():
    l = []
    for i,p in enumerate(tron_db.Program.all()):
        l.append(p)
    def by_skill(a,b):
        return cmp(b.skill, a.skill)
    l.sort(by_skill)
    for i,z in enumerate(l):
        z.rank = i
        z.put()


class StartHandler(webapp.RequestHandler):
    def get(self): 
        taskqueue.add(url='/worker/rank', countdown=0, params={})
        taskqueue.add(url='/worker/game', countdown=0, params={})
        self.redirect("/bots/")
        
class RankWorker(webapp.RequestHandler):
    def post(self): 
        recalcRanking()
        
        taskqueue.add(url='/worker/rank', countdown=TIMEOUT_RANK, params={})


class GameWorker(webapp.RequestHandler):
    def post(self): 
        for i in range(MGAMES):
            run_game()
            
        taskqueue.add(url='/worker/game', countdown=TIMEOUT_WORK, params={})

class ClearHandler(webapp.RequestHandler):
    def get(self):        
        db.delete(tron_db.GameInfo.all())
        for p in tron_db.Program.all():
            p.reset(TS_MU)
            p.put()
            
        self.redirect( "/bots/" )


        
def main():
    random.seed(time.time())
    application = webapp.WSGIApplication([
        ('/worker/game', GameWorker),
        ('/worker/rank', RankWorker),
        ('/worker/clear', ClearHandler),
        ('/worker/start', StartHandler),
        ], debug=True)
    util.run_wsgi_app(application)

    
if __name__ == '__main__':
    #~ profile_main()
    main()


