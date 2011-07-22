
def header(title=""):
    return """
    <html><head><title>"""+title+"""</title><link rel='stylesheet' href='/res/main.css'></head>
        <div  class='H'>
        <form action=/bots/search><b>
        <img src="/res/tron.png" height=15>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/ name=top> home </a> &nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/bots/> leaderboard </a> &nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/games/> games </a> &nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/up/form > upload </a> &nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/maps/> maps </a> &nbsp;&nbsp;&nbsp;&nbsp;
        <a href=/bbs/all > bbs </a> </b>&nbsp;&nbsp;&nbsp;&nbsp;
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <input type=text name='name' title='search bot' >
        <submit value='search bot'>
        </form>
        </div>
    """
    
def footer():
    return """
    <br>
    <!--a href=#top title='top'>^</a-->
    <p>
    <div> <font color=#333>kunst ist schoen, macht aber viel arbeit</font></div>
    </body>
    </html>
    """
    
def validate_form(n=1):
    return """
    <script>
            function valid(){
                with( document.forms["""+str(n)+"""] ) {
                    for ( var e=0;e< elements.length; e++ ) {
                        with(elements[e])
                        if(value==undefined || value==null || value=="") {
                            alert('please enter a valid ' + name + ' !');
                            return false;
                        }
                    }
                }
                return true;
            }
    </script>
    """
