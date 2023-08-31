
import re
import itertools



from ..comparison_tools import ComparisonTools
from .helper_part import HelperPart

class GenerateSatisfiabilityPart:

    def __init__(self, rule_head, current_rule_position, custom_printer, domain_lookup_dict, safe_variables_rules, rule_variables, rule_comparisons, rule_literals, rule_literals_signums):

        self.rule_head = rule_head
        self.current_rule_position = current_rule_position
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.safe_variables_rules = safe_variables_rules
        self.rule_variables = rule_variables
        self.rule_comparisons = rule_comparisons
        self.rule_literals = rule_literals
        self.rule_literals_signums = rule_literals_signums


    def generate_sat_part(self):

        self._generate_sat_variable_possibilities()

        covered_subsets = self._generate_sat_comparisons()

        self._generate_sat_functions(self.rule_head, covered_subsets)


    def _generate_sat_variable_possibilities(self):

        # MOD
        # domaining per rule variable
        for variable in self.rule_variables: # variables

            values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 

            disjunction = ""

            for value in values:
                disjunction += f"r{self.current_rule_position}_{variable}({value}) | "

            if len(disjunction) > 0:
                disjunction = disjunction[:-3] + "."
                self.printer.custom_print(disjunction)

            for value in values:
                self.printer.custom_print(f"r{self.current_rule_position}_{variable}({value}) :- sat.")



    def _generate_sat_comparisons(self):

        covered_subsets = {} # reduce SAT rules when compare-operators are pre-checked
        for f in self.rule_comparisons:

            left = f.term
            assert(len(f.guards) <= 1)
            right = f.guards[0].term
            comparison_operator = f.guards[0].comparison
                            
            symbolic_arguments = ComparisonTools.get_arguments_from_operation(left) +\
                ComparisonTools.get_arguments_from_operation(right)

            arguments = []
            for symbolic_argument in symbolic_arguments:
                arguments.append(str(symbolic_argument))

            var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
            vars = list (dict.fromkeys([a for a in arguments if a in self.rule_variables])) # which have to be grounded per combination
            dom_list = []
            for variable in vars:
                if str(self.current_rule_position) in self.safe_variables_rules and variable in self.safe_variables_rules[str(self.current_rule_position)]:

                    domain = HelperPart.get_domain_values_from_rule_variable(str(self.current_rule_position), variable, self.domain_lookup_dict, self.safe_variables_rules)
                        
                    dom_list.append(domain)
                else:
                    dom_list.append(self.domain_lookup_dict["0_terms"])

            combinations = [p for p in itertools.product(*dom_list)]

            for c in combinations:

                variable_assignments = {}
                
                for variable_index in range(len(vars)):
                    variable = vars[variable_index]
                    value = c[variable_index]

                    variable_assignments[variable] = value

                interpretation_list = []
                for variable in var:
                    if variable in vars:
                        interpretation_list.append(f"r{self.current_rule_position}_{variable}({variable_assignments[variable]})")

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
                    interpretation = f"{','.join(interpretation_list)}"

                    sat_atom = f"sat_r{self.current_rule_position}"

                    self.printer.custom_print(f"{sat_atom} :- {interpretation}.")

                    if sat_atom not in covered_subsets:
                        covered_subsets[sat_atom] = []

                    covered_subsets[sat_atom].append(interpretation_list)

        return covered_subsets

    def _generate_sat_functions(self, head, covered_subsets):

        for f in self.rule_literals:
            args_len = len(f.arguments)
            if (args_len == 0):
                self.printer.custom_print(
                    f"sat_r{self.current_rule_position} :-{'' if (self.rule_literals_signums[self.rule_literals.index(f)] or f is head) else ' not'} {f}.")
                continue
            arguments = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # all arguments (incl. duplicates / terms)
            var = list(dict.fromkeys(arguments)) if args_len > 0 else [] # arguments (without duplicates / incl. terms)
            vars = list (dict.fromkeys([a for a in arguments if a in self.rule_variables])) if args_len > 0 else [] # which have to be grounded per combination

            dom_list = []
            for variable in vars:
                values = HelperPart.get_domain_values_from_rule_variable(self.current_rule_position, variable, self.domain_lookup_dict, self.safe_variables_rules) 
                dom_list.append(values)

            combinations = [p for p in itertools.product(*dom_list)]

            for c in combinations:
                f_args = ""

                sat_atom = f"sat_r{self.current_rule_position}"

                sat_body_list = []
                sat_body_dict = {}
                for v in var:
                    if v in self.rule_variables:
                        body_sat_predicate = f"r{self.current_rule_position}_{v}({c[vars.index(v)]})"
                        sat_body_list.append(body_sat_predicate)
                        sat_body_dict[body_sat_predicate] = body_sat_predicate

                        f_args += f"{c[vars.index(v)]},"
                    else:
                        f_args += f"{v},"


                if f is head:
                    f_name = f"{f.name}{self.current_rule_position}"
                else:
                    f_name = f"{f.name}"

                if len(f_args) > 0:
                    f_args = f"{f_name}({f_args[:-1]})"
                else:
                    f_args = f"{f_name}"

                if sat_atom in covered_subsets:
                    possible_subsets = covered_subsets[sat_atom]
                    found = False

                    for possible_subset in possible_subsets:
                        temp_found = True
                        for possible_subset_predicate in possible_subset:
                            if possible_subset_predicate not in sat_body_dict:
                                temp_found = False
                                break

                        if temp_found == True:
                            found = True
                            break

                    if found == True:
                        continue


                if self.rule_literals_signums[self.rule_literals.index(f)] or f is head:
                    sat_predicate = f"{f_args}"
                else:
                    sat_predicate = f"not {f_args}"

                if len(sat_body_list) > 0:
                    body_interpretation = ",".join(sat_body_list) + ","
                else:
                    body_interpretation = ""
            
                self.printer.custom_print(f"{sat_atom} :- {body_interpretation}{sat_predicate}.")

