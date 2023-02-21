import sys
import argparse


from newground.newground import Newground
from newground.default_output_printer import DefaultOutputPrinter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='newground', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--ground', action='store_true',
                        help='Output program fully grounded. ')
    parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()
    # no output from clingo itself
    #sys.argv.append("--outf=3")
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


    contents = ""
    for f in sys.argv[1:]:
        contents += open(f, "r").read()

    #clingo.clingo_main(ClingoApp(sys.argv[0], no_show, ground_guess, ground), sys.argv[1:])

    newground = Newground(sys.argv[0], no_show=no_show, ground_guess = ground_guess, ground = ground, output_printer = DefaultOutputPrinter())
    newground.start(contents)


