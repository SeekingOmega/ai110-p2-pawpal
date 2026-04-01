from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner_jordan = Owner(name="Jordan", available_time=120, preferences="morning routines")

pet_mochi = Pet(name="Mochi", species="cat", age=3)
pet_buddy = Pet(name="Buddy", species="dog", age=5, special_needs="joint supplements")

# --- Tasks added intentionally out of time order ---
pet_mochi.add_task(Task(name="Feeding",    duration=5,  priority="high",   frequency="daily",    time="07:00"))
pet_mochi.add_task(Task(name="Playtime",   duration=20, priority="medium", frequency="daily",    time="15:30"))
pet_mochi.add_task(Task(name="Vet meds",   duration=5,  priority="high",   frequency="daily",    time="12:00"))

pet_buddy.add_task(Task(name="Morning walk", duration=30, priority="high",   frequency="daily",  time="08:00"))
pet_buddy.add_task(Task(name="Joint meds",   duration=5,  priority="high",   frequency="daily",  time="07:30"))
pet_buddy.add_task(Task(name="Grooming",     duration=25, priority="low",    frequency="weekly", time="16:00"))
pet_buddy.add_task(Task(name="Evening walk", duration=30, priority="medium", frequency="daily",  time="18:00"))

# Mark one task complete to test filtering
pet_mochi.tasks[2].mark_complete()   # "Vet meds" is done

owner_jordan.add_pet(pet_mochi)
owner_jordan.add_pet(pet_buddy)

scheduler = Scheduler(owner_jordan)

# --- Today's schedule ---
print("=" * 50)
print(scheduler.get_summary())

# --- Sorted by time ---
print("\n" + "=" * 50)
print("All tasks sorted by scheduled time:")
for task in scheduler.sort_tasks_by_time():
    status = "[x]" if task.completed else "[ ]"
    print(f"  {task.time or '--:--'}  {status}  {task.name} ({task.priority}, {task.duration} min)")

# --- Filter: pending tasks only ---
print("\n" + "=" * 50)
print("Pending tasks (not yet completed):")
for task in scheduler.filter_tasks(completed=False):
    print(f"  [ ]  {task.name} ({task.time or 'no time set'})")

# --- Filter: completed tasks only ---
print("\n" + "=" * 50)
print("Completed tasks:")
for task in scheduler.filter_tasks(completed=True):
    print(f"  [x]  {task.name}")

# --- Filter: Buddy's tasks only ---
print("\n" + "=" * 50)
print("Buddy's tasks only:")
for task in scheduler.filter_tasks(pet_name="Buddy"):
    print(f"  {task.time}  {task.name} ({task.priority})")
