class CountAggregateHelper:
    
    @classmethod
    def all_diff_generator(cls, all_diff_list_terms, upper):
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
        try:
            a = int(string, 10)
            return True
        except ValueError:
            return False
