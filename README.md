# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Today's Schedule for Chelsea - Tuesday, October 20, 2026
============================================================
07:30-08:00  Morning walk         Buddy      HIGH
08:00-08:15  Breakfast feeding    Whiskers   MEDIUM
14:00-15:00  Vet check-up         Buddy      HIGH
18:30-18:50  Grooming             Whiskers   LOW
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```
```
python -m pytest
```
This command checks the following:
- Basics: mark_complete flips a task's status, and add_task adds to the pet's task list.

- Recurrence:
--> Daily and weekly tasks spawn the next occurrence.
--> Completing the same task twice doesn't create a duplicate.
--> Late or early completion lands on the correct next slot.
--> A completion exactly at the next slot skips to the one after.
--> A non-recurring task spawns nothing.
--> The new task copies the old one's fields but gets a fresh id.
--> A task with no pet returns an unattached next task.

- Sorting:
--> Tasks come back in chronological order by full datetime, with ties broken by priority.
--> sort_by_time is stable, can be reversed, and doesn't mutate its input.
--> Empty inputs return empty lists.

- Conflict detection:
--> Same-time tasks are flagged for the same pet and across pets.
--> Back-to-back tasks and completed tasks don't conflict.
--> A contained task counts as a single conflict.
--> Chained overlaps report only the real pairs.
--> check_conflict returns a message or None without raising.

- Availability: build_schedule excludes completed tasks and tasks outside the owner's available hours, and returns the rest in order.

--> A task that crosses midnight is never considered available.
--> A zero-duration task at another task's start time is flagged by conflict_warnings but not by overlaps or check_conflict.

Confidence Level on system's reliability based on test results: 5 stars!

Sample test output:

```
========================= test session starts =========================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\kai_1\Coding\codepath\aiEng101\pawpal
plugins: anyio-4.15.1
collected 26 items                                                     

tests\test_pawpal.py ..........................                  [100%]

========================= 26 passed in 0.06s ==========================
```

## 📐 Smarter Scheduling

### Implementation summary

The scheduling logic lives in `pawpal_system.py`and is built from four classes plus two enums (`Priority` and `Recurrence`):

- **Owner** holds a list of pets and the hours of the day they're available. `is_available(task)` checks whether a task fits inside those hours, and `get_all_tasks()` gathers every pet's tasks.
- **Pet** holds its own list of tasks. Tasks live only on pets, so there is a single source of truth.
- **Task** has a start time, duration, priority, and recurrence. It knows its `end_time`, whether it `overlaps` another task, and how to `mark_complete()`. Completing a daily or weekly task creates the next occurrence and adds it to the same pet.
- **Scheduler** wraps an `Owner` and does the planning:
  - `filter_tasks` narrows tasks by pet, completion, minimum priority, or time range.
  - `sort_tasks` orders tasks chronologically, with higher priority first on ties.
  - `find_conflicts` finds overlapping pairs across all pets, since the owner can only do one thing at a time.
  - `build_schedule` returns the pending tasks that fit the owner's available hours, in order.

Owner ↔ Pet ↔ Task are linked in both directions. `add_pet` and `add_task` keep both sides in sync and move an item off its previous parent. The classes use identity equality, so two identical-looking tasks or pets are still treated as separate objects.

### Features at a glance

|      Feature      | Method(s)                                                                                          | Notes                               |
|-------------------|----------------------------------------------------------------------------------------------------|-------------------------------------|
| Task sorting      | `Scheduler.sort_tasks`, `Scheduler.sort_by_time`                                                   | Chronological; `sort_tasks` breaks ties by priority
| Filtering         | `Scheduler.filter_tasks`, `Scheduler.filter_by_status_or_pet`, `Owner.is_available`                | By pet, status, priority, time range, or pet name; within owner hours
| Conflict handling | `Task.overlaps`, `Scheduler.find_conflicts`, `conflicts_with`, `conflict_warnings`, `check_conflict` | Warns instead of blocking; works within and across pets
| Recurring tasks   | `Recurrence.interval`, `Task.mark_complete`                                                        | Daily or weekly; next occurrence created automatically

### Sorting

- `Scheduler.sort_tasks(tasks)` orders tasks by start time. When two start at the same time, the higher priority comes first. `build_schedule` uses this.
- `Scheduler.sort_by_time(tasks=None, reverse=False)` orders by start time only. The sort is stable, so ties keep their input order. It defaults to every task across the owner's pets, and `reverse=True` gives latest first.
- Both return a new list and leave each pet's own task list untouched.

### Filtering

- `Scheduler.filter_tasks(...)` narrows tasks by pet object, `completed`, `min_priority`, and a `start`/`end` time range. Any criterion you leave out is ignored.
- `Scheduler.filter_by_status_or_pet(completed=None, pet_name=None)` filters by completion status and/or pet name. The name match is case-insensitive and exact. Giving both narrows to tasks matching both.
- `Owner.is_available(task)` checks that a task falls inside the owner's available hours.
- `Scheduler.build_schedule()` combines these: pending tasks only, within available hours, sorted with `sort_tasks`.

### Conflict detection

The owner can only do one thing at a time, so conflicts are checked across all pets as well as within one pet. Two tasks at exactly the same time count as a conflict. Back-to-back tasks (one ends when the next starts) do not.

- `Task.overlaps(other)` is true when the two time windows overlap.
- `Scheduler.find_conflicts(tasks=None)` sorts the tasks and sweeps once, stopping early for each task once the next one starts after it ends. It returns the overlapping pairs. It counts completed tasks too, so filter first if you only want pending ones.
- `Scheduler.conflict_warnings(tasks=None)` returns one readable message per overlapping pair of pending tasks, labeled "same pet" or "different pets".
- `Scheduler.conflicts_with(task)` lists the pending tasks that overlap one task.
- `Scheduler.check_conflict(task)` returns a warning message for one task, or `None` if it is clear.

This is a lightweight strategy: conflicts are reported as messages and never raise or reject a task. The app shows a warning when you add a clashing task and lists conflicts when you generate the schedule.

### Recurring tasks

- `Recurrence.interval()` gives the gap between occurrences: one day for `DAILY`, one week for `WEEKLY`, and `None` for `NONE`.
- `Task.mark_complete(now=None)` marks the task done. For a recurring task it creates the next occurrence, copying the description, duration, priority and recurrence, and attaches it to the same pet via `Pet.add_task`. It returns the new task, or `None` for a one-off task.
- Calling it again on an already completed task does nothing, so double-clicks can't create duplicates.
- If a task is completed late, the next occurrence skips ahead to the first slot after `now` instead of landing in the past. The next start is computed from the task's original start time, so the schedule keeps its cadence. The optional `now` argument exists so tests don't depend on the clock.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
