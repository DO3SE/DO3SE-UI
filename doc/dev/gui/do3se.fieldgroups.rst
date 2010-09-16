:mod:`do3se.fieldgroups` -- Application-specific field groups
=============================================================

.. automodule:: do3se.fieldgroups

Base classes / Mixins
---------------------
.. autoclass:: ParameterGroup
    :members:
.. autoclass:: PreviewCanvasMixin
    :members:

Simple parameter groups
-----------------------
These parameter groups just subclass :class:`ParameterGroup` and set the :attr:`PARAMETERS` 
attribute appropriately.

.. autoclass:: SiteLocationParams
.. autoclass:: MeasurementParams
.. autoclass:: VegCharParams
.. autoclass:: VegEnvParams
.. autoclass:: ModelOptionsParams

Custom parameter groups
-----------------------
These parameter groups do something more than just display a list of fields.

.. autoclass:: InputFormatParams
    :members:
.. autoclass:: SeasonParams
    :members:
.. autoclass:: FphenParams
    :members:
.. autoclass:: LeafFphenParams
    :members:
