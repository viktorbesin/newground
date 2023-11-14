"""
The default output printer module contains the default output printer class.
It prints the output to stdout (unique, so it does not print two exact same lines of ASP code).
"""


class DefaultOutputPrinter:
    """
    The default output printer prints an ASP program to STDOUT,
    and takes care of printing it uniquely (no two exact same lines are printed).
    """

    def __init__(self):
        self.current_rule_hashes = {}

    def custom_print(self, string):
        """
        Prints a line of code, if not already printed.
        """
        string_hash = hash(string)

        if string_hash in self.current_rule_hashes:
            return

        # else: -> Print output
        self.current_rule_hashes[string_hash] = string_hash
        print(string)
