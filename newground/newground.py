#import os 


import clingo
from clingo.ast import Transformer, Variable, parse_string, ProgramBuilder

from clingo.control import Control

from .aggregate_transformer import AggregateTransformer
from .term_transformer import TermTransformer
from .domain_transformer import DomainTransformer
from .main_transformer import MainTransformer

class Newground:

    def __init__(self, name="", no_show=False, ground_guess=False, ground=False, output_printer = None):
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground
        self.output_printer = output_printer
        
        self.rules = False

    def start(self, contents):

        aggregate_transformer = AggregateTransformer()
        parse_string(contents, lambda stm: aggregate_transformer(stm))

        shown_predicates = list(set(aggregate_transformer.shown_predicates))
        program_string = '\n'.join(shown_predicates + aggregate_transformer.new_prg)

        combined_inputs = program_string

        if self.ground:
            self.output_printer.custom_print(contents)

        term_transformer = TermTransformer(self.output_printer, self.no_show)
        parse_string(combined_inputs, lambda stm: term_transformer(stm))

        safe_variables = term_transformer.safe_variable_rules
        domain = term_transformer.domain

        comparisons = term_transformer.comparison_operators_variables

        new_domain_hash = hash(str(domain))
        old_domain_hash = None
    
        while new_domain_hash != old_domain_hash:
        
            old_domain_hash = new_domain_hash

            domain_transformer = DomainTransformer(safe_variables, domain, comparisons)
            parse_string(combined_inputs, lambda stm: domain_transformer(stm))       

            safe_variables = domain_transformer.safe_variables_rules
            domain = domain_transformer.domain


            new_domain_hash = hash(str(domain))

        ctl = Control()
        with ProgramBuilder(ctl) as bld:
            transformer = MainTransformer(bld, term_transformer.terms, term_transformer.facts, term_transformer.ng_heads, term_transformer.shows, self.ground_guess, self.ground, self.output_printer, domain, safe_variables)
            #parse_files(combined_inputs, lambda stm: bld.add(transformer(stm)))
            parse_string(combined_inputs, lambda stm: bld.add(transformer(stm)))
            if len(transformer.non_ground_rules.keys()) > 0:
                parse_string(":- not sat.", lambda stm: bld.add(stm))
                self.output_printer.custom_print(":- not sat.")

                sat_strings = []
                non_ground_rules = transformer.non_ground_rules
                for non_ground_rule_key in non_ground_rules.keys():
                    sat_strings.append(f"sat_r{non_ground_rule_key}")

    
                self.output_printer.custom_print(f"sat :- {','.join(sat_strings)}.")

                for key in transformer.unfounded_rules.keys():

                    unfounded_rules_heads = transformer.unfounded_rules[key]

                    sum_strings = []

                    for rule_key in unfounded_rules_heads.keys():

                        unfounded_rules_list = unfounded_rules_heads[rule_key]
                        unfounded_rules_list = list(set(unfounded_rules_list)) # Remove duplicates

                        sum_list = []
                        for index in range(len(unfounded_rules_list)):
                            unfounded_rule = unfounded_rules_list[index]
                            sum_list.append(f"1,{index} : {unfounded_rule}")

                        sum_strings.append(f"#sum{{{'; '.join(sum_list)}}} >=1 ")

                    
                    self.output_printer.custom_print(f":- {key}, {','.join(sum_strings)}.")
                

                if not self.ground_guess:
                    for t in transformer.terms:
                        self.output_printer.custom_print(f"dom({t}).")

                if not self.no_show:
                    if not term_transformer.show:
                        for f in transformer.shows.keys():
                            for l in transformer.shows[f]:
                                self.output_printer.custom_print(f"#show {f}/{l}.")



