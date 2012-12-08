grepint
=============

Grep interface plugin for Gedit.

Performs quick grep on current file, or in associated folders. 
Overrides \<Ctrl\>G and \<Ctrl\>\<Shift\>G 
accelerators with _Grep file_ and _Grep project_. 

If there is some selected text when invoked, it performs 
a quick search using it as pattern. 
Once invoked you can directly edit the pattern, 
or navigate through the results list with up/down keys. 
No mouse needed.

_File Search_ performs grep on current file. 
Changes reflect live on the hits list below.

_Project Search_ performs grep on related folders. 
The search (this one is heavier) is only 
performed when you hit enter. Related folders are variable, 
and configurable. In order:
 - Currently open files
 - Current file browser plugin root
 - GIT base dirs for any of previous paths
 - RVM gemset path for any of previous paths

You can see the actual grep command performed, 
in case you are brave enough to go for the real thing.

Roughly based on [[https://github.com/rubencaro/gedit-snapopen-plugin]]