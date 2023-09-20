from clingo.ast import parse_string, ProgramBuilder

from clingo.control import Control

from .aggregate_transformer import AggregateTransformer
from .aggregate_strategies.aggregate_mode import AggregateMode
from .term_transformer import TermTransformer
from .domain_transformer import DomainTransformer
from .main_transformer import MainTransformer
from .cyclic_strategy import CyclicStrategy

from .main_transformer_helpers.level_mappings_part import LevelMappingsPart
from .grounding_modes import GroundingModes

import matplotlib as plt
import networkx as nx

class HybridGrounding:

    def __init__(self, name="", no_show=False, ground_guess=False, ground=False, output_printer = None, aggregate_mode = AggregateMode.RA, cyclic_strategy = CyclicStrategy.ASSUME_TIGHT, grounding_mode = GroundingModes.RewriteAggregatesGroundPartly):
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground
        self.output_printer = output_printer

        self.aggregate_mode = aggregate_mode
        self.cyclic_strategy = cyclic_strategy

        self.rules = False
        self.grounding_mode = grounding_mode

    def start(self, contents):

        domain, safe_variables, term_transformer, rule_strongly_connected_comps, predicates_strongly_connected_comps, rule_strongly_connected_comps_heads  = self.start_domain_inference(contents)

        if "0_terms" not in domain:
            # No domain could be inferred, therefore return nothing.
            return

        aggregate_transformer_output_program = self.start_aggregate_transformer(contents, domain)

        if self.grounding_mode == GroundingModes.RewriteAggregatesNoGround:
            # Only rewrite
            self.output_printer.custom_print(aggregate_transformer_output_program)
        else:
            # Rewrite and ground
            self.start_main_transformation(aggregate_transformer_output_program, domain, safe_variables, term_transformer, rule_strongly_connected_comps, predicates_strongly_connected_comps, rule_strongly_connected_comps_heads)

    def start_aggregate_transformer(self, contents, domain):
 
        aggregate_transformer = AggregateTransformer(self.aggregate_mode, domain, self.grounding_mode)
        parse_string(contents, lambda stm: aggregate_transformer(stm))

        shown_predicates = list(set(aggregate_transformer.shown_predicates))
        program_string = '\n'.join(shown_predicates + aggregate_transformer.new_prg)

        return program_string

    def start_domain_inference(self, combined_inputs):
        
        term_transformer = TermTransformer(self.output_printer, self.no_show)
        parse_string(combined_inputs, lambda stm: term_transformer(stm))

        safe_variables = term_transformer.safe_variable_rules
        domain = term_transformer.domain

        comparisons = term_transformer.comparison_operators_variables
    
        strongly_connected_comps = [c for c in sorted(nx.strongly_connected_components(term_transformer.dependency_graph), key=len, reverse=True)]

        strongly_connected_comps_counter = 0
        predicates_strongly_connected_comps = {}
        rule_strongly_connected_comps = {}
        rule_head_strongly_connected_comps = {}

        for strongly_connected_comp in strongly_connected_comps:
            if len(strongly_connected_comp) > 1:
                
                occurs_in_pi_t = False
                occurs_in_pi_c = False
                for node in strongly_connected_comp:
                    string_node = list(term_transformer.dependency_graph_rule_node_lookup.keys())[list(term_transformer.dependency_graph_rule_node_lookup.values()).index(node)]
                    occuring_in = term_transformer.dependency_graph_node_rules_part_lookup[string_node]
                    if False in occuring_in:
                        occurs_in_pi_c = True
                    if True in occuring_in:
                        occurs_in_pi_t = True

                if not occurs_in_pi_t:
                    continue

                predicates_strongly_connected_comps[strongly_connected_comps_counter] = []

                for node in strongly_connected_comp:
                    for rule in term_transformer.dependency_graph_node_rule_bodies_lookup[node].keys():
                        if rule not in rule_strongly_connected_comps:
                            rule_strongly_connected_comps[rule] = []

                        rule_strongly_connected_comps[rule] += term_transformer.dependency_graph_node_rule_bodies_lookup[node][rule]

                        predicates_strongly_connected_comps[strongly_connected_comps_counter] += term_transformer.dependency_graph_node_rule_bodies_lookup[node][rule]

                    for rule in term_transformer.dependency_graph_node_rule_heads_lookup[node].keys():
                        if rule not in rule_head_strongly_connected_comps:
                            rule_head_strongly_connected_comps[rule] = []

                        rule_head_strongly_connected_comps[rule] += term_transformer.dependency_graph_node_rule_heads_lookup[node][rule]


                strongly_connected_comps_counter += 1

        new_domain_hash = hash(str(domain))
        old_domain_hash = None
    
        while new_domain_hash != old_domain_hash:
        
            old_domain_hash = new_domain_hash

            domain_transformer = DomainTransformer(safe_variables, domain, comparisons)
            parse_string(combined_inputs, lambda stm: domain_transformer(stm))       

            safe_variables = domain_transformer.safe_variables_rules
            domain = domain_transformer.domain


            new_domain_hash = hash(str(domain))

        return (domain, safe_variables, term_transformer, rule_strongly_connected_comps, predicates_strongly_connected_comps, rule_head_strongly_connected_comps)
       

    def start_main_transformation(self, aggregate_transformer_output_program, domain, safe_variables, term_transformer, rule_strongly_connected_comps, predicates_strongly_connected_comps, rule_strongly_connected_comps_heads):

        ctl = Control()
        with ProgramBuilder(ctl) as program_builder:
            transformer = MainTransformer(program_builder, term_transformer.terms, term_transformer.facts,
                                          term_transformer.ng_heads, term_transformer.shows,
                                          self.ground_guess, self.ground, self.output_printer,
                                          domain, safe_variables, self.aggregate_mode,
                                          rule_strongly_connected_comps,
                                          self.cyclic_strategy,
                                          rule_strongly_connected_comps_heads,
                                          predicates_strongly_connected_comps
                                          )

            parse_string(aggregate_transformer_output_program, lambda stm: program_builder.add(transformer(stm)))

            level_mappings_part = LevelMappingsPart(self.output_printer, domain, predicates_strongly_connected_comps, self.ground_guess, self.cyclic_strategy)
            level_mappings_part.generate_level_mappings()

            if len(transformer.non_ground_rules.keys()) > 0:


                self.global_main_transformations(program_builder, transformer, term_transformer)




    def global_main_transformations(self, program_builder, transformer, term_transformer):



        parse_string(":- not sat.", lambda stm: program_builder.add(stm))
        self.output_printer.custom_print(":- not sat.")

        sat_strings = []
        non_ground_rules = transformer.non_ground_rules
        for non_ground_rule_key in non_ground_rules.keys():
            sat_strings.append(f"sat_r{non_ground_rule_key}")


        self.output_printer.custom_print(f"sat :- {','.join(sat_strings)}.")

        additional_foundedness_set = set(transformer.additional_foundedness_part)
        for additional_rule in additional_foundedness_set:
            self.output_printer.custom_print(additional_rule)

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



