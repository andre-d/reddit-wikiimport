from BeautifulSoup import BeautifulSoup, NavigableString

class MarkDowner(object):
    def __init__(self, md):
        self.content = unicode()
        self.e = md.contents[0] if len(md.contents) else md
        while self.e != None:
            if isinstance(self.e, NavigableString):
                if self.e.strip():
                    if self.e[0] == ' ':
                        self.content += ' '
                    self.content += self.e.strip()
                    if self.e[-1] == ' ':
                        self.content += ' '
            else:
                tagname = self.e.name.lower()
                if tagname in ('tr', 'td', 'table', 'thead', 'tfoot', 'tbody'):
                    attr_str = ' '.join(["%s='%s'" % (attr[0], attr[1]) for attr in self.e.attrs])
                    self.content += '\n<%s %s>%s</%s>' % (tagname, attr_str, self.default(), tagname)
                else:
                    try:
                        self.content += getattr(self, 'tag_%s' % tagname.upper(), self.default)()
                    except Exception as e: # Exceptions fallback to default handler
                        print 'Warning: tag %s threw with %s\n\n' % (self.e, e)
                        self.content += self.default()
            self.e = self.e.nextSibling
    
    def default(self):
        if len(self.e.contents):
            return MarkDowner(self.e).content
        return '' # Unhandled tag without content
    
    def tag_DIV(self):
        return self.tag_P()

    def tag_SPAN(self):
        return ' %s' % self.default()
    
    def tag_LI(self):
        if self.e.parent.name == 'ul':
            return '\n\n*   %s\n\n' % self.default()
        else:
            i = self.e.parent.contents.index(self.e)
            content = '\n'.join(['   %s' % s for s in self.default().strip().splitlines()])
            return '\n%d. %s\n\n' % (i + 1, content)
    
    def tag_HR(self):
        return '\n---------------------------------------\n'
    
    def tag_H1(self):
        return '%s\n================\n' % self.default()
    
    def tag_H2(self):
        return '%s\n-------------------\n' % self.default()
    
    def h(self, n):
        return '%s%s\n' % ('#' * n, self.default().strip())
    
    def tag_H3(self):
        return self.h(3)
        
    def tag_H4(self):
        return self.h(4)
    
    def tag_H5(self):
        return self.h(5)
    
    def tag_H6(self):
        return self.h(6)
    
    def tag_STRONG(self):
        return '**%s**' % self.default()
    
    def tag_BLOCKQUOTE(self): # Nesting?
        return '\n> %s\n\n' % self.default().strip()
    
    def tag_PRE(self):
        return '\n'.join(['     %s\n\n' % s for s in self.default().strip().splitlines()])
    
    def tag_CODE(self):
        return self.tag_PRE()
    
    def tag_IMG(self):
        src = self.e.get('src', '')
        title = self.e.get('title', '')
        alt = self.e.get('alt')
        alt = ' "%s"' % alt if alt else ''
        return '![%s](%s%s)' % (title, src, alt)
    
    def tag_DEL(self):
        return '~~%s~~' % self.default()
    
    def tag_P(self):
        return '%s\n\n' % self.default()
    
    def tag_BR(self):
        return '  \n'
    
    def tag_A(self):
        return '[%s](%s)' % (self.default(), self.e.get('href', ''))
  
if __name__ == '__main__':
    import snudown
    template =  '<textarea>%s</textarea><hr/>%s'
    original = unicode(open('input3.html', 'r').read(), 'utf-8')
    markdowned = MarkDowner(BeautifulSoup(original)).content.encode('ascii', 'xmlcharrefreplace')
    final = snudown.markdown(markdowned, renderer=snudown.RENDERER_WIKI)
    open('output.html', 'w').write(template % (markdowned, final))
