
class DefaultOutputPrinter:

    def __init__(self):
        self.current_rule_hashes = {}

    def custom_print(self, string):

        string_hash = hash(string)

        if string_hash in self.current_rule_hashes:
            return
        else:
            self.current_rule_hashes[string_hash] = string_hash
            print(string)

