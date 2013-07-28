# -*- coding: utf-8 -*-
# Copyright: Pepijn Kokke <pepijn.kokke@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# 
# This plugin adds the possibility to generate "Heisig levels"
# for the words in your decks.
#
# The 'Heisig level' of a word is defined as the highest Heisig
# number of any kanji in the word, i.e. how far you must be with
# the Heisig method to be able to read and write the word.
# These levels can be used to unsuspend vocabulary cards, so that
# you'll only see words of which you know all the kanji.
#
# To make your deck work with this plugin, you'll need to add the
# "heisig_levels" tag to the model you use, and make sure you have
# a field called 'Expression' [from which the word is read] and a
# field called 'Heisig Level' [to which the Heisig level is written].
#
# The levels are generated as the with Japanese Support plugin, by
# editing the 'Expression' field or by selecting the 'Regenerate Heisig
# Levels' option from the menu.
#
# Currently, only the Heisig method is supported by this plugin,
# though you could replace the "heisig_levels.csv" file with a file
# that enumerates the kanji in a different order.
#
# This plugin borrows heavily from the Japanese Support reading generation
# code, so my thanks goes out to Damien Elmes for writing the plugin and
# obviously for writing Anki.

import os, csv
from ankiqt               import mw
from ankiqt.ui.facteditor import FactEditor
from anki.facts           import Fact
from anki.hooks           import addHook, wrap
from anki.utils           import findTag, stripHTML
from PyQt4.QtCore         import *
from PyQt4.QtGui          import *

###############################################################################
# Calculation of Heisig Levels from ordered CSV file
###############################################################################

def heisigNumberCsv():
    csvFile = os.path.join(mw.config.configPath, 'plugins', 'heisig_levels.csv')
    return open(csvFile, 'rb')
    
# calculates the heisig_number for a specific character
heisigNumberDict = None
def heisigNumber(kanji):
    global heisigNumberDict
    if heisigNumberDict == None:
        reader = unicodeCsvReader(heisigNumberCsv())
        # patch for bug that skips the first kanji in the csv-file
        heisigNumberDict = {u'一': 1}
        number = 0
        for input in reader:
            number += 1
            heisigNumberDict[input[0]] = number
    if kanji in heisigNumberDict:
        return heisigNumberDict[kanji]
    else:
        return 0

def unicodeCsvReader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

# calculates the heisig_level as the maximum heisig_number found in a word
def heisigLevel(word):
    level = 0
    for letter in word:
        level = max(level, heisigNumber(letter))
    return level
    
def uHeisigLevel(word):
    return unicode(heisigLevel(word))

# tags and fields used in anki
modelTag  = 'heisig_levels'
srcFields = ['Expression']
dstFields = ['Heisig Level']

###############################################################################
# Generate Heisig Levels in Editor on Unfocus of 'Expression' Field
###############################################################################

# hook to generate heisig level on expression change
def onFocusLost(fact, field):
    if field.name not in srcFields:
        return
    if not findTag(modelTag, fact.model.tags):
        return
    if field.value == '':
        return
    dstField = dstFields[srcFields.index(field.name)]
    try:
        if fact[dstField]:
            return
    except:
        return
    fact[dstField] = uHeisigLevel(field.value)

addHook('fact.focusLost', onFocusLost)

###############################################################################
# Bulk Generation of Heisig Levels through Menu
###############################################################################
    
def regenerateHeisigLevel(factIds):
    mw.deck.startProgress(max=len(factIds))
    for c, id in enumerate(factIds):
        mw.deck.updateProgress(label="Generating Heisig levels...", value=c)
        fact = mw.deck.s.query(Fact).get(id)
        try:
            for i in range(len(srcFields)):
                fact[dstFields[i]] = uHeisigLevel(fact[srcFields[i]])
        except:
            pass
    try:
        mw.deck.refreshSession()
    except:
        # old style
        mw.deck.refresh()
    mw.deck.updateCardQACacheFromIds(factIds, type="facts")
    mw.deck.finishProgress()

def setupMenu(editor):
    a = QAction("Regenerate Heisig Levels", editor)
    editor.connect(a, SIGNAL("triggered()"), lambda e=editor: onRegenerate(e))
    editor.dialog.menuActions.addSeparator()
    editor.dialog.menuActions.addAction(a)

def onRegenerate(editor):
    n = "Regenerate Readings"
    editor.parent.setProgressParent(editor)
    editor.deck.setUndoStart(n)
    regenerateHeisigLevel(editor.selectedFacts())
    editor.deck.setUndoEnd(n)
    editor.parent.setProgressParent(None)
    editor.updateSearch()

addHook("editor.setupMenus", setupMenu)
