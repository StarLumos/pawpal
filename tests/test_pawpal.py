from datetime import datetime

from pawpal_system import Owner, Pet, Recurrence, Scheduler, Task


def make_task() -> Task:
    return Task(
        description="Morning walk",
        start_time=datetime(2025, 1, 1, 8, 0),
        duration=30,
    )


def test_mark_complete_changes_task_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", age=3, breed="Shiba Inu")
    assert len(pet.list_tasks()) == 0

    pet.add_task(make_task())

    assert len(pet.list_tasks()) == 1


def make_recurring(recurrence: Recurrence) -> tuple[Pet, Task]:
    pet = Pet(name="Mochi", age=3, breed="Shiba Inu")
    task = Task("Walk", datetime(2025, 1, 1, 8, 0), 30, recurrence=recurrence)
    pet.add_task(task)
    return pet, task


def test_mark_complete_twice_does_not_duplicate_recurring_task():
    pet, task = make_recurring(Recurrence.DAILY)

    first = task.mark_complete(now=datetime(2025, 1, 1, 8, 5))
    second = task.mark_complete(now=datetime(2025, 1, 1, 8, 6))

    assert first is not None
    assert second is None
    assert len(pet.list_tasks()) == 2


def test_on_time_completion_schedules_next_interval():
    _, daily = make_recurring(Recurrence.DAILY)
    _, weekly = make_recurring(Recurrence.WEEKLY)

    now = datetime(2025, 1, 1, 8, 5)

    assert daily.mark_complete(now=now).start_time == datetime(2025, 1, 2, 8, 0)
    assert weekly.mark_complete(now=now).start_time == datetime(2025, 1, 8, 8, 0)


def test_late_completion_skips_past_occurrences():
    _, daily = make_recurring(Recurrence.DAILY)
    _, weekly = make_recurring(Recurrence.WEEKLY)

    now = datetime(2025, 1, 10, 12, 0)

    assert daily.mark_complete(now=now).start_time == datetime(2025, 1, 11, 8, 0)
    assert weekly.mark_complete(now=now).start_time == datetime(2025, 1, 15, 8, 0)


def make_scheduler():
    owner = Owner(name="Sam")
    a, b = Pet("Mochi", 3, "Shiba"), Pet("Luna", 2, "Tabby")
    owner.add_pet(a)
    owner.add_pet(b)
    return Scheduler(owner), a, b


def test_same_start_time_conflicts_for_same_pet():
    scheduler, mochi, _ = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    mochi.add_task(Task("Walk", t, 30))
    mochi.add_task(Task("Feed", t, 10))

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert "same pet" in warnings[0]


def test_same_start_time_conflicts_across_pets():
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    mochi.add_task(Task("Walk", t, 30))
    luna.add_task(Task("Feed", t, 10))

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    scheduler, mochi, luna = make_scheduler()
    mochi.add_task(Task("Walk", datetime(2025, 1, 1, 8, 0), 30))
    luna.add_task(Task("Feed", datetime(2025, 1, 1, 8, 30), 10))

    assert scheduler.conflict_warnings() == []


def test_completed_tasks_do_not_conflict_and_conflicts_with_excludes_self():
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    done = Task("Walk", t, 30)
    mochi.add_task(done)
    done.mark_complete()
    new = Task("Feed", t, 10)
    luna.add_task(new)

    assert scheduler.conflicts_with(new) == []
    assert scheduler.conflict_warnings() == []


def test_check_conflict_returns_message_or_none_without_raising():
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    mochi.add_task(Task("Walk", t, 30))
    clash = Task("Feed", t, 10)
    luna.add_task(clash)
    free = Task("Groom", datetime(2025, 1, 1, 12, 0), 10)
    luna.add_task(free)

    assert "different pets" in scheduler.check_conflict(clash)
    assert scheduler.check_conflict(free) is None
    assert len(luna.list_tasks()) == 2  # the clashing task was still added
