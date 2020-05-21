import random
from copy import copy
from deap import base, creator, tools
from ontology_file import MyOntology


class myGAoptimize:

    def __init__(self, my_onto, free_tasks):
        self.free_tasks = free_tasks
        self.n_pop = 100 # n_pop - number of individuals in population
        self.toolbox = self.create_toolbox(free_tasks,my_onto)
        # probability for crossover/mutating
        self.probab_crossing, self.probab_mutating = 0.5, 0.2

    # def __del__(self):
    #     print("удален из памяти")

    # def init_func(self, people, tasks):
    #     rez = list()
    #     t = 0
    #     while t < len(tasks):
    #         #choose other people until find condition with true
    #         pers = random.choice(people)
    #         his_role = pers.is_role_of
    #         # there is func onto_district
    #         if tasks[t].specialize in pers.know and \
    #                 tasks[t].have_priority in his_role[0].related_to and len(pers.assigned):
    #             # print("correct ", t, pers)
    #             t += 1
    #             rez.append(pers)
    #     return rez

    # !!! the comma in the return statement. This is because the fitness function
    # in DEAP is returned as a tuple to allow multi-objective fitness functions

    # создать набор инструментов с правильными параметрами
    def create_toolbox(self, tasks,my_onto):
        # args: name_new_class, base_class,attr_class:        v- maximize the 1 fitness/objective
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)  # gp.PrimitiveTree
        toolbox = base.Toolbox()
        #                args: alias, funct_assigned_to_alias
        toolbox.register("attr_pers", my_onto.init_func, tasks)
        toolbox.register("individual", tools.initIterate, creator.Individual,
                         toolbox.attr_pers)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        # Зарегистрировать оператор оценки
        toolbox.register("evaluate", my_onto.eval_func2)
        # Зарегистрировать оператор кроссовера
        toolbox.register("mate", tools.cxTwoPoint)  # gp.cxOnePoint
        # Зарегистрировать оператор мутации
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)  # gp.mutUniformin, expr = toolbox.attr_str, pset = )
        # Определить оператор для разведения
        toolbox.register("select", tools.selTournament, tournsize=3)
        # !!!!!!!!!some idea from screenshot. Decorate with instruments of GP
        # i don't need it because mate&mutate into population with each other
        # toolbox.decorate("mate", )
        return toolbox

    # Применить кроссовер и мутации на потомство
    def my_varAnd(self, toolbox, offspring, P_crossing, P_mutating):
        # Сначала клонировать выбранных лиц
        # ---             deepcopy isn't for my ontology class https://stackoverflow.com/questions/40659963/python-shallow-deep-copy-error
        offspring = list(map(copy, offspring))
        # Теперь примените кроссовер
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < P_crossing:
                toolbox.mate(child1, child2)
                # Удалить значение фитнеса ребенка
                del child1.fitness.values
                del child2.fitness.values
        # Теперь примените мутацию
        for mutant in offspring:
            if random.random() < P_mutating:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        pass

    # Оцените людей с недопустимой пригодностью
    def eval_invalid_ind(self, toolbox, offspring):
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        print('Evaluated', len(invalid_ind), 'individuals')
        pass

    def print_Statistic(self, population):
        fits = [ind.fitness.values[0] for ind in population]
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        print('\n Fitness\n', fits, sep='\t')
        print('\nMin =', min(fits), ', Max =', max(fits))
        print('Average =', round(mean, 2),
              ', Standard deviation откл. =', round(std, 2))
        '''
       stats_fit = tools.Statistics(lambda x: x.fitness.values)
       stats_size = tools.Statistics(len)
       mstats = tools.MultiStatistics(fitness=stats_fit, size = stats_size)
       #ключ и функция. Применен.ф-и к данным, по которым вычисляется статистика
       mstats.register("avg", np.mean)
       mstats.register("std", np.std)
       mstats.register("min", np.min)
       mstats.register("max", np.max)
       #отражают настройку одного из типов эволюционных алгоритмов
       population, log = algorithms.eaSimple(population, toolbox,
                          probab_crossing, probab_mutating, number_gen,
                          #Объект статистики, который обновляется на месте
                          stats = mstats, 
                          #будет содержать лучших людей,
                          halloffame = tools.HallOfFame(1),
                          #стоит ли регистрировать статистику
                          verbose = True)
       '''
        pass

    def main(self):
        num_gen=0 # num_gen -  max number of generations for stopping condition
        random.seed()
        population = self.toolbox.population(self.n_pop)
        print('Evolution process starts')
        # Оцените все население
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        print('\nСозданное (Evaluated)', len(population), 'individuals')
        print('and individuals:')
        i_pop = 0
        for pop in population:
            print(f"{i_pop+1}) {pop}")
            i_pop += 1
        fits = [ind.fitness.values[0] for ind in population]
        while num_gen < 50 and \
                max(fits) < len(self.free_tasks) * 3:
            # for g in range(num_gen):
            num_gen += 1
            print("\n- Generation ", num_gen)
            # Выбор людей следующего поколения
            offspring = self.toolbox.select(population, len(population))
            # Применить кроссовер и мутации на потомство
            self.my_varAnd(self.toolbox, offspring,
                           self.probab_crossing, self.probab_mutating)
            # Оцените людей с недопустимой пригодностью –
            self.eval_invalid_ind(self.toolbox, offspring)
            # Теперь замените население на следующее поколение людей –
            population[:] = offspring
            # Распечатать статистику по текущим поколениям
        self.print_Statistic(population)
        print("\n- Evolution ends -")
        # Распечатать окончательный вывод.
        # Select the 1 best individuals
        best_ind = tools.selBest(population, 1)[0]
        print('\nBest individual:\n', best_ind)
        return best_ind
#
# if __name__ == "__main__":
#onto = MyOntology()
#ga = myGAoptimize(onto, onto.new_tasks)
#rez = self.main()
#print("Finish !!!!!!! \n\t",rez)
