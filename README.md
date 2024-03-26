# mathrandomcrack

Cracking JavaScript V8 `Math.random()` and xs128 from arbitrary bit leaks.

This is largely inspired by https://imp.ress.me/blog/2023-04-17/plaidctf-2023#fastrology.

*Disclaimer: This tool is made for educational purposes only. Please don't use it to break into stuff.*

## What is this?

This tool can be used to recover the internal state of the V8 implementation of `Math.random()` knowing enough bits of randomly generated values. The values don't have to be successive and the position of the known bits can vary.

For example, you can use this tool to recover all the possibles internal states of `Math.random()` in one of the following situations:

- You know 4 values generated by `Math.random()`.
- You know *enough* integer values generated by `Math.floor(Math.random() * k + b)`.
- You know *enough* approximate values generated by `Math.random()`.

After the internal state is recovered, this tool is also able to predict all the next and previous (#TODO) returned values of `Math.random()`.

## How do I protect my applications against this?

Never use `Math.random()` for anything related to security. If someone recovering randomly generated values is bad for your application, use the cryptographically secure [Crypto.getRandomValues()](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues) method instead.

## I just want to run it

You should have Python3 and [Sage](https://doc.sagemath.org/html/en/installation/index.html) installed.

#TODO CLI coming soon, meanwhile you can check examples in the `tests/` folder.

## I have a more complex use case

If you manage to extract some bits of multiple `Math.random()` outputs, you can directly use the `recover_state_from_math_random_known_bits` function in `mathrandomcrack.py` to recover the initial internal state of `Math.random()`.

## How does it work?

`Math.random()` is defined as a function that returns pseudo-random numbers between 0 and 1 and does not provide cryptographically secure random numbers. Under the hood, in V8 (the JavaScript engine used by Chrome and NodeJS), random numbers are generated using the fast, reversible, seed-based, deterministic PRNG called [XorShift128](https://github.com/v8/v8/blob/12.5.66/src/base/utils/random-number-generator.h#L119).

### Cracking XorShift128 initial state

XorShift128 is a simple PRNG with a 128-bit internal state. It uses only XOR and shift operations and the transition from a state to the next is linear. Each bit of a XorShift128 state can be expressed as a linear combination of pre-determined bits of the initial state. Knowing enough total bits from arbitrary states, the initial state can be recovered through basic linear algebra in GF(2).

Initial XorShift128 state recovery from known bits is implemented in `xs128crack.py`.

*Note: many other projects like [v8_rand_buster](https://github.com/d0nutptr/v8_rand_buster/tree/master) use symbolic execution with z3 to recover the initial state but this is not viable if your known bits are scattered over too many states.*

### Recovering Math.random() internal state

`Math.random()` doesn't directly output XorShift128 random values. It generates [a cache](https://github.com/v8/v8/blob/12.5.66/src/numbers/math-random.cc#L35) of 64 values at a time and returns them one by one in reverse order. This makes the internal state recovery a little tricky because we have to account for the initial position of the cache index for the first known state. If only a few outputs are known (< 64), there will be up to 64 possible internal states due to the unknown position of the cache index.

Internal state recovery is implemented in `mathrandomcrack.py`.

## Tests

You can run the tests to make sure everything works using [unittest](https://docs.python.org/3/library/unittest.html).

```console
$ python3 -m unittest discover -s tests
```

## References

- https://blog.securityevaluators.com/hacking-the-javascript-lottery-80cc437e3b7f - "Hacking the JavaScript Lottery" article from 2016.
- https://security.stackexchange.com/a/123554 - "Predicting Math.random() numbers?" question on StackExchange.
- https://github.com/d0nutptr/v8_rand_buster/tree/master - Another implementation to crack XorShift128 using z3.
- https://imp.ress.me/blog/2023-04-17/plaidctf-2023#fastrology - The writeups of 2023 PlaidCTF challenges by @y4n that inspired me to make this tool.
