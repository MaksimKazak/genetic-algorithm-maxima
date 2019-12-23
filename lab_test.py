from ga_core import GACore
import ga_core
import functions

def run_test(func_name, expected, func, min_arg, max_arg):
    tester = GACore(func)
    result = tester.find_extremum(min_arg, max_arg)
    print("{0} for [{1}, {2}]".format(func_name, min_arg, max_arg))
    print("Expected: {0}".format(expected))
    print("Result x: {0}".format(str(result)))
    print("Result y: {0}".format(func(result)))
    print()

# Test suit
print("Running tests with next settings:")
print("Binary string length = " + str(ga_core.Chromosome.BIT_LEN))
print("Population = " + str(ga_core.GACore.POPULATION))
print("Mutation rate = " + str(ga_core.GACore.MUTATION_RATE))
print()

run_test("results", "1", functions.myf, 1, 25)

run_test("results", "-5", functions.myf, -25, 25)
