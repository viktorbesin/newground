
import itertools
import re

from .helper_part import HelperPart



class GuessHeadPart:

    def __init__(self, rule_head, current_rule_position, custom_printer, domain_lookup_dict, safe_variables_rules, rule_variables, rule_comparisons, rule_literals, rule_literals_signums, current_rule, strongly_connected_components, ground_guess, unfounded_rules):

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
                 
    def guess_head(self):

        if self.current_rule in self.rule_strongly_restricted_components:

            string_preds = ",".join([str(predicate) for predicate in self.rule_strongly_restricted_components[self.current_rule]])

            additional_arguments = f" :- {string_preds}."
        else:
            additional_arguments = "."

        new_head_name = self.rule_head.name + "'"
        new_arguments = ",".join([str(argument) for argument in self.rule_head.arguments])

        new_head = f"{new_head_name}({new_arguments})"

        # head
        h_args_len = len(self.rule_head.arguments)
        h_args = re.sub(r'^.*?\(', '', str(self.rule_head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
        h_args_nd = list(dict.fromkeys(h_args)) # arguments (without duplicates / incl. terms)
        h_vars = list(dict.fromkeys(
            [a for a in h_args if a in self.rule_variables]))  # which have to be grounded per combination


        rem = [v for v in self.rule_variables if
               v not in h_vars]  # remaining variables not included in head atom (without facts)

        # GUESS head
        if self.ground_guess:  
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
                self.printer.custom_print(f"{{{new_head} : {','.join(domains)}}} {additional_arguments}")
            else:
                self.printer.custom_print(f"{{{new_head}}} {additional_arguments}")

            self.printer.custom_print(f"{str(self.rule_head)} :- {new_head}.")

