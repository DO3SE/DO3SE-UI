UI redesign (2010) notes
========================

Time for a more project-oriented view!  Input/site/vegetation parameters being saved separately are 
a bit passé...  A project file contains the settings for a single project/dataset.  This means all 
site parameters, all vegetation parameters, and the input and output file formats.

When launching the application, launched with no arguments it will show the "about DO3SE" stuff with 
a list of recent projects and the opportunity to open/create a project::

    +--------------------------------------------------------+
    | o  DO3SE                                        _ [] X |
    |--------------------------------------------------------|
    | Blah blah blah blah all about DO3SE                    |
    |                                                        |
    |                                                        |
    |                                                        |
    |                                                        |
    |                                                        |
    |                                                        |
    |                                                        |
    |--------------------------------------------------------|
    | Recent projects                                        |
    |+------------------------------------------------------+|
    || Project 1                                            ||
    || Project 2                                            ||
    |+------------------------------------------------------+|
    |          [Open selected] [Open other...] [New project] |
    +--------------------------------------------------------+

Any action (other than closing the window) will result in a project window.  If a command line 
argument is supplied, it is treated as a project file to open.  This allows associating the tool 
with a file extension (e.g. ``.do3se``).  (An ``--automate`` flag can be provided which will run the 
model and provide output on stdout without ever opening the UI).

The single-instance behaviour should be modified to the following:

  + If called with no arguments and application is running, tell the user it's already running.
  + If called with an argument, it should open a project window for that project.
  + If called with ``--automate`` and an argument, should act exactly as if the application wasn't 
    running, i.e. running the model and providing output.


The project window
------------------


Default parameterisations
-------------------------
A default parameterisation is a named set of parameter/value pairs which can be applied to a 
project, overwriting existing values.  Some kind of "Apply parameterisation" should allow user to 
browse and select one (possibly via treebook where each item is the name and the page is a list of 
variable names and values).

It should hopefully (maybe not yet) be possible for a user to save a parameterisation, giving them a 
tree that matches the structure of the parameter setting UI where each variable has a checkbox.  
They should be able to give it a name.  Custom parameterisations should override default ones of the 
same name in display, but defaults should never be saved to user configuration - they are combined 
at point of usage.
