import unittest

from mathrandomcrack.xs128 import *

class TestXS128(unittest.TestCase):

    def test_xs128(self):
        state0, state1 = 12092933408070727569, 7218780437263453395
        for _ in range(100):
            state0, state1 = xs128(state0, state1)
        self.assertEqual(state0, 5753612509715215338)
        self.assertEqual(state1, 17782382993159823008)

    def test_reverse_xs128(self):
        state0, state1 = 5753612509715215338, 17782382993159823008
        for _ in range(100):
            state0, state1 = reverse_xs128(state0, state1)
        self.assertEqual(state0, 12092933408070727569)
        self.assertEqual(state1, 7218780437263453395)

    def test_xs128_both(self):
        init_state0, init_state1 = 5753612509715215338, 17782382993159823008
        state0, state1 = init_state0, init_state1
        for _ in range(1000):
            state0, state1 = xs128(state0, state1)
        for _ in range(1000):
            state0, state1 = reverse_xs128(state0, state1)
        self.assertEqual(state0, init_state0)
        self.assertEqual(state1, init_state1)
