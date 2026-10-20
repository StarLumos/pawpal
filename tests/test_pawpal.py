from datetime import datetime

from pawpal_system import Pet, Task


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
