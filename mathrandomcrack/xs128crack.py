from .xs128 import *

import logging
from sage.all import Matrix, GF

logger = logging.getLogger(__name__)

# Should be a lot more than enough to get only one solution to any system (i think...)
# Avoids the solver DOSing itself with too many equations
MAX_EQUATIONS = 10000

class StateBitDeps():
    """
    A class that represents a 64-bit state0 of xs128 relatively to an initial 128-bit state.
    Each bit of the current xs128 state0 can be expressed as a subset sum of the initial state bits.
    
    Attributes:
        data: A 64-long list of 128 bit integers that represents dependency to the initial 128-bit state.
            data[i] represents a bitmask of all the bits from the initial state to sum together to obtain the i-th bit of the current state.
    """
    def __init__(self, data):
        assert len(data) == HALF_STATE_SIZE
        self.data = data

    def __and__(self, mask):
        if mask != (1 << HALF_STATE_SIZE) - 1:
            raise NotImplementedError("StateBitDeps & mask not implemented")
        return StateBitDeps(self.data)

    def __xor__(self, other):
        return StateBitDeps([self.data[i] ^ other.data[i] for i in range(HALF_STATE_SIZE)])

    def __lshift__(self, shift):
        # Shifting left makes the less significant bits zero
        return StateBitDeps([0 for _ in range(shift)] + self.data[:-shift])
    
    def __rshift__(self, shift):
        # Shifting right makes the most significant bits zero
        return StateBitDeps(self.data[shift:] + [0 for _ in range(shift)])

    def to_coeff(self, index):
        """
        Convert the bitmask of the index-th bit to a list of coefficients in GF(2).
        """
        return [int((self.data[index] >> i) & 1) for i in range(STATE_SIZE)]

class StateEquation():
    """
    A class that represents a linear equation with 128 unknowns with values in GF(2).
    
    Attributes:
        coefficients: 128 coefficients in GF(2).

        result: the result of the equation in GF(2).
    """
    def __init__(self, coefficients, result):
        assert len(coefficients) == STATE_SIZE
        assert all(c in [0, 1] for c in coefficients)
        assert result in [0, 1]
        self.coefficients = coefficients
        self.result = result

def solve_linear_system(equations):
    """
    Solve a list of equations in GF(2). Yield all the solutions.

    Attributes:
        equations: a list of StateEquation that represents the linear system.
    """
    M = []
    b = []
    # Create linear system
    for eq in equations:
        row = [coeff for coeff in eq.coefficients]
        M.append(row)
        b.append(eq.result)
    M = Matrix(GF(2), M)
    b = Matrix(GF(2), b).transpose()
    # Find a solution
    v0 = M.solve_right(b).transpose()[0]
    # Iterate over all solutions
    K = M.right_kernel()
    total_solutions = len(K)
    if total_solutions > 100:
        logger.warning(f'Found {len(K)} valid xs128 seed(s)')
    else:
        logger.debug(f'Found {len(K)} valid xs128 seed(s)')
    for v in K:
        yield sum(int(c) << i for i, c in enumerate(v0 + v))

def recover_seed_from_known_bits(known_states_bits):
    """
    Recover all the possible initial xs128 128-bit states from a list of known bits of successive xs128 state0s.
    The position of known bits can vary between states.
    Intermediate states in the list can have no known bits.

    Arguments:
        known_states_bits: a list of 64-bit vectors where known_states_bits[i][j] is:
            - 0 or 1 if the j-th bit of the i-th state0 of xs128 is known.
            - None if the j-th bit of the i-th state0 of xs128 is unknown.
    
    Return a generator that yields all possible initial 128-bit states of xs128 as a (state0, state1) tuple.
    """
    assert all(len(state) == 64 for state in known_states_bits)
    # Initial state before the xs128 call
    # Initial s0 is the low 64 bits of the initial state
    # Initial s1 is the high 64 bits of the initial state
    s0 = StateBitDeps([1 << i for i in range(HALF_STATE_SIZE)])
    s1 = StateBitDeps([1 << i for i in range(HALF_STATE_SIZE, STATE_SIZE)])
    equations = []
    # Generate bit dependencies between all states
    total_equations = 0
    for state_bits in known_states_bits:
        s0, s1 = xs128(s0, s1)
        # For each known bit, we generate a new equation
        for i, bit in enumerate(state_bits):
            if bit is not None:
                total_equations += 1
                coefficients = s0.to_coeff(i)
                equations.append(StateEquation(coefficients, bit))
        if total_equations > MAX_EQUATIONS:
            total_equations = MAX_EQUATIONS
            equations = equations[:MAX_EQUATIONS]
            logger.debug(f'Total number of equations in linear system reduced to {MAX_EQUATIONS}')
            break
    logger.debug(f'Total number of equations in linear system: {total_equations}')
    if total_equations < 110:
        logger.error(f'Number of equations is too small and will generate too many possible seeds')
    elif total_equations < 140:
        logger.warning(f'Number of equations is small and will generate a lot of possible seeds')
    # Solve the linear system of equations to find all possible seeds
    seeds = solve_linear_system(equations)
    for seed in seeds:
        seed0 = seed & ((1 << HALF_STATE_SIZE) - 1)
        seed1 = seed >> HALF_STATE_SIZE
        yield seed0, seed1

