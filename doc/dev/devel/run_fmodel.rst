The F model, when built, is a stand-alone command-line program. To run
it, make sure there is an input file of the correct filename in the
current directory and then execute the program from the command line:

::

    C:\...\DO3SE-src-F-20090620>dir
    ...
    20/06/2009  18:53   <DIR>       .
    20/06/2009  18:53   <DIR>       ..
    20/06/2009  18:53   <DIR>       F
    20/06/2009  18:53               Makefile
    20/06/2009  18:56               dose.exe
    20/06/2009  18:56               input_newstyle.csv
    ...
    C:\...\DO3SE-src-F-20090620>dose.exe
    C:\...\DO3SE-src-F-20090620>dir
    ...
    20/06/2009  18:53   <DIR>       .
    20/06/2009  18:53   <DIR>       ..
    20/06/2009  18:53   <DIR>       F
    20/06/2009  18:53               Makefile
    20/06/2009  18:56               dose.exe
    20/06/2009  18:56               input_newstyle.csv
    20/06/2009  18:59               output.csv
    ...

Alternatively, double-click on ``dose.exe`` to run it—be aware that this
will hide any errors that might have been visible on the command line.

If the output file (``output.csv`` by default) is empty, it is most
likely that no output columns have been specified (see the next
section).

Configuring Input and Output
----------------------------

The input and output of the F model is configured in ``F/dose.f90``.

-  The input and output filenames are set near the bottom of the file,
   in the ``Run_DOSE`` section.

-  The columns to include in the output are set in the ``WriteData``
   subroutine. Uncomment a line to include that variable in the output.
   The variables and their meanings are documented in
   ``F/variables.f90``.

-  The input format is defined in the ``ReadData`` subroutine. *This
   should be used for guidance, but not modified.* The variables and
   their meanings are documented in ``F/inputs.f90``.

-  Where certain calculations have multiple implementations, these can
   be chosen between in the ``Calculate`` subroutine.

To change any of these options, edit ``F/dose.f90`` as necessary and
save it. To use the changes, rebuild the model (see [dev:build]) and run
it again. *If the output filename has not been changed and the previous
results have not been moved, they will be overwritten.*
