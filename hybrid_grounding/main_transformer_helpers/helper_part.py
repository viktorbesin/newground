
class HelperPart:

    @classmethod
    def get_domain_values_from_rule_variable(cls, rule, variable, domain, safe_variables_rules):
        """ 
            Provided a rule number and a variable in that rule, one gets the domain of this variable.
            If applicable it automatically calculates the intersection of different domains.
        """

        if "0_terms" not in domain:
            # If no domain could be inferred
            raise Exception("A domain must exist when calling this method!")

        possible_domain_value_name = f"term_rule_{str(rule)}_variable_{str(variable)}"
        if possible_domain_value_name in domain:
            return domain[possible_domain_value_name]['0']

        if str(rule) not in safe_variables_rules:
            return domain["0_terms"]

        if str(variable) not in safe_variables_rules[str(rule)]:
            return domain["0_terms"]

        total_domain = None

        for domain_type in safe_variables_rules[str(rule)][str(variable)]:
       
            if domain_type["type"] == "function":
                domain_name = domain_type["name"]
                domain_position = domain_type["position"]

                if domain_name not in domain:
                    return domain["0_terms"]

                if domain_position not in domain[domain_name]:
                    return domain["0_terms"]

                cur_domain = domain[domain_name][domain_position]

                if total_domain:
                    total_domain = total_domain.intersection(set(cur_domain))
                else:
                    total_domain = set(cur_domain)

        return list(total_domain)

    @classmethod
    def ignore_exception(cls, IgnoreException=Exception,DefaultVal=None):
        """ Decorator for ignoring exception from a function
        e.g.   @ignore_exception(DivideByZero)
        e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
        """
        def dec(function):
            def _dec(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except IgnoreException:
                    return DefaultVal
            return _dec
        return dec
