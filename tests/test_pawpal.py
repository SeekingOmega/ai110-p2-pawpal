from pawpal_system import Pet, Task


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
