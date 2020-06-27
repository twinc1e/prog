import random
from owlready2 import onto_path, get_ontology, os
from datetime import datetime
import re


class MyOntology:

    def __init__(self, iri="http://test.org/bug.owl/",
                 dir_name=os.path.dirname(__file__)
                 ):
        onto_path.append(dir_name)
        self.bug_onto = get_ontology(iri).load()
        # instance of Domain class
        self.new_task = []  # = self.__inst_task
        self.__inst_task = []
        self.inst_task = self.bug_onto.Task.instances()
        self.__inst_domain = self.bug_onto.Domain.instances()
        self.__inst_people = self.bug_onto.People.instances()
        self.__inst_priority = self.bug_onto.Priority.instances()
        self.__inst_role = self.bug_onto.Role.instances()
        # self.save_owl()

    @property
    def inst_domain(self):
        return self.__inst_domain

    @inst_domain.setter
    def inst_domain(self, domain):
        for i in domain:
            self.__inst_domain.append(i)

    @property
    def inst_people(self):
        return self.__inst_people

    @inst_people.setter
    def inst_people(self, people):
        for i in people:
            # adding role for person
            #i.is_role_of.append(self.role_of_pers(i))
            self.__inst_people.append(i)

    @property
    def inst_priority(self):
        return self.__inst_priority

    @inst_priority.setter
    def inst_priority(self, priority):
        for i in priority:
            self.__inst_priority.append(i)

    @property
    def inst_role(self):
        return self.__inst_role

    @inst_role.setter
    def inst_role(self, role):
        for i in role:
            self.__inst_role.append(i)

    @property
    def inst_task(self):
        return self.__inst_task

    @inst_task.setter
    def inst_task(self, tasks):
        for i in tasks:
            if i in self.__inst_task: continue
            self.__inst_task.append(i)
            self.get_new_task(i)

    # @property
    # def new_task(self):
    #     return self.__new_task
    #
    # @new_task.setter
    def get_new_task(self, t):
        # for t in tasks:
        if t.is_assigned is None:
            # self.__new_task.append(i)
            self.new_task.append(t)

    # V---------- не передаётся первый аргумент неявным образом.
    @staticmethod
    # get nice string from onto without onto name
    def str_onto(data):
        try:  # r - подавляют экранирование строки ("Сырые" строки)
            ostr = re.split(r'\.', str(data), maxsplit=1)[1]  # search.group(0)  # findall([^.]+$)[0]
        except IndexError or AttributeError:
            if data is None:
                ostr = None
            else:
                ostr = str(data)
        return ostr

    # format onto date
    def str_odate(self, data):
        try:
            odate = datetime.strptime(self.str_onto(data), '%d.%m.%YT%H-%M-%S')
        except ValueError:
            odate = datetime.strptime(self.str_onto(data), '%Y-%m-%d %H:%M:%S')
        return odate

    @staticmethod
    def odate_str(date):
        return date.strftime('%d.%m.%YT%H-%M-%S')

    def min_role(self, priority):
        role = self.__inst_role[0]  # junior
        min_rol = 5
        for i in priority.related_to:
            if i.is_same_as < min_rol:
                role = i
                min_rol = i.is_same_as
        return role

    def max_prior(self, priors):
        max_pr = 0
        prior = self.__inst_priority[3]  # urgent
        for i in priors:
            if i.is_same_as > max_pr:
                prior = i
                max_pr = i.is_same_as
        return prior

    # set roles for people
    def role_of_pers(self, pers):
        # pers doesn't have tasks
        if len(pers.assigned) == 0:
            return self.__inst_role[0]
        # all priorities's tasks by pers
        pr_task_i = [who.have_priority for who in pers.assigned]
        # who has higher weight of priority
        pr_i = self.max_prior(pr_task_i)
        # who has less weight of role
        role = self.min_role(pr_i)
        print(pers,' have ',role)
        return role

    def item_onto(self, item):
        i_task = self.__inst_task[item]
        # Convert onto date to datetime
        start_date = self.str_odate(i_task.start_doing)
        end_date = self.str_odate(i_task.end_doing)
        # duration = (end_date-start_date).days
        # Format onto domain to string without name of ontology
        task = i_task.name
        domain = self.str_onto(i_task.specialize)
        assign = self.str_onto(i_task.is_assigned)
        priority = self.str_onto(i_task.have_priority)
        tasks = [task, domain, str(start_date), assign, str(end_date), priority]
        return tasks

    # additional func
    def count_free_date(self, pers, time_start):
        n_day = []
        # determine gap start time of task between
        # last task of i_people
        for pt in pers.assigned:  # pt - people's task
            if len(pers.assigned) == 0:
                break
            # for ot in inst_task: # ot - from all tasks
            # get ending date from one of the person's task
            end_date_task = pt.end_doing
            # is the i_people free? what time is it?
            # prev date for pers - end_date_task = j.end_doing
            days_date = self.str_odate(time_start) - self.str_odate(end_date_task)
            n_day.append(days_date.days)
            # print(f"how much days {n_day}")
        # n_day.clear()
        return n_day

    # -------- Find assigners to this domain -----------------
    @staticmethod
    def check_domain(pers, domain):
        k = 0
        # Select all of them
        # print(f"person {i}")
        for d in pers.know:
            if domain == d:
                k = 1
                # print(f"who have domain")
        # if k_as[i] > 0:  #just for people which match with needed domain
        return k

    # -------- Check by priority-----
    @staticmethod
    def check_priority(pers, priority):
        k = 0
        for r in priority.related_to:
            if pers.is_role_of[0] == r:
                k = 1
                # print(f"who have qualification")
        return k

    # ------------Check by date-----------------
    def check_date(self, pers, time_start, time_end):
        k = 0
        # Remember person which finished task (time_end)
        # print(f'v--- have free day {last_task}')
        # check is it old new_task?
        j = 0
        if time_end is not None:
            if self.str_odate(time_end) < datetime.now():
                j = 1
                # if you distribute old task then you restart this task
                # time_end = "" #time_start = datetime.now()
        # rezulting condition
        if len(pers.assigned) == 0 or \
                min(self.count_free_date(pers, time_start)) >= 0 or \
                j == 1:
            k = 1
            # print(f"who is free")
        # print(f"coef = {k_as[inst_people.index(i)]}")
        return k

    # district by one pers
    def onto_district(self, task, pers):
        domain = self.check_domain(pers, task.specialize)
        priority = self.check_priority(pers, task.have_priority)
        date = self.check_date(pers, task.start_doing, pers.end_doing)
        return 0 + domain + priority + date

    # create coefficient which match task
    # to people - searching assigner
    def weights(self, otask):
        k_as = []
        for i in self.__inst_people:
            k_as.append(self.onto_district(otask, i))
        return k_as

    # init individuals with restriction for GA
    def init_func(self, tasks):
        rez = list()
        t = 0
        while t < len(tasks):
            pers = random.choice(self.__inst_people)
            # if self.onto_district(tasks[t],pers) == 3:
            his_role = pers.is_role_of
            # there is func onto_district
            if tasks[t].specialize in pers.know and \
                    tasks[t].have_priority in his_role[0].related_to and\
                    len(pers.assigned):
                # print("correct ", t, pers)
                rez.append(pers)
                t += 1
        # print(rez)
        return rez

    # people with lowest role
    def fit1(self, people):
        k = 0  # num_pers_with_lowest_role
        for i in range(len(people)):
            prior_t = self.new_task[i].have_priority
            # the lowest role for this task
            if people[i].is_role_of[0] == self.min_role(prior_t):
                k += 1
                # print(f"low role - {individuals[i]}", end='\t')
        return k

    # min count task
    @staticmethod
    def fit2(people):
        n_tasks = [len(p.assigned) for p in people]
        n_min = min(n_tasks)
        min_tasks = [index for index, element in enumerate(n_tasks)
                     if n_min == element]
        return n_min, len(min_tasks)

        # date

    def fit3(self, people):
        # Когда меньше всего простоя (свободного времени)  было
        # с предыдущей задачи? Или кто больше всех отдыхал
        # for pers in people:
        #     free_date = min(self.count_free_date(pers, time_start))
        pass

    def eval_func2(self, individuals):
        k = self.fit1(individuals)
        # how many tasks of pers
        k_min, n_tasks = self.fit2(individuals)
        fit = n_tasks * 2 / (k_min + 1) + k * 2  # weight = 2
        return fit,  # min_count_tasks + k

    # update adding info to array and ontology
    def update_onto(self, arr_o_task):
        # o_name = self.bug_onto.name + "."
        start = self.odate_str(self.str_odate(arr_o_task[2]))
        end = self.odate_str(self.str_odate(arr_o_task[4]))
        start = self.bug_onto.Date(start)
        end = self.bug_onto.Date(end)
        # update ontology
        t_instance = self.bug_onto.Task(arr_o_task[0])
        # relations
        t_instance.specialize = arr_o_task[1]
        t_instance.start_doing = start
        if arr_o_task[3] is not None:
            t_instance.is_assigned = arr_o_task[3]
        t_instance.end_doing = end
        t_instance.have_priority = arr_o_task[5]
        # p_instance = self.bug_onto.People(task[3])
        # p_instance.know.append(task[1])
        return t_instance

    def save_owl(self):
        # be saved in the first directory in onto_path
        self.bug_onto.save(file="saved_bug.owl",format="rdfxml")
        # self.bug_onto.save(file = "onto_role")# default format = "rdfxml")
        pass


if __name__ == "__main__":
    my_onto = MyOntology("http://test.org/bug.owl/")
    print(my_onto.inst_role)
    # my_onto.save_owl()
    # del my_onto
