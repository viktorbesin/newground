from regression_tests.as_equiv_checker import EquivChecker

if __name__ == "__main__":
    checker = EquivChecker()
    (instance, encoding) = checker.parse()
    checker.start(instance, encoding, verbose = True)


