from datetime import date, timedelta
from pawpal_system import Pet, Task, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(name="Feeding", duration=5, priority="high", frequency="daily")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Playtime", duration=20, priority="medium", frequency="daily"))
    assert len(pet.tasks) == 1


def test_sort_tasks_by_time_returns_chronological_order():
    """Tasks should be returned sorted earliest to latest; no-time tasks go last."""
    pet = Pet(name="Mochi", species="cat", age=3)
    pet.add_task(Task(name="Evening med",  duration=5,  priority="low",  frequency="daily", time="20:00"))
    pet.add_task(Task(name="Lunch walk",   duration=20, priority="low",  frequency="daily", time="12:00"))
    pet.add_task(Task(name="Breakfast",    duration=10, priority="high", frequency="daily", time="07:00"))
    pet.add_task(Task(name="No time task", duration=5,  priority="high", frequency="once"))

    owner = Owner(name="Jordan", available_time=120)
    owner.add_pet(pet)
    sorted_tasks = Scheduler(owner).sort_tasks_by_time()

    times = [t.time if t.time else "99:99" for t in sorted_tasks]
    assert times == sorted(times)


def test_daily_task_creates_next_day_recurrence():
    """Marking a daily task complete should add a new task due tomorrow."""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    task = Task(name="Feeding", duration=5, priority="high", frequency="daily", due_date=today)
    pet  = Pet(name="Mochi", species="cat", age=3)
    pet.add_task(task)

    owner = Owner(name="Jordan", available_time=60)
    owner.add_pet(pet)
    Scheduler(owner).handle_completion(pet, task)

    assert task.completed == True
    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == tomorrow


def test_conflict_detection_flags_duplicate_times():
    """Two tasks at the same time should be flagged as a conflict."""
    pet = Pet(name="Buddy", species="dog", age=5)
    pet.add_task(Task(name="Walk",   duration=30, priority="high",   frequency="daily", time="08:00"))
    pet.add_task(Task(name="Bath",   duration=20, priority="medium", frequency="weekly", time="08:00"))

    owner = Owner(name="Jordan", available_time=120)
    owner.add_pet(pet)
    conflicts = Scheduler(owner).get_conflicts()

    assert "08:00" in conflicts
    assert len(conflicts["08:00"]) == 2
