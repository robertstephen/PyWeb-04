"""
For your homework this week, you'll be creating a new WSGI application.

The MEMEORIZER acquires a phrase from one of two sources, and applies it
to one of two meme images.

The two possible sources are:

  1. A fact from http://unkno.com
  2. One of the 'Top Stories' headlines from http://www.cnn.com

For the CNN headline you can use either the current FIRST headline, or
a random headline from the list. I suggest starting by serving the FIRST
headline and then modifying it later if you want to.

The two possible meme images are:

  1. The Buzz/Woody X, X Everywhere meme
  2. The Ancient Aliens meme (eg https://memegenerator.net/instance/11837275)

To begin, you will need to collect some information. Go to the Ancient
Aliens meme linked above. Open your browser's network inspector; in Chrome
this is Ctrl-Shift-J and then click on the network tab. Try typing in some
new 'Bottom Text' and observe the network requests being made, and note
the imageID for the Ancient Aliens meme.

TODO #1:
The imageID for the Ancient Aliens meme is: 627067
The imageID for Buzz/Woody X, X Everywhere meme is: 8619102

You will also need a way to identify headlines on the CNN page using
BeautifulSoup. On the 'Unnecessary Knowledge Page', our fact was
wrapped like so:

```
<div id="content">
  Penguins look like they're wearing tuxedos.
</div>
```

So our facts were identified by the tag having
* name: div
* attribute name: id
* attribute value: content

We used the following BeautifulSoup call to isolate that element:

```
element = parsed.find('div', id='content')
```

Now we have to figure out how to isolate CNN headlines. Go to cnn.com and
'inspect' one of the 'Top Stories' headlines. In Chrome, you can right
click on a headline and click 'Inspect'. If an element has a rightward
pointing arrow, then you can click on it to see its contents.

element = parsed.find('span', class='cd_headline-text')

element = parsed.find_all('span', class='cd_headline-text')

TODO #2:
Each 'Top Stories' headline is wrapped in a tag that has:
* name: span
* attribute name: class
* attribute value: cd__headline-text

NOTE: We used the `find` method to find our fact element from unkno.com.
The `find` method WILL ALSO work for finding a headline element from cnn.com,
although it will return exactly one headline element. That's enough to
complete the assignment, but if you want to isolate more than one headline
element you can use the `find_all` method instead.


TODO #3:
You will need to support the following four requests:

```
  http://localhost:8080/fact/buzz
  http://localhost:8080/fact/aliens
  http://localhost:8080/news/buzz
  http://localhost:8080/news/aliens
```

You can accomplish this by modifying the memefacter.py that we created
in class.

There are multiple ways to architect this assignment! You will probably
have to either change existing functions to take more arguments or create
entirely new functions.

I have started the assignment off by passing `path` into `process` and
breaking it apart using `strip` and `split` on lines 136, 118, and 120.

To submit your homework:

  * Fork this repository (PyWeb-04).
  * Edit this file to meet the homework requirements.
  * Your script should be runnable using `$ python memeorizer.py`
  * When the script is running, I should be able to view your
    application in my browser.
  * Commit and push your changes to your fork.
  * Submit a link to your PyWeb-04 fork repository!

"""

from bs4 import BeautifulSoup
import requests

def meme_it(imagename,text):
    url = 'http://cdn.meme.am/Instance/Preview'

    if imagename == 'buzz':
      imageID = 8619102
    elif imagename == 'aliens':
      imageID = 627067
    else:
      raise NameError('Your entry for the image name is invalid')

    params = {
        'imageID': imageID,
        'text1': text,
    }

    response = requests.get(url, params)

    return response.content


def parse_txt(sourcename,body):
    parsed = BeautifulSoup(body, 'html5lib')

    if sourcename == 'fact': 
      txt = parsed.find('div',id='content')
    # Q1: It returned an error: SyntaxError: invalid syntax. But this seemed to be exactly what cnn layout is for their headline text... 
    elif sourcename == 'news':
      txt = parsed.find('span',class_='cd__headline-text')
    else:
      raise NameError('Your entry for the source is invalid')
    
    return txt.text.strip()

def get_txt(sourcename):

    if sourcename == 'fact':
      link = 'http://unkno.com'
    elif sourcename == 'news':
      link = 'http://cnn.com'
    else:
      raise NameError('Your entry for the source is invalid')

    response = requests.get(link)
    
    return parse_txt(sourcename,response.text)

def process(path):
    args = path.strip("/").split("/")

    sourcename = args[0]

    imagename = args[1]

    text = get_txt(sourcename)

    meme = meme_it(imagename,text)

    return meme

def application(environ, start_response):
    headers = [('Content-type', 'image/jpeg')]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError

        body = process(path)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1> Internal Server Error</h1>"
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        # Q2: It returned an error: AssertionError: write() argument must be a bytes instance. But if I change it to encode('utf8') then the meme won't show up, but just a blank...
        return [body]
        # [body.encode('utf8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
