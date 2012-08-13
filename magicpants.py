from BeautifulSoup import BeautifulSoup

import sqlite3

from trac.wiki.formatter import HtmlFormatter
from trac.test import Mock, MockPerm
from trac.env import Environment
from trac.mimeview.api import Context
from markdowner import MarkDowner

from trac.web.href import Href

import snudown

import json

from trac.wiki.formatter import format_to_html

# CREATE TABLE wiki (
#    name text,
#    version integer,
#    time integer,
#    author text,
#    ipnr text,
#    text text,
#    comment text,
#    readonly integer,
#    UNIQUE (name,version)
# );

conn = sqlite3.connect('wiki.db')
conn.row_factory = sqlite3.Row

env = Environment('/home/user/testproj')
req = Mock(href=Href('/'), abs_href=Href('/'), perm=MockPerm())
context = Context.from_request(req)


override = {
'leagueoflegendsmeta/help/faq': ('faq', 'leagueoflegendsmeta')
}

class Page:
    def __init__(self, row):
        self.user = row['author']
        self.subreddit = None
        self.original_body = row['text']
        self.body = self._format(row['text'])
        name = row['name'] 
        self.page = name
        self.name = name
        if name.startswith('help/faqs/'):
            self.page = 'faq'
            subreddit = name.split('help/faqs/')[1]
            self.subreddit = subreddit.split('/r/')[1] if subreddit.startswith('/r/') else subreddit
        else:
            if name not in override:
                self.subreddit = 'reddit.com'
            else:
                p = override[name]
                self.subreddit = p[1]
                self.page = p[0]
    
    def _format(self, text):
        markup = format_to_html(env, context, text)
        return MarkDowner(BeautifulSoup(unicode(markup))).content

def get_pages():
    c = conn.cursor()
    c.execute("""select w.name as name, w.author as author, w.text as text
from (
   select name, max(version) as maxversion
   from wiki group by name
) as x inner join wiki as w on w.name = x.name and w.version = x.maxversion;""")
    result = ''
    while result is not None:
        result = c.fetchone()
        if result is not None:
            yield Page(result)

def main():
    f = open('dump.json', 'w')
    json.dump([p.__dict__ for p in get_pages()], f)
      #  if p.subreddit == 'reddit.com':
        #    print p.page
        #f = open('rendered/%s.html' % p.name.replace('/', '.'), 'w')
        #f.write(snudown.markdown(p.body.encode('ascii', 'xmlcharrefreplace'), renderer=snudown.RENDERER_WIKI, enable_toc=True))
        #f.close()
        

if __name__ == '__main__':
    main()
