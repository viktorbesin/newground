

class RecursiveAggregateRewriting:
    
    #--------------------------------------------------------------------------------------------------------
    #------------------------------------ SUM-PART ----------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------
                      
    @classmethod
    def _add_sum_aggregate_rules(cls, aggregate):
        """
            Adds the necessary rules for the recursive sum aggregate.
        """

        new_prg_part = []

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        
        new_prg_part.append(f"#program {str_type}.")

        rule_string = f"{str_type}_ag{str_id}(S) :- "
       
        element_strings = []
        element_variables = [] 

        for element_id in range(len(aggregate["elements"])):
            element = aggregate["elements"][element_id]

            element_strings.append(f"{str_type}_ag{str_id}_elem{element_id}(S{element_id})")
            element_variables.append(f"S{element_id}")

        rule_string += ','.join(element_strings)

        rule_string += f", S = {'+'.join(element_variables)}."

        new_prg_part.append(rule_string)

        for element_id in range(len(aggregate["elements"])):

            element = aggregate["elements"][element_id]
            guard = aggregate["right_guard"]
            # Body
            body_head_def = f"body_ag{str_id}_elem{element_id}({','.join(element['terms'])})"
            body_head_def_terms = ','.join(element['terms'])

            # DRY VIOLATION START: DRY (Do Not Repeat) justification: Because it is only used here and writing a subroutine creates more overload than simply duplicating the code
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "1")
            body_head_1 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_1_def_terms = ','.join(term_strings_temp)
             
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "2")
            body_head_2 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_2_first = term_strings_temp[0]
            body_head_2_def_terms = ','.join(term_strings_temp)

            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "3")
            body_head_3 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            # DRY VIOLATION END

            if len(element['condition']) > 0:
                rule_string = f"{body_head_def} :- {','.join(element['condition'])}."
            else:
                rule_string = f"{body_head_def}."


            new_prg_part.append(rule_string)

            # Partial Sum Last

            rule_string = f"{str_type}_ag{str_id}_elem{element_id}(S) :- last_ag{str_id}_elem{element_id}({body_head_def_terms}), partial_{str_type}_ag{str_id}_elem{element_id}({body_head_def_terms},S)."
            new_prg_part.append(rule_string)

            # Partial Sum Middle

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}({body_head_2_def_terms},S2) :- next_ag{str_id}_elem{element_id}({body_head_1_def_terms},{body_head_2_def_terms}), partial_{str_type}_ag{str_id}_elem{element_id}({body_head_1_def_terms},S1), S2 = S1 + {body_head_2_first}, S2 <= {guard.term}."
            new_prg_part.append(rule_string)

            # Partial Sum First

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}({body_head_def_terms},S) :- first_ag{str_id}_elem{element_id}({body_head_def_terms}), S = {body_head_def_terms}."
            new_prg_part.append(rule_string)

            # not_last
            rule_string = f"not_last_ag{str_id}_elem{element_id}({body_head_1_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            new_prg_part.append(rule_string)

            # Last
            rule_string = f"last_ag{str_id}_elem{element_id}({body_head_def_terms}) :- {body_head_def}, not not_last_ag{str_id}_elem{element_id}({body_head_def_terms})."
            new_prg_part.append(rule_string)

            # not_next
            rule_string = f"not_next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_3}, {body_head_1} < {body_head_3}, {body_head_3} < {body_head_2}."
            new_prg_part.append(rule_string)

            # next
            rule_string = f"next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}, not not_next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms})."
            new_prg_part.append(rule_string)

            # not_first
            rule_string = f"not_first_ag{str_id}_elem{element_id}({body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            new_prg_part.append(rule_string)

            # first
            rule_string = f"first_ag{str_id}_elem{element_id}({body_head_1_def_terms}) :- {body_head_1}, not not_first_ag{str_id}_elem{element_id}({body_head_1_def_terms})."
            new_prg_part.append(rule_string)

            return new_prg_part

