:mod:`do3se.model` -- Interface to Fortran model
================================================

.. module:: do3se.model

The :mod:`~do3se.model` module imports everything from the compiled :mod:`~do3se._model` module 
generated from the Fortran source code.  It also defines several extra data definitions for tying 
together aspects of the user interface and interactions with the Fortran model, and helper functions 
for interacting with the model in a more "Pythonic" way.

Data definitions
----------------

These data definitions associate useful information with parts of the Fortran model.

.. data:: input_fields
    
    Available input columns.  An :class:`~do3se.util.ordereddict.OrderedDict` mapping variable name 
    (the unique identifier of an input field) to a dictionary of the following:

    +---------------+------------------------------------------------------------------------------+
    | Key           | Description                                                                  |
    +===============+==============================================================================+
    | ``module``    | The module the input variable resides in                                     |
    +---------------+------------------------------------------------------------------------------+
    | ``variable``  | The variable name, used as field key and name of attribute of ``module``)    |
    +---------------+------------------------------------------------------------------------------+
    | ``type``      | Callable to convert input data to correct type (usually an actual type, e.g. |  
    |               | :class:`int` or :class:`float`)                                              |
    +---------------+------------------------------------------------------------------------------+
    | ``required``  | Is the field always required?  (Some field have more complex rules, but this |
    |               | covers the simple ones)                                                      |
    +---------------+------------------------------------------------------------------------------+
    | ``short``     | Short field description                                                      |
    +---------------+------------------------------------------------------------------------------+
    | ``long``      | Long field description, used in column selection widget                      |
    +---------------+------------------------------------------------------------------------------+

.. data:: output_fields

    Available output columns.  An :class:`~do3se.util.ordereddict.OrderedDict` mapping variable name 
    (the unique identifier of an input field) to a dictionary of the following:

    +---------------+------------------------------------------------------------------------------+
    | Key           | Description                                                                  |
    +===============+==============================================================================+
    | ``module``    | The module the output variable resides in                                    |
    +---------------+------------------------------------------------------------------------------+
    | ``variable``  | The variable name, used as field key and name of attribute of ``module``)    |
    +---------------+------------------------------------------------------------------------------+
    | ``type``      | Callable to convert output data to correct type when extracted from the      |   
    |               | Fortran model                                                                |
    +---------------+------------------------------------------------------------------------------+
    | ``short``     | Short field description, used as column header in results output             |
    +---------------+------------------------------------------------------------------------------+
    | ``long``      | Long field description, used in column selection widget                      |
    +---------------+------------------------------------------------------------------------------+

.. data:: paramdefs

    Attempts to centrally define the majority of the model parameters in a way that is useful for UI 
    generation.
    
    Since most of the parameters are simply an input field, this definition in conjunction with the 
    classes in the :mod:`~do3se.fields` module abstract this as a dictionary keyed on the variable 
    name which includes relevant information for constructing the UI.
    
    Some parameters are not so simple---for example the ``input_fields`` and ``input_trim`` fields 
    which control data loading---but they are still defined here to keep their descriptions in one 
    place.

    Each field definition contains the following:

    +---------------+------------------------------------------------------------------------------+
    | Key           | Description                                                                  |
    +===============+==============================================================================+
    | ``group``     | A parameter group name, for use with :func:`parameters_by_group`             |
    +---------------+------------------------------------------------------------------------------+
    | ``variable``  | The variable name, used as parameter key and name of attribute of            |
    |               | :mod:`do3se._model.parameters`)                                              |
    +---------------+------------------------------------------------------------------------------+
    | ``cls``       | :mod:`~do3se.fields.Field` subclass to use for the parameter in the UI       |
    +---------------+------------------------------------------------------------------------------+
    | ``args``      | Arguments to pass to constructor of ``cls``, following the parent widget as  |
    |               | the first argument                                                           |
    +---------------+------------------------------------------------------------------------------+
    | ``name``      | Parameter description, used for label alongside the input field              |
    +---------------+------------------------------------------------------------------------------+

Helper functions
----------------

.. autofunction:: parameters_by_group
.. autofunction:: extract_outputs
