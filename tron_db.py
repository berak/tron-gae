#!/usr/bin/env python

from google.appengine.ext import db


#~ class GameSettings(db.Model):
    #~ TABSIZE =  db.IntegerProperty()
    #~ TS_MU =  db.FloatProperty()
    #~ MGAMES = db.IntegerProperty()
    #~ TIMEOUT_RANK = db.IntegerProperty()
    #~ TIMEOUT_WORK = db.IntegerProperty()
#~ GameSettings().put()


class GameInfo(db.Model):
    turn = db.IntegerProperty()
    players = db.StringListProperty()
    history = db.StringListProperty()
    errors = db.StringListProperty()
    rank = db.ListProperty(int)
    mapname = db.StringProperty(int)
    date = db.DateTimeProperty(auto_now_add=True)
    def html(self):
        s = "<tr>"
        s += "<td width=15%><a href=/viz?key="+str(self.key().id())+" title='run in visualizer'> game_"+str(self.key().id())+"</a></td>"
        s += "<td width=15%><a href=/maps/sh?key="+str(self.mapname)+"  title='look at the map'>"+str(self.mapname)+"</a></td>"
        s += "<td width=10%>"+str(self.turn)+"</td>"
        s += "<td width=60%> "+userlist(self)+" </td>"
        s += "</tr>"
        return s 
        
class GraveYard (GameInfo):
    pass
    

class Program(db.Model):
    text = db.TextProperty()
    name = db.StringProperty()
    date = db.DateProperty(auto_now_add=True)
    ngames = db.IntegerProperty()
    rank = db.IntegerProperty()
    skill = db.FloatProperty()
    mu    = db.FloatProperty()
    sigma = db.FloatProperty()
    won  = db.IntegerProperty()
    errors = db.IntegerProperty()

    def html(self):
        name = self.name
        s =  "<tr><td>"+str(self.rank+1)+"</td>"
        s += "<td><a name="+name+" href=/bots?name="+name+">"+name+"</a></td>"
        s += "<td title='mu=%3.2f sigma=%3.2f'>%3.2f</td>" % (self.mu,self.sigma,self.skill)
        s += "<td>"+str(self.ngames)+"</td>"
        if self.ngames:
            s += "<td title='winrate=%2.2f'>%d</td>" % ( float(self.won)/self.ngames, self.won)
        else:
            s += "<td>"+str(self.won)+"</td>"
        s += "<td>"+str(self.errors)+"</td></tr>"
        return s
        
    def reset(self, mu=30.0):
        self.rank = 10000
        self.ngames = 0
        self.won = 0
        self.skill = 0.0
        self.mu = mu
        self.sigma = mu / 3.0
        self.errors = 0
        
    def kill(self):
        d = DeadCode(name=self.name,text=self.text,ngames=self.ngames,skill=self.skill,mu=self.mu,sigma=self.sigma,won=self.won,errors=self.errors)
        d.put()
        db.delete(self)
        
Program_head = "<th>rank</th><th>bot</th><th>skill</th><th>games</th><th>won</th><th>errors</th>"

class DeadCode(Program):
    pass
        
class Map(db.Model):
    author = db.StringProperty()
    text = db.TextProperty()
    date = db.DateProperty(auto_now_add=True)

    def html(self):
        return "<tr><td><a href=/maps/sh?key="+str(self.key().name())+">"+self.key().name()+"</a></td><td>&nbsp;"+str(self.date)+"</td><td>&nbsp;<a href=/bots?name="+self.author+">"+self.author+"</a></td></tr>"

    


    
        
def userlist(r):
    s=""
    for i,u in enumerate(r.players):
        e = ""
        if r.errors[i]:
            e = r.errors[i]
        s += "&nbsp;&nbsp;<a href=/bots?name="+u+" title='"+e+"'>"
        if r.rank[i]==0:
            s += "<b>"+u+"</b>"
        elif e:
            s += "<s>"+u+"</s>"
        else:
            s += u
        s += "(" + str(len(r.history[i])-1) + ")</a>&nbsp;&nbsp;"
    return s
    

class BulletinThread(db.Model):
    author = db.StringProperty()
    title  = db.StringProperty()
    date   = db.DateProperty(auto_now_add=True)
    
class BulletinEntry(db.Model):
    ref    = db.IntegerProperty()
    author = db.StringProperty()
    text   = db.TextProperty()
    date   = db.DateProperty(auto_now_add=True)
