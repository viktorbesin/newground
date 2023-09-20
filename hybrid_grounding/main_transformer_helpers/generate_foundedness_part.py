


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

        rem = [v for v in self.rule_variables if
               v not in h_vars]  # remaining variables not included in head atom (without facts)

        g_r = {}

        # path checking
        g = nx.Graph()
        for f in self.rule_literals:
            f_args_len = len(f.arguments)
            f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
            if f != self.rule_head and f_args_len > 0:
                f_vars = list(dict.fromkeys([a for a in f_args if a in self.rule_variables]))  # which have to be grounded per combination
                for v1 in f_vars:
                    for v2 in f_vars:
                        g.add_edge(v1,v2)

        for comp in self.rule_comparisons:

            left = comp.term
            assert(len(comp.guards) <= 1)
            right = comp.guards[0].term

            unparsed_f_args = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)
            f_vars = []
            for unparsed_f_arg in unparsed_f_args:
                f_arg = str(unparsed_f_arg)
                if f_arg in self.rule_variables:
                    f_vars.append(f_arg)
            
            for v1 in f_vars:
                for v2 in f_vars:
                    g.add_edge(v1, v2) 

        self._generate_foundedness_head(self.rule_head, rem, g, g_r, h_vars, h_args, h_args_len, h_args_nd)

        if self.program_rules:
            covered_subsets = self._generate_foundedness_comparisons(self.rule_head, rem, h_vars, h_args, g)
        else:
            covered_subsets = {}

        self._generate_foundedness_functions(self.rule_head, rem, h_vars, h_args, g, covered_subsets)


    def _generate_foundedness_head(self, head, rem, g, g_r, h_vars, h_args, h_args_len, h_args_nd):
        # ---------------------------------------------
        # REM -> is for the ''remaining'' variables that do not occur in the head
        # The next part is about the introduction of the ''remaining'' variables

        for r in rem:
            g_r[r] = []
            for n in nx.dfs_postorder_nodes(g, source=r):
                if n in h_vars:
                    g_r[r].append(n)

            dom_list = []
            for variable in g_r[r]:
                values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                dom_list.append(values)

            combinations = [p for p in itertools.product(*dom_list)]

           
            for combination in combinations:
                if not self.ground_guess:
                    #head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")

                    head_tuple_list = []
                    partly_head_tuple_list = []

                    comb_counter = 0
                    for h_arg in h_args:
                        if h_arg in h_vars and h_arg in g_r[r]:
                            head_tuple_list.append(combination[comb_counter])
                            partly_head_tuple_list.append(combination[comb_counter])
                            comb_counter += 1
                        elif h_arg not in h_vars:
                            head_tuple_list.append(h_arg)
                            partly_head_tuple_list.append(h_arg)
                        else:
                            head_tuple_list.append(h_arg)


                    head_interpretation = f"{head.name}{self.current_rule_position}"


                    if len(head_tuple_list) > 0:
                        head_tuple_interpretation = ','.join(head_tuple_list)
                        head_interpretation += f"({head_tuple_interpretation})"

                    if str(self.current_rule_position) in self.safe_variables_rules and str(r) in self.safe_variables_rules[str(self.current_rule_position)]:

                        values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, r, self.domain_lookup_dict, self.safe_variables_rules) 
                        for value in values:
                            self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{r}({value}).")

                        domain_string = f"domain_rule_{self.current_rule_position}_variable_{r}({r})"
                    else:
                        domain_string = f"dom({r})"


                    domains = []
                    for variable in h_vars:
                        domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")

                    """
                    if len(domains) > 0:
                        self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")
                    else:
                        self.printer.custom_print(f"{{{head}}}.")
                    """

                    rem_tuple_list = [r] + partly_head_tuple_list
                    rem_tuple_interpretation = ','.join(rem_tuple_list)


                    if len(g_r[r]) == 0:
                        self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{r}({rem_tuple_interpretation}):{domain_string}}}<=1.")
                    else:
                        self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{r}({rem_tuple_interpretation}):{domain_string}}}<=1 :- {head_interpretation}.")

                else:
                    head_interpretation = f"{head.name}" + (
                        f"({','.join([combination[g_r[r].index(a)] if a in g_r[r] else a for a in h_args])})" if h_args_len > 0 else "")
                    rem_interpretation = ','.join([combination[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                    rem_interpretations = ';'.join([f"r{self.current_rule_position}f_{r}({v}{','+rem_interpretation if h_args_len>0 else ''})" for v in (self.sub_doms[r] if r in self.sub_doms else self.terms)])
                    mis_vars  = [v for v in h_vars if v not in g_r[r]]
                    if len(h_vars) == len(g_r[r]):  # removed none
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {head_interpretation}.")
                    elif len(g_r[r]) == 0:  # removed all
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1.")
                    else:  # removed some
                        dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in mis_vars]
                        combinations_2 = [p for p in itertools.product(*dom_list)]
                        h_interpretations = [f"{head.name}({','.join(c2[mis_vars.index(a)] if a in mis_vars else combination[g_r[r].index(a)] for a in h_args)})" for c2 in combinations_2]
                        for hi in h_interpretations:
                            self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {hi}.")



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

                    if len(head_combination_list_2) > 0:
                        head_string = f"{head.name}{self.current_rule_position}({','.join(list(combination_2))})"
                    else:
                        head_string = f"{head.name}{self.current_rule_position}"

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
                            body_combination_tmp = [body_combination[v]] + head_combination_list_2
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
                                head_predicate = f"{head.name}{self.current_rule_position}({','.join(full_head_args)})"
                                unfound_level_mapping = f"{unfound_atom} :-{unfound_body} not prec({unfound_predicate},{head_predicate})."
                                self.printer.custom_print(unfound_level_mapping)

                                original_head_predicate = f"{head.name}({','.join(full_head_args)})"
                                new_unfound_atom = f"r{self.current_rule_position}_{self.current_rule_position}_unfound({','.join(full_head_args)})"
                                unfound_level_mapping = f"{new_unfound_atom} :-{unfound_body} not prec({head_predicate},{original_head_predicate})."
                                self.printer.custom_print(unfound_level_mapping)

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
                        self.current_rule_position
                        
                        if len(list(combination_2)) > 0:
                            head_string = f"{head.name}{self.current_rule_position}({','.join(list(combination_2))})"
                        else:
                            head_string = f"{head.name}{self.current_rule_position}"

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

            if len(head_combination_list_2) > 0:
                unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"
            else:
                unfound_atom = f"r{self.current_rule_position}_unfound_"

            not_head_counter = head_counter
        elif len(h_args) > 0 and len(h_vars) == 0:

            for h_arg in h_args:
                head_combination_list_2.append(h_arg)
                head_combination[h_arg] = h_arg
                full_head_args.append(h_arg)
                
            unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"

            not_head_counter = 0

        else:
            unfound_atom = f"r{self.current_rule_position}_unfound"
            not_head_counter = 0

        return (head_combination, head_combination_list_2, unfound_atom, not_head_counter, full_head_args)

    def _add_atom_to_unfoundedness_check(self, head_string, unfound_atom):

        if head_string not in self.unfounded_rules:
            self.unfounded_rules[head_string] = {}

        if str(self.current_rule_position) not in self.unfounded_rules[head_string]:
            self.unfounded_rules[head_string][str(self.current_rule_position)] = []

        self.unfounded_rules[head_string][str(self.current_rule_position)].append(unfound_atom)

