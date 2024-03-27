import argparse
import ast
import logging
import math
import sys

from .mathrandomcrack import *

def parse_args():
    parser = argparse.ArgumentParser(
            prog = 'python3 -m mathrandomcrack',
            description ='A tool to recover the internal state of the V8 implementation of Math.random() ' \
                    'and predict previous and next values of Math.random() calls',
            epilog = 'Example usages:\n' \
                    '  python3 -m mathrandomcrack --method doubles --next 10 ./samples/doubles.txt\n' \
                    '  python3 -m mathrandomcrack --method scaled --next 5 --previous 5 --factor 36 --output-fmt scaled ./samples/scaled_values.txt\n'\
                    '  python3 -m mathrandomcrack --method bounds --next 10 ./samples/bounds.txt --debug\n',
                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--method', required=True, choices=['doubles', 'scaled', 'bounds'],
            help='the kind of leaked values to use to recover possible Math.random() states\n'\
                 '"doubles": one output of Math.random() per line (between 0.0 and 1.0)\n'\
                 '"scaled": one output of Math.floor(Math.random() * factor + translation) per line\n'\
                 '"bounds": one pair of space-separated min / max bounds of Math.random() outputs per line')
    parser.add_argument('--factor', default=1, type=int,
            help='the factor to use for method / output_fmt "scaled"')
    parser.add_argument('--translation', default=0, type=int,
            help='the translation to use for method / output_fmt "scaled"')
    parser.add_argument('--next', default=10, type=int,
            help='how many next Math.random() outputs to predict')
    parser.add_argument('--previous', default=0, type=int,
            help='how many previous Math.random() outputs to predict')
    parser.add_argument('--output-fmt', default='doubles', choices=['doubles', 'scaled'],
            help='the format of the predicted values\n'\
                 '"doubles" (default): a list of doubles\n'\
                 '"scaled": a list of integers generated with Math.floor(Math.random() * factor + translation')
    parser.add_argument('--debug', action='store_true',
            help='raise log level')
    parser.add_argument('file',
            help='the file containing the random leaked values')
    args = parser.parse_args()

    if args.method == 'scaled' and args.factor < 2:
        raise ValueError(f'--factor should be specified and larger than 1 when using method "scaled"')

    return args

def parse_file(filename, method):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            if method == 'doubles':
                d = ast.literal_eval(line)
                assert type(d) in [int, float] and d >= 0.0 and d <= 1.0
                data.append(d)
            elif method == 'scaled':
                i = ast.literal_eval(line)
                assert type(i) is int and i >= 0 and i <= pow(2, 64) - 1
                data.append(i)
            elif method == 'bounds':
                splitted = line.split(' ')
                bounds = [ast.literal_eval(s) for s in splitted]
                assert len(bounds) == 2 and all(type(b) in [int, float] and b >= 0 and b <= 1.0 for b in bounds)
                data.append(bounds)
            else:
                raise NotImplementedError(f'Unsupported method "{method}"')
    return data

def recover_all_states(data, args):
    if args.method == 'doubles':
        return recover_state_from_math_random_doubles(data)
    elif args.method == 'scaled':
        return recover_state_from_math_random_scaled_values(data, args.factor, args.translation)
    elif args.method == 'bounds':
        return recover_state_from_math_random_approximate_values(data)
    else:
        raise NotImplementedError(f'Unsupported method "{method}"')

def format_random(value, args):
    if args.output_fmt == 'doubles':
        return value
    elif args.output_fmt == 'scaled':
        return math.floor(value * args.factor + args.translation)
    else:
        raise NotImplementedError(f'Unsupported output_fmt "{method}"')

if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.debug else logging.INFO)
    data = parse_file(args.file, args.method)

    found = False
    for state in recover_all_states(data, args):
        found = True
        print('Found a possible Math.random internal state')
        if args.previous > 0:
            print(f'Predicted previous {args.previous} values:',
                    [format_random(state.previous(), args) for _ in range(args.previous)][::-1])
            [state.next() for _ in range(args.previous)] # Return to initial state
        if args.next > 0:
            [state.next() for _ in data] # Skip known values
            print(f'Predicted next {args.next} values:',
                    [format_random(state.next(), args) for _ in range(args.next)])
        print()

    if not found:
        print("Couldn't recover any possible Math.random internal state. Please check your values file.")

