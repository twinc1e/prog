import random
from copy import copy

import self
from owlready2 import onto_path, get_ontology, os
from deap import base, creator, tools

inst_domain = []  # table.item(new_row,1).text()
inst_people = []  # table.item(new_row,3).text()
inst_task = []  # table.item(new_row,0).text()
inst_priority = []
inst_role = []  # unuseful
new_tasks = []


# set roles for people
def role_of_pers(pers):
    if len(pers.assigned) == 0:
        return inst_role[0]
    pr_task_i = [who.have_priority for who in pers.assigned]
    # who often met
    pr_i = max(set(pr_task_i), key=lambda x: pr_task_i.count(x))
    # who has higher weight of priority
    max_pr = 0
    for i in pr_task_i:
        if i.is_same_as > max_pr:
            pr_i = i
            max_pr = i.is_same_as
    # who has less weight of role
    role = pr_i.related_to[-1]  # .is_same_as
    min_rol = 5
    for i in pr_i.related_to:
        if i.is_same_as < min_rol:
            role = i
            min_rol = i.is_same_as
    return role


def ontology():
    dir_name = os.path.dirname(__file__)
    onto_path.append(dir_name)  # ("C://Users/newLenovo/Desktop/prog")
    bug_onto = get_ontology("http://test.org/bug.owl/").load()

    for i in bug_onto.Task.instances():
        inst_task.append(i)
        if i.is_assigned is None: new_tasks.append(i)
    for i in bug_onto.Role.instances():
        inst_role.append(i)
    for i in bug_onto.Priority.instances():
        inst_priority.append(i)
    for i in bug_onto.People.instances():
        i.is_role_of.append(role_of_pers(i))
        inst_people.append(i)
        # adding role for person
    for i in bug_onto.Domain.instances():
        inst_domain.append(i)
    pass


def init_func(people, tasks):
    rez = list()
    t = 0
    while t < len(tasks):
        pers = random.choice(people)
        his_role = pers.is_role_of
        # there is func onto_district
        if tasks[t].specialize in pers.know and \
                tasks[t].have_priority in his_role[0].related_to and len(pers.assigned):
            # print("correct ", t, pers)
            rez.append(pers)
            t += 1
        # else:
        #     print("Not correct")
        #     t -= 1
    return rez


def min_role(pr_i):
    role = inst_role[0]  # junior
    min_rol = 5
    for i in pr_i.related_to:
        if i.is_same_as < min_rol:
            role = i
            min_rol = i.is_same_as
    return role


def eval_func2(individuals):
    k = 0  # num_pers_with_lowest_role
    n_tasks = list()
    for i in range(len(individuals)):
        prior_t = new_tasks[i].have_priority
        # the lowest role for this task
        if (individuals[i].is_role_of)[0] == min_role(prior_t):
            k += 1
            # print(f"low role - {individuals[i]}", end='\t')
        n_tasks.append(len(individuals[i].assigned))
    n_min = [p for p in individuals if min(n_tasks)==len(p.assigned)]
    fit = len(n_min)*2/(min(n_tasks)+1) + k*2 #weight = 2
    return fit,  # min_count_tasks + k


# ! the comma in the return statement. This is because the fitness function in DEAP
# is returned as a tuple to allow multi-objective fitness functions
# Определить функцию оценки
def eval_func(individuals):
    sum_k = 0
    # print(people)
    # для каждой новой задачи подсчитать коэф.
    for task in new_tasks:  # num_bits tasks with people--v
        i = new_tasks.index(task)  # vs iterating i++
        # check eperiments with part of new tasks, not all of them
        if i >= self.num_bits:  # <-------------------------
            break
        # print(people[i], end = '-')
        k = 0
        # domain
        if task.specialize in individuals[i].know:
            k += 1
        his_role = individuals[i].is_role_of
        # priority
        if task.have_priority in his_role[0].related_to:
            k += 1
        # print(f"{new_tasks.index(task)}+1) {k}", end = '\t')
        sum_k += k
    # print(f"  sum {sum_k}")
    return sum_k,  # comma need because it's weights --------v


# создать набор инструментов с правильными параметрами
def create_toolbox(num_bits):
    # args: name_new_class, base_class,attr_class:        v- maximize the 1 fitness/objective
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)  # gp.PrimitiveTree
    toolbox = base.Toolbox()
    #                args: alias, funct_assigned_to_alias
    # toolbox.register("attr_pers", random.choice, inst_people)
    toolbox.register("attr_pers", init_func, inst_people, new_tasks)
    # toolbox.register("attr_task", init_func, new_tasks)
    toolbox.register("individual", tools.initIterate, creator.Individual,
                     toolbox.attr_pers)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # Зарегистрировать оператор оценки
    toolbox.register("evaluate", eval_func2)
    # Зарегистрировать оператор кроссовера
    toolbox.register("mate", tools.cxTwoPoint)  # gp.cxOnePoint
    # Зарегистрировать оператор мутации
    toolbox.register("mutate", tools.mutShuffleIndexes,
                     indpb=0.05)  # gp.mutUniformin, expr = toolbox.attr_str, pset = )
    # Определить оператор для разведения
    toolbox.register("select", tools.selTournament, tournsize=3)
    # !!!!!!!!!some idea from screenshot. Decorate with instruments of GP
    toolbox.decorate("mate", )
    return toolbox


if __name__ == "__main__":
    ontology()
    # num at the individuals = tasks without distribution
    num_bits = len(new_tasks)
    random.seed(2)
    toolbox = create_toolbox(num_bits)  # emtpy
    population = toolbox.population(n=500)  # 450)
    # вероятность спаривания/мутации каждого человека в каждом поколении
    probab_crossing, probab_mutating = 0.5, 0.2
    num_gen = 10  # количество поколений для достижения
    print('Evolution process starts')
    # Оцените все население
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    print('\nСозданное (Evaluated)', len(population), 'individuals')
    print('and individuals:')
    # for pop in population:
    #     print(f"{len(pop)}={pop}")
    fits = [ind.fitness.values[0] for ind in population]

    while num_gen < 50 and max(fits) < num_bits*3:
    #for g in range(num_gen):
        num_gen+=1
        print("\n- Generation", num_gen)
        # Выбор людей следующего поколения
        offspring = toolbox.select(population, len(population))
        # Теперь, клонировать выбранных лиц
        # deepcopy isn't for my ontology class https://stackoverflow.com/questions/40659963/python-shallow-deep-copy-error
        offspring = list(map(copy, offspring))
        # Применить кроссовер и мутации на потомство
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < probab_crossing:
                toolbox.mate(child1, child2)
                # Удалить значение фитнеса ребенка
                del child1.fitness.values
                del child2.fitness.values
        # Теперь примените мутацию
        for mutant in offspring:
            if random.random() < probab_mutating:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # Оцените людей с недопустимой пригодностью –
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        print('Evaluated', len(invalid_ind), 'individuals')
        # Теперь замените население на следующее поколение людей –
        population[:] = offspring
        # Распечатать статистику по текущим поколениям
        fits = [ind.fitness.values[0] for ind in population]
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        print('\n Fitness\n',fits,sep='\t')
        print('\nMin =', min(fits), ', Max =', max(fits))
        print('Average =', round(mean, 2),
              ', Standard deviation откл. =', round(std, 2))
    print("\n- Evolution ends -")
    # Распечатать окончательный вывод.
    # Select the 1 best individuals
    best_ind = tools.selBest(population, 1)[0]
    print('\nBest individual:\n', best_ind)
    # print('\nNumber of ones:', sum(best_ind))
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
