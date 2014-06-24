from unittest import TestCase

import injections as di


class TestCore(TestCase):

    def setUp(self):
        @di.has
        class Consumer:
            value = di.depends(str, 'name')

            def hello(self):
                return "Hello {}!".format(self.value)

        self.Consumer = Consumer

    def test_ok(self):
        c = di.Container()
        c['name'] = "John"
        cons = c.inject(self.Consumer())
        self.assertEqual(cons.hello(), 'Hello John!')

    def test_interconnect(self):
        @di.has
        class Source:
             value = di.depends(self.Consumer, 'consumer')

             def __injected__(self):
                assert self.value.value is 'John'

        c = di.Container()
        c['name'] = "John"
        c['consumer'] = self.Consumer()
        c.interconnect_all()
        res = c.inject(Source())
        self.assertEqual(res.value.hello(), 'Hello John!')

    def test_cyclic(self):
        class Base:
            pass

        @di.has
        class Processor(Base):
             cache = di.depends(Base, 'cache')

        @di.has
        class Cache(Base):
             processor = di.depends(Base, 'processor')

        c = di.Container()
        c['cache'] = Cache()
        c['processor'] = Processor()
        try:
            c.interconnect_all()
        except RuntimeError as e:
            self.assertSetEqual({'cache', 'processor'},
                set(e.objects_in_cycle.keys()))
        else:
            raise AssertionError("Exception not raised")

    def test_larger_cycle(self):

        @di.has
        class Y(object):
            pass

        @di.has
        class A(object):
             b = di.depends(object, 'b')
             y = di.depends(Y, 'y')

        @di.has
        class B(object):
             c = di.depends(object, 'c')

        @di.has
        class C(object):
             a = di.depends(object, 'a')

        @di.has
        class X(object):
             a = di.depends(object, 'a')

        @di.has
        class Z(object):
             x = di.depends(object, 'x')

        c = di.Container()
        c['a'] = A()
        c['b'] = B()
        c['c'] = C()
        c['x'] = X()
        c['y'] = Y()
        c['z'] = Z()
        try:
            c.interconnect_all()
        except RuntimeError as e:
            self.assertSetEqual({'a', 'b', 'c'},
                set(e.objects_in_cycle.keys()))
        else:
            raise AssertionError("Exception not raised")

    def test_clone(self):
        @di.has
        class User:
            value = di.depends(self.Consumer, 'consumer')

        @di.has
        class Girl:
            father = di.depends(User, 'user')

        c = di.Container()
        c['name'] = "John"
        c['consumer'] = self.Consumer()
        c.interconnect_all()
        c = c.clone()
        c['user'] = User()
        c.interconnect_all()
        r = c.inject(Girl())
        self.assertTrue(r.father is c['user'])
        self.assertTrue(r.father.value is c['consumer'])

    def test_wrong_type(self):
        c = di.Container()
        c['name'] = 1
        with self.assertRaises(TypeError):
            c.inject(self.Consumer())
