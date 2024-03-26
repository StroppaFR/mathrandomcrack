from .xs128 import *

import copy
import struct
from random import randint

MATH_RANDOM_CACHE_SIZE = 64

def v8_to_double(state0):
    """
    Convert a 64-bit integer state0 from xs128 to a double output.
    The result is between 0.0 and 1.0.
    The 12 least significant bits of state0 are lost during conversion.

    See also: https://github.com/v8/v8/blob/12.5.66/src/base/utils/random-number-generator.h#L111
    """
    r = (state0 >> 12) | 0x3ff0000000000000
    return struct.unpack('d', struct.pack('<Q', r))[0] - 1

def v8_from_double(double):
    """
    Convert a double back to a 64-bit integer.
    The 12 least significant bits of the result cannot be recovered.
    """
    if double == 1.0:
        return 0xffffffffffffffff
    return (struct.unpack('<Q', struct.pack('d', double + 1.0))[0] & 0xfffffffffffff) << 12

def int64_to_bits(val):
    """
    Convert a 64-bit integer to a list of bits.
    """
    return [(val >> i) & 1 for i in range(64)]

class MathRandom():
    """
    A class that simulates V8 Math.random behaviour.
    
    Attributes:
        state0, state1: the 128-bit state to use for next cache refill.
        
        cache_idx: the index in the internal cache.
            Decrements every time a random value is consumed by next().

        cache: the 64-long list of random 64-bit values generated by xs128.
    """
    def __init__(self, state0=None, state1=None):
        """
        Initialize internal Math.random state.

        Arguments:
            (optional) state0 and state1 of xs128. If not specified, random values will be set.
        """
        if not state0:
            state0 = randint(0, 1 << HALF_STATE_SIZE)
        if not state1:
            state1 = randint(0, 1 << HALF_STATE_SIZE)
        self.state0 = state0
        self.state1 = state1
        self.cache_idx = -1
        self.cache = []
        self.refill()

    def refill(self):
        """
        Refill the Math.random cache using xs128.
        Can only be used when Math.random cache is empty.

        A new 64-long list of random values is stored in cache.
        The cache_idx is set to the last index of the cache (63).
        """
        assert self.cache_idx == -1
        self.cache = []
        for _ in range(MATH_RANDOM_CACHE_SIZE):
            self.state0, self.state1 = xs128(self.state0, self.state1)
            self.cache.append(self.state0)
        self.cache_idx = MATH_RANDOM_CACHE_SIZE - 1

    def next(self):
        """
        Output the result of a call to Math.random() (a double between 0.0 and 1.0).
        Decrement cache_idx and refill the cache if needed.
        """
        if self.cache_idx < 0:
            self.refill()
        val = v8_to_double(self.cache[self.cache_idx])
        self.cache_idx -= 1
        return val

    #TODO add previous() and previousRefill() mechanism to get previous random values

    def recover_from_previous_state(self, prev_state0, prev_state1, cache_idx):
        """
        Recover a MathRandom internal state using the values of state0 and state1 before the previous refill.
        Refill the entire cache and set cache_idx accordingly.

        Arguments:
            prev_state0, prev_state1: the values of state0 and state1 before the previous refill.

            cache_idx: the cache index that should be set after refill.
        """
        self.cache = []
        self.cache_idx = -1
        self.state0 = prev_state0
        self.state1 = prev_state1
        self.refill()
        self.cache_idx = cache_idx
    
    def __copy__(self):
        """
        copy.copy() helper function.
        """
        new_math_random = MathRandom()
        new_math_random.state0 = self.state0
        new_math_random.state1 = self.state1
        new_math_random.cache_idx = self.cache_idx
        new_math_random.cache = [d for d in self.cache]
        return new_math_random
    
    def __eq__(self, other):
        return self.cache_idx == other.cache_idx \
                and self.state0 == other.state0 \
                and self.state1 == other.state1 \
                and self.cache == other.cache

