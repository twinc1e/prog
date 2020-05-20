import random
from owlready2 import onto_path, get_ontology, os
from datetime import datetime

inst_domain = []  # table.item(new_row,1).text()
inst_people = []  # table.item(new_row,3).text()
inst_task = []  # table.item(new_row,0).text()
inst_priority = []
inst_role = []  # unuseful
new_tasks = []

class MyOntology:

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
            if individuals[i].is_role_of == min_role(prior_t):
                k += 1
                print(f"low role - {individuals[i]}", end='\t')
            n_tasks.append(len(individuals[i].assigned))
        return min(n_tasks) + k,  # min_count_tasks + k

    # -------- Find assigners to this domain -----------------
        def check_domain(self,pers, domain):
            k=0
            # Select all of them
            # print(f"person {i}")
            for d in pers.know:
                if domain == d:
                    k += 1
                    # print(f"who have domain")
            # if k_as[i] > 0:  #just for people which match with needed domain
            return k
        # -------- Check by priority-----
        def check_priority(self,pers,priority):
            k=0
            for r in priority.related_to:
                if pers.is_role_of[0] == r:
                    k += 1
                    # print(f"who have qualification")
            return k
        # ------------Check by date-----------------
        def check_date(self,pers,fill_row):
            k = 0
            n_day=[]
            # determine date of last task of i_people
            for pt in pers.assigned:  # pt - people's task
                if len(pers.assigned) == 0: break
                # for ot in inst_task: # ot - from all tasks
                # get ending date from one of the person's task
                end_date_task = pt.end_doing
                # is the i_people free? what time is it?
                # prev date for pers - end_date_task = j.end_doing
                start_date_cur_t = self.str_date(self.table.item(fill_row, 2).text())
                days_date = start_date_cur_t - self.str_odate(end_date_task)
                n_day.append(days_date.days)
                # print(f"how much days {n_day}")
            #n_day.clear()

            # Remember person which finished task (end_date)
            # print(f'v--- have free day {last_task}')
            j = 0
            end_task = self.table.item(fill_row, 4).text()
            if end_task is not None:
                if self.str_date(end_task) < datetime.now():
                    j = 1
            if len(pers.assigned) == 0 or min(n_day) >= 0 or j == 1:
                k += 1
                # print(f"who is free")
            # print(f"coef = {k_as[inst_people.index(i)]}")
            return k

        # ----------------------------------------------------------------
        def onto_district(self, fill_row, domain, prior):
            # create coefficient which match task to people - searching assigner
            k_as = [0 for _ in range(len(inst_people))]
            for i in inst_people:
                k_as[inst_people.index(i)] = self.check_domain(i, domain)+\
                    self.check_priority(i, priority)+\
                    self.check_date(i, fill_row)
            print(f"in row {fill_row}")
            # Remember index from max number of array k_as
            # win_as = [k_as.index(k) for k in k_as if k==3]
            # если все истина, то записать в область допустимых
            if k_as.count(3) == 0:
                res = "No one can be assigner"
            else:
                # using enumerate() + list comprehension
                # range deletion of elements
                all_win = [i for i, x in enumerate(k_as) if x == 3]
                # add to the table
                self.table.setItem(fill_row, 3, QTableWidgetItem(inst_people[all_win[0]].name))
                print("in cell " + self.table.item(fill_row, 3).text())
                if k_as.count(3) > 1:
                    res = f"more than one assigner: {len(all_win)}"
                else:
                    res = f"assigner - {inst_people[all_win[0]].name}"
                print(f"\n people for task\n\t{[inst_people[win].name for win in all_win]}")
            print(f"task {self.table.item(fill_row, 0).text()}")
            return res

dir_name = os.path.dirname(__file__)
onto_path.append(dir_name)  # ("C://Users/newLenovo/Desktop/prog")
bug_onto = get_ontology("http://test.org/bug.owl/").load()
