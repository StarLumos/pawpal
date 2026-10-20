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

Sample test output:

```
# Paste your pytest output here
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

> Fill in once you've implemented scheduling logic.

|      Feature      | Method(s) |               Notes               |
|-------------------|-----------|-----------------------------------|
| Task sorting      |           | e.g., by priority, duration       |
| Filtering         |           | e.g., skip tasks if time runs out |
| Conflict handling |           | e.g., overlapping time slots      |
| Recurring tasks   |           | e.g., daily vs. weekly            |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
