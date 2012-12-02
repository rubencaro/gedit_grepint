# -*- coding: utf8 -*-
#  Grepint plugin for gedit
#
#  Copyright (C) 2012-2013 Rubén Caro
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gedit, Gtk, Gio, Gdk, GLib
import os, os.path
from urllib import pathname2url
import tempfile

max_result = 50
app_string = "Grepint"

# essential interface
class GrepintPluginInstance:
    def __init__( self, plugin, window ):
        self._window = window
        self._plugin = plugin
        self._dirs = [] # to be filled
        self._tmpfile = os.path.join(tempfile.gettempdir(), 'grepint.%s.%s' % (os.getuid(),os.getpid()))
        self._show_hidden = False
        self._liststore = None;
        self._init_ui()
        self._insert_menu()
        self._single_file_grep = True

    def deactivate( self ):
        self._remove_menu()
        self._action_group = None
        self._window = None
        self._plugin = None
        self._liststore = None;
        os.popen('rm %s &> /dev/null' % (self._tmpfile))

    def update_ui( self ):
        return

    # MENU STUFF
    def _insert_menu( self ):
        manager = self._window.get_ui_manager()
        # replace keybindings from main window
        self._action_group = Gtk.ActionGroup( "GeditWindowActions" )
        self._action_group.add_actions([
            ("GrepintFileAction", Gtk.STOCK_FIND, "Grep on file...",
             '<Ctrl>G', "Grep on file",
             lambda a: self.on_grepint_file_action()),
            ("GrepintProjectAction", Gtk.STOCK_FIND, "Grep on project...",
             '<Ctrl><Shift>G', "Grep on project",
             lambda a: self.on_grepint_project_action()),
        ])

        manager.insert_action_group(self._action_group)

        ui_str = """
          <ui>
            <menubar name="MenuBar">
              <menu name="SearchMenu" action="Search">
                <placeholder name="SearchOps_7">
                  <menuitem name="GrepintF" action="GrepintFileAction"/>
                  <menuitem name="GrepintP" action="GrepintProjectAction"/>
                </placeholder>
              </menu>
            </menubar>
          </ui>
          """

        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu( self ):
        manager = self._window.get_ui_manager()
        manager.remove_ui( self._ui_id )
        manager.remove_action_group( self._action_group )
        manager.ensure_update()

    # UI DIALOGUES
    def _init_ui( self ):
        filename = os.path.dirname( __file__ ) + "/grepint.ui"
        self._builder = Gtk.Builder()
        self._builder.add_from_file(filename)

        #setup window
        self._grepint_window = self._builder.get_object('GrepintWindow')
        self._grepint_window.connect("key-release-event", self.on_window_key)
        self._grepint_window.set_transient_for(self._window)

        #setup buttons
        self._builder.get_object( "ok_button" ).connect( "clicked", self.open_selected_item )
        self._builder.get_object( "cancel_button" ).connect( "clicked", lambda a: self._grepint_window.hide())

        #setup entry field
        self._glade_entry_name = self._builder.get_object( "entry_name" )
        self._glade_entry_name.connect("key-release-event", self.on_pattern_entry)

        #setup list field
        self._hit_list = self._builder.get_object( "hit_list" )
        self._hit_list.connect("select-cursor-row", self.on_select_from_list)
        self._hit_list.connect("button_press_event", self.on_list_mouse)
        self._liststore = Gtk.ListStore(str, str)

        self._hit_list.set_model(self._liststore)
        self._column1 = Gtk.TreeViewColumn("Name" , Gtk.CellRendererText(), text=0)
        self._column1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self._column2 = Gtk.TreeViewColumn("File", Gtk.CellRendererText(), text=1)
        self._column2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self._hit_list.append_column(self._column1)
        self._hit_list.append_column(self._column2)
        self._hit_list.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    #mouse event on list
    def on_list_mouse( self, widget, event ):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.open_selected_item( event )

    #key selects from list (passthrough 3 args)
    def on_select_from_list(self, widget, event):
        self.open_selected_item(event)

    #keyboard event on entry field
    def on_pattern_entry( self, widget, event ):
        oldtitle = self._grepint_window.get_title().replace(" * too many hits", "")

        if event.keyval == Gdk.KEY_Return:
            self.open_selected_item( event )
            return
        pattern = self._glade_entry_name.get_text()
        pattern = pattern.replace(" ",".*")
        cmd = ""
        if self._show_hidden:
            filefilter = ""
        if len(pattern) > 0:
            # TODO: do grep on project
            # To search by name
            cmd = "grep -inH -m %d -e '%s' '%s' 2> /dev/null" % (max_result, pattern, self._current_file)
            self._grepint_window.set_title("Searching ... ")
        else:
            self._grepint_window.set_title("Enter pattern ... ")

        self._liststore.clear()
        maxcount = 0
        hits = os.popen(cmd).readlines()
        for hit in hits:
            parts = hit.split(':')
            path,line = parts[0:2]
            text = ':'.join(parts[2:])[:160].replace("\n",'').strip()
            name = os.path.basename(path)
            # TODO: center text on hit using regex pattern
            item = []
            if self._single_file_grep:
                item = [line, text]
            else:
                item = [name + ":" + line + ": " + text, path + ":" + line]
            self._liststore.append(item)

            if maxcount > max_result:
                break
            maxcount = maxcount + 1
        if maxcount > max_result:
            oldtitle = oldtitle + " * too many hits"
        self._grepint_window.set_title(oldtitle)

        selected = []
        self._hit_list.get_selection().selected_foreach(self.foreach, selected)

        if len(selected) == 0:
            iter = self._liststore.get_iter_first()
            if iter != None:
                self._hit_list.get_selection().select_iter(iter)

    def get_git_base_dir( self, path ):
        """ Get git base dir if given path is inside a git repo. None otherwise. """
        gitdir = os.popen("cd '%s'; git rev-parse --show-toplevel 2> /dev/null" % path).readlines()
        if len(gitdir) > 0:
            return gitdir[0].replace("\n","")
        return None

    def map_to_git_base_dirs( self ):
        """ Replace paths with respective git repo base dirs if it exists """
        # use git repo base dir is more suitable if we are inside a git repo, for any dir we have guessed before
        dirs = []
        for d in self._dirs:
            gitdir = self.get_git_base_dir(d)
            if gitdir is None:
                dirs.append(d)
            else:
                dirs.append(gitdir)
        self._dirs = dirs
        # we could have introduced duplicates here
        self.ensure_unique_entries()

    def ensure_unique_entries( self ):
        """ Remove duplicates from dirs list """
        # this also looks for paths already included in other paths
        unique = []
        for d in self._dirs:
            d = d.replace("file://","").replace("//","/")
            should_append = True
            for i,u in enumerate(unique): # replace everyone with its wider parent
                if u in d: # already this one, or a parent
                    should_append = False
                elif d in u: # replace with the parent
                    unique[i] = d
                    should_append = False

            if should_append:
                unique.append(d)

        self._dirs = set(unique)

    def get_dirs_string( self ):
        """ Gets the quoted string built with dir list, ready to be passed on to 'find' """
        string = ''
        for d in self._dirs:
            string += "'%s' " % d
        return string

    def status( self,msg ):
        statusbar = self._window.get_statusbar()
        statusbar_ctxtid = statusbar.get_context_id('Grepint')
        statusbar.push(statusbar_ctxtid,msg)

    #on menuitem activation (incl. shortcut)
    def on_grepint_file_action( self ):
        self._single_file_grep = True
        self.show_popup()

    def on_grepint_project_action( self ):
        self._single_file_grep = False
        self.show_popup()

    def show_popup( self ):
        self._init_ui()

        doc = self._window.get_active_document()
        location = doc.get_location()
        if location and doc.is_local():
            self._current_file = location.get_uri().replace("file:///","")
        else:
            self.status("Cannot grep on remote or void files !")
            return

        if self._single_file_grep:
            self._column1.set_title('Line')
            self._column2.set_title('Text')
        else:
            self._column1.set_title('Match')
            self._column2.set_title('File path')

        self._grepint_window.show()
        # TODO: insert currently selected text
        self._glade_entry_name.select_region(0,-1)
        self._glade_entry_name.grab_focus()


    #on any keyboard event in main window
    def on_window_key( self, widget, event ):
        if event.keyval == Gdk.KEY_Escape:
            self._grepint_window.hide()

    def foreach(self, model, path, iter, selected):
        match = ''
        if self._single_file_grep:
            match = self._current_file + ':' + model.get_value(iter, 0)
        else:
            match = model.get_value(iter, 1)
        selected.append(match)

    def _open_document(self, filename, line, column):
        """ open a the file specified by filename at the given line and column
        number. Line and column numbering starts at 1. """

        if line == 0:
            raise ValueError, "line and column numbers start at 1"

        location = Gio.File.new_for_uri("file:///" + filename)
        print filename
        print location.get_uri()
        for doc in self._window.get_documents():
            locat = doc.get_location()
            if locat and doc.is_local():
                print locat.get_uri()

        tab = self._window.get_tab_from_location(location)
        if tab is None:
            tab = self._window.create_tab_from_location(location, None,
                                            line, column+1, False, True)
            view = tab.get_view()
        else:
            view = self._set_active_tab(tab, line, column)
        GLib.idle_add(view.grab_focus)
        return tab

    def _set_active_tab(self, tab, lineno, offset):
        self._window.set_active_tab(tab)
        view = tab.get_view()
        if lineno > 0:
            doc = tab.get_document()
            doc.goto_line(lineno - 1)
            cur_iter = doc.get_iter_at_line(lineno-1)
            linelen = cur_iter.get_chars_in_line() - 1
            if offset >= linelen:
                cur_iter.forward_to_line_end()
            elif offset > 0:
                cur_iter.set_line_offset(offset)
            elif offset == 0 and self.options.smart_home_end == 'before':
                cur_iter.set_line_offset(0)
                while cur_iter.get_char().isspace() and cur_iter.forward_char():
                    pass
            doc.place_cursor(cur_iter)
            view.scroll_to_cursor()
        return view

    #open file in selection and hide window
    def open_selected_item( self, event ):
        items = []
        self._hit_list.get_selection().selected_foreach(self.foreach, items)
        for item in items:
            path,line = item.split(':')
            self._open_document( path,int(line),1 )
        self._grepint_window.hide()

    # FILEBROWSER integration
    def get_filebrowser_root(self):
        base = u'org.gnome.gedit.plugins.filebrowser'

        settings = Gio.Settings.new(base)
        root = settings.get_string('virtual-root')

        if root is not None:
            filter_mode = settings.get_strv('filter-mode')

            if 'hide-hidden' in filter_mode:
                self._show_hidden = False
            else:
                self._show_hidden = True

            return root

# STANDARD PLUMMING
class GrepintPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "GrepintPlugin"
    DATA_TAG = "GrepintPluginInstance"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def _get_instance( self ):
        return self.window.get_data( self.DATA_TAG )

    def _set_instance( self, instance ):
        self.window.set_data( self.DATA_TAG, instance )

    def do_activate( self ):
        self._set_instance( GrepintPluginInstance( self, self.window ) )

    def do_deactivate( self ):
        self._get_instance().deactivate()
        self._set_instance( None )

    def do_update_ui( self ):
        self._get_instance().update_ui()
