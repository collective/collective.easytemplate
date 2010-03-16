# -*- coding: utf-8 -*-
"""

    Fix non-breaking spacebar characters which have ended up to reST .txt files.
    This is Unicode character code A0.
    
    Press CTRL+space / AltGr space on Linux to accidentally create it. 


    E.g. as a sympton the following exception is raised if you try 
    to upload Python egg::
    
          File "/Library/Python/2.6/site-packages/docutils-0.6-py2.6.egg/docutils/parsers/rst/states.py", line 2621, in blank
            self.parent += self.literal_block()
          File "/Library/Python/2.6/site-packages/docutils-0.6-py2.6.egg/docutils/parsers/rst/states.py", line 2712, in literal_block
            literal_block = nodes.literal_block(data, data)
          File "/Library/Python/2.6/site-packages/docutils-0.6-py2.6.egg/docutils/nodes.py", line 810, in __init__
            TextElement.__init__(self, rawsource, text, *children, **attributes)
          File "/Library/Python/2.6/site-packages/docutils-0.6-py2.6.egg/docutils/nodes.py", line 798, in __init__
            textnode = Text(text)
          File "/Library/Python/2.6/site-packages/docutils-0.6-py2.6.egg/docutils/nodes.py", line 331, in __new__
            return reprunicode.__new__(cls, data)
        UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 715: ordinal not in range(128)


"""

import os


def fix(name):
    """ Fix a single .TXT file
    """
    input = open(name, "rt")
    text = input.read()
    input.close()
    text = text.decode("utf-8")
    
    # Show if we get bad hits
    for c in text:
        if c == u"\xa0":
            print "Ufff"
            
    text = text.replace(u"\xa0", u" ")
    
    text = text.encode("utf-8")
    
    output = open(name, "wt")
    output.write(text)
    output.close()
        
        
# Process all .txt files in the 
# current folder
for f in os.listdir(os.getcwd()):
    if f.endswith(".txt"):
        fix(f)

