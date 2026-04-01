from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    duration: int       # minutes
    priority: str       # "high", "medium", "low"
    frequency: str      # "daily", "weekly", "once"
    time: str = ""      # scheduled start time in "HH:MM" format, e.g. "08:00"
    due_date: str = ""  # "YYYY-MM-DD" format
    completed: bool = False

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def reset(self):
        """Reset this task to incomplete."""
        self.completed = False

    def next_occurrence(self) -> "Task | None":
        """Return a new Task for the next recurrence, or None if the task is once-only."""
        if self.frequency == "once":
            return None
        base = date.fromisoformat(self.due_date) if self.due_date else date.today()
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            time=self.time,
            due_date=(base + delta).isoformat(),
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    available_time: int     # minutes per day
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Returns all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[Task]:
        """Returns only incomplete tasks across every pet."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def _get_pending_with_pets(self) -> list[tuple["Pet", Task]]:
        """Returns (pet, task) pairs for all incomplete tasks, sorted by priority."""
        pairs = [(pet, task) for pet in self.owner.pets for task in pet.get_pending_tasks()]
        return sorted(pairs, key=lambda pt: PRIORITY_ORDER.get(pt[1].priority, 99))

    def get_conflicts(self) -> dict[str, list[tuple["Pet", Task]]]:
        """Return groups of pending tasks that share the same time slot (conflicts).
        Only slots with 2+ tasks are returned. Tasks with no time set are ignored."""
        slots: dict[str, list[tuple["Pet", Task]]] = {}
        for pet, task in self._get_pending_with_pets():
            if not task.time:
                continue
            slots.setdefault(task.time, []).append((pet, task))
        return {k: v for k, v in slots.items() if len(v) > 1}

    def generate_plan(self) -> list[Task]:
        """Picks tasks in priority order until the owner's available time is filled.
        Only one task per time slot is scheduled; lower-priority conflicts are skipped."""
        plan = []
        time_remaining = self.owner.available_time
        booked_slots: set[str] = set()
        for _, task in self._get_pending_with_pets():
            if task.time and task.time in booked_slots:
                continue  # conflict — a higher-priority task already owns this slot
            if task.duration <= time_remaining:
                plan.append(task)
                time_remaining -= task.duration
                if task.time:
                    booked_slots.add(task.time)
        return plan

    def handle_completion(self, pet: "Pet", task: Task):
        """Mark a task complete and auto-schedule the next occurrence for recurring tasks."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)

    def sort_tasks_by_time(self) -> list[Task]:
        """Return all tasks sorted by scheduled time using a lambda key; unscheduled tasks go last."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda t: t.time if t.time else "99:99")

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Filter tasks by completion status and/or pet name; omit a parameter to skip that filter."""
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def get_summary(self) -> str:
        """Returns a human-readable summary of the generated plan."""
        plan = self.generate_plan()

        if not plan:
            all_tasks = self.owner.get_all_tasks()
            if all_tasks and all(t.completed for t in all_tasks):
                return "All tasks are already completed. Great job!"
            return "No tasks fit within the available time."

        pet_by_task = {id(task): pet for pet in self.owner.pets for task in pet.tasks}
        lines = [f"{self.owner.name}'s plan for today ({self.owner.available_time} min available):"]
        for task in plan:
            pet = pet_by_task.get(id(task))
            when = " | ".join(filter(None, [task.due_date, task.time]))
            when_str = f"  @ {when}" if when else ""
            lines.append(f"  [{task.priority.upper()}] {task.name} ({pet.name if pet else '?'}){when_str} — {task.duration} min ({task.frequency})")

        total = sum(t.duration for t in plan)
        lines.append(f"Total: {total} / {self.owner.available_time} min used")
        return "\n".join(lines)
