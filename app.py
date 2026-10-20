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

scheduler = Scheduler(owner)

def task_rows(tasks: list[Task]) -> list[dict[str, str]]:
    """Table-ready rows for a list of tasks."""
    return [
        {
            "Date": t.start_time.strftime("%a %b %d"),
            "Time": f"{t.start_time:%H:%M} - {t.end_time:%H:%M}",
            "Pet": t.pet.name if t.pet else "-",
            "Task": t.description,
            "Priority": t.priority.name.title(),
            "Repeats": t.recurrence.value.title(),
            "Status": "✅ Done" if t.completed else "⏳ Pending",
        }
        for t in tasks
    ]


def show_conflicts(tasks: list[Task], empty_message: str) -> None:
    """Warn about each overlapping pair of pending tasks, or confirm there are none."""
    warnings = scheduler.conflict_warnings(tasks)
    if warnings:
        st.warning(
            f"**{len(warnings)} scheduling conflict(s) found.** "
            "You can only do one thing at a time, so consider moving one of each pair."
        )
        for message in warnings:
            st.warning(message, icon="⚠️")
    else:
        st.success(empty_message)


st.subheader("All Tasks")
all_tasks = scheduler.get_all_tasks()
if all_tasks:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pet_filter = st.selectbox(
            "Pet", [None] + owner.list_pets(), format_func=lambda p: "All pets" if p is None else p.name
        )
    with col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col3:
        min_priority = st.selectbox(
            "Min priority", [None] + list(Priority),
            format_func=lambda p: "Any" if p is None else p.name.title(),
        )
    with col4:
        sort_order = st.selectbox("Sort by", ["Time (earliest first)", "Time (latest first)", "Time, then priority"])

    visible = scheduler.filter_tasks(
        pet=pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
        min_priority=min_priority,
    )
    if sort_order == "Time, then priority":
        visible = scheduler.sort_tasks(visible)
    else:
        visible = scheduler.sort_by_time(visible, reverse=sort_order == "Time (latest first)")

    done_count = sum(t.completed for t in all_tasks)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total tasks", len(all_tasks))
    m2.metric("Pending", len(all_tasks) - done_count)
    m3.metric("Completed", done_count)

    if visible:
        st.caption(f"Showing {len(visible)} of {len(all_tasks)} tasks.")
        st.table(task_rows(visible))
    else:
        st.info("No tasks match these filters.")

    show_conflicts(all_tasks, "No conflicts among your pending tasks.")

    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        with st.form("complete_task_form"):
            to_complete = st.selectbox(
                "Mark a task complete",
                pending,
                format_func=lambda t: f"{t.start_time:%b %d %H:%M} - {t.description} ({t.pet.name if t.pet else '-'})",
            )
            if st.form_submit_button("Mark complete"):
                next_task = to_complete.mark_complete()
                if next_task:
                    st.success(
                        f"Completed '{to_complete.description}'. "
                        f"Next {to_complete.recurrence.value} occurrence scheduled for {next_task.start_time:%b %d at %H:%M}."
                    )
                else:
                    st.success(f"Completed '{to_complete.description}'.")
else:
    st.info("No tasks yet. Schedule one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    f"Pending tasks in chronological order, limited to {owner.name}'s available hours "
    f"({owner.available_start:02d}:00-{owner.available_end % 24:02d}:00)."
)

if st.button("Generate schedule"):
    schedule = scheduler.build_schedule()
    if schedule:
        total_minutes = sum(t.duration for t in schedule)
        st.success(f"Scheduled {len(schedule)} task(s) totalling {total_minutes} minutes.")
        st.table(task_rows(schedule))
    else:
        st.info("No pending tasks to schedule.")

    skipped = [t for t in scheduler.filter_tasks(completed=False) if t not in schedule]
    if skipped:
        st.warning(
            "Outside your available hours, so not scheduled: "
            + ", ".join(f"'{t.description}'" for t in scheduler.sort_by_time(skipped))
        )
    show_conflicts(schedule, "No conflicts. Your schedule is clear.")
