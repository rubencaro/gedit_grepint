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

Overrides __\<Ctrl\>G__, __\<Ctrl\>\<Shift\>G__ and __\<Ctrl\>T__
accelerators with __Grep file__, __Grep project__ and __Ctags project__.

__Grep file__ performs a quick grep on current file. 
Changes reflect live on the hits list below.

__Grep project__ performs grep on _related folders_. 
The search (this one is heavier) is only 
performed when you hit enter. Related folders are variable, 
and configurable. In order:
 - Currently open files
 - Current file browser plugin root
 - [GIT](http://git-scm.com/) base dirs for any of previous paths
 - Ruby gems path for any of previous paths

GIT base dirs are guessed going into that path and asking git itself
for the base dir. If any path gathered at this point (open files and file browser root) 
is inside a GIT repository, then the search is performed on this entire repository.

Ruby gems a trickier to catch, and often bigger to search in. That's why this is 
deactivated by default. They are guessed the same way that GIT base dirs: 
going inside the path and asking Ruby itself about the active gem paths. This
is compatible with RVM gemsets. If any path gathered at this point 
(open files and file browser root or its GIT base dirs) has any Ruby gem path associated, 
then the search is performed on that gems folder __also__.

You can see the actual grep command performed, 
in case you are brave enough to go for the real thing.

Configurable options are in a `config.json` placed in the plugin folder. You can edit this file
using the menu entry _Edit Configuration_. Then that file is openend inside gedit, 
and you can apply any changes
just by saving the file, or using the _Reload Coniguration_ menu entry.

__Ctags project__ performs tag searching using a tag file.
First you should make a tag file at the top of project:
```
ctags -n -R
```
Open any file at the top project and press __\<Ctrl\>T__. That's it.

Roughly based on, and perfect match with: 
 - https://github.com/rubencaro/gedit-snapopen-plugin
 - https://github.com/rubencaro/gedit_fastprojects
 - https://github.com/rubencaro/gedit_click_regex
