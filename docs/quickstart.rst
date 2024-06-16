.. _quickstart:

Quickstart
============

This guide provides a tour of Yatla's features. Once Yalta is :doc:`installed </installation>`, you can follow along.

Create a template
-------------------

First, we need to define a template. Yatla's :func:`parse <yatla.parser.parse>` method accepts Python strings, this allows you to manage the template persistence yourself. For this tutorial, we'll define our templates as Python literals.
::

    >>> template_source = "Hello, {{ name }}!"

Slots represent the "gaps" in a template. They begin with ``{{`` and continue until ``}}``. For now, our template has only 1 slot, and that slot contains an identifier. When parsed by yatla, the templating engine will recognise that the slot contains an identifier: ``name``. This will be stored alongside the template, and will be used as a lookup value when executing the template. We'll go into more detail on filling these slots later.

The templating language has a similar syntax to Jinja and other Mustache-style languages, so it should be easy to bring your knowledge from other templating languages to Yatla.


Parse a template
-------------------

Now that we have defined our first template, we can use yatla's :func:`parse <yatla.parser.parse>` method to convert it to a :class:`Template <yatla.template.Template>` instance.
::

    >>> import yatla
    >>> template = yatla.parse(template_source)
    >>> template
    Template(source='Hello, {{ name }}!', slots=[Slot(name='name', type=<SlotType.Any: 3>)])

We can see that yatla has detected the ``name`` parameter in our template. It has also inferred that the variable can have type :attr:`Any <yatla.types.SlotType.Any>`. This means the identifier can be replaced with either a string or a number. For the available types see the :class:`SlotType <yatla.types.SlotType>` enum. This guide will cover the type system in more detail further on.


Fill a template
-------------------

Now that we have a template, we can use it! A template instance contains a :meth:`Fill <yatla.template.Template.fill>` method. This method takes a mapping (commonly a ``dict``) of identifiers to values and executes the template with those values.
::

    >>> parameters = { "name" : "world" }
    >>> template.fill(parameters)
    'Hello, world!'
    >>> parameters = { "name" : "James" }
    >>> template.fill(parameters)
    'Hello, James!'



Get type information
---------------------

To see the name-type pairs of a template's slots, you can use the :attr:`slots <yatla.template.Template.slots>` property of a template.
::

    >>> template.slots
    [Slot(name='name', type=<SlotType.Any: 3>)]

This property contains all the detected slots in the template. The  :class:`Slot <yatla.template.Slot>` instances contain a name and a type.


Aside: the type system
-----------------------

Yatla's type system is designed to be expressive, whilst preventing comeplexity. The following is a complete list of all supported slot types.

- :attr:`String <yatla.types.SlotType.String>`: used to repesent strings.
- :attr:`Num <yatla.types.SlotType.Num>`: used to represent numbers. Yatla does not distinguish between numeric types (compared to Python's ``float`` or ``int``, for example).
- :attr:`Any <yatla.types.SlotType.Any>`: used to represent either strings or numbers.
- :attr:`StringArray <yatla.types.SlotType.StringArray>`: used to represent an array of :attr:`String <yatla.types.SlotType.String>`.
- :attr:`NumArray <yatla.types.SlotType.NumArray>`: used to represent an array of :attr:`Num <yatla.types.SlotType.Num>`.
- :attr:`AnyArray <yatla.types.SlotType.AnyArray>`: used to represent an array of either :attr:`String <yatla.types.SlotType.String>` or :attr:`Num <yatla.types.SlotType.Num>`. Note: this union is at the element level.

The type system does not support objects. 

Mathematics
-------------------

Template slots also support mathematical expressions.
::

    >>> yatla.parse("3 * 7 = {{ 3 * 7 }}").fill({})
    '3 * 7 = 21'
    >>> yatla.parse("3 * (7 + 1) = {{ 3 * (7 + 1) }}").fill({})
    '3 * (7 + 1) = 24'

You can use ``+``, ``-``, ``*`` and  ``/`` to create arithmetic expressions, and ``(`` ``)`` to override the standard operator precedence.

Yatla will identify parameters in arithmetic expressions and will infer their type to be :attr:`Num <yatla.types.SlotType.Num>`.
::

    >>> yatla.parse("{{ 1 + operand }}").slots
    [Slot(name='operand', type=<SlotType.Num: 2>)]

Functions
-------------------

To create more powerful mathematical expressions, Yatla provides a standard-library of built-in functions which are can be invoked from the slot of any template. These are the only functions which can be used within a template.

The functions are stored in the :mod:`Builtins <yatla.builtins>` module. See each function's linked reference for their documentation:

- :func:`Maximum <yatla.builtins.Maximum>`
- :func:`Minimum <yatla.builtins.Minimum>`
- :func:`RoundDown <yatla.builtins.RoundDown>`
- :func:`RoundUp <yatla.builtins.RoundUp>`

Invoking a function in Yatla uses the same syntax as Python, first the method name, then the argument list in parentheses.
:: 

    >>> yatla.parse("{{ Maximum(3, 7) }}").fill({})
    '7'
    >>> yatla.parse("{{ RoundUp(3, 5) }}").fill({})
    '5'

We can also use parameters as a function argument.
::

    >>> template = yatla.parse("{{ Maximum(3, number) }}")
    >>> template.slots
    [Slot(name='number', type=<SlotType.Num: 2>)]
    >>> template.fill({"number": 2})
    3
    >>> template.fill({"number": 10})
    10


Iteration
-------------------

The templating engine supports simple iteration using a ``foreach`` loop.
::

    >>> yatla.parse("{{ foreach name in name_list }}\n"
                    "Hello {{ name }}\n"
                    "{{ endforeach }}").fill({ "name_list" : ["Patrick", "Paul", "Timothy"]})
    'Hello Patrick\nHello Paul\nHello Timothy'

A ``foreach`` loop begins with ``{{ foreach name in iterator }}``. The opening foreach block must be the only text on the line. If any text or slot appears before or after this slot, a parser error will be thrown. The first key: ``foreach`` indicates that we would like to start a loop. The second word in the opening slot defines the iterand, in this example that is ``name``. This variable will be available in the body of the loop. The third keyword ``in`` is used to separate the iterand from the iterator. The fourth and final keyword is the iterator. This is an array over which the iterand's value will range during execution. 

The body of the ``foreach`` loop begins on the next line, and continues until ``{{ endforeach }}``. The loop body is able to contain any combination of slots and text over many lines. However, foreach loops cannot be nested. The body will be repeated for each of the values in the iterator. No identation rules are enforced, unlike Python. Indentation on each body line will be included in the evaluated template.
::

    >>> yatla.parse("{{ foreach name in name_list }}\n"
                    "    Hello {{ name }}\n"
                    "{{ endforeach }}").fill({ "name_list" : ["Patrick", "Paul", "Timothy"]})
    '    Hello Patrick\n     Hello Paul\n    Hello Timothy'

The end of the loop is marked with a slot containing the ``endforeach`` keyword: ``{{ endforeach }}``. This must also be the only text on a line.

At execution time, the body of the loop will be executed by subsituting the iterand with advancing values of the iterator.

The type of iterators will be inferred when a template is parsed.
::

    >>> yatla.parse("{{ foreach name in name_list }}\n"
                    "Hello {{ name }}\n"
                    "{{ endforeach }}").slots
    [Slot(name='name_list', type=<SlotType.AnyArray: 6>)]

Iterators can be any array type:

- :attr:`StringArray <yatla.types.SlotType.StringArray>`
- :attr:`NumArray <yatla.types.SlotType.NumArray>`
- :attr:`AnyArray <yatla.types.SlotType.AnyArray>`

::
    
    >>> yatla.parse("{{ foreach factor in num_list }}\n"
                    "{{ factor * 7 }}\n"
                    "{{ endforeach }}").slots
    [Slot(name='num_list', type=<SlotType.NumArray: 5>)]

You can also refer other, non-iterator slots inside a loop:
::

    >>> yatla.parse("{{ foreach factor in num_list }}\n"
                    "{{ factor * multipler }}\n"
                    "{{ endforeach }}").slots
    [Slot(name='multipler', type=<SlotType.Num: 2>), Slot(name='num_list', type=<SlotType.NumArray: 5>)]