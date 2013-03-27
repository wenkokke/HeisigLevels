# Heisig Levels

"Heisig Levels" is a plugin for [Anki 1][ankisrs] that helps combine Japanese vocabulary study
with James Heisig's "Remembering The Kanji" method. The plugin adds the possibility to generate
*Heisig levels* for the words in your decks.

The *Heisig level* of a word is defined as the highest Heisig number of any kanji in the word,
i.e. how far you must be with the Heisig method to be able to read and write the word. These levels
can be used to unsuspend vocabulary cards, so that you'll only see words of which you know all the kanji. 

To make your deck work with this plugin, you'll need to add the `heisig_levels` tag to the model you use,
and make sure you have a field called `Expression` (from which the word is read) and a field called `Heisig
Level` (to which the Heisig level is written).

The levels are generated as the with Japanese Support plugin, by editing the `Expression` field or by selecting
the *Regenerate Heisig Levels* option from the menu. 

Currently, only the Heisig method is supported by this plugin, though you could replace the `heisig_levels.csv`
file with a file that enumerates the kanji in a different order. 

This plugin borrows heavily from the Japanese Support reading generation code, so my thanks goes out to Damien
Elmes for writing the plugin and obviously for writing Anki.

[ankisrs]: http://ankisrs.net
