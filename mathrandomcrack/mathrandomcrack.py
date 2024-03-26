from .mathrandom import *
from .xs128crack import recover_seed_from_known_bits

import logging

logger = logging.getLogger(__name__)

def recover_state_from_math_random_known_bits(known_bits, positions=None):
    """
    Recover all the possible MathRandom states given a list of known bits of values generated by Math.random().

    Arguments:
        known_bits: a list of 64-bit vectors where known_bits[i][j] is:
            - 0 or 1 if the j-th bit of the i-th value generated by Math.random() is known.
            - None if the j-th bit of the i-th value generated by Math.random() is unknown.
    
        positions: a list that defines the position of the call that generated each known_bits value with Math.random().
            If not specified, it will be assumed that values represented by known_bits were generated by successive Math.random() calls.

    Yield possible MathRandom() objects that are initialized to a valid internal state before the
        generation of the given list of known_bits values at specified positions.
    """
    assert all(len(state) == 64 for state in known_bits)
    # If positions are not specified, assume the doubles are successive values of Math.random()
    if not positions:
        positions = [i for i in range(len(known_bits))]
    assert len(known_bits) == len(positions)
    index_to_known_bits = {positions[i]:known_bits[i] for i in range(len(known_bits))}
    # Bruteforce the cache_idx value at the first Math.random call
    for cache_idx in range(MATH_RANDOM_CACHE_SIZE):
        logger.debug(f'Trying to find a good seed for cache index {cache_idx}')
        known_states_bits = []
        # Account for Math.random cache reverting outputs order by blocks of size 64
        for i in range(MATH_RANDOM_CACHE_SIZE * ((max(positions) // MATH_RANDOM_CACHE_SIZE) + 2)):
            cache_n = i // MATH_RANDOM_CACHE_SIZE
            value_index = cache_n * MATH_RANDOM_CACHE_SIZE + cache_idx - (i % MATH_RANDOM_CACHE_SIZE)
            if value_index in index_to_known_bits:
                # If we know bits of the value at this index, add its bits to the list of known states bits
                known_states_bits.append(index_to_known_bits[value_index])
            else:
                # Else, we don't know any bits for this state
                known_states_bits.append([None for _ in range(64)])
        # Try to recover possible seeds for this starting cache_idx
        seeds = recover_seed_from_known_bits(known_states_bits)
        try:
            for seed in seeds:
                math_random = MathRandom()
                math_random.recover_from_previous_state(seed[0], seed[1], cache_idx)
                yield math_random
        except ValueError as e:
            # No solution, cache_idx is wrong
            pass

def recover_state_from_math_random_doubles(doubles, positions=None):
    """
    Recover all the possible MathRandom states given a list of doubles generated by Math.random().

    Arguments:
        doubles: a list of doubles outputs generated by V8 Math.random().
            The doubles don't have to be generated successively but their positions must be known.
    
        positions: a list that defines the position of the call that generated each double with Math.random().
            If not specified, it will be assumed that doubles were generated by successive Math.random() calls.

    Yield possible MathRandom() objects that are initialized to a valid internal state before the
        generation of the given list of doubles at specified positions.
    """
    assert all(0.0 <= d <= 1.0 for d in doubles)
    # Convert doubles to known bits
    known_bits = []
    for double in doubles:
        # V8 double conversion loses 12 bits of information
        known_bits.append([None for _ in range(12)] + int64_to_bits(v8_from_double(double))[12:HALF_STATE_SIZE])
    # Recover possible states from known bits
    for math_random in recover_state_from_math_random_known_bits(known_bits, positions):
        yield math_random

def recover_state_from_math_random_scaled_values(scaled_vals, factor, translation=0, positions=None):
    """
    Recover all the possible MathRandom states given a list of values generated by Math.floor(Math.random() * factor + translate).

    Arguments:
        scaled_vals: a list of scaled values outputs generated by V8 Math.floor(Math.random() * factor)
            The values don't have to be generated successively but their positions must be known.
        
        factor, translation: the integers used in the expression Math.floor(Math.random() * factor + translation)
    
        positions: a list that defines the position of the call that generated each values with Math.floor(Math.random() * factor).
            If not specified, it will be assumed that values were generated by successive Math.random() calls.

    Yield possible MathRandom() objects that are initialized to a valid internal state before the
        generation of the given list of scaled values at specified positions.
    """
    assert type(factor) is int
    assert type(translation) is int
    # Convert scaled values to known bits
    known_bits = []
    for scaled_val in scaled_vals:
        # Recover the lower and higher bound of the internal xs128 state
        low, high = v8_from_double((scaled_val - translation) / factor), v8_from_double((scaled_val - translation + 1) / factor) | 0xfff
        # Find the common bits in the state representation of all values between the bounds
        common_known_bits = common_bits_between(low, high)
        # Only keep the common bits
        known_bits.append([None for _ in range(64 - len(common_known_bits))] + common_known_bits)
    # Recover possible states from known bits
    for math_random in recover_state_from_math_random_known_bits(known_bits, positions):
        yield math_random

def recover_state_from_math_random_approximate_values(bounds, positions=None):
    """
    Recover all the possible MathRandom states given a list of bounds that bound values generated by Math.random().

    Arguments:
        bounds: a list of tuples that represents the known bounds of values generated by Math.random().
    
        positions: a list that defines the position of the call that generated each values with Math.random().
            If not specified, it will be assumed that values were generated by successive Math.random() calls.

    Yield possible MathRandom() objects that are initialized to a valid internal state before the
        generation of the given list of approximated values at specified positions.
    """
    assert all(len(b) == 2 for b in bounds)
    # Convert bounds to known bits
    known_bits = []
    for b in bounds:
        # Recover the lower and higher bound of the internal xs128 state
        low, high = v8_from_double(float(b[0])), v8_from_double(float(b[1])) | 0xfff
        # Find the common bits in the state representation of all values between the bounds
        common_known_bits = common_bits_between(low, high)
        # Only keep the common bits
        known_bits.append([None for _ in range(64 - len(common_known_bits))] + common_known_bits)
    # Recover possible states from known bits
    for math_random in recover_state_from_math_random_known_bits(known_bits, positions):
        yield math_random

def common_bits_between(low, high):
    """
    Returns the list of most significant bits that are the same for all value between low and high.

    Arguments:
        low, high: 64-bit integers for the bounds.
    """
    low = max(0, low)
    high = min(2**64-1, high)
    exp = 63
    common_bits = []
    s = 0
    while True:
        v = pow(2, exp)
        if s + v <= low <= high:
            common_bits.append(1)
            s += v
        elif low <= high <= s + v:
            common_bits.append(0)
        else:
            break
        exp -= 1
    return common_bits[::-1]

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    #TODO add a CLI

