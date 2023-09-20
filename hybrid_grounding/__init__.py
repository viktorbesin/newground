import sys
import argparse

from .hybrid_grounding import HybridGrounding
from .default_output_printer import DefaultOutputPrinter
from .aggregate_transformer import AggregateMode
from .cyclic_strategy import CyclicStrategy
from .grounding_modes import GroundingModes

def main():

    cyclic_choices = {
        "TIGHT":{"cmd_line": "assume-tight", "enum_mode": CyclicStrategy.ASSUME_TIGHT},
        "LVL-MAP":{"cmd_line": "level-mappings", "enum_mode": CyclicStrategy.LEVEL_MAPPING},
        "SCBP":{"cmd_line": "shared-cycle-body-predicates", "enum_mode": CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES},
        "LVL-MAP-AAAI":{"cmd_line": "level-mappings-AAAI", "enum_mode": CyclicStrategy.LEVEL_MAPPING_AAAI}
    }

    aggregate_choices = {
        "RA":{"cmd_line":"RA","enum_mode":AggregateMode.RA},
        "RS":{"cmd_line":"RS","enum_mode":AggregateMode.RS},
        "RS_PLUS":{"cmd_line":"RS-PLUS","enum_mode":AggregateMode.RS_PLUS},
        "RS_STAR":{"cmd_line":"RS-STAR","enum_mode":AggregateMode.RS_STAR},
        "RECURSIVE":{"cmd_line":"RECURSIVE","enum_mode":AggregateMode.RECURSIVE},
    }

    grounding_modes_choices = {
        "PAR":{"cmd_line":"rewrite-aggregates-ground-partly", "enum_mode":GroundingModes.RewriteAggregatesGroundPartly},
        "AGG":{"cmd_line":"rewrite-aggregates-no-ground", "enum_mode":GroundingModes.RewriteAggregatesNoGround},
        "FUL":{"cmd_line":"rewrite-aggregates-ground-fully", "enum_mode":GroundingModes.RewriteAggregatesGroundFully},
    }

    parser = argparse.ArgumentParser(prog='hybrid_grounding', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--mode', default=GroundingModes.RewriteAggregatesGroundPartly, choices=[grounding_modes_choices[key]["cmd_line"] for key in grounding_modes_choices.keys()])
    parser.add_argument('--aggregate-strategy', default=aggregate_choices["RA"]["cmd_line"], choices=[aggregate_choices[key]["cmd_line"] for key in aggregate_choices.keys()])
    parser.add_argument('--cyclic-strategy', default=cyclic_choices["TIGHT"]["cmd_line"], choices=[cyclic_choices[key]["cmd_line"] for key in cyclic_choices.keys()])
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

    grounding_mode = None
    for key in grounding_modes_choices.keys():
        if args.mode == grounding_modes_choices[key]["cmd_line"]:
            grounding_mode = grounding_modes_choices[key]["enum_mode"]

    if grounding_mode and grounding_mode == GroundingModes.RewriteAggregatesGroundFully:
        ground = True
        ground_guess = True

    aggregate_strategy = None
    for key in aggregate_choices.keys():
        if args.aggregate_strategy == aggregate_choices[key]["cmd_line"]:
            aggregate_strategy = aggregate_choices[key]["enum_mode"]

    normal_strategy = None
    for key in cyclic_choices.keys():
        if args.cyclic_strategy == cyclic_choices[key]["cmd_line"]:
            normal_strategy = cyclic_choices[key]["enum_mode"]

    contents = ""
    for f in args.files:
        contents += f.read()

    hybrid_grounding = HybridGrounding(sys.argv[0], no_show=no_show, ground_guess = ground_guess, ground = ground, output_printer = DefaultOutputPrinter(), aggregate_mode = aggregate_strategy, cyclic_strategy = normal_strategy, grounding_mode = grounding_mode)
    hybrid_grounding.start(contents)



