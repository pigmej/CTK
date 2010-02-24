# CTK: Cherokee Toolkit
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2009 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Table import Table
from Widget import Widget
from RawHTML import RawHTML
from Submitter import Submitter
from Container import Container
from HiddenField import HiddenField

HTML_TABLE = """
<div class="propstable">%s</div>
"""

HTML_ENTRY = """
<div class="entry">
   <div class="title">%(title)s</div>
   <div class="widget">%(widget_html)s</div>
   <div class="comment">%(comment)s</div>
   <div class="after"></div>
</div>
"""

HEADERS = ['<link rel="stylesheet" type="text/css" href="/CTK/css/CTK.css" />']


class PropsTable (Widget):
    """Property Table: Formatting"""

    def __init__ (self, **kwargs):
        Widget.__init__ (self, **kwargs)
        self.entries = []

    def Add (self, title, widget, comment):
        self.entries.append ((title, widget, comment))

    def Render (self):
        render = Widget.Render(self)

        for e in self.entries:
            title, widget, comment = e
            if widget:
                r = widget.Render()
            else:
                r = Container().Render()

            props = {'title':       title,
                     'widget_html': r.html,
                     'comment':     comment}

            r.html = HTML_ENTRY %(props)
            render += r

        render.html = HTML_TABLE %(render.html)
        return render


class PropsTableAuto (PropsTable):
    """Property Table: Adds Submitters and constants"""

    def __init__ (self, url, **kwargs):
        PropsTable.__init__ (self, **kwargs)
        self._url      = url
        self.constants = {}

    def AddConstant (self, key, val):
        self.constants[key] = val

    def Add (self, title, widget, comment):
        submit = Submitter (self._url)

        if self.constants:
            box = Container()
            box += widget
            for key in self.constants:
                box += HiddenField ({'name': key, 'value': self.constants[key]})

            submit += box
        else:
            submit += widget

        return PropsTable.Add (self, title, submit, comment)


class PropsAuto (Widget):
    def __init__ (self, url, **kwargs):
        Widget.__init__ (self, **kwargs)
        self._url      = url
        self.constants = {}
        self.entries   = []

    def AddConstant (self, key, val):
        self.constants[key] = val

    def Add (self, title, widget, comment, use_submitter=True):
        # No constants, just the widget
        if not self.constants:
            self.entries.append ((title, widget, comment, use_submitter))
            return

        # Wrap it
        box = Container()
        box += widget
        for key in self.constants:
            box += HiddenField ({'name': key, 'value': self.constants[key]})
        self.entries.append ((title, box, comment, use_submitter))

    def Render (self):
        render = Widget.Render(self)

        for e in self.entries:
            title, widget, comment, use_submitter = e

            if use_submitter:
                submit = Submitter (self._url)
                submit += widget
            else:
                submit = widget

            widget_r    = submit.Render()
            widget_html = widget_r.html

            html = HTML_ENTRY %(locals())

            render.html    += html
            render.js      += widget_r.js
            render.headers += widget_r.headers
            render.helps   += widget_r.helps

        render.html     = HTML_TABLE %(render.html)
        render.headers += HEADERS
        return render
