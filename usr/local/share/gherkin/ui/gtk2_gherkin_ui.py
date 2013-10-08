#!/usr/bin/env python

'''
This module should be replaced by a gtk3 implementation. This
wasn't done at the time as I (Nevyn) found very little usable
documentation on gtk3 and layout. Specifically, I was looking
for margins for the password input dialogue.

Due to time restraints, I chose not to fight this battle and
to instead make sure that it was easy enough to drop in whatever
interface was needed.

This needs a bit of a rewrite - remove vbox and hbox and replace
with box - in order to make it a lesser transition to gtk3.

I'm hoping people design a range of interfaces according to 
need.
'''

import gtk
import gobject
import re
import sys

sys.path.append( sys.path[0] + "/..")
from constants import *
gobject.threads_init()

SINGLE = 0
MULTI = 1

#Base GTK classes (to avoid some redundancy)
class Window( gtk.Window ):
    def __init__( self ):
        gtk.Window.__init__( self )
        self.set_deletable( False )
        self.set_position( gtk.WIN_POS_CENTER )
        self.margin = gtk.Alignment( 1, 0, 1, 1 )
        self.margin.set_padding( 10, 10, 10, 10 )
        self.add( self.margin )

class alignedEntry( gtk.Alignment ):
    def __init__( self, value="", hAlign=0, vAlign=0, topPadding=0, bottomPadding=0,
            leftPadding=0, rightPadding=0 ):
        gtk.Alignment.__init__( self )
        self.set( hAlign, vAlign, 1, 1 )
        self.set_padding( topPadding, bottomPadding, leftPadding, rightPadding )
        self.entry = gtk.Entry()
        self.entry.set_text( value )
        self.add( self.entry )

    def resize( self, x, y ):
        self.set_size_request( x, y )
        self.entry.set_size_request( x, y )

class Buttons( gtk.HBox ):
    def __init__( self, positive="OK", negative="Cancel" ):
        gtk.HBox.__init__( self, True )
        self.OKBut = gtk.Button( positive )
        self.CancelBut = gtk.Button( negative )
        self.pack_start( self.OKBut )
        self.pack_start( self.CancelBut )
        self.OKBut.set_flags( gtk.CAN_DEFAULT )

class alignedLabel( gtk.Alignment ):
    def __init__( self, label="", hAlign=0, vAlign=0, topPadding=0, bottomPadding=0, 
            leftPadding=0, rightPadding=0 ):
        gtk.Alignment.__init__( self )
        self.set( hAlign, vAlign, 0, 0 )
        self.set_padding( topPadding, bottomPadding, leftPadding, rightPadding )
        self.Label = gtk.Label( repr( label ).replace("\\\\n","\n" ).strip( '"\'' ))
        self.add( self.Label )

class selectBox( Window ):
    def __init__( self, title, message, options ):
        Window.__init__( self )
        self.set_title( title )
        self.set_default_size( 400, 300 )
        self._vbox = gtk.VBox( False )
        self.margin.add( self._vbox )
        self._label = gtk.Label( message )
        self._liststore = gtk.ListStore( str, str )
        self._treeview = gtk.TreeView( self._liststore )
        self._treeview.append_column( gtk.TreeViewColumn( "", gtk.CellRendererText(), text=0 ) )
        self._sw = gtk.ScrolledWindow()
        self._sw.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
        self._sw.add( self._treeview )
        self.buttons = Buttons()
        self._vbox.pack_start( self._label, False, False )
        self._vbox.pack_start( self._sw, True, True )
        self._vbox.pack_end( self.buttons, False, False, 0 )
        self.populateList( options )
        self.show_all()

    def populateList( self, options ):
        for item in options:
            self._liststore[ self._liststore.append() ] = ( item[0], item[1] )

#Input interfaces

class cancel_dialogue( Window):
    __gsignals__ = {
        "cancel": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) ),
        "continue": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) ) 
    }

    def __init__( self ):
        Window.__init__( self )
        self.set_title("Are you sure?")
        self.vbox = gtk.VBox()
        self.label = gtk.Label( "Are you sure you want to quit?\n\n" +
            "Quitting takes you right back to the beginning.\n\n" )
        self.buttons = Buttons( "Yes", "No" )
        self.margin.add( self.vbox )
        self.vbox.pack_start( self.label )
        self.vbox.pack_start( self.buttons )
        self.buttons.OKBut.connect( "clicked", self.Yes )
        self.buttons.CancelBut.connect( "clicked", self.No )
        self.connect( "key-press-event", self.Keypressed )
        self.show_all()

    def Keypressed( self, widget, event, *args ):
        if event.keyval == gtk.keysyms.Escape:
            self.No()

    def Yes( self, *args ):
        self.emit( "cancel", True )

    def No( self, *args ):
        self.emit( "continue", True )

class selection_box( selectBox ):
    __gsignals__ = {
        "value_returned": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ) ),
        "canceled": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) )
    }
    def __init__( self, mode, title, message, options, canNull ):
        selectBox.__init__( self, title, message, options )
        if ( mode == MULTI ):
            self._treeview.get_selection().set_mode( gtk.SELECTION_MULTIPLE )
            self.buttons.OKBut.connect( 'clicked', self.returnValueMulti )
        else:
            self._treeview.get_selection().set_mode( gtk.SELECTION_SINGLE )
            self.buttons.OKBut.connect( 'clicked', self.returnValueSingle )
        if not canNull:
            self.buttons.OKBut.set_sensitive( False )
            self._treeview.connect( 'cursor_changed', self.activateOK )
        self.buttons.CancelBut.connect( 'clicked', self.cancel )
        self.connect( 'key-press-event', self.keyPressed )

    def activateOK( self, *var ):
        self.buttons.OKBut.set_sensitive( True )

    def keyPressed( self, widget, event):
        if ( event.keyval == gtk.keysyms.Escape ):
            self.cancel( self )

    def cancel( self, *var ):
        self.emit( "canceled", True )

    def returnValueMulti(self, *args):
        selected = [] 
        self._treeview.get_selection().selected_foreach( self.getSelection, selected )
        self.emit( "value_returned", selected )

    def returnValueSingle( self, *args ):
        index, _ = self._treeview.get_cursor()
        self.emit( "value_returned", self._liststore[ index ][ 1 ] )

    def getSelection( self, liststore, iteration, treeIter, selected ):
        selected.append( liststore.get_value( treeIter, 1 ) )

class siteSelection( selectBox ):
    __gsignals__ = {
        "value_returned": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ) )
    }

    def __init__( self, sites ):
        selectBox.__init__( self, SITE_SELECTION_DIALOGUE_TITLE, SITE_SELECTION_DIALOGUE_MESSAGE, sites )
        self._treeview.get_selection().set_mode( gtk.SELECTION_SINGLE )
        self.buttons.hide()
        self.butOK = gtk.Button( "OK" )
        self.butOK.set_sensitive( False )
        self._vbox.pack_start( self.butOK, False, 0 )
        self.butOK.show()
        self.butOK.connect( 'clicked', self.returnValue )
        self._treeview.connect( "cursor_changed", self.activateOK )
        self._treeview.connect( "row_activated", self.returnValue )

    def activateOK( self, *args ):
        self.butOK.set_sensitive( True )

    def returnValue( self, *args ):
        index, _ = self._treeview.get_cursor()
        self.emit( "value_returned", self._liststore[ index ][ 1 ] )

class textInput( Window ):
    __gsignals__ = {
        "value_returned": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_STRING, ) ),
        "canceled": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) )
    }

    def __init__( self, title, message, pattern='.*' ):
        Window.__init__( self )

        self.pattern = re.compile( pattern )
        self.set_title( title )
        self.set_size_request( 300, 200 )
        self._vbox = gtk.VBox( True, 10 )
        self._message = gtk.Label( message )
        self._message.set_line_wrap( True )
        self._message.set_width_chars( 42 )
        self._inputArea = gtk.Entry()
        self.buttons = Buttons()
        self.margin.add( self._vbox )
        self.buttons.OKBut.set_sensitive( False )
        self._vbox.pack_start( self._message )
        self._vbox.pack_start( self._inputArea )
        self._vbox.pack_end( self.buttons )
        self.connect( "key-press-event", self.keyPressed )
        self.buttons.CancelBut.connect( "clicked", self.isCancel )
        self.buttons.OKBut.connect( "clicked", self.returnValue )
        self._inputArea.connect( "changed", self.onChange )
        self.set_default( self.buttons.OKBut )
        self._inputArea.set_activates_default( True )
        self.show_all()

    def keyPressed( self, widget, event):
        if ( event.keyval == gtk.keysyms.Escape ):
            self.isCancel()

    def isCancel( self, *args ):
        self.emit( "canceled", True )

    def returnValue( self, *args ):
        self.emit( "value_returned", self._inputArea.get_text() )

    def onChange( self, inputArea ):
        results = self.pattern.search( self._inputArea.get_text() )
        if not results or self._inputArea.get_text() == "":
                self.buttons.OKBut.set_sensitive( False )
        else:
            self.buttons.OKBut.set_sensitive( True )

class passwordInput( Window ):
    __gsignals__ = {
        "value_returned": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_STRING, ) ),
        "canceled": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) )
    }

    def __init__( self, title, message, length ):
        Window.__init__( self )
        self.length = length
        self.pattern = re.compile( '^[a-zA-Z0-9 `~\-\[\]?._]+$' )
        self.set_title( title )
        self.set_size_request( 400, 0 )
        self._vbox = gtk.VBox()
        self.lblMessage = alignedLabel( message, hAlign=LEFT )
        self.lblMessage.Label.set_line_wrap( True )
        lbl_x_size, lbl_y_size = self.lblMessage.Label.size_request()
        lbl_line_height = lbl_y_size
        lbl_y_size = (( lbl_x_size / ( self.size_request()[0] )) + 1 ) * lbl_line_height
        lbl_x_size = self.size_request()[0]
        self.set_size_request( 400, lbl_y_size + 200 )
        self.lblMessage.set_size_request( lbl_x_size, lbl_y_size )
        self.lblPassword1 = alignedLabel( "Enter Password:", leftPadding=10, hAlign=LEFT )
        self.entPassword1 = alignedEntry( leftPadding=20, bottomPadding=10, hAlign=LEFT )
        self.entPassword1.entry.set_visibility( False )
        self.lblPassword2 = alignedLabel( "Re-Enter Password:", leftPadding=10, hAlign=LEFT )
        self.entPassword2 = alignedEntry( leftPadding=20, bottomPadding=10, hAlign=LEFT )
        self.entPassword2.entry.set_sensitive( False )
        self.entPassword2.entry.set_visibility( False )
        self._hbox = gtk.HBox()
        self.lblStatus = gtk.Label()
        self.lblStatus.set_line_wrap( True )
        self.buttons = Buttons()
        self.buttons.OKBut.set_sensitive( False )
        self.margin.add( self._vbox )
        self._vbox.pack_start( self.lblMessage, True, True )
        self._vbox.pack_start( self.lblPassword1, True, True )
        self._vbox.pack_start( self.entPassword1, True, True )
        self._vbox.pack_start( self.lblPassword2, True, True )
        self._vbox.pack_start( self.entPassword2, True, True )
        self._vbox.pack_start( self._hbox )
        self._hbox.pack_start( self.lblStatus )
        self._hbox.pack_end( self.buttons )

        # default control
        self.set_default( self.buttons.OKBut )
        self.entPassword1.entry.set_activates_default( True )
        self.entPassword2.entry.set_activates_default( True )

        # signals
        self.connect( "key-press-event", self.keyPressed )
        self.entPassword1.entry.connect( "changed", self.password1Change )
        self.entPassword2.entry.connect( "changed", self.password2Change )
        self.buttons.OKBut.connect( "clicked", self.OKClicked )
        self.buttons.CancelBut.connect( "clicked", self.cancel )
        self.buttons.OKBut.connect( "clicked", self.OKClicked )
        self.buttons.CancelBut.connect( "clicked", self.cancel )

        self.show_all()

    def keyPressed( self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.cancel()

    def cancel(self, *args):
        self.emit( "canceled", True )

    def OKClicked( self, *args ):
        self.emit( "value_returned", self.entPassword1.entry.get_text() )

    def password1Change( self, entPassword1 ):
        self.buttons.OKBut.set_sensitive( False )
        if len( entPassword1.get_text() ) < self.length:
            self.entPassword2.entry.set_sensitive( False )
            self.lblStatus.set_markup( "<span foreground='red'>Password too short.</span>" )

        elif not self.pattern.search( entPassword1.get_text() ):
            self.entPassword2.entry.set_sensitive( False )
            self.lblStatus.set_markup( "<span foreground='red'>Illegal characters found in password.</span>")
        else:
            self.entPassword2.entry.set_sensitive( True )
            self.lblStatus.set_text("")
            self.password2Change( self )

    def password2Change( self, entPassword2 ):
        self.buttons.OKBut.set_sensitive( False )
        if self.entPassword1.entry.get_text() != self.entPassword2.entry.get_text():
            self.lblStatus.set_markup( "<span foreground='red'>Passwords do not match.</span>" )
        else:
            self.lblStatus.set_markup( "" )
            self.buttons.OKBut.set_sensitive( True )
            self.lblStatus.set_text( " Passwords Match!" )


#Accessors. Abstraction to allow for integration with procedural programming.
def getText( title, message, pattern='.*' ):
    inputBox = textInput( title, message, pattern )
    inputBox.connect( "value_returned", returnValue )
    inputBox.connect( "canceled", cancel )
    gtk.main()
    return Return_Value 

def getPassword( title="Enter Password", message="Please enter your password.", length=6 ):
    passwordBox = passwordInput( title, message, length )
    passwordBox.connect( "value_returned", returnValue )
    passwordBox.connect( "canceled", cancel )
    gtk.main()
    return Return_Value

def getMultipleSelection( title, message, options, canNull = False ):
    selection = selection_box( 1, title, message, options, canNull )
    selection.connect( "value_returned", returnValue )
    selection.connect( "canceled", cancel )
    gtk.main()
    return Return_Value

def getSingleSelection( title, message, options, canNull = False ):
    selection = selection_box( SINGLE, title, message, options, canNull )
    selection.connect( "value_returned", returnValue )
    selection.connect( "canceled", cancel )
    gtk.main()
    return Return_Value


def getSite( sites ):
    site_selection = siteSelection( sites )
    site_selection.connect( "value_returned", returnValue )
    gtk.main()
    return Return_Value

class leftLabel( gtk.Label ):
    def __init__( self, value ):
        gtk.Label.__init__( self )
        self.set_label( value )
        self.set_alignment( 0, 0 )

class Confirmation( Window ):
    __gsignals__ = {
        "yes": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ( gobject.TYPE_BOOLEAN, ) ),
        "no": ( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN, ) )
    }
    def __init__( self, site, variables, displayPairs ):
        Window.__init__( self )
        self.set_title( "Do you want to continue?" )
        vbox = gtk.VBox()
        buttons = Buttons( "Yes", "No" )
        vbox.pack_end( buttons, expand=False, fill=True )
        self.margin.add( vbox )
        self.set_default_size( 400, 300 )
        
        label = leftLabel( "Please make sure these details are correct.\nAre you absolutely sure that you want to continue?\n\n"
                + SITE_SHOW_TEXT + "\n\t" + site )
        label.set_line_wrap( True )
        vbox.pack_start( label, expand=False, fill=False )
        for item in displayPairs:
            for ( counter, value ) in enumerate( item ):
                if ( counter == 0 ):
                    label = leftLabel( value )
                    vbox.pack_start( label, expand=False, fill=False )
                else:
                    if isinstance( variables[ value ], list):
                        for variable in variables[ value ]:
                            label = leftLabel( "\t" + variable )
                            vbox.pack_start( label, expand=False, fill=False )
                    else:
                        label = leftLabel( "\t" + variables[ value ] )
                        vbox.pack_start( label, expand=False, fill=False )
        buttons.OKBut.connect( "clicked", self.Yes )
        buttons.CancelBut.connect( "clicked", self.No )
        self.show_all()

    def Yes( self, *args ):
        self.emit( "yes", True )

    def No( self, *args ):
        self.emit( "no", False )

def getConfirmation( site, variables, displayPairs ):
    confirmation = Confirmation( site, variables, displayPairs )
    confirmation.connect( "yes", returnValue )
    confirmation.connect( "no", returnValue)
    gtk.main()
    return Return_Value

#working dialogue stuff
class workDialogue(Window):
    def __init__( self ):
        Window.__init__(self)
        vbox = gtk.VBox()
        self.spinner = gtk.Spinner()
        self.status = gtk.Label("Working...")
        vbox.pack_start(self.spinner, True, True, 0)
        vbox.pack_start(self.status, False, False, 0)
        self.margin.add(vbox)

working_dialogue = workDialogue()

def show_working_dialogue():
    working_dialogue.show_all()
    working_dialogue.spinner.start()
    gtk.main()

def hide_working_dialogue():
    gtk.main_quit()

def update_working_dialogue( status ):
    working_dialogue.status.set_text(status)

# Use these functions for EVERYTHING (Because I really am that lazy...)
def returnValue( widget, value ):
    global Return_Value
    Return_Value = value
    widget.destroy()
    gtk.main_quit()

def cancel( widget, value ):
    confirmCancel = cancel_dialogue()
    confirmCancel.connect( "cancel", reallyCancel, widget )
    confirmCancel.connect( "continue", resume )

def resume( widget, *args ):
    widget.destroy()

def reallyCancel( widget, *args ):
    args[1].destroy()
    returnValue( widget, CANCEL_CODE )
