from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: str = ""


@dataclass
class Owner:
    name: str
    available_time: int  # minutes per day
    preferences: str = ""


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: str  # "high", "medium", "low"


class Scheduler:
    def __init__(self, tasks: list[Task], constraints: dict):
        self.tasks = tasks
        self.constraints = constraints

    def generate_plan(self) -> list[Task]:
        # TODO: sort tasks by priority and fit within available time
        pass
