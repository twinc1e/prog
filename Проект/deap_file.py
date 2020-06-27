import random
from copy import copy
from deap import base, creator, tools, algorithms
#from ontology_file import MyOntology
import numpy as np


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
        toolbox.register("mate", tools.cxTwoPoint)
        # Зарегистрировать оператор мутации
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)  # gp.mutUniformin, expr = toolbox.attr_str, pset = )
        # Определить оператор для разведения
        toolbox.register("select", tools.selRandom)#selTournament, tournsize=2)
        # !!!!!!!!!some idea from screenshot. Decorate with instruments of GP
        # i don't need it because mate&mutate into population with each other
        # toolbox.decorate("mate", )
        return toolbox

    # Применить кроссовер и мутации на потомство
    def my_varAnd(self, toolbox, offspring, P_crossing, P_mutating):
        # Сначала клонировать выбранных лиц
        # ---             deepcopy isn't for my ontology class https://stackoverflow.com/questions/40659963/python-shallow-deep-copy-error
        offspring = list(map(copy, offspring))
        count = 0
        # Теперь примените кроссовер
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < P_crossing:
                toolbox.mate(child1, child2)
                count+=1
                # Удалить значение фитнеса ребенка
                del child1.fitness.values
                del child2.fitness.values
        print('num mates ',count)
        # Теперь примените мутацию
        count = 0
        for mutant in offspring:
            if random.random() < P_mutating:
                toolbox.mutate(mutant)
                count+=1#print('mutant ',len(mutant),end=' ')
                del mutant.fitness.values
        print('num mutants ',count)
        pass

    # Назначить новый фитнес индивидам
    def eval_ind(self, toolbox, offspring):
        new_ind = [ind for ind in offspring if not ind.fitness.valid]
        #new_valid = [ind for ind in offspring if ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, new_ind))# map - итератор, где ф-ю к каждому эл-ту последоватетельности без циклов
        #fitnesses_v = map(toolbox.evaluate,new_valid)
        #tmp = {i:fitnesses.count(i) for i in fitnesses} #without duplicates
        fitt = list(map(tuple.__getitem__,fitnesses,[0]*82))
        #fits_v = list(map(tuple.__getitem__,list(fitnesses_v),[0]*82))
        for ind, fit in zip(new_ind, fitnesses):# zip - пара элементов
            ind.fitness.values = fit
            # if fit in tmp.:
            #     invalid_ind.remove(ind)
            #print('fit',fit,end=',')
        print('Evaluated', len(new_ind), 'individuals with ', len(set(fitt)),
              'difference fit')#\n\t\tand max fit = ', max(set(fitt)))  # '\n',set(fits_v))
        pass

    def print_Statistic(self, population):
        fits = [ind.fitness.values[0] for ind in population]
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        #print('\n Fitness\n', fits, sep='\t')
        print('\nMin =', min(fits), ', Max =', max(fits))
        print('Average =', round(mean, 2),
              ', Standard deviation откл. =', round(std, 2))

    def base_Statistics (self,pop):
        stats_fit = tools.Statistics(lambda x: x.fitness.values)
        stats_size = tools.Statistics(len)
        mstats = tools.MultiStatistics(fitness=stats_fit, size = stats_size)
        #ключ и функция. Применен.ф-и к данным, по которым вычисляется статистика
        mstats.register("avg", np.mean)
        mstats.register("std", np.std)
        mstats.register("min", np.min)
        mstats.register("max", np.max)
        #отражают настройку одного из типов эволюционных алгоритмов
        population, log = algorithms.eaSimple(pop, self.toolbox,
                          self.probab_crossing, self.probab_mutating, ngen = 0,
                          #Объект статистики, который обновляется на месте
                          stats = mstats,
                          #будет содержать лучших людей,
                          halloffame = tools.HallOfFame(1),
                          #стоит ли регистрировать статистику
                          verbose = True)
        print(log)
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
        # i_pop = 0
        # for pop in population:
        #     print(f"{i_pop+1}) {pop}")
        #     i_pop += 1

        fits = [ind.fitness.values[0] for ind in population]
        fit_max = len(self.free_tasks) * 3
        step = fit_max*0.1 #20% - отклонение от функции
        print(step)
        while num_gen < 50 and \
                max(fits) not in range(round(fit_max-step),round(fit_max+step)) : #len(population) > 1:
            # for g in range(num_gen):
            num_gen += 1
            print("\n- Generation ", num_gen)
            # Выбор людей следующего поколения
            offspring = self.toolbox.select(population, len(population))
            # Применить кроссовер и мутации на потомство
            self.my_varAnd(self.toolbox, offspring,
                           self.probab_crossing, self.probab_mutating)
            # Оцените людей с недопустимой пригодностью
            self.eval_ind(self.toolbox, offspring)
            # Теперь замените население на следующее поколение людей –
            population[:] = offspring
        # Распечатать статистику по текущим поколениям
        #self.base_Statistics(population)
            self.print_Statistic(population)
        print("\n- Evolution ends - ",num_gen)
        # Распечатать окончательный вывод.
        # Select the 1 best individuals
        best_ind = tools.selBest(population, 1)[0]
        print('\nBest individual:\n', best_ind)


        return best_ind
#
# if __name__ == "__main__":
#     onto = MyOntology()
#     ga = myGAoptimize(onto, onto.new_task)
#     rez = ga.main()
#     #print("BEST \n\t",rez)
