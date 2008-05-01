#################################### IMPORTS ###################################

from __future__ import with_statement
from os.path import join, split, normpath

import sublime, sublimeplugin, re, os

############################### COMMON FUNCTIONS ###############################

def stripPreceding(selection, padding="", rstrip=True):
    "Strips preceding common space so only relative indentation remains"
    
    spacesList = []
    spaces = 0
    
    split = selection.split("\n")
    for l in split:
        for ch in l:
            if ch == '\t' or ch == ' ': spaces += 1
            else:
                spacesList.append(spaces)
                spaces = 0
                break
                                       
    try: anchorPoint = min(spacesList)
    except ValueError: anchorPoint = 0
    
    stripped = "\n".join(   [split[0][anchorPoint:]]      +\
                [padding + l[anchorPoint:] for l in split[1:]] )

    return  stripped.rstrip("\n") if rstrip else stripped

def linesGetFirstsDisplacement(view, region):
    "Expands a selection to encompass the lines it is situated in. "
    "It then contracts the start point to where the first non space "
    "character is found. Returns the start pt of the expanded "
    "selection, displacement( characters to contracted selection), " 
    "and then the end pt."
    
    region = view.line(region)
    start, end = region.begin(), region.end()
    displace = 0
    for x in xrange(start, end):
        if view.substr(x).isspace():
            displace += 1
        else: break
    return start, end, displace

def linesFirstNoPrecedingSpace(view, region, returnDisplace=False):
    "Expands a selection to encompass the lines it is situated in. "
    "It then contracts the start point to where the first non space "
    "character is found. Returns a region"
    
    start, end, displace = linesGetFirstsDisplacement(view, region)
    return sublime.Region(start+displace, end)
    
def getTab(view):
    "Gets a series of empty space characters of size 'tabSize', the "
    "current views setting for size of tab"
    
    return view.options().get('tabSize') * " "

def substrStripPrecedingCommonSpace(view, region, padSecondary=""):
    "takes a view, and a Region of it, strips preceding common space "
    "so only relative indentation remains"
    
    region = view.line(region)
    tab = getTab(view)
    sel = view.substr(region).replace("\t", tab)
    return stripPreceding(sel, padding = padSecondary or tab)   

def eraseSelectionLines(view):
    "Erases any line with any selection, even if empty"
    for sel in view.sel(): view.erase(view.fullLine(sel))

################################ PLUGIN COMMANDS ###############################

class RelativeIndentCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        if args[0] == 'paste':
            selection = sublime.getClipboard().replace("\r\n", "\n")
            selection = stripPreceding(selection)
                        
            view.runCommand('insertInlineSnippet', ['$PARAM1', selection])
        else:
            view.runCommand('expandSelectionTo line')
            view.runCommand(args[0])

class ParamPerSelectionSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        selections = []
        selSet = view.sel()
        sel1 = selSet[0]
        
        for sel in selSet:
            selections.append(substrStripPrecedingCommonSpace(view, sel))
        
        start, end, displace = linesGetFirstsDisplacement( view, sel1) 
        
        eraseSelectionLines(view)
        selSet.clear()
        
        view.insert(start, (displace * ' ') + '\n')
        putCursorAt = start+displace
        
        selSet.add(sublime.Region(putCursorAt, putCursorAt))
        
        view.runCommand('insertSnippet', args + selections)
        
class RelativeIndentSnippetCommand(sublimeplugin.TextCommand):
    def run(self, view, args):
        selSet = view.sel()
        for sel in selSet:
            if sel.empty(): continue

            selectionStripped = substrStripPrecedingCommonSpace(view, sel)
            modifiedRegion = linesFirstNoPrecedingSpace(view, sel)

            selSet.subtract(sel)
            selSet.add(modifiedRegion)
            view.replace(modifiedRegion, selectionStripped)

        view.runCommand('insertSnippet', args)
        
################################################################################