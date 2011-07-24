from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import tron_db
import tron
from Header import header,footer,validate_form

test_map = """
#########
#       #
#   1   #
#       #
#########
"""
#~ from worker import TS_MU
import worker

class CodeUpLoad(webapp.RequestHandler):
    def post(self):
        s = header();

        name = self.request.get("name")
        text  = self.request.get("text").replace('\r\n','\n')
        py = tron_db.Program.all().filter("name", name).get()
        if not py: 
            py = tron_db.Program( name=name )
        py.text = text
        py.reset(worker.TS_MU)
        
        try :
            #~ compile(py.code,py.title,'exec')
            game = tron.Game()
            game.readmap(test_map)
            game.add_player( py.text, py.name )
            game.run()
            if not game.errors[0]:
                py.put()
                s += "SUCCESS ! "+py.name+" is going to play soon !"
            else:
                s += "FAIL! "+py.name+" caused an error:&nbsp;&nbsp;&nbsp; '" + game.errors[0] + "\'"
        except Exception, e:
            s += "FAIL! "+py.name+" caused an exception:&nbsp;&nbsp;&nbsp; '" + str(e) + "\'"
            #raise
        s += footer()
        self.response.out.write( s )


class CodeUpForm(webapp.RequestHandler):           
    def get(self):
        res = header("submit a bot to the competition")
        res += validate_form(1)
        res += """
        <br>
        <table width=90%><tr><td>
        <form name='upload' action='/up/load' method=post enctype='multipart/form-data' onsubmit='return valid();'>
        <!--form name='upload' action='/up/load' method=post enctype='multipart/form-data'-->
        <textarea name='text' rows='30' cols='60' title='your code goes here'>def turn(board,r,c): """+'\n    '+"""return "N"</textarea>
        <br>
        <input name='name' title='botname'> &nbsp; &nbsp; &nbsp; &nbsp;
        <input type='submit' value='  upload  your   bot  '>
        </td><td valign=top>
        <br>
        First of all: it's <a href='http://python.org'>Python</a> only, sorry for that<p>
        A single function 'turn(board,r,c)' is called in each step,<br>
        you are given the board(as a row-column grid[][]), and the position of your bot.<br>
        you return the direction of your next move, one of ["N","E","S","W"] <p>
        you'll die, if you<ul><li> hit a wall('#')<li>walk onto your own tail, or into another player('1','2','3',etc)</ul>
        note, that since your code is running in a separate namespace,<br>
        you'll have to address non-const global vars as 'global'<p>
        some snippets:
        <pre>
        // roundabout
        t = 0
        DIRS=["N","E","S","W"]       
        def turn(board,r,c):
            global t
            t += 1
            t %= 4
            return DIRS[t]
            

        STEPS={'N':[-1,0],'S':[1,0],'E':[0,-1],'W':[0,1]};       
        def walk(r,c,dir): 
           return r+STEPS[dir][0], c+STEPS[dir][1]
           
        def passable(board,r,c): 
           return board[r][c] == ' '
           
        </pre>
        </td></tr></table><br>
        """
        res += footer()
        self.response.out.write(res)		



def main():
    application = webapp.WSGIApplication([
            ('/up/form', CodeUpForm),
            ('/up/load', CodeUpLoad),
        ],  debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
