from mathrandomcrack.xs128crack import *
import unittest
import random

class TestXS128Crack(unittest.TestCase):

    def test_recover_seed_from_known_bits(self):
        seed0, seed1 = random.randint(0, 2**64), random.randint(0, 2**64)
        state0, state1 = seed0, seed1

        # Generate a few random integers using xs128
        random_integers = []
        for i in range(7):
            state0, state1 = xs128(state0, state1)
            random_integers.append(state0)

        # Only keep some bits from each integer
        known_states_bits = []
        for i in random_integers:
            state = []
            for j in range(18):
                state.append((i >> j) & 1)
            known_states_bits.append(state)

        # Try to recover the right seed
        found_correct_seed = False
        for rec_seed0, rec_seed1 in recover_seed_from_known_bits(known_states_bits):
            found_correct_seed = rec_seed0 == seed0 and rec_seed1 == seed1
            if found_correct_seed:
                break
        self.assertTrue(found_correct_seed)

