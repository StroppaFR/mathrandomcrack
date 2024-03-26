STATE_SIZE = 128
HALF_STATE_SIZE = STATE_SIZE // 2

def xs128(state0, state1):
    """
    Execute XorShift128 and return the new 128-bit state.
    
    Arguments:
        state0, state1: integers or objects that can represent 64-bit integers.
    
    See also: https://github.com/v8/v8/blob/12.5.66/src/base/utils/random-number-generator.h#L119
    """
    mask = (1 << HALF_STATE_SIZE) - 1
    s1 = state0 & mask
    s0 = state1 & mask
    s1 ^= (s1 << 23) & mask
    s1 ^= (s1 >> 17) & mask
    s1 ^= s0
    s1 ^= (s0 >> 26) & mask
    return s0, s1

def reverse_xs128(state0, state1):
    """
    Reverse the execution of XorShift128 and return the previous 128-bit state.

    Arguments:
        state0, state1: 64-bit integers.
    """
    mask = (1 << HALF_STATE_SIZE) - 1
    s0 = state1
    s1 = state0
    s0 ^= s1
    s0 ^= (s1 >> 26) & mask
    s0 = reverse_xor_rshift(s0, 17)
    s0 = reverse_xor_lshift(s0, 23)
    return s0, s1

# Helper functions to reverse operations used in XorShift128
# https://stackoverflow.com/questions/31513168/finding-inverse-operation-to-george-marsaglias-xorshift-rng/31515396#31515396
def reverse_xor_lshift(y, shift):
    x = y & ((1 << shift) - 1)
    for i in range(HALF_STATE_SIZE - shift):
        x |= (1 if bool(x & (1 << i)) ^ bool(y & (1 << (shift + i))) else 0) << (shift + i)
    return x
def reverse_bin(x):
    return int(bin(x)[2:].rjust(HALF_STATE_SIZE, '0')[::-1], 2)
def reverse_xor_rshift(y, shift):
    return reverse_bin(reverse_xor_lshift(reverse_bin(y), shift))

