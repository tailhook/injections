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

.. note::

    Name of dependency is unique among all services in single dependency
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


.. note:: In the last two examples where name is omitted, it's got from
   the name of the attribute to assign to. It's used to avoid repetitive
   typing, but may be error prone.


History
=======

The library was ininitally named ``zorro.di`` and was a part of zorro_
networking library.

.. _zorro: http://github.com/tailhook/zorro
