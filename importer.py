import json
from r2.models import wiki, subreddit
from r2.lib.db.thing import NotFound

AUTHOR_USER = 'reddit'

f = open('dump.obj')
pages = json.load(f)

for p in pages:
    sr = p['subreddit']
    try:
        sr = Subreddit._by_name(sr)
    except NotFound:
        print("WARNING! Subreddit %s not found" % sr)
        continue
    page = p['page']
    try:
        p_obj = wiki.WikiPage.create(sr, page)
    except wiki.WikiPageExists:
        p_obj = wiki.WikiPage.get(sr, page)
    p_obj.revise(p['original_body'], author=AUTHOR_USER, force=True,
                 reason='Original trac wiki markdown')
    p_obj.revise(p['body'], author=AUTHOR_USER, force=True,
                 reason='Imported markdown')
