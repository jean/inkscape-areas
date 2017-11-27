#! /usr/bin/python
'''
This extension module measures path areas.

'''
# standard library
import locale
# local library
import inkex
import measure
import simplestyle


# On darwin, fall back to C in cases of 
# - incorrect locale IDs (see comments in bug #406662)
# - https://bugs.python.org/issue18378
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

# Initialize gettext for messages outside an inkex derived class
inkex.localize() 


class Areas(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

    def effect(self):
        pass

    def addTextOnPath(self, node, x, y, text, id, anchor, startOffset, dy = 0):
                new = inkex.etree.SubElement(node,inkex.addNS('textPath','svg'))
                s = {'text-align': 'center', 'vertical-align': 'bottom',
                    'text-anchor': anchor, 'font-size': str(self.options.fontsize),
                    'fill-opacity': '1.0', 'stroke': 'none',
                    'font-weight': 'normal', 'font-style': 'normal', 'fill': '#000000'}
                new.set('style', simplestyle.formatStyle(s))
                new.set(inkex.addNS('href','xlink'), '#'+id)
                new.set('startOffset', startOffset)
                new.set('dy', str(dy)) # dubious merit
                #new.append(tp)
                if text[-2:] == "^2":
                    appendSuperScript(new, "2")
                    new.text = str(text)[:-2]
                else:
                    new.text = str(text)
                #node.set('transform','rotate(180,'+str(-x)+','+str(-y)+')')
                node.set('x', str(x))
                node.set('y', str(y))

    def addTextWithTspan(self, node, x, y, text, id, anchor, angle, dy = 0):
                new = inkex.etree.SubElement(node,inkex.addNS('tspan','svg'), {inkex.addNS('role','sodipodi'): 'line'})
                s = {'text-align': 'center', 'vertical-align': 'bottom',
                    'text-anchor': anchor, 'font-size': str(self.options.fontsize),
                    'fill-opacity': '1.0', 'stroke': 'none',
                    'font-weight': 'normal', 'font-style': 'normal', 'fill': '#000000'}
                new.set('style', simplestyle.formatStyle(s))
                new.set('dy', str(dy))
                if text[-2:] == "^2":
                    appendSuperScript(new, "2")
                    new.text = str(text)[:-2]
                else:
                    new.text = str(text)
                node.set('x', str(x))
                node.set('y', str(y))
                node.set('transform', 'rotate(%s, %s, %s)' % (angle, x, y))

if __name__ == '__main__':
    e = Areas()
    e.affect()

