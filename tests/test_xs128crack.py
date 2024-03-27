import unittest

from mathrandomcrack.xs128crack import *

class TestXS128Crack(unittest.TestCase):

    def test_recover_seed_from_known_bits(self):
        # Pick a random seed
        seed0, seed1 = 12092933408070727569, 7218780437263453395
        state0, state1 = seed0, seed1

        # Generate random integers using xs128
        random_integers = []
        for i in range(8):
            state0, state1 = xs128(state0, state1)
            random_integers.append(state0)

        # Only keep a few bits of some integers
        known_states_bits = []
        for i, n in enumerate(random_integers):
            if i == 3:
                # Skip unknown integer
                state = [None for _ in range(64)]
            else:
                # Keep only 18 bits
                state = [None for _ in range(20)] # Unknown LSBs
                state.extend([(n >> j) & 1 for j in range(20, 38)]) # Known bits
                state.extend([None for _ in range(38, 64)]) # Unknown MSBs
            known_states_bits.append(state)

        # Try to recover the right seed
        found_correct_seed = False
        for rec_seed0, rec_seed1 in recover_seed_from_known_bits(known_states_bits):
            found_correct_seed = rec_seed0 == seed0 and rec_seed1 == seed1
            if found_correct_seed:
                break
        self.assertTrue(found_correct_seed)

