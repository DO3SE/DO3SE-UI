Building the DO3SE model
========================


The command-line F model
------------------------


The graphical user interface
----------------------------

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

The dependencies of the GUI are:

* `Python 2.6.x`_ (not 3.x, and nothing above 2.6 until a NumPy build exists for it)
* NumPy_ 1.1.0 or later
* wxPython_ 2.8.10.1 or later

1.  Download and install Python
2.  Download and install NumPy
3.  Download and install wxPython
4.  Add the Python installation directory to the :envvar:`PATH` environment variable (e.g.  
    :file:`C:\\somepath\\bin` becomes :file:`C:\\Python26;C:\\somepath\\bin`)
    
    * **Windows XP**
        * Press the :kbd:`Win+Break` key combination to open the :guilabel:`System Properties` 
          dialog.
        * Click the :guilabel:`Advanced` tab, then :guilabel:`Environment Variables`.
        * In the :guilabel:`System variables` section, click the :envvar:`PATH` (or :envvar:`Path`) 
          row and click :guilabel:`Edit`.
        * Insert the new path (e.g.  :file:`C:\\Python26`), followed by a semicolon, before the 
          existing value.
        * Click :guilabel:`OK` on the edit dialog, then on the :guilabel:`Environment Variables` 
          window, and finally on the :guilabel:`System Properties` window.


.. _Python 2.6.x: http://python.org/download/releases/
.. _NumPy: http://numpy.scipy.org/
.. _wxPython: http://www.wxpython.org/
