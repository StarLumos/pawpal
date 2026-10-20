from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task


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


# --- Recurrence edge cases ---


def test_non_recurring_task_spawns_nothing():
    pet, task = make_recurring(Recurrence.NONE)

    assert task.mark_complete(now=datetime(2025, 1, 1, 8, 5)) is None
    assert len(pet.list_tasks()) == 1


def test_next_occurrence_copies_fields_with_fresh_identity():
    pet = Pet("Mochi", 3, "Shiba")
    task = Task("Meds", datetime(2025, 1, 1, 8, 0), 15, Priority.HIGH, Recurrence.DAILY)
    pet.add_task(task)

    nxt = task.mark_complete(now=datetime(2025, 1, 1, 8, 5))

    assert (nxt.description, nxt.duration, nxt.priority, nxt.recurrence) == (
        "Meds", 15, Priority.HIGH, Recurrence.DAILY,
    )
    assert nxt.completed is False
    assert nxt.id != task.id
    assert nxt.pet is pet and any(t is nxt for t in pet.list_tasks())


def test_early_completion_still_schedules_one_interval_ahead():
    _, task = make_recurring(Recurrence.DAILY)

    nxt = task.mark_complete(now=datetime(2025, 1, 1, 6, 0))

    assert nxt.start_time == datetime(2025, 1, 2, 8, 0)


def test_completion_exactly_at_next_slot_skips_to_following_slot():
    _, task = make_recurring(Recurrence.DAILY)

    nxt = task.mark_complete(now=datetime(2025, 1, 2, 8, 0))

    assert nxt.start_time == datetime(2025, 1, 3, 8, 0)


def test_recurring_task_without_pet_returns_unattached_next_task():
    task = Task("Walk", datetime(2025, 1, 1, 8, 0), 30, recurrence=Recurrence.DAILY)

    nxt = task.mark_complete(now=datetime(2025, 1, 1, 8, 5))

    assert nxt is not None and nxt.pet is None


# --- Sorting edge cases ---


def test_sort_tasks_ties_break_by_priority_and_order_by_full_datetime():
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 14, 0)
    low = Task("Groom", t, 10, Priority.LOW)
    high = Task("Meds", t, 10, Priority.HIGH)
    tomorrow = Task("Walk", datetime(2025, 1, 2, 7, 0), 30)
    late_tonight = Task("Last walk", datetime(2025, 1, 1, 23, 0), 20)
    for task in (tomorrow, low, late_tonight):
        mochi.add_task(task)
    luna.add_task(high)

    ordered = scheduler.sort_tasks(scheduler.get_all_tasks())

    assert ordered == [high, low, late_tonight, tomorrow]


def test_sort_by_time_is_stable_reversible_and_non_mutating():
    scheduler, mochi, _ = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    first, second = Task("A", t, 10), Task("B", t, 10)
    later = Task("C", datetime(2025, 1, 1, 9, 0), 10)
    original = [later, first, second]

    assert scheduler.sort_by_time(original) == [first, second, later]
    assert scheduler.sort_by_time(original, reverse=True)[0] is later
    assert original == [later, first, second]


def test_sorting_empty_inputs_returns_empty_lists():
    scheduler, _, _ = make_scheduler()

    assert scheduler.sort_tasks([]) == []
    assert scheduler.sort_by_time() == []
    assert scheduler.build_schedule() == []


# --- Conflict edge cases ---


def test_contained_task_is_a_single_conflict():
    scheduler, mochi, luna = make_scheduler()
    mochi.add_task(Task("Vet", datetime(2025, 1, 1, 8, 0), 60))
    luna.add_task(Task("Meds", datetime(2025, 1, 1, 8, 10), 10))

    assert len(scheduler.find_conflicts()) == 1


def test_chained_overlaps_report_only_the_real_pairs():
    scheduler, mochi, luna = make_scheduler()
    a = Task("A", datetime(2025, 1, 1, 8, 0), 60)
    b = Task("B", datetime(2025, 1, 1, 8, 30), 60)
    c = Task("C", datetime(2025, 1, 1, 9, 15), 45)
    mochi.add_task(a)
    luna.add_task(b)
    mochi.add_task(c)

    pairs = scheduler.find_conflicts()

    assert len(pairs) == 2
    assert {frozenset(id(t) for t in p) for p in pairs} == {
        frozenset((id(a), id(b))),
        frozenset((id(b), id(c))),
    }


# --- Availability ---


def test_build_schedule_excludes_completed_and_out_of_hours_tasks_in_order():
    scheduler, mochi, _ = make_scheduler()
    scheduler.owner.available_start, scheduler.owner.available_end = 6, 22
    day = datetime(2025, 1, 1)
    evening = Task("Walk", day.replace(hour=18), 30)
    morning = Task("Feed", day.replace(hour=7), 10)
    spills_over = Task("Late", day.replace(hour=21, minute=45), 30)
    too_early = Task("Dawn", day.replace(hour=5), 10)
    done = Task("Done", day.replace(hour=9), 10)
    for task in (evening, morning, spills_over, too_early, done):
        mochi.add_task(task)
    done.mark_complete()

    assert scheduler.build_schedule() == [morning, evening]


# --- Core behaviors, stated plainly ---


def test_tasks_are_returned_in_chronological_order():
    scheduler, mochi, luna = make_scheduler()
    day = datetime(2025, 1, 1)
    evening = Task("Groom", day.replace(hour=18), 20)
    morning = Task("Walk", day.replace(hour=7, minute=30), 30)
    noon = Task("Vet", day.replace(hour=12), 60)
    mochi.add_task(evening)
    luna.add_task(morning)
    mochi.add_task(noon)

    assert scheduler.sort_by_time() == [morning, noon, evening]
    assert scheduler.sort_tasks(scheduler.get_all_tasks()) == [morning, noon, evening]
    assert scheduler.build_schedule() == [morning, noon, evening]


def test_completing_daily_task_creates_task_for_the_following_day():
    pet, task = make_recurring(Recurrence.DAILY)

    nxt = task.mark_complete(now=datetime(2025, 1, 1, 8, 5))

    assert task.completed is True
    assert nxt.start_time == task.start_time + timedelta(days=1)
    assert nxt in pet.list_tasks()


def test_scheduler_flags_tasks_scheduled_at_the_same_time():
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 14, 0)
    vet = Task("Vet", t, 60)
    meds = Task("Meds", t, 10)
    mochi.add_task(vet)
    luna.add_task(meds)

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert "Vet" in warnings[0] and "Meds" in warnings[0]
    assert scheduler.check_conflict(meds) is not None


# --- Known limitations: these pin CURRENT behavior, flip them if it changes ---


def test_task_crossing_midnight_is_never_available():
    # is_available compares against the same calendar day's window, so even a
    # 24-hour owner can't be scheduled for a 23:30 task that runs 60 minutes.
    scheduler, mochi, _ = make_scheduler()
    scheduler.owner.available_start, scheduler.owner.available_end = 0, 24
    spans_midnight = Task("Night walk", datetime(2025, 1, 1, 23, 30), 60)
    mochi.add_task(spans_midnight)

    assert scheduler.owner.is_available(spans_midnight) is False
    assert scheduler.build_schedule() == []


def test_zero_duration_task_at_another_tasks_start_is_flagged_inconsistently():
    # find_conflicts only stops scanning once b.start >= a.end, so it reports
    # the clash, but Task.overlaps uses strict < on both sides and says no.
    # conflict_warnings and check_conflict therefore disagree (the UI blocks
    # zero durations with min_value=1, so this only bites direct API use).
    scheduler, mochi, luna = make_scheduler()
    t = datetime(2025, 1, 1, 8, 0)
    walk = Task("Walk", t, 30)
    instant = Task("Reminder", t, 0)
    mochi.add_task(walk)
    luna.add_task(instant)

    assert len(scheduler.conflict_warnings()) == 1
    assert walk.overlaps(instant) is False
    assert scheduler.check_conflict(instant) is None
