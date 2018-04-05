#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  remember.py
#
#  Copyright 2018 Drazen <drazenzen@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import os
import pickle
import collections
import geany


# folds and bookmarks Record entry
Record = collections.namedtuple('Record', ['folds', 'bookmarks'])

DEBUG = False


class RememberPlugin(geany.Plugin):

    # Plugin info
    __plugin_name__ = "Remember"
    __plugin_version__ = "0.02"
    __plugin_description__ = "Remember folds and bookmarks between sessions."
    __plugin_author__ = "Drazen <drazenzen@gmail.com>"

    # Scintilla.h
    # https://sourceforge.net/p/scintilla/code/ci/default/tree/include/Scintilla.h
    SCI_GETLINECOUNT = 2154
    SC_FOLDLEVELHEADERFLAG = 0x2000
    SCI_GETFOLDLEVEL = 2223
    SCI_GETFOLDEXPANDED = 2230
    SCI_COLOURISE = 4003
    SCI_TOGGLEFOLD = 2231

    # Data path
    DATA_PATH = conf_path = os.path.join(
        geany.app.configdir, "plugins", "remember.pcl")

    def __init__(self):
        """Init plugin."""
        geany.Plugin.__init__(self)
        geany.signals.connect('document-open', self.doc_open)
        geany.signals.connect('document-close', self.doc_close)

        # Internal data holder
        self.data = {}

        self.init()

        if DEBUG: self.debug("DATA_PATH={}".format(self.DATA_PATH))  # noqa

    def init(self):
        """Load data from file to internal data holder."""
        if os.path.exists(self.DATA_PATH):
            with open(self.DATA_PATH, 'r') as f:
                self.data = pickle.load(f)

        if DEBUG: self.debug("DATA loaded={}".format(self.data))  # noqa

    def cleanup(self):
        """Write data from data holder to file."""
        with open(self.DATA_PATH, 'w') as f:
            pickle.dump(self.data, f)

        if DEBUG: self.debug("DATA written={}".format(self.data))  # noqa

    def doc_open(self, *args):
        """Load and set data from internal data holder if possible."""
        # mng = args[0]
        doc = args[1]

        if DEBUG: self.debug("OPEN={}".format(doc.real_path))  # noqa

        if doc.real_path in self.data:
            scintilla = geany.scintilla.Scintilla
            sci = doc.editor.scintilla
            scintilla.send_message(sci, self.SCI_COLOURISE, 0, -1)
            # Folds
            if self.data[doc.real_path].folds:
                for i in self.data[doc.real_path].folds:
                    scintilla.send_message(
                        sci, self.SCI_TOGGLEFOLD, i, 1)
            # Bookmarks
            if self.data[doc.real_path].bookmarks:
                for i in self.data[doc.real_path].bookmarks:
                    scintilla.set_marker_at_line(sci, i, 1)

    def doc_close(self, *args):
        """Save data to internal data holder."""
        # mng = args[0]
        doc = args[1]

        folds = []
        bookmarks = []

        if DEBUG: self.debug("CLOSE={}\tREAL_PATH={}".format(doc, doc.real_path))  # noqa

        if doc.real_path is None:
            return

        scintilla = geany.scintilla.Scintilla
        sci = doc.editor.scintilla
        num_of_lines = scintilla.send_message(sci, self.SCI_GETLINECOUNT, 0, 0)

        if DEBUG:
            self.debug("LINES={}\tFold Level Header Flag={}".format(
                num_of_lines, self.SC_FOLDLEVELHEADERFLAG))

        for i in range(num_of_lines):
            # Folds
            flag = scintilla.send_message(sci, self.SCI_GETFOLDLEVEL, i, 0)
            status = flag & self.SC_FOLDLEVELHEADERFLAG
            if status:
                expanded = scintilla.send_message(
                    sci, self.SCI_GETFOLDEXPANDED, i, 0)
                if expanded == 0:

                    if DEBUG:
                        self.debug("LINE={}\tFold Level={}\tFoldStatus={}\tExpanded={})".format(  # noqa
                            i, flag, status, False if expanded else True))

                    folds.append(i)

            # Bookmarks
            marker = geany.scintilla.Scintilla.is_marker_set_at_line(sci, i, 1)
            if marker:
                bookmarks.append(i)

                if DEBUG: self.debug("LINE={}\tMarker={}".format(i, marker))  # noqa

        if DEBUG: self.debug("FOLDS={}".format(folds))  # noqa
        if DEBUG: self.debug("BOOKMARKS={}".format(bookmarks))  # noqa

        if folds or bookmarks:
            self.data[doc.real_path] = Record(folds, bookmarks)

        if DEBUG: self.debug("DATA={}".format(self.data))  # noqa

    def debug(self, msg):
        geany.msgwindow.status_add(msg)
