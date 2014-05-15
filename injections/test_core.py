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

    def testOk(self):
        c = di.Container()
        c['name'] = "John"
        cons = c.inject(self.Consumer())
        self.assertEqual(cons.hello(), 'Hello John!')

    def testWrongType(self):
        c = di.Container()
        c['name'] = 1
        with self.assertRaises(TypeError):
            c.inject(self.Consumer())
