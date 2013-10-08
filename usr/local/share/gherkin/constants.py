#!/usr/bin/env python

#CANCEL_CODE provides a 'code' for canceled dialogues.
#It needs to be a value unlikely to ever be entered. By having it here, it allows
#the UI components to use this constant as well as gherkin to use the same code to
#test for a canceled diaglogue.
CANCEL_CODE = "b748d7f9f3d5197c46052_120625a4550131d8 67049c13e11,02d.7?sa83a2e39b4ff"

#Change these to individual need.
#The title is probably a good place to have some sort of title as a grouping.
SITE_SELECTION_DIALOGUE_TITLE = "Manaiakalani Schools"
SITE_SELECTION_DIALOGUE_MESSAGE = "Select your school"
SITE_SHOW_TEXT = "School"

#Folder for definiton files
DEFINITIONS_FOLDER = "/usr/local/share/gherkin/definitions"

#Default Groups (when Groups not specified when adding users)
DEFAULT_GROUPS="dialout,cdrom,dip,plugdev"

#Don't change these. Bunch of constants that are used internally
LEFT = 0
RIGHT = 1
TOP = 0
BOTTOM = 1
