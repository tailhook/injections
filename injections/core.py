"""Injections dependency injection framework

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

"""

from .topsort import topologically_sorted


def has(cls):
    """Class decorator that declares dependencies"""
    deps = {}
    for i in dir(cls):
        if i.startswith('__') and i.endswith('__'):
            continue
        val = getattr(cls, i, None)
        if isinstance(val, Dependency):
            deps[i] = val
            if val.name is None:
                val.name = i
    cls.__injections__ = deps
    return cls


class Dependency:
    """Property that represents single dependency"""

    def __init__(self, typ, name=None):
        self.type = typ
        self.name = name

    def __get__(self, inst, owner):
        if inst is None:
            return self
        raise RuntimeError("Dependency {!r} is not configured".format(self))

    def __repr__(self):
        return "<Dependency {!r}:{!r}>".format(self.type, self.name)


depends = Dependency  # nicer declarative name


class Container(object):
    """Container for things that will be dependency-injected

    Set all dependencies with::

        >>> inj = Container()
        >>> inj['name'] = value
        >>> obj = inj.inject(DependentClass())

    Propagate dependencies with::

        >>> injections.propagate(obj, NewObject())
    """

    def __init__(self, *args, **kw):
        self._provides = dict(*args, **kw)

    def inject(self, inst, **renames):
        """Injects dependencies and propagates dependency injector"""
        if renames:
            di = self.clone(**renames)
        else:
            di = self
        pro = di._provides
        inst.__injections_source__ = di
        deps = getattr(inst, '__injections__', None)
        if deps:
            for attr, dep in deps.items():
                val = pro[dep.name]
                if not isinstance(val, dep.type):
                    raise TypeError("Wrong provider for {!r}".format(val))
                setattr(inst, attr, val)
        meth = getattr(inst, '__injected__', None)
        if meth is not None:
            meth()
        return inst

    def __setitem__(self, name, value):
        if name in self._provides:
            raise RuntimeError("Two providers for {!r}".format(name))
        self._provides[name] = value

    def __getitem__(self, name):
        return self._provides[name]

    def __contains__(self, name):
        return name in self._provides

    def clone(self, **renames):
        di = self.__class__()
        mypro = self._provides
        pro = di._provides
        pro.update(mypro)
        for name, alias in renames.items():
            pro[name] = mypro[alias]
        return di

    def interconnect_all(self):
        """Propagate dependencies for provided instances"""
        for dep in topologically_sorted(self._provides):
            if hasattr(dep, '__injections__') and not hasattr(dep, '__injections_source__'):
                self.inject(dep)


def dependencies(cls):
    """Returns dict of dependencies of a class declared with
    ``@injections.has``
    """
    return getattr(cls, '__injections__', {})


def get_container(obj):
    """Returns dependency injector used to construct class

    This instance is useful to propagate dependencies
    """
    try:
        return obj.__injections_source__
    except AttributeError:
        raise RuntimeError("No dependency injector found")


def propagate(source, target):
    """Propagates dependencies from container used to fill `source` to fill
        target's dependencies

         Equivalent of::

            get_container(source).inject(target)
    """
    return get_container(source).inject(target)
