import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A daily pet care planner.")

# ── Session state init ────────────────────────────────────────────────────────
if "pets" not in st.session_state:
    st.session_state.pets = []

st.divider()

# ── Owner ─────────────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input("Available time (min/day)", min_value=1, max_value=480, value=60)

st.divider()

# ── Add a pet ─────────────────────────────────────────────────────────────────
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=30, value=1)
    special_needs = st.text_input("Special needs (optional)")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        st.session_state.pets.append(
            Pet(name=pet_name.strip(), species=species, age=age, special_needs=special_needs)
        )

if st.session_state.pets:
    st.write(f"{len(st.session_state.pets)} pet(s) registered:")
    st.table([
        {"Name": p.name, "Species": p.species, "Age": p.age, "Special needs": p.special_needs or "—"}
        for p in st.session_state.pets
    ])
    if st.button("Remove all pets"):
        st.session_state.pets = []
        st.rerun()
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Add a task ────────────────────────────────────────────────────────────────
st.subheader("Tasks")

if not st.session_state.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names  = [p.name for p in st.session_state.pets]
        target_pet = st.selectbox("Assign to pet", pet_names)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_name = st.text_input("Task name")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col4:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        if not task_name.strip():
            st.warning("Please enter a task name.")
        else:
            pet = next(p for p in st.session_state.pets if p.name == target_pet)
            pet.add_task(Task(
                name=task_name.strip(),
                duration=int(duration),
                priority=priority,
                frequency=frequency,
            ))

    # Show tasks grouped by pet
    for pet in st.session_state.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}**")
            st.table([
                {"Task": t.name, "Duration (min)": t.duration, "Priority": t.priority, "Frequency": t.frequency}
                for t in pet.tasks
            ])

    total_tasks = sum(len(p.tasks) for p in st.session_state.pets)
    if total_tasks == 0:
        st.info("No tasks yet. Add one above.")

st.divider()

# ── Generate schedule ─────────────────────────────────────────────────────────
st.subheader("Generate Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif sum(len(p.tasks) for p in st.session_state.pets) == 0:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(name=owner_name, available_time=int(available_time))
        for pet in st.session_state.pets:
            owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plan      = scheduler.generate_plan()

        st.success("Schedule generated!")
        st.text(scheduler.get_summary())

        all_tasks = owner.get_all_tasks()
        skipped   = [t for t in all_tasks if t not in plan]
        if skipped:
            st.warning(
                f"{len(skipped)} task(s) didn't fit in {available_time} min: "
                + ", ".join(t.name for t in skipped)
            )
