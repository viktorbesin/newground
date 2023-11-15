# pylint: disable=W0108
"""
Main module.
Contains the Newground class,
which is used for the tranformations.
"""

import networkx as nx
from clingo.ast import ProgramBuilder, parse_string
from clingo.control import Control

from .aggregate_strategies.aggregate_mode import AggregateMode
from .aggregate_transformer import AggregateTransformer
from .cyclic_strategy import CyclicStrategy
from .domain_transformer import DomainTransformer
from .grounding_modes import GroundingModes
from .main_transformer import MainTransformer
from .main_transformer_helpers.level_mappings_part import LevelMappingsPart
from .term_transformer import TermTransformer


class Newground:
    """
    Main module.
    Contains the Newground class,
    which is used for the tranformations.
    """

    def __init__(
        self,
        no_show=False,
        ground_guess=False,
        output_printer=None,
        aggregate_mode=AggregateMode.RA,
        cyclic_strategy=CyclicStrategy.ASSUME_TIGHT,
        grounding_mode=GroundingModes.REWRITE_AGGREGATES_GROUND_PARTLY,
    ):
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.output_printer = output_printer

        self.aggregate_mode = aggregate_mode
        self.cyclic_strategy = cyclic_strategy

        self.rules = False
        self.grounding_mode = grounding_mode

        if self.grounding_mode == GroundingModes.REWRITE_AGGREGATES_GROUND_FULLY:
            self.ground_guess = True

    def start(self, contents):
        """
        Start method of the Newground.
        Call this method to start the rewriting procedure.
        """
        (
            domain,
            safe_variables,
            term_transformer,
            rule_strongly_connected_comps,
            predicates_strongly_connected_comps,
            rule_strongly_connected_comps_heads,
            scc_rule_functions_scc_lookup,
        ) = self.start_domain_inference(contents)

        if "0_terms" not in domain and len(domain.keys()) > 0:
            # No domain could be inferred, therefore return nothing.
            return

        aggregate_transformer_output_program = self.start_aggregate_transformer(
            contents, domain
        )

        if self.grounding_mode == GroundingModes.REWRITE_AGGREGATES_NO_GROUND:
            # Only rewrite
            self.output_printer.custom_print(aggregate_transformer_output_program)
        else:
            # Rewrite and ground
            self.start_main_transformation(
                aggregate_transformer_output_program,
                domain,
                safe_variables,
                term_transformer,
                rule_strongly_connected_comps,
                predicates_strongly_connected_comps,
                rule_strongly_connected_comps_heads,
                scc_rule_functions_scc_lookup,
            )

    def start_aggregate_transformer(self, contents, domain):
        """
        Starts the aggregate transformer.
        """
        aggregate_transformer = AggregateTransformer(
            self.aggregate_mode, domain, self.grounding_mode
        )
        parse_string(contents, lambda stm: aggregate_transformer(stm))

        shown_predicates = list(set(aggregate_transformer.shown_predicates))
        program_string = "\n".join(shown_predicates + aggregate_transformer.new_prg)

        return program_string

    def start_domain_inference(self, combined_inputs):
        """
        Starts the domain inference in general.
        It calls the term- and domain-transformers.
        It is the first general procedure which is called.
        """
        term_transformer = TermTransformer(self.output_printer, self.no_show)
        parse_string(combined_inputs, lambda stm: term_transformer(stm))

        safe_variables = term_transformer.safe_variable_rules
        domain = term_transformer.domain

        comparisons = term_transformer.comparison_operators_variables

        (
            predicates_strongly_connected_comps,
            rule_strongly_connected_comps,
            rule_head_strongly_connected_comps,
            scc_rule_functions_scc_lookup,
        ) = self.compute_scc_data_structures(term_transformer)

        new_domain_hash = hash(str(domain))
        old_domain_hash = None

        while new_domain_hash != old_domain_hash:
            old_domain_hash = new_domain_hash

            domain_transformer = DomainTransformer(safe_variables, domain, comparisons)
            parse_string(combined_inputs, lambda stm: domain_transformer(stm))

            safe_variables = domain_transformer.safe_variables_rules
            domain = domain_transformer.domain

            new_domain_hash = hash(str(domain))

        return (
            domain,
            safe_variables,
            term_transformer,
            rule_strongly_connected_comps,
            predicates_strongly_connected_comps,
            rule_head_strongly_connected_comps,
            scc_rule_functions_scc_lookup,
        )

    def start_main_transformation(
        self,
        aggregate_transformer_output_program,
        domain,
        safe_variables,
        term_transformer,
        rule_strongly_connected_comps,
        predicates_strongly_connected_comps,
        rule_strongly_connected_comps_heads,
        scc_rule_functions_scc_lookup,
    ):
        """
        Wrapper for calling the main transformer.
        """
        ctl = Control()
        with ProgramBuilder(ctl) as program_builder:
            transformer = MainTransformer(
                term_transformer.terms,
                term_transformer.facts,
                term_transformer.ng_heads,
                term_transformer.shown_predicates,
                self.ground_guess,
                self.output_printer,
                domain,
                safe_variables,
                self.aggregate_mode,
                rule_strongly_connected_comps,
                self.cyclic_strategy,
                rule_strongly_connected_comps_heads,
                predicates_strongly_connected_comps,
                scc_rule_functions_scc_lookup,
            )

            parse_string(
                aggregate_transformer_output_program,
                lambda stm: program_builder.add(transformer(stm)),
            )

            level_mappings_part = LevelMappingsPart(
                self.output_printer,
                domain,
                predicates_strongly_connected_comps,
                self.ground_guess,
                self.cyclic_strategy,
                scc_rule_functions_scc_lookup,
            )
            level_mappings_part.generate_level_mappings()

            if (
                len(transformer.non_ground_rules.keys()) > 0
                or len(transformer.shown_predicates.keys()) > 0
            ):
                self.global_main_transformations(
                    program_builder, transformer, term_transformer
                )

    def global_main_transformations(
        self, program_builder, transformer, term_transformer
    ):
        """
        Global main transformations, like adding '':- not sat.'', and similar.
        """

        self._add_global_sat_statements(program_builder, transformer)
        self._add_global_foundedness_statements(transformer)

        if not self.ground_guess:
            for t in transformer.terms:
                self.output_printer.custom_print(f"dom({t}).")

        if not self.no_show:
            if not term_transformer.show:
                for f in transformer.shown_predicates.keys():
                    for l in transformer.shown_predicates[f]:
                        self.output_printer.custom_print(f"#show {f}/{l}.")

    def _add_global_foundedness_statements(self, transformer):
        additional_foundedness_set = set(transformer.additional_foundedness_part)
        for additional_rule in additional_foundedness_set:
            self.output_printer.custom_print(additional_rule)

        for key in transformer.unfounded_rules.keys():
            unfounded_rules_heads = transformer.unfounded_rules[key]

            sum_strings = []

            for rule_key in unfounded_rules_heads.keys():
                unfounded_rules_list = unfounded_rules_heads[rule_key]
                unfounded_rules_list = list(
                    set(unfounded_rules_list)
                )  # Remove duplicates

                sum_list = []
                for index in range(len(unfounded_rules_list)):
                    unfounded_rule = unfounded_rules_list[index]
                    sum_list.append(f"1,{index} : {unfounded_rule}")

                sum_strings.append(f"#sum{{{'; '.join(sum_list)}}} >=1 ")

            self.output_printer.custom_print(f":- {key}, {','.join(sum_strings)}.")

    def _add_global_sat_statements(self, program_builder, transformer):
        parse_string(":- not sat.", lambda stm: program_builder.add(stm))
        self.output_printer.custom_print(":- not sat.")

        sat_strings = []
        non_ground_rules = transformer.non_ground_rules
        for non_ground_rule_key in non_ground_rules.keys():
            sat_strings.append(f"sat_r{non_ground_rule_key}")

        if len(sat_strings) > 0:
            self.output_printer.custom_print(f"sat :- {','.join(sat_strings)}.")
        else:
            self.output_printer.custom_print("sat.")

    def compute_scc_data_structures(self, term_transformer):
        """
        Important for non-tight ASP.
        This method computes the strongly-connected-components,
        and then prepares the necessary data-structures.
        """
        strongly_connected_comps = []

        for c in sorted(
            nx.strongly_connected_components(term_transformer.dependency_graph),
            key=len,
            reverse=True,
        ):
            strongly_connected_comps.append(c)

        strongly_connected_comps_counter = 0
        predicates_strongly_connected_comps = {}
        rule_strongly_connected_comps = {}
        rule_head_strongly_connected_comps = {}
        scc_rule_functions_scc_lookup = {}

        for strongly_connected_comp in strongly_connected_comps:
            if len(strongly_connected_comp) > 1:
                self.handle_strongly_connected_component(
                    term_transformer,
                    strongly_connected_comps_counter,
                    predicates_strongly_connected_comps,
                    rule_strongly_connected_comps,
                    rule_head_strongly_connected_comps,
                    scc_rule_functions_scc_lookup,
                    strongly_connected_comp,
                )

            strongly_connected_comps_counter += 1

        return (
            predicates_strongly_connected_comps,
            rule_strongly_connected_comps,
            rule_head_strongly_connected_comps,
            scc_rule_functions_scc_lookup,
        )

    def handle_strongly_connected_component(
        self,
        term_transformer,
        strongly_connected_comps_counter,
        predicates_strongly_connected_comps,
        rule_strongly_connected_comps,
        rule_head_strongly_connected_comps,
        scc_rule_functions_scc_lookup,
        strongly_connected_comp,
    ):
        """
        Handle a single strongly-connected-component.
        """
        occurs_in_pi_t = False
        for node in strongly_connected_comp:
            string_node = list(
                term_transformer.dependency_graph_rule_node_lookup.keys()
            )[
                list(term_transformer.dependency_graph_rule_node_lookup.values()).index(
                    node
                )
            ]
            occuring_in = term_transformer.dependency_graph_node_rules_part_lookup[
                string_node
            ]
            if False in occuring_in:
                pass
            if True in occuring_in:
                occurs_in_pi_t = True

        if not occurs_in_pi_t:
            return

        predicates_strongly_connected_comps[strongly_connected_comps_counter] = []

        for node in strongly_connected_comp:
            self.scc_extract_relevant_bodies(
                term_transformer,
                strongly_connected_comps_counter,
                predicates_strongly_connected_comps,
                rule_strongly_connected_comps,
                scc_rule_functions_scc_lookup,
                strongly_connected_comp,
                node,
            )
            self.scc_extract_relevant_heads(
                term_transformer,
                strongly_connected_comps_counter,
                rule_head_strongly_connected_comps,
                scc_rule_functions_scc_lookup,
                strongly_connected_comp,
                node,
            )

    def scc_extract_relevant_heads(
        self,
        term_transformer,
        strongly_connected_comps_counter,
        rule_head_strongly_connected_comps,
        scc_rule_functions_scc_lookup,
        strongly_connected_comp,
        node,
    ):
        """
        Necessary method for SCCs for extracting relevant heads.
        """
        for rule in term_transformer.dependency_graph_node_rule_heads_lookup[
            node
        ].keys():
            if rule in term_transformer.rules_functions_lookup:
                functions_rule = term_transformer.rules_functions_lookup[rule]

                relevant_heads = []
                relevant_bodies = []

                head_functions_rule = functions_rule["head"]
                for head_function in head_functions_rule:
                    # head_counter = self.dependency_graph_rule_node_lookup[str(rule.head)]
                    if (
                        str(head_function.name)
                        in term_transformer.dependency_graph_rule_node_lookup
                    ):
                        looked_up_value = (
                            term_transformer.dependency_graph_rule_node_lookup[
                                head_function.name
                            ]
                        )

                        if looked_up_value in strongly_connected_comp:
                            relevant_heads.append(head_function)

                body_functions_rule = functions_rule["body"]
                for body_function in body_functions_rule:
                    # head_counter = self.dependency_graph_rule_node_lookup[str(rule.head)]
                    if (
                        str(body_function.name)
                        in term_transformer.dependency_graph_rule_node_lookup
                    ):
                        looked_up_value = (
                            term_transformer.dependency_graph_rule_node_lookup[
                                body_function.name
                            ]
                        )

                        if looked_up_value in strongly_connected_comp:
                            relevant_bodies.append(body_function)

                if len(relevant_bodies) == 0 or len(relevant_heads) == 0:
                    continue

                scc_rule_functions_scc_lookup[rule] = {
                    "body": relevant_bodies,
                    "head": relevant_heads,
                    "scc": strongly_connected_comp,
                    "scc_key": strongly_connected_comps_counter,
                }

                if rule not in rule_head_strongly_connected_comps:
                    rule_head_strongly_connected_comps[rule] = []

                rule_head_strongly_connected_comps[rule] += relevant_heads

    def scc_extract_relevant_bodies(
        self,
        term_transformer,
        strongly_connected_comps_counter,
        predicates_strongly_connected_comps,
        rule_strongly_connected_comps,
        scc_rule_functions_scc_lookup,
        strongly_connected_comp,
        node,
    ):
        """
        Necessary method for SCC for extracting bodies.
        """
        for rule in term_transformer.dependency_graph_node_rule_heads_lookup[
            node
        ].keys():
            if rule in term_transformer.rules_functions_lookup:
                functions_rule = term_transformer.rules_functions_lookup[rule]

                relevant_heads = []
                relevant_bodies = []

                head_functions_rule = functions_rule["head"]
                for head_function in head_functions_rule:
                    # head_counter = self.dependency_graph_rule_node_lookup[str(rule.head)]
                    if (
                        str(head_function.name)
                        in term_transformer.dependency_graph_rule_node_lookup
                    ):
                        looked_up_value = (
                            term_transformer.dependency_graph_rule_node_lookup[
                                head_function.name
                            ]
                        )

                        if looked_up_value in strongly_connected_comp:
                            relevant_heads.append(head_function)

                body_functions_rule = functions_rule["body"]
                for body_function in body_functions_rule:
                    # head_counter = self.dependency_graph_rule_node_lookup[str(rule.head)]
                    if (
                        str(body_function.name)
                        in term_transformer.dependency_graph_rule_node_lookup
                    ):
                        looked_up_value = (
                            term_transformer.dependency_graph_rule_node_lookup[
                                body_function.name
                            ]
                        )

                        if looked_up_value in strongly_connected_comp:
                            relevant_bodies.append(body_function)

                if len(relevant_bodies) == 0 or len(relevant_heads) == 0:
                    continue

                scc_rule_functions_scc_lookup[rule] = {
                    "body": relevant_bodies,
                    "head": relevant_heads,
                    "scc": strongly_connected_comp,
                    "scc_key": strongly_connected_comps_counter,
                }

                if rule not in rule_strongly_connected_comps:
                    rule_strongly_connected_comps[rule] = []

                rule_strongly_connected_comps[rule] += relevant_bodies
                predicates_strongly_connected_comps[
                    strongly_connected_comps_counter
                ] += relevant_bodies
