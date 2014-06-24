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
        with self.assertRaises(RuntimeError):
            c.interconnect_all()

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
