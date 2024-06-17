.. yatla documentation master file, created by
   sphinx-quickstart on Tue May 28 22:23:21 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yatla: typed templating
=================================
.. image:: https://img.shields.io/pypi/l/yatla
   :target: https://pypi.org/project/yatla/
   :alt: PyPI - License

.. image:: https://img.shields.io/pypi/pyversions/yatla
   :target: https://pypi.org/project/yatla/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/wheel/yatla
   :target: https://pypi.org/project/yatla/
   :alt: PyPI - Wheel

**Yatla** is an simple, statically-typed templating language for Python.

-------------

Statically typed templates::

   >>> template = yatla.parse("Hello, {{ name }}!")
   >>> template.slots
   [Slot(name='name', type=<SlotType.Any: 3>)]
   >>> template.fill({"name": "world"})
   'Hello, world!'
   >>> template = yatla.parse("{{ factor }} * 2 = {{ factor * 2 }}")
   >>> template.slots
   [Slot(name='factor', type=<SlotType.Num: 2>)]
   >>> template.fill({"factor": 3})
   '3 * 2 = 6'

You can install the library directly from PyPI::

   $ pip install yatla

User guide
-------------------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   support
   API Reference <source/modules>
   Changelog <changelog>
   License (MIT) <license>
   

