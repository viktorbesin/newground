


import re
import itertools

import networkx as nx

from ..comparison_tools import ComparisonTools
from .helper_part import HelperPart
from ..cyclic_strategy import CyclicStrategy



class GenerateFoundednessPart:

    def __init__(self, rule_head, current_rule_position, custom_printer, domain_lookup_dict, safe_variables_rules, rule_variables, rule_comparisons, rule_predicate_functions, rule_literals_signums, current_rule, strongly_connected_components, ground_guess, unfounded_rules, cyclic_strategy, strongly_connected_components_heads, program_rules, additional_unfounded_rules):

        self.rule_head = rule_head
        self.current_rule_position = current_rule_position
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.safe_variables_rules = safe_variables_rules
        self.rule_variables = rule_variables
        self.rule_comparisons = rule_comparisons
        self.rule_literals = rule_predicate_functions
        self.rule_literals_signums = rule_literals_signums
        self.current_rule = current_rule
        self.rule_strongly_restricted_components = strongly_connected_components
        self.ground_guess = ground_guess
        self.unfounded_rules = unfounded_rules
        self.cyclic_strategy = cyclic_strategy
        self.rule_strongly_restricted_components_heads = strongly_connected_components_heads
        self.program_rules = program_rules

        self.additional_unfounded_rules = additional_unfounded_rules

    def generate_foundedness_part(self):

        # head
        h_args_len = len(self.rule_head.arguments)
        h_args = re.sub(r'^.*?\(', '', str(self.rule_head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
        h_args_nd = list(dict.fromkeys(h_args)) # arguments (without duplicates / incl. terms)
        h_vars = list(dict.fromkeys(
            [a for a in h_args if a in self.rule_variables]))  # which have to be grounded per combination

        variables_not_in_head = [v for v in self.rule_variables if
               v not in h_vars]  # remaining variables not included in head atom (without facts)

        g_r = {}

        # Generate Graph for performance improvement
        graph = nx.Graph()
        for literal in self.rule_literals:
            literal_arguments_length = len(literal.arguments)
            literal_arguments = re.sub(r'^.*?\(', '', str(literal))[:-1].split(',')  # all arguments (incl. duplicates / terms)
            if literal != self.rule_head and literal_arguments_length > 0:
                #f_vars = list(dict.fromkeys([a for a in f_args if a in self.rule_variables]))  # which have to be grounded per combination
                literal_variables = []
                for argument in literal_arguments:
                    if argument in self.rule_variables:
                        literal_variables.append(argument)

                literal_variables = list(set(literal_variables))

                for variable_1 in literal_variables:
                    for variable_2 in literal_variables:
                        graph.add_edge(variable_1,variable_2)

        for comparison in self.rule_comparisons:

            left = comparison.term
            assert(len(comparison.guards) <= 1) # Assume top level one guard
            right = comparison.guards[0].term

            unparsed_f_args = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)
            f_vars = []
            for unparsed_f_arg in unparsed_f_args:
                f_arg = str(unparsed_f_arg)
                if f_arg in self.rule_variables:
                    f_vars.append(f_arg)
            
            for variable_1 in f_vars:
                for variable_2 in f_vars:
                    graph.add_edge(variable_1, variable_2) 

        self._generate_foundedness_head(self.rule_head, variables_not_in_head, graph, g_r, h_vars, h_args, h_args_len, h_args_nd)

        if self.program_rules:
            covered_subsets = self._generate_foundedness_comparisons(self.rule_head, variables_not_in_head, h_vars, h_args, graph)
        else:
            covered_subsets = {}

        self._generate_foundedness_functions(self.rule_head, variables_not_in_head, h_vars, h_args, graph, covered_subsets)


    def _generate_foundedness_head(self, head, variables_not_in_head, graph, reachable_head_variables_from_not_head_variable, head_variables, head_arguments, length_of_head_arguments, head_arguments_no_duplicates):
        # ---------------------------------------------
        # REM -> is for the ''remaining'' variables that do not occur in the head
        # The next part is about the introduction of the ''remaining'' variables

        for not_head_variable in variables_not_in_head:
            reachable_head_variables_from_not_head_variable[not_head_variable] = []
            for node in nx.dfs_postorder_nodes(graph, source=not_head_variable):
                if node in head_variables:
                    reachable_head_variables_from_not_head_variable[not_head_variable].append(node)

            dom_list = []
            dom_list_lookup = {}
            index = 0
            for variable in reachable_head_variables_from_not_head_variable[not_head_variable]:
                not_head_variable_values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                dom_list.append(not_head_variable_values)
                dom_list_lookup[variable] = index

                index += 1

            combinations = [p for p in itertools.product(*dom_list)]

            for combination in combinations:
                if not self.ground_guess:
                    self._generate_foundedness_head_not_ground(head_arguments, head_variables, reachable_head_variables_from_not_head_variable, not_head_variable, combination, dom_list_lookup, head)
                else:
                    head_interpretation = f"{head.name}"
                    if length_of_head_arguments > 0:
                        argument_list = []
                        for argument in head_arguments:
                            if argument in reachable_head_variables_from_not_head_variable[not_head_variable]:
                                #argument_list.append(combination[reachable_head_variables_from_not_head_variable[not_head_variable].index(argument)])
                                argument_list.append(combination[dom_list_lookup[argument]])
                            else:
                                argument_list.append(argument)
                        head_interpretation += f"({','.join(argument_list)})"

                    remaining_head_values = []
                    for variable in head_arguments_no_duplicates:
                        if variable in reachable_head_variables_from_not_head_variable[not_head_variable]:
                            remaining_head_values.append(combination[dom_list_lookup[variable]])
                    
                    not_head_variable_values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, not_head_variable, self.domain_lookup_dict, self.safe_variables_rules) 

                    not_variable_interpretations = []
                    for value in not_head_variable_values:

                        name = f"r{self.current_rule_position}f_{not_head_variable}"
                        if length_of_head_arguments > 0:
                            arguments = f"({value}{','.join(remaining_head_values)})"
                        else:
                            arguments = f"({value})"

                        not_variable_interpretations.append(f"{name}{arguments}")
                    
                    not_variable_interpretations = ';'.join(not_variable_interpretations)

                    not_reached_head_variables = []
                    for variable in head_variables:
                        if variable not in reachable_head_variables_from_not_head_variable[not_head_variable]:
                            not_reached_head_variables.append(variable)

                    if len(head_variables) == len(reachable_head_variables_from_not_head_variable[not_head_variable]):  # removed none
                        self.printer.custom_print(f"1{{{not_variable_interpretations}}}1 :- {head_interpretation}.")
                    elif len(reachable_head_variables_from_not_head_variable[not_head_variable]) == 0:  # removed all
                        self.printer.custom_print(f"1{{{not_variable_interpretations}}}1.")
                    else:  # removed some
                        dom_list = []
                        dom_list_lookup = {}

                        index = 0
                        for variable in not_reached_head_variables:
                            values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, not_head_variable, self.domain_lookup_dict, self.safe_variables_rules) 
                            dom_list.append(values)
                            dom_list_lookup[variable] = index
                            index += 1

                        combinations_for_not_reached_variables = [p for p in itertools.product(*dom_list)]

                        head_interpretations = []
                        for combination_not_reached_variable in combinations_for_not_reached_variables:

                            head_arguments_not_reached = []

                            for argument in head_arguments:
                                if argument in not_reached_head_variables:
                                    head_arguments_not_reached.append(combination_not_reached_variable[dom_list_lookup[variable]])
                                else:
                                    head_arguments_not_reached.append(combination[dom_list_lookup[variable]])

                            current_head_interpretation = f"{head.name}({','.join(head_arguments_not_reached)})"
                            head_interpretations.append(current_head_interpretation)

                        for head_interpretation in head_interpretations:
                            self.printer.custom_print(f"1{{{not_variable_interpretations}}}1 :- {head_interpretation}.")


                    """
                    #rem_interpretation = ','.join([combination[reachable_head_variables_from_not_head_variable[not_head_variable].index(v)] for v in head_arguments_no_duplicates if v in reachable_head_variables_from_not_head_variable[not_head_variable]])
                    mis_vars  = [v for v in head_variables if v not in reachable_head_variables_from_not_head_variable[not_head_variable]]
                    rem_interpretations = ';'.join([f"r{self.current_rule_position}f_{not_head_variable}({v}{','+rem_interpretation if length_of_head_arguments>0 else ''})" for v in (self.sub_doms[not_head_variable] if not_head_variable in self.sub_doms else self.terms)])
                    if len(head_variables) == len(reachable_head_variables_from_not_head_variable[not_head_variable]):  # removed none
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {head_interpretation}.")
                    elif len(reachable_head_variables_from_not_head_variable[not_head_variable]) == 0:  # removed all
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1.")
                    else:  # removed some
                        dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in mis_vars]
                        combinations_for_not_reached_variables = [p for p in itertools.product(*dom_list)]
                        h_interpretations = [f"{head.name}({','.join(c2[mis_vars.index(a)] if a in mis_vars else combination[reachable_head_variables_from_not_head_variable[not_head_variable].index(a)] for a in head_arguments)})" for c2 in combinations_for_not_reached_variables]
                        for hi in h_interpretations:
                            self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {hi}.")
                    """

    def _generate_foundedness_head_not_ground(self, head_arguments, head_variables, graph_variable_dict, not_head_variable, combination, dom_list_lookup, head):
        # assume self.ground_guess == False

        #head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")

        head_tuple_list = []
        partly_head_tuple_list = []

        for head_argument in head_arguments:
            if head_argument in head_variables and head_argument in graph_variable_dict[not_head_variable]:

                combination_value = combination[dom_list_lookup[head_argument]]

                head_tuple_list.append(combination_value)
                partly_head_tuple_list.append(combination_value)
            elif head_argument not in head_variables:
                head_tuple_list.append(head_argument)
                partly_head_tuple_list.append(head_argument)
            else:
                head_tuple_list.append(head_argument)


        head_interpretation = f"{head.name}{self.current_rule_position}"
        #head_interpretation = f"{head.name}'"


        if len(head_tuple_list) > 0:
            head_tuple_interpretation = ','.join(head_tuple_list)
            head_interpretation += f"({head_tuple_interpretation})"

        if str(self.current_rule_position) in self.safe_variables_rules and str(not_head_variable) in self.safe_variables_rules[str(self.current_rule_position)]:

            values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, not_head_variable, self.domain_lookup_dict, self.safe_variables_rules) 
            for value in values:
                self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{not_head_variable}({value}).")

            domain_string = f"domain_rule_{self.current_rule_position}_variable_{not_head_variable}({not_head_variable})"
        else:
            domain_string = f"dom({not_head_variable})"


        domains = []
        for variable in head_variables:
            domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")

        """
        if len(domains) > 0:
            self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")
        else:
            self.printer.custom_print(f"{{{head}}}.")
        """

        rem_tuple_list = [not_head_variable] + partly_head_tuple_list
        rem_tuple_interpretation = ','.join(rem_tuple_list)


        if len(graph_variable_dict[not_head_variable]) == 0:
            self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{not_head_variable}({rem_tuple_interpretation}):{domain_string}}}<=1.")
        else:
            self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{not_head_variable}({rem_tuple_interpretation}):{domain_string}}}<=1 :- {head_interpretation}.")




    def _generate_foundedness_comparisons(self, head, rem, h_vars, h_args, g):
        # ---------------------------------------------
        # The next section is about the handling of the comparison operators (foundedness)

        covered_subsets = {}
        # for every cmp operator
        for f in self.rule_comparisons:

            left = f.term
            assert(len(f.guards) <= 1)
            right = f.guards[0].term
            comparison_operator = f.guards[0].comparison

            symbolic_arguments = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)

            arguments = []
            for symbolic_argument in symbolic_arguments:
                arguments.append(str(symbolic_argument))

            f_arguments_nd = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
            f_vars = list (dict.fromkeys([a for a in arguments if a in self.rule_variables])) # which have to be grounded per combination

            f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

            f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
            combination_variables = f_vars_needed + f_rem

            associated_variables = {}
            dom_list = []
            index = 0
            for variable in combination_variables:
                values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                dom_list.append(values)
                associated_variables[variable] = index
                index = index + 1

            combinations = [p for p in itertools.product(*dom_list)]

            #print(f"[INFO] -------> NUMBER OF COMBINATIONS: {len(combinations)}")
            for combination in combinations:

                variable_assignments = {}

                for variable_index in range(len(combination_variables)):
                    variable = combination_variables[variable_index]
                    value = combination[variable_index]

                    variable_assignments[variable] = value


                head_combination, head_combination_list_2, unfound_atom, not_head_counter, full_head_args = self.generate_head_atom(combination, h_vars, h_args, f_vars_needed, associated_variables)

                body_combination = {}

                for f_arg in arguments:
                    if f_arg in h_vars and f_arg in f_vars_needed: # Variables in head
                        body_combination[f_arg] = head_combination[f_arg]
                    elif f_arg in f_vars: # Not in head variables
                        body_combination[f_arg] = (combination[not_head_counter])
                        not_head_counter += 1
                    else: # Static
                        body_combination[f_arg] = f_arg 

                left_eval = ComparisonTools.evaluate_operation(left, variable_assignments)
                right_eval = ComparisonTools.evaluate_operation(right, variable_assignments)

                sint = HelperPart.ignore_exception(ValueError)(int)
                left_eval = sint(left_eval)
                right_eval = sint(right_eval)

                safe_checks = left_eval != None and right_eval != None
                evaluation = safe_checks and not ComparisonTools.compareTerms(comparison_operator, int(left_eval), int(right_eval))
            
                if not safe_checks or evaluation:

                    left_instantiation = ComparisonTools.instantiate_operation(left, variable_assignments)
                    right_instantiation = ComparisonTools.instantiate_operation(right, variable_assignments)
                    unfound_comparison = ComparisonTools.comparison_handlings(comparison_operator, left_instantiation, right_instantiation)

                    unfound_body_list = []

                    for v in f_arguments_nd:
                        if v in rem:
                            
                            body_combination_tmp = [body_combination[v]] + head_combination_list_2
                            body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                            unfound_body_list.append(body_predicate)


                    if len(unfound_body_list) > 0:
                        unfound_body = f" {','.join(unfound_body_list)}"
                        unfound_rule = f"{unfound_atom} :- {unfound_body}"
                        unfound_rule += "."

                    else:
                        unfound_rule = f"{unfound_atom}"
                        unfound_rule += "."

                    self.printer.custom_print(unfound_rule)

                    if unfound_atom not in covered_subsets:
                        covered_subsets[unfound_atom] = []

                    covered_subsets[unfound_atom].append(unfound_body_list)

                dom_list_2 = []
                for arg in h_args:
                    if arg in h_vars and arg not in head_combination: 
                        values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, arg, self.domain_lookup_dict, self.safe_variables_rules) 
                        dom_list_2.append(values)
                    elif arg in h_vars and arg in head_combination:
                        dom_list_2.append([head_combination[arg]])
                    else:
                        dom_list_2.append([arg])

                combinations_2 = [p for p in itertools.product(*dom_list_2)]

                for combination_2 in combinations_2:
                    #new_head_name = f"{head.name}{self.current_rule_position}"
                    new_head_name = f"{head.name}"

                    if len(head_combination_list_2) > 0 and len(list(combination_2)) > 0 and len((''.join(combination_2)).strip()) > 0:
                        head_string = f"{new_head_name}({','.join(list(combination_2))})"
                    else:
                        head_string = f"{new_head_name}"

                    #print(f"{head_string}/{unfound_atom}")
                    self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

        return covered_subsets

    def _generate_foundedness_functions(self, head, rem, h_vars, h_args, g, covered_subsets):
        # -------------------------------------------
        # over every body-atom
        for rule_predicate_function in self.rule_literals:
            if rule_predicate_function != head:

                f_args_len = len(rule_predicate_function.arguments)
                f_args = re.sub(r'^.*?\(', '', str(rule_predicate_function))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                f_vars = list(dict.fromkeys([a for a in f_args if a in self.rule_variables]))  # which have to be grounded per combination

                f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
                #f_vars_needed = h_vars

                associated_variables = {}
                dom_list = []
                index = 0
                for variable in f_vars_needed + f_rem:
                    values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                    dom_list.append(values)
                    associated_variables[variable] = index
                    index += 1

                combinations = [p for p in itertools.product(*dom_list)]

                for combination in combinations:

                    head_combination, head_combination_list_2, unfound_atom, not_head_counter, full_head_args = self.generate_head_atom(combination, h_vars, h_args, f_vars_needed, associated_variables)

                    # ---------
                    body_combination = {}

                    for f_arg in f_args:
                        if f_arg in h_vars and f_arg in f_vars_needed: # Variables in head
                            body_combination[f_arg] = head_combination[f_arg]
                        elif f_arg in f_vars: # Not in head variables
                            body_combination[f_arg] = (combination[not_head_counter])
                            not_head_counter += 1
                        else: # Static
                            body_combination[f_arg] = f_arg 

                    unfound_body_dict = {}
                    unfound_body_list = []
                    for v in f_args_nd:
                        if v in rem:
                            if len((''.join(head_combination_list_2)).strip()) > 0:
                                body_combination_tmp = [body_combination[v]] + head_combination_list_2
                            else:
                                body_combination_tmp = [body_combination[v]]
                            body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                            unfound_body_list.append(body_predicate)
                            unfound_body_dict[body_predicate] = body_predicate

    
                    if unfound_atom in covered_subsets:
                        possible_subsets = covered_subsets[unfound_atom]
                        found = False

                        for possible_subset in possible_subsets:
                            temp_found = True
                            for possible_subset_predicate in possible_subset:
                                if possible_subset_predicate not in unfound_body_dict:
                                    temp_found = False
                                    break

                            if temp_found == True:
                                found = True
                                break

                        if found == True:
                            continue
                                    
                    unfound_predicate_name = rule_predicate_function.name
                    unfound_predicate = unfound_predicate_name
                    if len(f_args) > 0:
                        unfound_predicate += f"("

                        unfound_predicate_args = []
                        for f_arg in f_args:
                            if f_arg in body_combination:
                                unfound_predicate_args.append(body_combination[f_arg])
                            else:
                                unfound_predicate_args.append(f_arg)

                        unfound_predicate += f"{','.join(unfound_predicate_args)})"

                    if len(unfound_body_list) > 0:
                        unfound_body = f" {','.join(unfound_body_list)},"
                    else:
                        unfound_body = ""

                    sign_adjusted_predicate = "" 
                    if not self.rule_literals_signums[self.rule_literals.index(rule_predicate_function)]: # i.e. a ''positive'' occurence (e.g. q(X) :- p(X) -> p(X) is positive)
                        sign_adjusted_predicate = f"not {unfound_predicate}"
                    else: # i.e. a ''negative'' occurence (e.g. q(X) :- p(X), not p(1). -> p(1) is negative)
                        sign_adjusted_predicate = f"{unfound_predicate}"

                    unfound_rule = f"{unfound_atom} :-{unfound_body} {sign_adjusted_predicate}."

                    if self.program_rules:
                        self.printer.custom_print(unfound_rule)


                    if self.cyclic_strategy in [CyclicStrategy.LEVEL_MAPPING, CyclicStrategy.LEVEL_MAPPING_AAAI]:
                        
                        if self.current_rule in self.rule_strongly_restricted_components:
                            relevant_bodies = self.rule_strongly_restricted_components[self.current_rule]

                            if rule_predicate_function in relevant_bodies:
                                new_head_name = f"{head.name}{self.current_rule_position}"
                                #new_head_name = f"{head.name}'"

                                head_predicate = f"{new_head_name}({','.join(full_head_args)})"
                                unfound_level_mapping = f"{unfound_atom} :-{unfound_body} not prec({unfound_predicate},{head_predicate})."
                                self.printer.custom_print(unfound_level_mapping)

                                original_head_predicate = f"{head.name}({','.join(full_head_args)})"

                                if len(unfound_predicate_args) > 0:
                                    new_unfound_atom = f"r{self.current_rule_position}_{self.current_rule_position}_unfound({','.join(unfound_predicate_args)})"
                                else:
                                    new_unfound_atom = f"r{self.current_rule_position}_{self.current_rule_position}_unfound_"

                                unfound_level_mapping = f"{new_unfound_atom} :-{unfound_body} not prec({head_predicate},{original_head_predicate})."
                                self.printer.custom_print(unfound_level_mapping)

                                #self._add_atom_to_unfoundedness_check(head_predicate, new_unfound_atom)
                                self.additional_unfounded_rules.append(f":- {new_unfound_atom}, {head_predicate}.")

                    dom_list_2 = []
                    for arg in h_args:
                        if arg in h_vars and arg not in head_combination: 
                            values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, arg, self.domain_lookup_dict, self.safe_variables_rules) 
                            dom_list_2.append(values)
                        elif arg in h_vars and arg in head_combination:
                            dom_list_2.append([head_combination[arg]])
                        else:
                            dom_list_2.append([arg])

                    combinations_2 = [p for p in itertools.product(*dom_list_2)]

                    for combination_2 in combinations_2:
                        new_head_name = f"{head.name}{self.current_rule_position}"
                        #new_head_name = f"{head.name}'"
                        
                        if len(list(combination_2)) > 0 and len(list(combination_2)) > 0 and len((''.join(combination_2)).strip()) > 0:
                            head_string = f"{new_head_name}({','.join(list(combination_2))})"
                        else:
                            head_string = f"{new_head_name}"

                        self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

    def _checkForCoveredSubsets(self, base, current, c_varset):
        for key in base:
            if key.issubset(current):
                c = tuple([c_varset[current.index(p)] for p in list(key)])
                if c in base[key]:
                    return True

        return False

    def _getVarsNeeded(self, h_vars, f_vars, f_rem, g):
        f_vars_needed = [f for f in f_vars if f in h_vars]  # bounded head vars which are needed for foundation
        for r in f_rem:
            for n in nx.dfs_postorder_nodes(g, source=r):
                if n in h_vars and n not in f_vars_needed:
                    f_vars_needed.append(n)
        return f_vars_needed


    def generate_head_atom(self, combination, h_vars, h_args, f_vars_needed, combination_associated_variables):

        head_combination_list_2 = []
        head_combination = {}

        full_head_args = []

        if len(h_vars) > 0:
            head_combination_list = list(combination[:len(h_vars)])

            head_counter = 0
            for h_arg in h_args:
                if h_arg in h_vars and h_arg in f_vars_needed:

                    combination_variable_position = combination_associated_variables[h_arg]
                    
                    head_combination[h_arg] = combination[combination_variable_position]
                    full_head_args.append(combination[combination_variable_position])

                    if combination_variable_position > head_counter:
                        head_counter = combination_variable_position

                elif h_arg not in h_vars:
                    head_combination[h_arg] = h_arg
                    
                    full_head_args.append(h_arg)
                else:   
                    full_head_args.append("_")
                    pass

            for h_arg in h_args:
                if h_arg in head_combination:
                    head_combination_list_2.append(head_combination[h_arg])

            if len(head_combination_list_2) > 0 and len(list(head_combination_list_2)) > 0 and len((''.join(head_combination_list_2)).strip()) > 0:
                unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"
            else:
                unfound_atom = f"r{self.current_rule_position}_unfound_"

            not_head_counter = head_counter
        elif len(h_args) > 0 and len(h_vars) == 0:

            for h_arg in h_args:
                head_combination_list_2.append(h_arg)
                head_combination[h_arg] = h_arg
                full_head_args.append(h_arg)

            
            if len(list(head_combination_list_2)) > 0 and len((''.join(head_combination_list_2)).strip()) > 0:
                unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"
            else:
                unfound_atom = f"r{self.current_rule_position}_unfound_"

            not_head_counter = 0

        else:
            unfound_atom = f"r{self.current_rule_position}_unfound_"
            not_head_counter = 0

        return (head_combination, head_combination_list_2, unfound_atom, not_head_counter, full_head_args)

    def _add_atom_to_unfoundedness_check(self, head_string, unfound_atom):

        if head_string not in self.unfounded_rules:
            self.unfounded_rules[head_string] = {}

        if str(self.current_rule_position) not in self.unfounded_rules[head_string]:
            self.unfounded_rules[head_string][str(self.current_rule_position)] = []

        self.unfounded_rules[head_string][str(self.current_rule_position)].append(unfound_atom)

