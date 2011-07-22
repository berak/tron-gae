from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import tron_db
import tron
from Header import header,footer, validate_form


class BulletinNewThread(webapp.RequestHandler):
    def post(self):
        s = header();
        b = tron_db.BulletinThread( title=self.request.get("title"), author=self.request.get("author"))
        b.put()
        self.redirect( "/bbs/thread?id="+str(b.key().id()) )


class BulletinAddEntry(webapp.RequestHandler):
    def post(self):
        s = header();
        ref=self.request.get("ref")
        e = tron_db.BulletinEntry( ref=int(ref), text=self.request.get("text"), author=self.request.get("author"))
        e.put()
        self.redirect( "/bbs/thread?id="+str(ref) )


class BulletinThreadHandler(webapp.RequestHandler):           
    def get(self):
        id = self.request.get("id")
        b = tron_db.BulletinThread.get_by_id(int(id))
        s = header();
        s += validate_form(1)
        s += "<table><th width=15%>"+b.author+":</th><th>"+b.title+"</th><th width=15%>"+str(b.date)+"</th>\n"
        for t in tron_db.BulletinEntry.all().filter('ref =',int(id)):
            s += "<tr><td width=15%>" + t.author + ": </td><td>" + t.text + "</td><td width=15%>" + str(t.date) + "</td></tr>\n"
        s += """
        </table>
        <p>
        <table>
        <tr><td>
        <form action=/bbs/add onSubmit='return valid()' method=post>
        <textarea name=text rows=2 cols=110></textarea></td><td>
        <input type=hidden name=ref value="""+str(id)+""">
        <input type=text name=author title='author'>
        <input type=submit value='add an entry'>
        </form>
        </td>
        </tr>
        </table>
        """
        s += footer()
        self.response.out.write( s )


class BulletinAllHandler(webapp.RequestHandler):           
    def get(self):
        s = header();
        s += validate_form(1)
        s += """
        <table>
        <form action=/bbs/new onSubmit='return valid()' method=post>
        <tr><td align=left>
        <input type=text size=120 name=title title='title'>
        <input type=text name=author title='author'>
        <input type=submit value='start a new thread'>
        </td></tr>
        </form>
        </table>
        <p>
        <table>
        <th width=15%>from</th><th>topic</th><th width=15%>date</th>
        """
        for b in tron_db.BulletinThread.all():
            s += "<tr><td width=15%>" + b.author + ": </td><td><a href=/bbs/thread?id=" + str(b.key().id())+">" + b.title + "</a></td><td width=15%>" + str(b.date) + "</td></tr>\n"
        s += """
        </form>
        </table>
        """
        s += footer()
        self.response.out.write( s )
        


def main():
    application = webapp.WSGIApplication([
            ('/bbs/all', BulletinAllHandler),
            ('/bbs/new', BulletinNewThread),
            ('/bbs/add', BulletinAddEntry),
            ('/bbs/thread', BulletinThreadHandler),
        ],  debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
