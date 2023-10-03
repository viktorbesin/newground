from clingo import Function

from ..cyclic_strategy import CyclicStrategy

class LevelMappingsPart:

    def __init__(self, custom_printer, domain_lookup_dict, strongly_connected_components_predicates, ground_guess, cyclic_strategy, scc_rule_functions_scc_lookup):
                 
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.strongly_connected_components_predicates = strongly_connected_components_predicates
        self.ground_guess = ground_guess
        self.cyclic_strategy = cyclic_strategy
        self.scc_rule_functions_scc_lookup = scc_rule_functions_scc_lookup
                 
    def generate_level_mappings(self):
        if self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING or self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING_AAAI:

            scc_predicates_per_scc_key = {}
            for rule in self.scc_rule_functions_scc_lookup.keys():
                dic = self.scc_rule_functions_scc_lookup[rule]
                if dic['scc_key'] not in scc_predicates_per_scc_key:
                    scc_predicates_per_scc_key[dic['scc_key']] = []

                scc_predicates_per_scc_key[dic['scc_key']] += dic['body']
                scc_predicates_per_scc_key[dic['scc_key']] += dic['head']


            #for scc_key in self.strongly_connected_components_predicates.keys():
            for scc_key in scc_predicates_per_scc_key.keys():

                #scc = self.strongly_connected_components_predicates[scc_key]

                # The following few lines make the nodes unique according to their name
                # Sort them
                # And create unique variable names
                scc = list(set(scc_predicates_per_scc_key[scc_key]))
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
                    new_scc.append(Function(name=head_name,arguments=arguments))

                scc = new_scc

                if self.ground_guess:
                    raise Exception("not implemented")
                else:

                    # Create rules (20)
                    for index_1 in range(len(scc)):
                        for index_2 in range(index_1 + 1, len(scc)):
                        #for index_2 in range(len(scc)):
                            #    if index_1 == index_2:
                            #        continue
                            p1 = str(scc[index_1])
                            p2 = str(scc[index_2])

                            variables_p1 = ((p1.split("(")[1])[:-1]).split(",")
                            new_variables_p1 = [variable + "_1" for variable in variables_p1]
                            #new_variables_p1 = [variable for variable in variables_p1]

                            variables_p2 = ((p2.split("(")[1])[:-1]).split(",")
                            new_variables_p2 = [variable + "_2" for variable in variables_p2]
                            #new_variables_p2 = [variable for variable in variables_p2]

                            np1 = scc[index_1].name + "(" + ",".join(new_variables_p1) + ")"
                            np2 = scc[index_2].name + "(" + ",".join(new_variables_p2) + ")"

                            doms1 = [f"dom({var})" for var in new_variables_p1]
                            doms2 = [f"dom({var})" for var in new_variables_p2]

                            self.printer.custom_print(f"1 <= {{prec({np1},{np2});prec({np2},{np1})}} <= 1 :- {','.join(doms1)}, {','.join(doms2)}.")

                    # Create rules (21)
                    for index_1 in range(len(scc)):
                        for index_2 in range(len(scc)):
                            if index_1 == index_2:
                                continue

                            for index_3 in range(len(scc)):
                                if index_1 == index_3 or index_2 == index_3:
                                    continue

                                p1 = str(scc[index_1])
                                p2 = str(scc[index_2])
                                p3 = str(scc[index_3])

                                variables_p1 = ((p1.split("(")[1])[:-1]).split(",")
                                new_variables_p1 = [variable + "_1" for variable in variables_p1]
                                #new_variables_p1 = [variable for variable in variables_p1]

                                variables_p2 = ((p2.split("(")[1])[:-1]).split(",")
                                new_variables_p2 = [variable + "_2" for variable in variables_p2]
                                #new_variables_p2 = [variable for variable in variables_p2]

                                variables_p3 = ((p3.split("(")[1])[:-1]).split(",")
                                new_variables_p3 = [variable + "_3" for variable in variables_p3]
                                #new_variables_p3 = [variable for variable in variables_p3]

                                np1 = scc[index_1].name + "(" + ",".join(new_variables_p1) + ")"
                                np2 = scc[index_2].name + "(" + ",".join(new_variables_p2) + ")"
                                np3 = scc[index_3].name + "(" + ",".join(new_variables_p3) + ")"
                                
                                doms1 = [f"dom({var})" for var in new_variables_p1]
                                doms2 = [f"dom({var})" for var in new_variables_p2]
                                doms3 = [f"dom({var})" for var in new_variables_p3]

                                self.printer.custom_print(f":- {','.join(doms1)}, {','.join(doms2)}, {','.join(doms3)}, prec({np1},{np2}), prec({np2},{np3}), prec({np3},{np1}).")
