==========
Injections
==========


Injections is a simple dependency injection library which is intended to
cleanup object dependency hell.


Usage
=====

Declare a class' dependencies::

    @injections.has
    class Hello(object):

        world = injections.depends(World, 'universe')

You must decorate class with ``@injections.has``. All dependencies has a
type(class), which is ``World`` in this case, and a name, which is ``universe``
in this case. This is for having multiple similar dependencies.

Note: Name of dependency is unique among all services in single dependency
injector and not tied to particular type. This is done to easier support
subclassing of dependencies (and you can also register subclass with abc
instead of subclassing directly)

Then at some initialisation code you create dependency injector, and set
apropriate services::

    inj = injections.Container()
    inj['universe'] = World()

Now you can create ``Hello`` instances and inject dependencies to them::

    hello = inj.inject(Hello())
    assert hello.world is inj['universe']

And you can propagate dependencies starting from existing instances::

    h2 = injections.propagate(hello, Hello())
    assert h2.world is hello.world


If you need do some class initialization when dependencies are ready, you
must do the work in ``__injected__`` method instead of ``__init__``::

    @injections.has
    class CachedValue(object):
        redis = injections.depends(Redis)
        def __injected__(self):
            self.cached_value = self.redis.get('cache')

If you need to propagate some dependencies, you are probably want do do
it in the ``__injected__`` method too::

    @injections.has
    class Child:
        redis = injections.depends(Redis)

    @injections.has
    class Parent:
        def __injected__(self):
            self.child = injections.propagate(self, Child())


Note: In the last two examples where name is omitted, it's got from
the name of the attribute to assign to. It's used to avoid repetitive
typing, but may be error prone.


Cyclic Dependencies
===================


Dependencies between objects might be cyclic as long as object don't use
each other in ``__injected__`` method. To handle cyclic depencency between
classes ``A`` and ``B`` use code similar to the following:

.. code-block:: python

   inj['a'] = A()
   inj['b'] = B()
   inj.inject(inj['a'])
   inj.inject(inj['b'])


Automatic Interconnection (experimental)
========================================

Sometimes it's useful to omit ``inject()`` calls for the objects put in
container, and then connect them all using ``interconnect_all()``:

.. code-block:: python

   inj['a'] = A()
   inj['b'] = B()
   inj['c'] = C()
   inj.interconnect_all()

This will call ``inj.inject`` for all objects in container in proper order
(using topology sort based on their dependencies). It doesn't make your
container sealed, so you can add more dependencies later, and interconnect new
ones too.

Note: Cyclic dependencies are not processed by ``interconnect_all``, so you
must either do ``inject()`` for them (in proper order) *before* calling
interconnect, or *add* them to the container *after*.  In any case
*injections* will not try to guess, but will fail with runtime exception if
can't find out proper order.


History
=======

The library was ininitally named ``zorro.di`` and was a part of zorro_
networking library.

.. _zorro: http://github.com/tailhook/zorro
