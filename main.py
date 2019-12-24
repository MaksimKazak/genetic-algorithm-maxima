import random
import math

class Chromosome:
    BIT_LEN = 32
    MIN_VALUE = 0
    MAX_VALUE = 2 ** BIT_LEN - 1

    def __init__(self, min_limit, max_limit, code = None):
        self.min_limit = min_limit
        self.max_limit = max_limit
        if code:
            self.code = code
        else:
            self.code = self._fill_randomly()
        self.fitness = None
		
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, number):
        if number < Chromosome.MIN_VALUE or number > Chromosome.MAX_VALUE:
            raise ValueError("Wrong value for chromosome: " + str(number))
        self._code = number

    def _fill_randomly(self):
        return random.randint(Chromosome.MIN_VALUE, Chromosome.MAX_VALUE)

    def get_limited_values(self):
        limits_interval = self.max_limit - self.min_limit
        limited = self.code * limits_interval / (Chromosome.MAX_VALUE + 1) + self.min_limit
        return limited

    def combine(self, other, bit_positions):
        '''print("Given: {0}, {1}".format(self, other));'''

        curr_chrm = self
        next_chrm = other
        new_code = 0
        
        new_code = curr_chrm.code

        for index in range(len(bit_positions)):
            bit_pos = bit_positions[index]
            curr_chrm.combineCode(next_chrm, bit_pos)
            curr_chrm, next_chrm = next_chrm, curr_chrm
        '''print("Combined: {0}".format(self));'''
        return Chromosome(curr_chrm.min_limit, curr_chrm.max_limit, new_code)
					  
    def combineCode(self, other, bit_pos):
        '''bit_pos is position starting from left'''
        if 0 <= bit_pos < Chromosome.BIT_LEN:
            self_mask = (1 << bit_pos) - 1
            other_mask = ~self_mask
            self_part = self.code & self_mask
            other_part = other.code & other_mask
            self.code = self_part + other_part
    
    def __str__(self):
        bin_str = []
        rest = self.code
        rated_value = 2 ** (Chromosome.BIT_LEN - 1)
        for i in range(Chromosome.BIT_LEN):
            if rest // rated_value:
                bin_str.append('1')
                rest -= rated_value
            else:
                bin_str.append('0')
            rated_value = rated_value // 2
        return ''.join(bin_str)


class GACore:
    MUTATION_RATE = 0.05
    POPULATION = 100

    SELECTION_AMOUNT = 10
    CHILDREN_AMOUNT = 20

    MAX_ITERATIONS = 50
    
    def __init__(self, func):
        self.func = func
        self.generation = []
        self.best_descendant = None
        self.min_val = 0
        self.max_val = 1
        

    def find_extremum(self, min_value, max_value):
        self.min_val = min_value
        self.max_val = max_value
        self._create_new_generation(min_value, max_value)
        self._count_and_set_population_fitness(self.generation)
        self.best_descendant = sorted(self.generation, key=lambda chrm: chrm.fitness, reverse = True)[0]
        best_one = self.best_descendant
		
        counter = 0
        while counter < GACore.MAX_ITERATIONS:
            selected = self._roulette_select()
            if len(selected):
                new_generation = self._cross_over(selected)
            else:
                new_generation = []
            self._mutate(new_generation, min_value, max_value)
            new_generation += self.generation
            self._count_and_set_population_fitness(new_generation)
            new_generation = self._best_population(new_generation)
            best_one = sorted(new_generation, key=lambda chrm: chrm.fitness, reverse = True)[0]
            if best_one.fitness > self.best_descendant.fitness:
                self.best_descendant = best_one
                counter = 0
            else:
                counter += 1
            self.generation = new_generation


        return self.best_descendant.get_limited_values()
        
    def _check_unique(self, generation, chrm):
        array = map(lambda x: x.code, generation)
        if chrm.code in array:
            return False
        return True

    def _create_new_generation(self, min_val, max_val):
        self.generation.clear()
        for i in range(GACore.POPULATION):
            chrm = Chromosome(min_val, max_val)
            if self._check_unique(self.generation, chrm):
                self.generation.append(chrm)
            else:
                i -= 1


    def _roulette_select(self):
        selected = []
        gen_sum = sum([c.fitness for c in self.generation])
        for i in range(GACore.SELECTION_AMOUNT):
            pick = random.uniform(0, gen_sum)
            current = 0
            curr_chrm = Chromosome(self.min_val, self.max_val)
            for chrm in self.generation:
                current += chrm.fitness
                if current > pick:
                    curr_chrm = chrm
                    break
            selected.append(curr_chrm)
        return selected

    def _tournament_select(self):
        selected = []
        for i in range(GACore.SELECTION_AMOUNT):
            applicants = (random.choice(self.generation) for i in range(2))
            selected.append(max(applicants, key=lambda chrm: chrm.fitness))
        return selected

    def _cross_over(self, selected):
        new_generation = []
        for i in range(GACore.CHILDREN_AMOUNT):
            father = random.choice(selected)
            mother = random.choice(selected)
            combined = self._combine_randomly(father, mother)
            if self._check_unique(new_generation, combined) and self._check_unique(self.generation, combined):
                new_generation.append(combined)
        return new_generation
		
    def _combine_randomly(self, chrm1, chrm2):
        bit_pos1 = random.randint(1, Chromosome.BIT_LEN - 2)
        bit_pos2 = random.randint(bit_pos1, Chromosome.BIT_LEN - 1)
        return chrm2.combine(chrm1, [bit_pos1, bit_pos2])

    def _mutate(self, generation, min_value, max_value):
        if random.random() < GACore.MUTATION_RATE and len(generation):
            chrm_idx = random.randint(0, len(generation) - 1)
            bit_pos = random.randint(0, Chromosome.BIT_LEN - 1)
            generation[chrm_idx].code = generation[chrm_idx].code ^ (1 << bit_pos)
            self._count_and_set_fitness(generation[chrm_idx])
	
    def _best_population(self, generation):
        return sorted(generation, key=lambda chrm: chrm.fitness, reverse = True)[0:GACore.POPULATION]		
			
    def _count_and_set_fitness(self, chrm):
        chrm.fitness = self.func(chrm.get_limited_values())

    def _count_and_set_population_fitness(self, generation):
        for chrm in generation:
            self._count_and_set_fitness(chrm)


def myf(x):
    return - (x + 5)**2 + 5

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
print("Binary string length = " + str(Chromosome.BIT_LEN))
print("Population = " + str(GACore.POPULATION))
print("Mutation rate = " + str(GACore.MUTATION_RATE))
print()

run_test("results", "1", myf, 1, 25)

run_test("results", "-5", myf, -25, 25)
