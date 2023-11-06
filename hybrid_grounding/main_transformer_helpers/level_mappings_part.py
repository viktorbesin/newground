# pylint: disable=W0102,R1721,W0108
"""
Module for generating the level-mappings.
"""
import itertools

from clingo import Function

from ..cyclic_strategy import CyclicStrategy


class LevelMappingsPart:
    """
    Class for generating the level mappings.
    """

    def __init__(
        self,
        custom_printer,
        domain_lookup_dict,
        strongly_connected_components_predicates,
        ground_guess,
        cyclic_strategy,
        scc_rule_functions_scc_lookup,
    ):
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.strongly_connected_components_predicates = (
            strongly_connected_components_predicates
        )
        self.ground_guess = ground_guess
        self.cyclic_strategy = cyclic_strategy
        self.scc_rule_functions_scc_lookup = scc_rule_functions_scc_lookup

    def generate_level_mappings(self):
        """
        Method that generates the level mappings.
        """
        if self.cyclic_strategy in [
            CyclicStrategy.LEVEL_MAPPING,
            CyclicStrategy.LEVEL_MAPPING_AAAI,
        ]:
            generated_domains = {}

            scc_predicates_per_scc_key = {}
            for rule in self.scc_rule_functions_scc_lookup.keys():
                dic = self.scc_rule_functions_scc_lookup[rule]
                if dic["scc_key"] not in scc_predicates_per_scc_key:
                    scc_predicates_per_scc_key[dic["scc_key"]] = []

                scc_predicates_per_scc_key[dic["scc_key"]] += dic["body"]
                scc_predicates_per_scc_key[dic["scc_key"]] += dic["head"]

            # for scc_key in self.strongly_connected_components_predicates.keys():
            for scc_key in scc_predicates_per_scc_key.keys():
                scc = list(set(scc_predicates_per_scc_key[scc_key]))
                self._generate_level_mappings_scc(scc, generated_domains)

    def _generate_level_mappings_scc(self, scc, generated_domains):
        scc_ = {}
        for predicate in scc:
            scc_[predicate.name] = predicate
        scc = []
        for key in scc_.keys():
            scc.append(scc_[key])

        scc.sort(key=lambda element: str(element))

        new_scc = []
        for item in scc:
            head_name = item.name

            arguments = []
            for arg_index in range(len(item.arguments)):
                arguments.append(Function("X" + str(arg_index)))

            if len(arguments) > 0:
                new_scc.append(Function(name=head_name, arguments=arguments))
            else:
                new_scc.append(Function(name=head_name))

        scc = new_scc

        self._generate_precs(generated_domains, scc)
        self._generate_transitivities(generated_domains, scc)

    def _generate_transitivities(self, generated_domains, scc):
        # Create rules (21)
        for index_1 in range(len(scc)):
            for index_2 in range(len(scc)):
                if index_1 == index_2:
                    continue

                for index_3 in range(len(scc)):
                    if index_3 in [index_1, index_2]:
                        continue

                    if self.ground_guess:
                        self.generate_ground_transitivity(
                            scc, index_1, index_2, index_3
                        )
                    else:
                        self.generate_non_ground_transitivity(
                            generated_domains, scc, index_1, index_2, index_3
                        )

    def _generate_precs(self, generated_domains, scc):
        # Create rules (20)
        for index_1 in range(len(scc)):
            for index_2 in range(index_1 + 1, len(scc)):
                if self.ground_guess:
                    self.generate_ground_precs(scc, index_1, index_2)
                else:
                    self.generate_non_ground_precs(
                        generated_domains, scc, index_1, index_2
                    )

    def generate_ground_precs(self, scc, index_1, index_2):
        """
        Generate the predecessor-guess rules (prec(p1,p2)|prec(p2,p1) - so p1 is before p2),
        for grounded predicates.
        """
        p1 = scc[index_1]
        p2 = scc[index_2]

        dom_list = []

        self._add_predicate_domains_to_dom_list(p1, dom_list)
        self._add_predicate_domains_to_dom_list(p2, dom_list)

        combinations = [p for p in itertools.product(*dom_list)]

        p1_arg_length = len(p1.arguments)

        for combination in combinations:
            p1_arguments = []
            p2_arguments = []
            for index in range(len(combination)):
                if index < p1_arg_length:
                    p1_arguments.append(combination[index])
                else:
                    p2_arguments.append(combination[index])

            if len(p1_arguments) > 0:
                p1_parsed_arguments = "(" + ",".join(p1_arguments) + ")"
            else:
                p1_parsed_arguments = ""
            p1_string = p1.name + p1_parsed_arguments

            if len(p2_arguments) > 0:
                p2_parsed_arguments = "(" + ",".join(p2_arguments) + ")"
            else:
                p2_parsed_arguments = ""
            p2_string = p2.name + p2_parsed_arguments

            self.printer.custom_print(
                f"1 <= {{prec({p1_string},{p2_string});prec({p2_string},{p1_string})}} <= 1."
            )

    def _add_predicate_domains_to_dom_list(self, predicate, dom_list):
        if predicate.name in self.domain_lookup_dict:
            domain_dict = self.domain_lookup_dict[predicate.name]
            for index in range(len(domain_dict.keys())):
                dom_list.append(domain_dict[str(index)])
        else:
            for _ in predicate.arguments:
                if "0_terms" in self.domain_lookup_dict:
                    dom_list.append(self.domain_lookup_dict["0_terms"])
                else:
                    dom_list.append([])

    def generate_ground_transitivity(self, scc, index_1, index_2, index_3):
        """
        Generate the transitivity-constraints for the grounded-case.
        """
        p1 = scc[index_1]
        p2 = scc[index_2]
        p3 = scc[index_3]

        dom_list = []

        self._add_predicate_domains_to_dom_list(p1, dom_list)
        self._add_predicate_domains_to_dom_list(p2, dom_list)
        self._add_predicate_domains_to_dom_list(p3, dom_list)

        combinations = [p for p in itertools.product(*dom_list)]

        p1_arg_length = len(p1.arguments)
        p2_arg_length = len(p2.arguments)

        for combination in combinations:
            p1_arguments = []
            p2_arguments = []
            p3_arguments = []

            for index in range(len(combination)):
                if index < p1_arg_length:
                    p1_arguments.append(combination[index])
                elif index < (p1_arg_length + p2_arg_length):
                    p2_arguments.append(combination[index])
                else:
                    p3_arguments.append(combination[index])

            if len(p1_arguments) > 0:
                p1_parsed_arguments = "(" + ",".join(p1_arguments) + ")"
            else:
                p1_parsed_arguments = ""
            p1_string = p1.name + p1_parsed_arguments

            if len(p2_arguments) > 0:
                p2_parsed_arguments = "(" + ",".join(p2_arguments) + ")"
            else:
                p2_parsed_arguments = ""
            p2_string = p2.name + p2_parsed_arguments

            if len(p3_arguments) > 0:
                p3_parsed_arguments = "(" + ",".join(p3_arguments) + ")"
            else:
                p3_parsed_arguments = ""
            p3_string = p3.name + p3_parsed_arguments

            self.printer.custom_print(
                f":- prec({p1_string},{p2_string}), prec({p2_string},{p3_string}), prec({p3_string},{p1_string})."
            )

    def generate_non_ground_transitivity(
        self, generated_domains, scc, index_1, index_2, index_3
    ):
        """
        Generate the transitivity-constraints for the partly-grounded case.
        """
        p1 = scc[index_1]
        p2 = scc[index_2]
        p3 = scc[index_3]

        doms1, predicate_1 = self._generate_doms_predicate(p1, "1")
        doms2, predicate_2 = self._generate_doms_predicate(p2, "2")
        doms3, predicate_3 = self._generate_doms_predicate(p3, "3")

        self._generate_domain_for_predicate(generated_domains, p1)
        self._generate_domain_for_predicate(generated_domains, p2)
        self._generate_domain_for_predicate(generated_domains, p3)

        if len(doms1) > 0 and len(doms2) > 0 and len(doms3) > 0:
            domain_body = f" {','.join(doms1)}, {','.join(doms2)}, {','.join(doms3)}, "
        elif len(doms1) > 0 and len(doms2) > 0:
            domain_body = f" {','.join(doms1)}, {','.join(doms2)}, "
        elif len(doms1) > 0 and len(doms3) > 0:
            domain_body = f" {','.join(doms1)}, {','.join(doms3)}, "
        elif len(doms2) > 0 and len(doms3) > 0:
            domain_body = f" {','.join(doms2)}, {','.join(doms3)}, "
        elif len(doms1) > 0:
            domain_body = f" {','.join(doms1)}, "
        elif len(doms2) > 0:
            domain_body = f" {','.join(doms2)}, "
        elif len(doms3) > 0:
            domain_body = f" {','.join(doms3)}, "
        else:
            domain_body = " "

        self.printer.custom_print(
            f":-{domain_body}prec({predicate_1},{predicate_2}), prec({predicate_2},{predicate_3}), "
            + f"prec({predicate_3},{predicate_1})."
        )

    def generate_non_ground_precs(self, generated_domains, scc, index_1, index_2):
        """
        Generate the guesses for the precs in the non-ground case.
        """

        p1 = scc[index_1]
        p2 = scc[index_2]

        doms1, predicate_1 = self._generate_doms_predicate(p1, "1")
        doms2, predicate_2 = self._generate_doms_predicate(p2, "2")

        self._generate_domain_for_predicate(generated_domains, p1)
        self._generate_domain_for_predicate(generated_domains, p2)

        if len(doms1) > 0 and len(doms2) > 0:
            body = f" :- {','.join(doms1)}, {','.join(doms2)}."
        elif len(doms1) > 0:
            body = f" :- {','.join(doms1)}."
        elif len(doms2) > 0:
            body = f" :- {','.join(doms2)}."
        else:
            body = "."

        self.printer.custom_print(
            f"1 <= {{prec({predicate_1},{predicate_2});prec({predicate_2},{predicate_1})}} <= 1{body}"
        )

    def _generate_doms_predicate(self, predicate, string_postfix):
        doms = []
        new_variables_predicate = []
        index = 0
        for variable in predicate.arguments:
            variable_name = f"{variable}_{string_postfix}"
            new_variables_predicate.append(variable_name)

            if predicate.name in self.domain_lookup_dict:
                doms.append(f"dom_{predicate.name}_{index}({variable_name})")
            else:
                doms.append(f"dom({variable_name})")

            index += 1

        if len(new_variables_predicate) > 0:
            string_predicate = (
                predicate.name + "(" + ",".join(new_variables_predicate) + ")"
            )
        else:
            string_predicate = predicate.name

        return doms, string_predicate

    def _generate_domain_for_predicate(self, generated_domains, predicate):
        if (
            predicate.name in self.domain_lookup_dict
            and predicate.name not in generated_domains
        ):
            generated_domains[predicate.name] = True

            dom_dict = self.domain_lookup_dict[predicate.name]
            for index in range(len(dom_dict.keys())):
                variable_domain = dom_dict[str(index)]
                for value in variable_domain:
                    self.printer.custom_print(f"dom_{predicate.name}_{index}({value}).")
