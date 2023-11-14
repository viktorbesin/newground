"""
Helper class for the count and RELATED aggregates.
I.e., it implements some commonly used methods, used also by other aggregates.
"""


class CountAggregateHelper:
    """
    Helper class for the count aggregate.
    """

    @classmethod
    def generate_all_diff_predicates(cls, terms):
        """
        Generate the alldiff predicates.
        """

        helper_bodies = []
        for index_1 in range(len(terms)):
            for index_2 in range(index_1 + 1, len(terms)):
                helper_body = "0 != "

                if len(terms[index_1]) != len(terms[index_2]):
                    continue

                term_length = min(len(terms[index_1]), len(terms[index_2]))

                term_combinations = []
                for term_index in range(term_length):
                    first_term = terms[index_1][term_index]
                    second_term = terms[index_2][term_index]

                    if (
                        CountAggregateHelper.check_string_is_int(first_term) is False
                        and CountAggregateHelper.check_string_is_int(second_term)
                        is False
                    ):
                        term_combinations.append(f"({first_term} ^ {second_term})")

                helper_body = f"0 != {'?'.join(term_combinations)}"
                helper_bodies.append(helper_body)
        return helper_bodies

    @classmethod
    def all_diff_generator(cls, all_diff_list_terms, upper):
        """
        Method that generates all helper literals/comparisons for the alldiff/all_diff predicate.
        """

        all_diff_list = []
        for index_1 in range(upper):
            for index_2 in range(index_1 + 1, upper):
                first_list = all_diff_list_terms[index_1]
                second_list = all_diff_list_terms[index_2]

                for index_3 in range(len(first_list)):
                    first_item = first_list[index_3]
                    second_item = second_list[index_3]

                    all_diff_list.append(first_item + "!=" + second_item)

        return all_diff_list

    @classmethod
    def check_string_is_int(cls, string):
        """
        Method that checks whether a string can be converted to an integer.
        """
        try:
            int(string, 10)
            return True
        except ValueError:
            return False
