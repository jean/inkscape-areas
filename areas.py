#! /usr/bin/python
'''
This extension module measures path areas.

'''
# standard library
import locale
import re
# local library
import inkex
import simpletransform
import cubicsuperpath
import measure # TODO drop
import simplestyle

# Turns debugging output on - Use debug = False to turn debugging output 'off'
# debug = inkex.debug
debug = lambda x: None

nspath = inkex.addNS('path','svg')

# On darwin, fall back to C in cases of 
# - incorrect locale IDs (see comments in bug #406662)
# - https://bugs.python.org/issue18378
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

# Initialize gettext for messages outside an inkex derived class
inkex.localize() 

# third party
try:
    import numpy
    import svgwrite
    import svgpathtools
except:
    inkex.errormsg(_("Failed to import the svgpathtools, svgwrite and numpy modules. These modules are required by this extension. Please install them and try again.  On a Debian-like system this can be done with the commands: `sudo apt-get install python-numpy; sudo pip install svgpathtools svgwrite`."))
    exit()

class Areas(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--tab",
                        action="store", type="string", 
                        dest="tab", default="sampling",
                        help="The selected UI-tab when OK was pressed") 

    def effect(self):

        # if self.options.mformat == '"presets"':
        #     self.setPreset()

        # njj: hack some options
        # get number of digits
        # prec = int(self.options.precision)
        prec = 2
        self.options.fontsize = 20
        self.options.unit = 'mm'
        self.options.scale = 1
        self.options.angle = 0
        self.options.offset = -6

        scale = self.unittouu('1px')    # convert to document units
        # self.options.offset *= scale
        factor = 1.0
        doc = self.document.getroot()
        if doc.get('viewBox'):
            (viewx, viewy, vieww, viewh) = re.sub(' +|, +|,',' ',doc.get('viewBox')).strip().split(' ', 4)
            factor = self.unittouu(doc.get('width'))/float(vieww)
            if self.unittouu(doc.get('height'))/float(viewh) < factor:
                factor = self.unittouu(doc.get('height'))/float(viewh)
            factor /= self.unittouu('1px')
            self.options.fontsize /= factor
        factor *= scale/self.unittouu('1'+self.options.unit)

        # Gather paths
        paths = []
        for id, node in self.selected.iteritems():
            if node.tag != nspath:
                nodes = node.findall('.//{0}'.format(nspath))
                debug(nodes)
                paths.extend(nodes)
            debug(paths)
        # Act on paths
        for node in paths:
            mat = simpletransform.composeParents(node, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
            p = cubicsuperpath.parsePath(node.get('d'))
            simpletransform.applyTransformToPath(mat, p)
            stotal = abs(measure.csparea(p)*factor*self.options.scale)
            self.group = inkex.etree.SubElement(node.getparent(),inkex.addNS('text','svg'))

            # Format the area as string
            resultstr = locale.format("%(len)25."+str(prec)+"f",{'len':round(stotal*factor*self.options.scale,prec)}).strip()
            # Fixed text, in the center of each path
            bbox = simpletransform.computeBBox([node])
            tx = bbox[0] + (bbox[1] - bbox[0])/2.0
            ty = bbox[2] + (bbox[3] - bbox[2])/2.0
            anchor = 'middle'
            self.addTextWithTspan(self.group, tx, ty, resultstr+' '+self.options.unit+'^2', id, anchor, -int(self.options.angle), -self.options.offset + self.options.fontsize/2)

    def addTextWithTspan(self, node, x, y, text, id, anchor, angle, dy = 0):
        new = inkex.etree.SubElement(node,inkex.addNS('tspan','svg'), {inkex.addNS('role','sodipodi'): 'line'})
        s = {'text-align': 'center', 'vertical-align': 'bottom',
            'text-anchor': anchor, 'font-size': str(self.options.fontsize),
            'fill-opacity': '1.0', 'stroke': 'none',
            'font-weight': 'normal', 'font-style': 'normal', 'fill': '#000000'}
        new.set('style', simplestyle.formatStyle(s))
        new.set('dy', str(dy))
        if text[-2:] == "^2":
            measure.appendSuperScript(new, "2")
            new.text = str(text)[:-2]
        else:
            new.text = str(text)
        node.set('x', str(x))
        node.set('y', str(y))
        node.set('transform', 'rotate(%s, %s, %s)' % (angle, x, y))

if __name__ == '__main__':
    e = Areas()
    e.affect()

