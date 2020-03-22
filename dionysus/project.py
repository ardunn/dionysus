import os
import random
from typing import List, Union
from collections import namedtuple

from dionysus.task import Task
from dionysus.constants import done_str, status_primitives, priority_primitives, notes_dir_str, tasks_dir_str, \
    task_extension, print_separator
from dionysus.util import process_name, AttrDict
from dionysus.exceptions import FileOverwriteError
from dionysus.logic import order_task_collection

class Project:
    def __init__(self, path: str, id: str):
        self.path = path
        self.id = id

        self.name = None
        self.prefix_path = None
        self.tasks_dir = None
        self.notes_dir = None
        self.done_dir = None
        self._refresh()

    def __str__(self):
        n_tasks = len(self.tasks.all)
        return f"<dionysus Project {self.id}: [{self.name}] ({n_tasks} tasks)>"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def create_from_spec(cls, id: str, path_prefix: str, name: str, init_notes: bool = True):
        name = process_name(name)
        id = process_id(id)

        dest_dir = os.path.join(path_prefix, name)
        if os.path.exists(dest_dir):
            raise FileOverwriteError(f"Project \'{name}\' already exists: \'{dest_dir}\'")
        else:
            tasks_dir = os.path.join(dest_dir, tasks_dir_str)
            os.makedirs(tasks_dir)

        done_dir = os.path.join(tasks_dir, done_str)
        if not os.path.exists(done_dir):
            os.mkdir(done_dir)
        if init_notes:
            notes_dir = os.path.join(dest_dir, notes_dir_str)
            if not os.path.exists(notes_dir):
                os.mkdir(notes_dir)

        return Project(dest_dir, id)

    def _refresh(self) -> None:
        self.prefix_path = os.path.dirname(self.path)
        self.name = self.path.split("/")[-1]
        self.tasks_dir = os.path.join(self.path, tasks_dir_str)  # must exist
        self.done_dir = os.path.join(self.tasks_dir, done_str)  # ok if this doesn't exist

        notes_dir = os.path.join(self.path, notes_dir_str)

        if not os.path.exists(notes_dir):
            notes_dir = None
        self.notes_dir = notes_dir

        if not os.path.exists(self.tasks_dir):
            os.mkdir(self.tasks_dir)

    def rename(self, new_name) -> None:
        new_name = process_name(new_name)
        new_path = os.path.join(self.prefix_path, new_name)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()

    def set_task_priorities(self, priority) -> None:
        for task in self.tasks.all:
            task.set_priority(priority)
        self._refresh()

    def create_new_task(self, name, priority, status, edit=True) -> Task:
        if name in [tn.name for tn in self.tasks.all]:
            raise FileOverwriteError(f"Task already exists with the name: {name}")
        t = Task.create_from_spec("<null>", self.tasks_dir, name, priority, status, edit=edit)
        self._refresh()
        return t

    @property
    def tasks(self) -> AttrDict:
        """
        A dictionary/class of tasks
        Returns:

        """
        # priority_dict = {priority: [] for priority in priority_primitives}
        task_dict = {status: [] for status in status_primitives}
        task_dict["all"] = []
        task_collection = AttrDict(task_dict)
        unique_id = 0
        for container_dir in [self.done_dir, self.tasks_dir]:
            for f in os.listdir(container_dir):
                fp = os.path.join(container_dir, f)
                if os.path.exists(fp):
                    if fp.endswith(task_extension):
                        unique_id += 1
                        pid_tid = f"{self.id}{unique_id}"
                        t = Task(path=fp, id=pid_tid)
                        task_collection[t.status].append(t)
                        task_collection["all"].append(t)
        return task_collection

    def get_n_highest_priority_tasks(self, n=1) -> Union[List, None]:
        # return the highest priority task
        ordered = order_task_collection(self.tasks, limit=n, include_done=False)
        if ordered:
            return ordered[:n]
        else:
            return None


def process_id(id: str) -> str:
    if len(id) == 1:
        return id.lower()
    else:
        raise ValueError("Project Ids must be a length 1 string.")



if __name__ == "__main__":
    import pprint

    # p = Project.create_from_spec(
    #     path_prefix="/home/x/dionysus/dionysus/tmp_projset",
    #     id="a",
    #     name="proj1",
    #     init_notes=True
    # )

    p = Project("/home/x/dionysus/dionysus/tmp_projset/proj2", id="a")

    # p.rename("proj2")

    # t = p.create_new_task("completed first", 1, "todo", edit=False)
    # t.complete()
    # t.set_status()
    # print(p.tasks)

    ordered = order_task_collection(p.tasks)
    pprint.pprint(ordered)

    ordered = order_task_collection(p.tasks, include_done=True)
    pprint.pprint(ordered)
