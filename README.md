grepint
=============

Grep interface plugin for Gedit.

Performs quick grep on current file, or in associated folders. 

If there is some selected text when invoked, it performs 
a quick search using it as pattern. 
Once invoked you can directly edit the pattern, 
or navigate through the hits list with up/down keys. 
Go there pressing enter on selected result.
No mouse needed.

Overrides __\<Ctrl\>G__ and __\<Ctrl\>\<Shift\>G__ 
accelerators with __Grep file__ and __Grep project__. 

__Grep file__ performs a quick grep on current file. 
Changes reflect live on the hits list below.

__Grep project__ performs grep on _related folders_. 
The search (this one is heavier) is only 
performed when you hit enter. Related folders are variable, 
and configurable. In order:
 - Currently open files
 - Current file browser plugin root
 - [GIT](http://git-scm.com/) base dirs for any of previous paths
 - [RVM](https://rvm.io/) gemset path for any of previous paths

GIT base dirs are guessed going into that path and asking git itself
for the base dir. If any path gathered at this point (open files and file browser root) 
is inside a GIT repository, then the search is performed on this entire repository.

RVM gemsets a trickier to catch, and often bigger to search in. That's why this is 
deactivated by default. They are guessed the same way that GIT base dirs: 
going inside the path and asking RVM itself about the active gemset. You will
need some rvmrc file magic for this to work. If not in a gemset, or not working, 
then RVM answers with the default gemset. If any path gathered at this point 
(open files and file browser root or its GIT base dirs) has any RVM gemset associated, 
then the search is performed on the gemset folder __also__.

You can see the actual grep command performed, 
in case you are brave enough to go for the real thing.

Roughly based on https://github.com/rubencaro/gedit-snapopen-plugin