
import itertools
import re

from clingo import Function

from .helper_part import HelperPart

from ..cyclic_strategy import CyclicStrategy



class GuessHeadPart:

    def __init__(self, rule_head, current_rule_position, custom_printer, domain_lookup_dict, safe_variables_rules, rule_variables, rule_comparisons, rule_literals, rule_literals_signums, current_rule, strongly_connected_components, ground_guess, unfounded_rules, cyclic_strategy,predicates_strongly_connected_comps):

        self.rule_head = rule_head
        self.current_rule_position = current_rule_position
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.safe_variables_rules = safe_variables_rules
        self.rule_variables = rule_variables
        self.rule_comparisons = rule_comparisons
        self.rule_literals = rule_literals
        self.rule_literals_signums = rule_literals_signums
        self.current_rule = current_rule
        self.rule_strongly_restricted_components = strongly_connected_components
        self.ground_guess = ground_guess
        self.unfounded_rules = unfounded_rules
        self.cyclic_strategy = cyclic_strategy
        self.predicates_strongly_connected_comps = predicates_strongly_connected_comps
                 
    def guess_head(self):

        if self.current_rule in self.rule_strongly_restricted_components and self.cyclic_strategy == CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES:
            string_preds = ",".join([str(predicate) for predicate in self.rule_strongly_restricted_components[self.current_rule]])
            cyclic_behavior_arguments = f" :- {string_preds}."
        else:
            cyclic_behavior_arguments = "."

        new_head_name = f"{self.rule_head.name}{self.current_rule_position}"
        new_arguments = ",".join([str(argument) for argument in self.rule_head.arguments])

        new_head = f"{new_head_name}({new_arguments})"

        h_args_len = len(self.rule_head.arguments)
        h_args = re.sub(r'^.*?\(', '', str(self.rule_head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
        h_vars = list(dict.fromkeys(
            [a for a in h_args if a in self.rule_variables]))  # which have to be grounded per combination

        if self.ground_guess:  
            if self.cyclic_strategy == CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES:
                print("NOT IMPLEMENTED!")
                raise Exception("Not Implemented!")

            dom_list = [HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) for variable in h_vars]
            combinations = [p for p in itertools.product(*dom_list)]

            h_argument_interpretations = [f"({','.join(c[h_vars.index(a)] if a in h_vars else a for a in h_args)})" for c in combinations]
            h_new_interpretations = [f"{new_head_name}{h_argument_interpretation}" for h_argument_interpretation in h_argument_interpretations]

            if h_args_len > 0:
                self.printer.custom_print(f"{{{';'.join(h_new_interpretations)}}}.")

                for h_argument_interpretation in h_argument_interpretations:
                    self.printer.custom_print(f"{self.rule_head.name}{h_argument_interpretation} :- {new_head_name}{h_argument_interpretation}.")

            else:
                self.printer.custom_print(f"{{{new_head_name}}}")
                self.printer.custom_print(f"{self.rule_head.name} :- {new_head_name}.")

        else:
            domains = []
            for variable in h_vars:
                domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")
                values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                for value in values:
                    self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{variable}({value}).")

            if len(domains) > 0:
                self.printer.custom_print(f"{{{new_head} : {','.join(domains)}}} {cyclic_behavior_arguments}")
            else:
                self.printer.custom_print(f"{{{new_head}}} {cyclic_behavior_arguments}")


            # Simple search for SCC KEY
            found_scc_key = -1

            for scc_key in self.predicates_strongly_connected_comps.keys():
                for pred in self.predicates_strongly_connected_comps[scc_key]:
                    if str(pred) == str(self.rule_head) or str(pred) == str(self.rule_head.name):
                        found_scc_key = scc_key
                        break

            if found_scc_key < 0:
                raise Exception("COULD NOT FIND SCC KEY")
            
            new_head_func = Function(name=new_head_name,arguments=[Function(arg_) for arg_ in new_arguments])

            self.predicates_strongly_connected_comps[found_scc_key].append(new_head_func)

            self.printer.custom_print(f"{str(self.rule_head)} :- {new_head}.")

