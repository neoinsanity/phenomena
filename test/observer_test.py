from unittest import TestCase

from phenomena.observer import Observer

class ObserverTest(TestCase):
    def test_init(self):
        o = Observer()
        self.assertIsNotNone(0)
