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

    def combine(self, other, dots):
        '''print("Given: {0}, {1}".format(self, other));'''
        if not len(dots):
            raise ValueError("'dots' should contain 1 or more dots")

        dot_lst = sorted(dots)
        dot_idx = 0
        curr_chrm = self
        next_chrm = other
        new_code = 0
        
        new_code = curr_chrm.code

        while dot_idx < len(dot_lst):
            pos_in_code = dot_lst[dot_idx] % Chromosome.BIT_LEN
            self.combineCode(next_chrm, pos_in_code)
			
            curr_chrm, next_chrm = next_chrm, curr_chrm
            dot_idx += 1
        '''print("Combined: {0}".format(self));'''
        return Chromosome(self.min_limit, self.max_limit, code = new_code)
					  
    def combineCode(self, other, bit_pos):
        '''bit_pos is position starting from left'''
        if 0 <= bit_pos < Chromosome.BIT_LEN:
            other_mask = 2 ** (Chromosome.BIT_LEN - bit_pos) - 1
            other_part = other.code & other_mask
            self_mask = Chromosome.MAX_VALUE - other_mask
            self_part = self.code & self_mask
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
    '''
    Genetic algorithm runner. Works with specified function and
    specified number of function arguments (number of genes).
    '''
    MUTATION_RATE = 0.05
    POPULATION = 100
    ELITISM_RATE = 0.1
    BEST_PARENTS = round(POPULATION * ELITISM_RATE)
    MAX_COUNTS = 5
    
    def __init__(self, func):
        self.func = func
        self.generation = []
        self.best_descendant = None

    def find_extremum(self, min_value, max_value):
        self._create_new_generation(min_value, max_value)
        self.best_descendant = self.generation[random.randint(0, GACore.POPULATION - 1)]
        self._count_and_set_population_fitness(self.generation)
        counter = 0
        best_one = self.best_descendant

        while counter < GACore.MAX_COUNTS:
            selected = self._tournament_select()
            new_generation = self._cross_over(selected)
            new_generation += self._best_parents()
            self._mutate(new_generation, min_value, max_value)
            self._count_and_set_population_fitness(new_generation)
            best_one = sorted(new_generation, key=lambda chrm: chrm.fitness, reverse = True)[0]
            if best_one.fitness > self.best_descendant.fitness:
                self.best_descendant = best_one
                counter = 0
            else:
                counter += 1
            self.generation = new_generation
            
        return self.best_descendant.get_limited_values()
        

    def _create_new_generation(self, min_val, max_val):
        self.generation.clear()
        for i in range(GACore.POPULATION):
            self.generation.append(Chromosome(min_val, max_val))

    def _count_and_set_fitness(self, chrm):
        chrm.fitness = self.func(chrm.get_limited_values())

    def _count_and_set_population_fitness(self, generation):
        for chrm in generation:
            self._count_and_set_fitness(chrm)

    def _tournament_select(self):
        selected = []
        for i in range(GACore.POPULATION):
            applicants = (random.choice(self.generation) for i in range(2))
            selected.append(min(applicants, key=lambda chrm: chrm.fitness))
        return selected

    def _combine_randomly(self, chrm1, chrm2):
        point1 = random.randint(1, Chromosome.BIT_LEN - 2)
        point2 = random.randint(point1, Chromosome.BIT_LEN - 1)
        return chrm2.combine(chrm1, [point1, point2])

    def _cross_over(self, selected):
        new_generation = []
        for i in range(GACore.POPULATION - GACore.BEST_PARENTS):
            father = random.choice(selected)
            mother = random.choice(selected)
            new_generation.append(self._combine_randomly(father, mother))
        return new_generation

    def _best_parents(self):
        return sorted(self.generation, key=lambda chrm: chrm.fitness, reverse = True)[0:GACore.BEST_PARENTS]

    def _mutate(self, new_generation, min_value, max_value):
        if random.random() < GACore.MUTATION_RATE:
            chrm_idx = random.randint(0, GACore.POPULATION - 1)
            mutagen = Chromosome(min_value, max_value)
            mutant = self._combine_randomly(self.generation[chrm_idx], mutagen)
            self.generation[chrm_idx] = mutant
            
