import streamlit as st

from datetime import datetime

from pawpal_system import Owner, Pet, Priority, Recurrence, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
owner: Owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        pet_age = st.number_input("Age", min_value=0, max_value=40, value=1)
    with col3:
        pet_breed = st.text_input("Breed")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), age=int(pet_age), breed=pet_breed.strip()))
        else:
            st.error("Pet name is required.")

if owner.pets:
    st.table(
        [{"name": p.name, "age": p.age, "breed": p.breed, "tasks": len(p.tasks)} for p in owner.list_pets()]
    )
else:
    st.info("No pets yet. Add one above.")

st.subheader("Schedule a Task")
if owner.pets:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Pet", owner.list_pets(), format_func=lambda p: p.name)
        description = st.text_input("Task description", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            task_date = st.date_input("Date", value=datetime.now().date())
        with col2:
            task_time = st.time_input("Start time", value=datetime.now().replace(hour=8, minute=0).time())
        col3, col4, col5 = st.columns(3)
        with col3:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col4:
            priority = st.selectbox(
                "Priority", list(Priority), index=2, format_func=lambda p: p.name.title()
            )
        with col5:
            recurrence = st.selectbox(
                "Repeats", list(Recurrence), format_func=lambda r: r.value.title()
            )
        if st.form_submit_button("Add task"):
            new_task = Task(
                description=description,
                start_time=datetime.combine(task_date, task_time),
                duration=int(duration),
                priority=priority,
                recurrence=recurrence,
            )
            pet_choice.add_task(new_task)
            st.success(f"Added '{description}' for {pet_choice.name}.")
            warning = Scheduler(owner).check_conflict(new_task)
            if warning:
                st.warning(f"Heads up: {warning}")
else:
    st.info("Add a pet before scheduling tasks.")

st.divider()

st.subheader("Build Schedule")
scheduler = Scheduler(owner)

if st.button("Generate schedule"):
    schedule = scheduler.build_schedule()
    if schedule:
        st.table(
            [
                {
                    "start": t.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end": t.end_time.strftime("%H:%M"),
                    "pet": t.pet.name if t.pet else "",
                    "task": t.description,
                    "priority": t.priority.name.title(),
                    "repeats": t.recurrence.value,
                }
                for t in schedule
            ]
        )
    else:
        st.info("No pending tasks to schedule.")
    for message in scheduler.conflict_warnings(schedule):
        st.warning(f"Conflict: {message}")
