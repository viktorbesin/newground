import sys
import argparse

from .hybrid_grounding import HybridGrounding
from .default_output_printer import DefaultOutputPrinter
from .aggregate_transformer import AggregateMode
from .cyclic_strategy import CyclicStrategy

def main():
    choice_tight = "assume-tight"
    choice_level_mappings = "level-mappings"
    choice_shared_cycle_body_predicates = "shared-cycle-body-predicates"

    aggregate_choices = {
        "RA":{"cmd_line":"RA","enum_mode":AggregateMode.RA},
        "RS":{"cmd_line":"RS","enum_mode":AggregateMode.RS},
        "RS_PLUS":{"cmd_line":"RS-PLUS","enum_mode":AggregateMode.RS_PLUS},
        "RS_STAR":{"cmd_line":"RS-STAR","enum_mode":AggregateMode.RS_STAR},
        "RECURSIVE":{"cmd_line":"RECURSIVE","enum_mode":AggregateMode.RECURSIVE},
    }



    parser = argparse.ArgumentParser(prog='hybrid_grounding', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--ground', action='store_true',
                        help='Output program fully grounded. ')
    parser.add_argument('--aggregate-strategy', default=aggregate_choices["RA"]["cmd_line"], choices=[aggregate_choices[key]["cmd_line"] for key in aggregate_choices.keys()])
    parser.add_argument('--cyclic-strategy', default=choice_tight, choices=[choice_tight, choice_level_mappings, choice_shared_cycle_body_predicates])
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
    for key in aggregate_choices.keys():
        if args.aggregate_strategy == aggregate_choices[key]["cmd_line"]:
            aggregate_strategy = aggregate_choices[key]["enum_mode"]
    
    normal_strategy = None
    if args.cyclic_strategy == choice_tight:
        normal_strategy = CyclicStrategy.ASSUME_TIGHT
    elif args.cyclic_strategy == choice_level_mappings:
        normal_strategy = CyclicStrategy.LEVEL_MAPPING
    elif args.cyclic_strategy == choice_shared_cycle_body_predicates:
        normal_strategy = CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES

    contents = ""
    for f in args.files:
        contents += f.read()

    hybrid_grounding = HybridGrounding(sys.argv[0], no_show=no_show, ground_guess = ground_guess, ground = ground, output_printer = DefaultOutputPrinter(), aggregate_mode = aggregate_strategy, cyclic_strategy = normal_strategy)
    hybrid_grounding.start(contents)



