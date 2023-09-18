

class SumAggregateHelper:

    @classmethod
    def _generate_sum_up_predicates(cls, terms, current_number_of_predicate_tuples_considered, total_sum_value):
        sum_up_predicates = []

        sum_up_list = [terms[index][0] for index in range(current_number_of_predicate_tuples_considered)]
        my_helper_sum = f"{total_sum_value} <= {'+'.join(sum_up_list)}"
        sum_up_predicates.append(my_helper_sum)

        return sum_up_predicates