import sys
import argparse

from .newground import Newground
from .default_output_printer import DefaultOutputPrinter
from .aggregate_transformer import AggregateMode

def main():
    parser = argparse.ArgumentParser(prog='newground', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--ground', action='store_true',
                        help='Output program fully grounded. ')
    parser.add_argument('--aggregate-strategy', default='replace', choices=['replace','rewrite','rewrite-no-body'])
    parser.add_argument('files', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()

    no_show = False
    ground_guess = False
    ground = False
    if args.no_show:
        sys.argv.remove('--no-show')
        no_show = True
    if args.ground_guess:
        sys.argv.remove('--ground-guess')
        ground_guess = True
    if args.ground:
        sys.argv.remove('--ground')
        ground_guess = True
        ground = True

    aggregate_strategy = None
    if args.aggregate_strategy == 'replace':
        aggregate_strategy = AggregateMode.REPLACE
    elif args.aggregate_strategy == 'rewrite':
        aggregate_strategy = AggregateMode.REWRITING
    elif args.aggregate_strategy == 'rewrite-no-body':
        aggregate_strategy = AggregateMode.REWRITING_NO_BODY

    contents = ""
    for f in args.files:
        contents += f.read()

    newground = Newground(sys.argv[0], no_show=no_show, ground_guess = ground_guess, ground = ground, output_printer = DefaultOutputPrinter(), aggregate_strategy = aggregate_strategy)
    newground.start(contents)



