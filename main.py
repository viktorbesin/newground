import sys
import itertools
import re
import argparse

import clingo
from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule, ComparisonOperator
from clingo.control import Control
from pprint import pprint
from clingox.program import Program, ProgramObserver, Remapping

import networkx as nx

class DefaultOutputPrinter:

    def custom_print(self, string):
        print(string)


class ClingoApp(object):
    def __init__(self, name, no_show=False, ground_guess=False, ground=False, output_printer = None):
        self.program_name = name
        self.sub_doms = {}
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground

        if not output_printer:
            self.printer = DefaultOutputPrinter()
        else:
            self.printer = output_printer

        self.prg = Program()

    def main(self, ctl, inputs):

        print(''.join(inputs)) 

        combined_inputs = '\n'.join(inputs)
        

        ctl_insts = Control()
        ctl_insts.register_observer(ProgramObserver(self.prg))
        if self.ground:
            self.printer.custom_print(self.prg)

        term_transformer = TermTransformer(self.sub_doms, self.printer, self.no_show)
        #parse_files(inputs, lambda stm: term_transformer(stm))
        parse_string(combined_inputs, lambda stm: term_transformer(stm))

        safe_variables = term_transformer.safe_variable_rules
        domain = term_transformer.domain

        comparisons = term_transformer.comparison_operators_variables

        new_domain_hash = hash(str(domain))
        old_domain_hash = None
    

        #print(''.join(inputs))
        """
        print(domain)
        print(safe_variables)
        """


        while new_domain_hash != old_domain_hash:
        
            old_domain_hash = new_domain_hash

            domain_transformer = DomainTransformer(safe_variables, domain, comparisons)
            parse_string(combined_inputs, lambda stm: domain_transformer(stm))       

            safe_variables = domain_transformer.safe_variables_rules
            domain = domain_transformer.domain


            new_domain_hash = hash(str(domain))

        with ProgramBuilder(ctl) as bld:
            transformer = NglpDlpTransformer(bld, term_transformer.terms, term_transformer.facts, term_transformer.ng_heads, term_transformer.shows, term_transformer.sub_doms, self.ground_guess, self.ground, self.printer, domain, safe_variables)
            #parse_files(combined_inputs, lambda stm: bld.add(transformer(stm)))
            parse_string(combined_inputs, lambda stm: bld.add(transformer(stm)))
            if transformer.counter > 0:
                parse_string(":- not sat.", lambda stm: bld.add(stm))
                self.printer.custom_print(":- not sat.")
                #parse_string(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.", lambda stm: self.bld.add(stm))

                sat_strings = []
                non_ground_rules = transformer.non_ground_rules
                for non_ground_rule_key in non_ground_rules.keys():
                    sat_strings.append(f"sat_r{non_ground_rule_key}")

    
                self.printer.custom_print(f"sat :- {','.join(sat_strings)}.")

                #print(transformer.unfounded_rules)

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

                    
                    self.printer.custom_print(f":- {key}, {','.join(sum_strings)}.")
                

                if not self.ground_guess:
                    for t in transformer.terms:
                        self.printer.custom_print(f"dom({t}).")

                if not self.no_show:
                    if not term_transformer.show:
                        for f in transformer.shows.keys():
                            for l in transformer.shows[f]:
                                self.printer.custom_print(f"#show {f}/{l}.")

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads, shows, sub_doms, ground_guess, ground, printer, domain, safe_variables_rules):
        self.rules = False
        self.ng = False
        self.bld = bld
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads
        self.sub_doms = sub_doms
        self.ground_guess = ground_guess
        self.ground = ground
        self.printer = printer

        self.domain = domain
        self.safe_variables_rules = safe_variables_rules

        self.cur_anon = 0
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.shows = shows
        self.foundness ={}
        self.f = {}
        self.counter = 0
        self.non_ground_rules = {}
        self.g_counter = 'A'

        self.current_comparison = None

        self.unfounded_rules = {}
        self.current_rule_position = 0

    def _reset_after_rule(self):
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.cur_anon = 0
        self.ng = False
        #self.head = None

    def _get_domain_values_from_rule_variable(self, rule, variable):
        """ 
            Provided a rule number and a variable in that rule, one gets the domain of this variable.
            If applicable it automatically calculates the intersection of different domains.
        """

        possible_domain_value_name = f"term_rule_{str(rule)}_variable_{str(variable)}"
        if possible_domain_value_name in self.domain:
            return self.domain[possible_domain_value_name]['0']

        if str(rule) not in self.safe_variables_rules:
            return self.domain["0_terms"]

        if str(variable) not in self.safe_variables_rules[str(rule)]:
            return self.domain["0_terms"]

        total_domain = None

        for domain_type in self.safe_variables_rules[str(rule)][str(variable)]:
       
            if domain_type["type"] == "function":
                domain_name = domain_type["name"]
                domain_position = domain_type["position"]

                if domain_name not in self.domain:
                    return self.domain["0_terms"]

                if domain_position not in self.domain[domain_name]:
                    return self.domain["0_terms"]

                cur_domain = self.domain[domain_name][domain_position]

                if total_domain:
                    total_domain = total_domain.intersection(set(cur_domain))
                else:
                    total_domain = set(cur_domain)

        return list(total_domain)

    def visit_Rule(self, node):

        if not self.rules:
            self._reset_after_rule()
            if not self.ground:
                self._outputNodeFormatConform(node)

            self.current_rule_position += 1
            self.counter += 1
            return node

        # check if AST is non-ground
        self.visit_children(node)

        # if so: handle grounding
        if self.ng:
            self.non_ground_rules[self.current_rule_position] = self.current_rule_position
            #self.counter += 1
            if str(node.head) != "#false":
                head = self.cur_func[0]
            else:
                head = None

            # MOD
            # domaining per rule variable
            for variable in self.cur_var: # variables

                values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 

                disjunction = ""

                for value in values:
                    disjunction += f"r{self.counter}_{variable}({value}) | "

                if len(disjunction) > 0:
                    disjunction = disjunction[:-3] + "."
                    self.printer.custom_print(disjunction)

                for value in values:
                    self.printer.custom_print(f"r{self.counter}_{variable}({value}) :- sat.")

            # ----------------------------
            # SAT
            # SAT for comparison operators

            covered_cmp = {} # reduce SAT rules when compare-operators are pre-checked
            for f in self.cur_comp:
                                
                symbolic_arguments = ComparisonOperations.get_arguments_from_operation(f.left) + ComparisonOperations.get_arguments_from_operation(f.right)

                arguments = []
                for symbolic_argument in symbolic_arguments:
                    arguments.append(str(symbolic_argument))

                var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination
                dom_list = []
                for variable in vars:
                    if str(self.current_rule_position) in self.safe_variables_rules and variable in self.safe_variables_rules[str(self.current_rule_position)]:

                        domain = self._get_domain_values_from_rule_variable(str(self.current_rule_position), variable)
                            
                        dom_list.append(domain)
                    else:
                        dom_list.append(self.domain["0_terms"])

                combinations = [p for p in itertools.product(*dom_list)]

                vars_set = frozenset(vars)
                if vars_set not in covered_cmp:
                    covered_cmp[vars_set] = set()

                for c in combinations:
    
                    variable_assignments = {}
                    
                    for variable_index in range(len(vars)):
                        variable = vars[variable_index]
                        value = c[variable_index]

                        variable_assignments[variable] = value

                    interpretation = ""
                    for variable in var:
                        if variable in vars:
                            interpretation += f"r{self.counter}_{variable}({variable_assignments[variable]}),"

                    left = ComparisonOperations.instantiate_operation(f.left, variable_assignments)
                    right = ComparisonOperations.instantiate_operation(f.right, variable_assignments)
                    comparison = ComparisonOperations.comparison_handlings(f.comparison, left, right)

                    interpretation += f" not {comparison}"

                    self.printer.custom_print(f"sat_r{self.counter} :- {interpretation}.")

            # SAT - Functions
            for f in self.cur_func:
                args_len = len(f.arguments)
                if (args_len == 0):
                    self.printer.custom_print(
                        f"sat_r{self.counter} :-{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else ' not'} {f}.")
                    continue
                arguments = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # all arguments (incl. duplicates / terms)
                var = list(dict.fromkeys(arguments)) if args_len > 0 else [] # arguments (without duplicates / incl. terms)
                vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) if args_len > 0 else [] # which have to be grounded per combination

                dom_list = []
                for variable in vars:
                    values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                    dom_list.append(values)

                combinations = [p for p in itertools.product(*dom_list)]
                vars_set = frozenset(vars)

                for c in combinations:
                    c_varset = tuple([c[vars.index(v)] for v in vars_set])
                    if not self._checkForCoveredSubsets(covered_cmp, list(vars_set), c_varset):  # smaller sets are also possible
                    #if vars_set not in covered_cmp or c_varset not in covered_cmp[vars_set]:
                        f_args = ""
                        # vars in atom
                        interpretation = ""
                        for v in var:
                            interpretation += f"r{self.counter}_{v}({c[vars.index(v)]}), " if v in self.cur_var else f""
                            f_args += f"{c[vars.index(v)]}," if v in self.cur_var else f"{v},"

                        if len(f_args) > 0:
                            f_args = f"{f.name}({f_args[:-1]})"
                        else:
                            f_args = f"{f.name}"

                        self.printer.custom_print(f"sat_r{self.counter} :- {interpretation}{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else 'not '}{f_args}.")

            # reduce duplicates; track combinations
            sat_per_f = {}
            for f in self.cur_func:
                sat_per_f[f] = []

            # FOUND NEW
            if head is not None:
                # head
                h_args_len = len(head.arguments)
                h_args = re.sub(r'^.*?\(', '', str(head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                h_args_nd = list(dict.fromkeys(h_args)) # arguments (without duplicates / incl. terms)
                h_vars = list(dict.fromkeys(
                    [a for a in h_args if a in self.cur_var]))  # which have to be grounded per combination

                rem = [v for v in self.cur_var if
                       v not in h_vars]  # remaining variables not included in head atom (without facts)

                # GUESS head
                if not self.ground_guess:

                    domains = []
                    for variable in h_vars:
                        domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")
                        values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                        for value in values:
                            self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{variable}({value}).")

                    self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")

                else:
                    
                    dom_list = [self._get_domain_values_from_rule_variable(self.current_rule_position, variable) for variable in h_vars]
                    combinations = [p for p in itertools.product(*dom_list)]
                    h_interpretations = [f"{head.name}({','.join(c[h_vars.index(a)] if a in h_vars else a for a in h_args)})" for c in combinations]
                    self.printer.custom_print(f"{{{';'.join(h_interpretations)}}}." if h_args_len > 0 else f"{{{head.name}}}.")

                g_r = {}

                # path checking
                g = nx.Graph()
                for f in self.cur_func:
                    f_args_len = len(f.arguments)
                    f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                    if f != head and f_args_len > 0:
                        f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination
                        for v1 in f_vars:
                            for v2 in f_vars:
                                g.add_edge(v1,v2)

                for comp in self.cur_comp:
                    g.add_edge(str(comp.left), str(comp.left))

                # ---------------------------------------------
                # REM -> is for the ''remaining'' variables that do not occur in the head
                # The next part is about the introduction of the ''remaining'' variables
                for r in rem:
                    g_r[r] = []
                    for n in nx.dfs_postorder_nodes(g, source=r):
                        if n in h_vars:
                            g_r[r].append(n)




                    dom_list = []
                    for variable in h_vars + [r]:
                        values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                        dom_list.append(values)


                    combinations = [p for p in itertools.product(*dom_list)]

                   
                    for combination in combinations:
                        if not self.ground_guess:
                            #head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")

                            head_tuple_list = []
        
                            comb_counter = 0
                            for h_arg in h_args:
                                if h_arg in h_vars:
                                    head_tuple_list.append(combination[comb_counter])
                                    comb_counter += 1
                                else:
                                    head_tuple_list.append(h_arg)


                            #print(head)
                            head_interpretation = f"{head.name}"
                            #head_tuple_list = [c[index] for index in range(len(c))]
                            head_tuple_interpretation = ','.join(head_tuple_list)

                            if len(combination) > 0:
                                head_interpretation += f"({head_tuple_interpretation})"

                            if str(self.current_rule_position) in self.safe_variables_rules and str(r) in self.safe_variables_rules[str(self.current_rule_position)]:

                                values = self._get_domain_values_from_rule_variable(self.current_rule_position, r) 
                                for value in values:
                                    self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{r}({value}).")

                                domain_string = f"domain_rule_{self.current_rule_position}_variable_{r}({r})"
                            else:
                                domain_string = f"dom({r})"


                            domains = []
                            for variable in h_vars:
                                domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")
                            self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")



                            rem_tuple_list = [r] + head_tuple_list
                            rem_tuple_interpretation = ','.join(rem_tuple_list)

                            self.printer.custom_print(f"1<={{r{self.counter}f_{r}({rem_tuple_interpretation}):{domain_string}}}<=1 :- {head}.")

                        else:
                            head_interpretation = f"{head.name}" + (
                                f"({','.join([combination[g_r[r].index(a)] if a in g_r[r] else a for a in h_args])})" if h_args_len > 0 else "")
                            rem_interpretation = ','.join([combination[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                            rem_interpretations = ';'.join([f"r{self.counter}f_{r}({v}{','+rem_interpretation if h_args_len>0 else ''})" for v in (self.sub_doms[r] if r in self.sub_doms else self.terms)])
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

                # ---------------------------------------------
                # The next section is about the handling of the comparison operators (foundedness)
                covered_cmp = {}
                # for every cmp operator
                for f in self.cur_comp:

                    symbolic_arguments = ComparisonOperations.get_arguments_from_operation(f.left) + ComparisonOperations.get_arguments_from_operation(f.right)

                    arguments = []
                    for symbolic_argument in symbolic_arguments:
                        arguments.append(str(symbolic_argument))

                    f_arguments_nd = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                    f_vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                    f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                    f_vars_needed = h_vars

                    vars_set = frozenset(f_vars_needed + f_rem)

                    combination_variables = f_vars_needed + f_rem

                    dom_list = []
                    for variable in combination_variables:
                        dom_list.append(self.domain["0_terms"])


                    combinations = [p for p in itertools.product(*dom_list)]

                    for c in combinations:
     
                        variable_assignments = {}

                        for variable_index in range(len(combination_variables)):
                            variable = combination_variables[variable_index]
                            value = c[variable_index]

                            variable_assignments[variable] = value

                        head_combination_list = list(c[:len(h_vars)])

                        head_combination = {}

                        for h_arg in h_args:
                            if h_arg in h_vars:
                                head_combination[h_arg] = variable_assignments[h_arg]
                            else:
                                head_combination[h_arg] = h_arg

                        head_combination_list_2 = []
                        for h_arg in h_args:
                            head_combination_list_2.append(head_combination[h_arg])

                        unfound_atom = f"r{self.counter}_unfound({','.join(head_combination_list_2)})"

                        body_combination = {}

                        for f_arg in arguments:
                            if f_arg in f_vars: # Is a variable
                                body_combination[f_arg] = variable_assignments[f_arg]
                            else: # Static
                                body_combination[f_arg] = f_arg 

                        left = ComparisonOperations.instantiate_operation(f.left, variable_assignments)
                        right = ComparisonOperations.instantiate_operation(f.right, variable_assignments)

                        unfound_comparison = ComparisonOperations.comparison_handlings(f.comparison, left, right)

                        unfound_body_list = []
                        for v in f_arguments_nd:
                            if v in rem:

                                #if not ComparisonOperations.compareTerms(f.comparison, f_args_unf_left, f_args_unf_right):
                                
                                body_combination_tmp = [body_combination[v]] + head_combination_list_2
                                body_predicate = f"r{self.counter}f_{v}({','.join(body_combination_tmp)})"
                                unfound_body_list.append(body_predicate)


                        if len(unfound_body_list) > 0:
                            unfound_body = f" {','.join(unfound_body_list)},"
                        else:
                            unfound_body = ""

                        unfound_rule = f"{unfound_atom} :-{unfound_body} not {unfound_comparison}."
                        self.printer.custom_print(unfound_rule)

                        if len(head_combination_list_2) > 0:
                            head_string = f"{head.name}({','.join(head_combination_list_2)})"
                        else:
                            head_string = f"{head.name}"

                        self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

                # -------------------------------------------
                # over every body-atom
                for f in self.cur_func:
                    if f != head:

                        

                        f_args_len = len(f.arguments)
                        f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                        f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                        f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                        f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                        #f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
                        f_vars_needed = h_vars

                        vars_set = frozenset(f_vars_needed + f_rem)

                        dom_list = []
                        for variable in f_vars_needed + f_rem:
                            values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                            dom_list.append(values)

                        combinations = [p for p in itertools.product(*dom_list)]

                        for c in combinations:
                            head_combination_list = list(c[:len(h_vars)])

                            head_combination = {}

                            head_counter = 0
                            for h_arg in h_args:
                                if h_arg in h_vars:
                                    head_combination[h_arg] = c[head_counter]
                                    head_counter += 1
                                else:
                                    head_combination[h_arg] = h_arg

                            head_combination_list_2 = []
                            for h_arg in h_args:
                                head_combination_list_2.append(head_combination[h_arg])

                            unfound_atom = f"r{self.counter}_unfound({','.join(head_combination_list_2)})"


                            # ---------
                            body_combination = {}

                            not_head_counter = len(h_vars)
                            for f_arg in f_args:
                                if f_arg in h_vars: # Variables in head
                                    index_head = h_vars.index(f_arg)
                                    body_combination[f_arg] = (c[index_head])
                                elif f_arg in f_vars: # Not in head variables
                                    body_combination[f_arg] = (c[not_head_counter])
                                    not_head_counter += 1
                                else: # Static
                                    body_combination[f_arg] = f_arg 
    

                            unfound_body_list = []
                            for v in f_args_nd:
                                if v in rem:
                                    body_combination_tmp = [body_combination[v]] + head_combination_list_2
                                    body_predicate = f"r{self.counter}f_{v}({','.join(body_combination_tmp)})"
                                    unfound_body_list.append(body_predicate)

                            unfound_predicate = f"{f.name}"
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
                            if not self.cur_func_sign[self.cur_func.index(f)]: # i.e. a ''positive'' occurence (e.g. q(X) :- p(X) -> p(X) is positive)
                                sign_adjusted_predicate = f"not {unfound_predicate}"
                            else: # i.e. a ''negative'' occurence (e.g. q(X) :- p(X), not p(1). -> p(1) is negative)
                                sign_adjusted_predicate = f"{unfound_predicate}"

                            
                            unfound_rule = f"{unfound_atom} :-{unfound_body} {sign_adjusted_predicate}."
                            self.printer.custom_print(unfound_rule)


                            if len(head_combination_list_2) > 0:
                                head_string = f"{head.name}({','.join(head_combination_list_2)})"
                            else:
                                head_string = f"{head.name}"

                            self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

        else: # found-check for ground-rules (if needed) (pred, arity, combinations, rule, indices)
            pred = str(node.head).split('(', 1)[0]
            arguments = re.sub(r'^.*?\(', '', str(node.head))[:-1].split(',')
            arity = len(arguments)
            arguments = ','.join(arguments)

            if pred in self.ng_heads and arity in self.ng_heads[pred] \
                    and not (pred in self.facts and arity in self.facts[pred] and arguments in self.facts[pred][arity]):

                for body_atom in node.body:
                    if str(body_atom).startswith("not "):
                        neg = ""
                    else:
                        neg = "not "
                    self.printer.custom_print(f"r{self.g_counter}_unfound({arguments}) :- "
                          f"{ neg + str(body_atom)}.")
                self._addToFoundednessCheck(pred, arity, [arguments.split(',')], self.g_counter, range(0,arity))
                self.g_counter = chr(ord(self.g_counter) + 1)
            # print rule as it is
            self._outputNodeFormatConform(node)

        self.counter += 1
        self.current_rule_position += 1
        self._reset_after_rule()
        return node

    def visit_Literal(self, node):
        if str(node) != "#false":
            if node.atom.ast_type is clingo.ast.ASTType.SymbolicAtom: # comparisons are reversed by parsing, therefore always using not is sufficient
                self.cur_func_sign.append(str(node).startswith("not "))
        self.visit_children(node)
        return node

    def visit_Function(self, node):

        if not self.current_comparison:
            # shows
            if node.name in self.shows:
                self.shows[node.name].add(len(node.arguments))
            else:
                self.shows[node.name] = {len(node.arguments)}

            node = node.update(**self.visit_children(node))
            self.cur_func.append(node)

        return node

    def visit_Variable(self, node):
        self.ng = True
        if (str(node) not in self.cur_var) and str(node) not in self.terms:
            if str(node) == '_':
                node = node.update(name=f"Anon{self.cur_anon}")
                self.cur_anon += 1
            self.cur_var.append(str(node))
        return node

    def visit_SymbolicTerm(self, node):
        return node

    def visit_Program(self, node):

        if node.name == 'rules':
            self.rules = True
        else:
            self.rules = False

        return node

    def visit_Comparison(self, node):
        # currently implements only terms/variables
        supported_types = [clingo.ast.ASTType.Variable, clingo.ast.ASTType.SymbolicTerm, clingo.ast.ASTType.BinaryOperation, clingo.ast.ASTType.UnaryOperation, clingo.ast.ASTType.Function]

        assert(node.left.ast_type in supported_types)
        assert (node.right.ast_type in supported_types)

        self.cur_comp.append(node)

        self.current_comparison = node

        self.visit_children(node)

        self.current_comparison = None

        return node

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

    def _generateCombinationInformation(self, h_args, f_vars_needed, c, head):

        interpretation = []  # interpretation-list
        interpretation_incomplete = []  # uncomplete; without removed vars
        nnv = []  # not needed vars
        combs_covered = []  # combinations covered with the (reduced combinations); len=1 when no variable is removed

        if h_args == ['']: # catch head/0
            return interpretation, interpretation_incomplete, [['']],  [str(h_args.index(v)) for v in h_args if v in f_vars_needed or v in self.terms]

        for id, v in enumerate(h_args):
            if v not in f_vars_needed and v not in self.terms:
                nnv.append(v)
            else:
                interpretation_incomplete.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)
            interpretation.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)

        head_interpretation = ','.join(interpretation)  # can include vars

        nnv = list(dict.fromkeys(nnv))

        if len(nnv) > 0:
            dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in nnv]
            combs_left_out = [p for p in itertools.product(*dom_list)]  # combinations for vars left out in head
            # create combinations covered for later use in constraints
            for clo in combs_left_out:
                covered = interpretation.copy()
                for id, item in enumerate(covered):
                    if item in nnv:
                        covered[id] = clo[nnv.index(item)]
                if head.name in self.facts and len(h_args) in self.facts[
                    head.name] and ','.join(covered) in self.facts[head.name][len(h_args)]:
                    # no foundation check for this combination, its a fact!
                    continue
                combs_covered.append(covered)
        else:
            if head.name in self.facts and len(h_args) in self.facts[head.name] and head_interpretation in \
                    self.facts[head.name][len(h_args)]:
                # no foundation check for this combination, its a fact!
                return None, None, None, None
            combs_covered.append(interpretation)

        index_vars = [str(h_args.index(v)) for v in h_args if v in f_vars_needed or v in self.terms]

        return interpretation, interpretation_incomplete, combs_covered, index_vars

    def _addToFoundednessCheck(self, pred, arity, combinations, rule, indices):
        indices = tuple(indices)

        for c in combinations:
            c = tuple(c)
            if pred not in self.f:
                self.f[pred] = {}
                self.f[pred][arity] = {}
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif arity not in self.f[pred]:
                self.f[pred][arity] = {}
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif c not in self.f[pred][arity]:
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif rule not in self.f[pred][arity][c]:
                self.f[pred][arity][c][rule] = {indices}
            else:
                self.f[pred][arity][c][rule].add(indices)

    def _outputNodeFormatConform(self, node):
        if str(node.head) == "#false":  # catch constraints and print manually since clingo uses #false
            self.printer.custom_print(f":- {', '.join(str(n) for n in node.body)}.")
        else:
            if len(node.body) > 0:
                if (str(node.head).startswith('{')):
                    self.printer.custom_print(f"{str(node.head)} :- {', '.join([str(b) for b in node.body])}.")
                else:
                    self.printer.custom_print(f"{str(node.head).replace(';', ',')} :- {', '.join([str(b) for b in node.body])}.")
            else:
                if (str(node.head).startswith('{')):
                    self.printer.custom_print(f"{str(node.head)}.")
                else:
                    self.printer.custom_print(f"{str(node.head).replace(';', ',')}.")

    def _add_atom_to_unfoundedness_check(self, head_string, unfound_atom):

        if head_string not in self.unfounded_rules:
            self.unfounded_rules[head_string] = {}

        if str(self.current_rule_position) not in self.unfounded_rules[head_string]:
            self.unfounded_rules[head_string][str(self.current_rule_position)] = []

        self.unfounded_rules[head_string][str(self.current_rule_position)].append(unfound_atom)



class TermTransformer(Transformer):
    def __init__(self, sub_doms, printer, no_show=False):
        self.terms = []
        self.sub_doms = sub_doms
        self.facts = {}
        self.ng_heads = {}
        self.ng = False
        self.show = False
        self.shows = {}
        self.no_show = no_show
        self.printer = printer

        self.current_head = None
        self.current_head_functions = []
        self.safe_variable_rules = {}

        self.domain = {}
        self.comparison_operators_variables = {}

        self.current_comparison = None
        self.current_function = None
        self.current_function_position = 0

        self.current_rule_position = 0

    def visit_Rule(self, node):
        self.current_head = node.head
        self.current_head_functions.append(str(node.head))

        self.visit_children(node)

        pred = str(node.head).split('(', 1)[0]
        arguments = re.sub(r'^.*?\(', '', str(node.head))[:-1].split(',')
        arity = len(arguments)

        if self.ng:
            self.ng = False
            if str(node.head) != "#false":
                # save pred and arity for later use
                if pred not in self.ng_heads:
                    self.ng_heads[pred] = {arity}
                else:
                    self.ng_heads[pred].add(arity)
        elif node.body.__len__() == 0:
            arguments = ','.join(arguments)
            if pred not in self.facts:
                self.facts[pred] = {}
                self.facts[pred][arity] = {arguments}
            elif arity not in self.facts[pred]:
                self.facts[pred][arity] = {arguments}
            else:
                self.facts[pred][arity].add(arguments)


        self.current_rule_position += 1
        self._reset_temporary_rule_variables()
        return node

    def visit_Aggregate(self, node):

        if str(node) == str(self.current_head):
            for elem in node.elements:
                self.current_head_functions.append(str(elem.literal))

        self.visit_children(node)

        return node


    def _reset_temporary_rule_variables(self):
        self.current_head = None
        self.current_head_functions = []

    def _reset_temporary_function_variables(self):
        self.current_function = None
        self.current_function_position = 0

    def _reset_temporary_comparison_variables(self):
        self.current_comparison = None

    def _add_symbolic_term_to_domain(self, identifier, position, value):
        """
            e.g. consider p(1,2).
            then one has to call this method twice:
            First Call:
                - p is the identifier
                - 0 is the position
                - 1 is the value
            Second Call:
                - p is the identifier
                - 1 is the position
                - 2 is the value
        """
        if str(identifier) not in self.domain:
            self.domain[str(identifier)] = {}

        if str(position) not in self.domain[str(identifier)]:
            self.domain[str(identifier)][str(position)] = []

        if str(value) not in self.domain[str(identifier)][str(position)]:
            self.domain[str(identifier)][str(position)].append(str(value))

        if "0_terms" not in self.domain:
            self.domain["0_terms"] = []

        if str(value) not in self.domain["0_terms"]:
            self.domain["0_terms"].append(str(value))

    def _add_safe_variable(self, identifier, position, value, safe_type):


        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = str(safe_type)
        to_add_dict["name"] = str(identifier)
        to_add_dict["position"] = str(position)

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)

    def _add_comparison_to_safe_variables(self, value, operation):

        arguments = ComparisonOperations.get_arguments_from_operation(operation)
        variables = []
        for argument in arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                variables.append(str(argument))

        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = "term"
        to_add_dict["variables"] = variables
        to_add_dict["operation"] = operation

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)


    def visit_Function(self, node):

        self.current_function = node

        # shows
        #if not str(node.name).startswith('_dom_'):
        if node.name in self.shows:
            self.shows[node.name].add(len(node.arguments))
        else:
            self.shows[node.name] = {len(node.arguments)}

        self.visit_children(node)

        self._reset_temporary_function_variables()

        return node

    def visit_Comparison(self, node):

        self.current_comparison = node

        if node.comparison == int(clingo.ast.ComparisonOperator.Equal):
            if node.left.ast_type == clingo.ast.ASTType.Variable:
                self._add_comparison_to_safe_variables(str(node.left), node.right)

            if node.right.ast_type == clingo.ast.ASTType.Variable: 
                self._add_comparison_to_safe_variables(str(node.right), node.left)
   
        self.visit_children(node)

        self._reset_temporary_comparison_variables()

        return node

    def _add_comparison(self, rule_name, variable, comparison):
        
        if rule_name not in self.comparison_operators_variables:
            self.comparison_operators_variables[rule_name] = {}

        if variable not in self.comparison_operators_variables[rule_name]:
            self.comparison_operators_variables[rule_name][variable] = []

        self.comparison_operators_variables[rule_name][variable].append(comparison)

    def visit_Variable(self, node):

        if self.current_function and str(self.current_function) not in self.current_head_functions:
            self._add_safe_variable(self.current_function.name, self.current_function_position, str(node), "function")
            self.current_function_position += 1

        if self.current_comparison:

            self._add_comparison(str(self.current_rule_position), str(node), self.current_comparison)

        self.ng = True
        return node

    def visit_Interval(self, node):

        if self.current_function: 
            for value in range(int(str(node.left)), int(str(node.right)) + 1):
                self._add_symbolic_term_to_domain(self.current_function.name, self.current_function_position, str(value))

            self.current_function_position += 1

        for i in range(int(str(node.left)), int(str(node.right))+1):
            if (str(i) not in self.terms):
                self.terms.append(str(i))

        return node

    def visit_SymbolicTerm(self, node):
       
        if self.current_function: 
            self._add_symbolic_term_to_domain(self.current_function.name, self.current_function_position, str(node))
            self.current_function_position += 1

        if (str(node) not in self.terms):
            self.terms.append(str(node))

        return node

    def visit_ShowSignature(self, node):
        self.show = True
        if not self.no_show:
            self.printer.custom_print(node)
        return node


class DomainTransformer(Transformer):

    def __init__(self, safe_variables_rules, domain, comparisons):
        self.safe_variables_rules = safe_variables_rules
        self.domain = domain
        self.comparisons = comparisons

        self.current_head = None
        self.variables_visited = {}

        self.current_function = None
        self.current_function_position = 0
        self.current_head_function = None
        self.current_head_functions = {}

        self.current_rule_position = 0

    def visit_Rule(self, node):

        self.current_head = node.head

        head = node.head
        if hasattr(node.head, "atom") and hasattr(node.head.atom,"symbol"):
            head = node.head.atom.symbol
        self.current_head_functions[str(node.head)] = head

        self.visit_children(node)

        self.current_rule_position += 1
        self._reset_temporary_rule_variables()
        return node

    def visit_Function(self, node):

        self.current_function = node

        if str(self.current_function) == str(self.current_head):
            self.current_head_function = node

        self.visit_children(node)

        self._reset_temporary_function_variables()
        return node

    def visit_Aggregate(self, node):

        if str(node) == str(self.current_head):
            for elem in node.elements:
                self.current_head_functions[str(elem.literal)] = elem.literal.atom.symbol # is the function
                
        self.visit_children(node)

        return node


    def visit_Variable(self, node):
        
        rule_is_in_safe_variables = str(self.current_rule_position) in self.safe_variables_rules
        if rule_is_in_safe_variables: #and str(node) not in self.variables_visited:
            self.variables_visited[str(node)] = 0


            if str(node) in self.safe_variables_rules[str(self.current_rule_position)]:
                safe_positions = self.safe_variables_rules[str(self.current_rule_position)][str(node)]

                if len(safe_positions) > 1: 
                    
                    for safe_position_index in range(len(safe_positions)): # Remove terms if len > 1
                        safe_position = safe_positions[safe_position_index]

                        if safe_position['type'] == 'term':
                            del safe_positions[safe_position_index]

                        safe_position_index -= 1


                new_domain = None
                all_variables_present = True

                for safe_position in safe_positions:

                    if safe_position["type"] == "function":
                        safe_pos_name = safe_position['name']
                        safe_pos_position = safe_position['position']


                        if safe_pos_name in self.domain and safe_pos_position in self.domain[safe_pos_name]:

                            cur_domain = set(self.domain[safe_pos_name][safe_pos_position])

                            if new_domain:
                                new_domain = new_domain.intersection(cur_domain)
                            else:
                                new_domain = cur_domain
                        else:
                            all_variables_present = False
                            break
                    elif safe_position["type"] == "term":

                        rule_name = str(self.current_rule_position)
                        variable_name = str(node)

                        variable_assignments = {}
            
                        all_variables_present = True


                        for variable in safe_position["variables"]:
                            new_domain_variable_name = f"term_rule_{rule_name}_variable_{variable}"
                            if new_domain_variable_name in self.domain:
                                variable_assignments[variable] = self.domain[new_domain_variable_name]['0']
                            else:
                                all_variables_present = False
                                break

                        if all_variables_present:
                            new_domain = ComparisonOperations.generate_domain(variable_assignments, safe_position["operation"])                       
                    else:
                        # not implemented
                        assert(False)

                # If there is a comparison like X < 5 one can make the domain smaller...
                if all_variables_present and str(self.current_rule_position) in self.comparisons and str(node) in self.comparisons[str(self.current_rule_position)]:
                    comparisons = self.comparisons[str(self.current_rule_position)][str(node)]

                    for comparison in comparisons:
                        if str(node) == str(comparison.left) and str(comparison.right).isdigit() and (comparison.comparison == int(clingo.ast.ComparisonOperator.LessThan) or comparison.comparison == int(clingo.ast.ComparisonOperator.LessEqual)):
                            new_domain = list(new_domain)


                            new_domain_index = 0

                            while new_domain_index < len(new_domain):

                                domain_element = new_domain[new_domain_index]
   
                                violates = False
 
                                if comparison.comparison == int(clingo.ast.ComparisonOperator.LessEqual):
                                    if int(domain_element) > int(str(comparison.right)):
                                        violates = True
  
                                if comparison.comparison == int(clingo.ast.ComparisonOperator.LessThan):
                                    if int(domain_element) >= int(str(comparison.right)):
                                        violates = True          

                                if violates:
                                    del new_domain[new_domain_index]

                                    new_domain_index -= 1

                                new_domain_index += 1
                            

                            new_domain = set(new_domain)

                if all_variables_present:
                    variable_is_in_head = self.current_function and str(self.current_function) in self.current_head_functions

                    new_position = self.current_function_position

                    if variable_is_in_head:
                        head = self.current_head_functions[str(self.current_function)]
                        new_name = head.name

                    rule_name = str(self.current_rule_position)
                    variable_name = str(node)
                    new_domain_variable_name = f"term_rule_{rule_name}_variable_{variable_name}"

                    for new_value in new_domain:
                        if variable_is_in_head:
                            self._add_symbolic_term_to_domain(new_name, new_position, new_value)
                       
                        self._add_symbolic_term_to_domain(new_domain_variable_name, '0', new_value)

        if self.current_function:
            self.current_function_position += 1

        return node


    def _add_symbolic_term_to_domain(self, identifier, position, value):
        """
            e.g. consider p(1,2).
            then one has to call this method twice:
            First Call:
                - p is the identifier
                - 0 is the position
                - 1 is the value
            Second Call:
                - p is the identifier
                - 1 is the position
                - 2 is the value
        """
        if str(identifier) not in self.domain:
            self.domain[str(identifier)] = {}

        if str(position) not in self.domain[str(identifier)]:
            self.domain[str(identifier)][str(position)] = []

        if str(value) not in self.domain[str(identifier)][str(position)]:
            self.domain[str(identifier)][str(position)].append(str(value))

        if "0_terms" not in self.domain:
            self.domain["0_terms"] = []

        if str(value) not in self.domain["0_terms"]:
            self.domain["0_terms"].append(str(value))

    def visit_SymbolicTerm(self, node):
       
        if self.current_function: 
            self.current_function_position += 1

        return node


    def _reset_temporary_rule_variables(self):
        self.current_head = None
        self.current_head_functions = {}
        self.variables_visited = {}

    def _reset_temporary_function_variables(self):
        self.current_function = None
        self.current_function_position = 0
        self.current_head_function = None


class ComparisonOperations:

    @classmethod
    def getCompOperator(cls, comp):
        if comp is int(clingo.ast.ComparisonOperator.Equal):
            return "="
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return "!="
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return ">="
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return ">"
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return "<="
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return "<"
        else:
            assert(False) # not implemented

    @classmethod
    def comparison_handlings(cls, comp, c1, c2):
        if comp is int(clingo.ast.ComparisonOperator.Equal): # == 5
            return f"{c1} = {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return f"{c1} != {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return f"{c1} >= {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return f"{c1} > {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return f"{c1} <= {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return f"{c1} < {c2}"
        else:
            assert(False) # not implemented


    @classmethod
    def compareTerms(cls, comp, c1, c2):
        if comp is int(clingo.ast.ComparisonOperator.Equal): # == 5
            return c1 == c2
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return c1 != c2
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return c1 >= c2
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return c1 > c2
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return c1 <= c2
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return c1 < c2
        else:
            assert(False) # not implemented

    @classmethod
    def get_arguments_from_operation(cls, root):
        """
            Performs a tree traversal of an operation (e.g. X+Y -> first ''+'', then ''X'' and lasylt ''Y'' -> then combines together)
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            return ComparisonOperations.get_arguments_from_operation(root.left) + ComparisonOperations.get_arguments_from_operation(root.right)

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            return ComparisonOperations.get_arguments_from_operation(root.argument)

        elif root.ast_type is clingo.ast.ASTType.Variable or root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return [root]
        elif root.ast_type is clingo.ast.ASTType.Function:

            argument_list = []

            for argument in root.arguments:
                argument_list += cls.get_arguments_from_operation(argument)

            return argument_list

        else:
            assert(False) # not implemented

    @classmethod
    def instantiate_operation(cls, root, variable_assignments):
        """
            Instantiates a operation and returns a string
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            string_rep = ComparisonOperations._get_binary_operator_type_as_string(root.operator_type)
    
            return "(" + ComparisonOperations.instantiate_operation(root.left, variable_assignments) + string_rep + ComparisonOperations.instantiate_operation(root.right, variable_assignments) + ")"

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            string_rep = ComparisonOperations._get_unary_operator_type_as_string(root.operator_type)

            if string_rep != "ABSOLUTE":
                return "(" + string_rep + ComparisonOperations.instantiate_operation(root.argument, variable_assignments) + ")"
            elif string_rep == "ABSOLUTE":
                return "(|" + ComparisonOperations.instantiate_operation(root.argument, variable_assignments) + "|)"

        elif root.ast_type is clingo.ast.ASTType.Variable:
            variable_string = str(root)
            return variable_assignments[variable_string]

        elif root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return str(root)

        elif root.ast_type is clingo.ast.ASTType.Function:

            instantiations = []
            for argument in root.arguments:
                instantiations.append(cls.instantiate_operation(argument, variable_assignments))

            return f"{root.name}({','.join(instantiations)})"

        else:
            assert(False) # not implemented

    @classmethod
    def _get_unary_operator_type_as_string(cls, operator_type):
        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return "-"
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return "~"
        elif operator_type == int(clingo.ast.UnaryOperator.Absolute): # Absolute, i.e. |X| needs special handling
            return "ABSOLUTE"
        else:
            print(f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

    @classmethod
    def _get_binary_operator_type_as_string(cls, operator_type):
        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return "^"
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return "?"
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return "&"
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return "+"
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return "-"
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return "*"
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return "/"
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return "\\"
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return "**"
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

       
    @classmethod                     
    def generate_domain(cls, variable_assignments, operation):

        if operation.ast_type == clingo.ast.ASTType.SymbolicAtom: 
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.SymbolicTerm:
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.Variable:
            return variable_assignments[str(operation.name)]
        elif operation.ast_type == clingo.ast.ASTType.UnaryOperation:
            return cls.generate_unary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.argument))
        elif operation.ast_type == clingo.ast.ASTType.BinaryOperation:
            return cls.generate_binary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.left), cls.generate_domain(variable_assignments, operation.right))
        else:
            print(operation)
            print(operation.ast_type)
            assert(False)

    @classmethod 
    def generate_unary_operator_domain(cls, operator_type, domain):

        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return cls.apply_unary_operation(domain, lambda d: -d)
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return cls.apply_unary_operation(domain, lambda d: ~d)
        elif operator_type == int(clingo.ast.UnaryOperator.Absolute): 
            return cls.apply_unary_operation(domain, lambda d: abs(d))
        else:
            print(f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented


    @classmethod
    def generate_binary_operator_domain(cls, operator_type, left_domain, right_domain):

        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l ^ r)
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l | r)
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l & r)
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l + r)
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l - r)
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l * r)
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l / r)
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l % r)
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: pow(l,r))
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

        assert(False) # not implemented

       
    @classmethod     
    def apply_unary_operation(domain, unary_operation):

        new_domain = {}

        for element in domain:
            res = unary_operation(element)

            if res not in new_domain:
                new_domain[res] = res

        return list(new_domain.keys())

    @classmethod
    def apply_binary_operation(cls, left_domain, right_domain, binary_operation):
    
        new_domain = {}

        for left in left_domain:
            for right in right_domain:
                res = binary_operation(int(left), int(right))

                if res not in new_domain:
                    new_domain[res] = res

        return list(new_domain.keys())


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
    newground = ClingoApp(sys.argv[0], no_show, ground_guess, ground)
    newground.main(clingo.Control(), [contents])


