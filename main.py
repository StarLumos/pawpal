from datetime import datetime

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Today at the given time."""
    return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


def pet_name(task: Task) -> str:
    return task.pet.name if task.pet else "-"


def main() -> None:
    owner = Owner(name="Chelsea", contact="chelsea@example.com",
                  available_start=6, available_end=22)

    buddy = Pet(name="Buddy", age=3, breed="Golden Retriever")
    whiskers = Pet(name="Whiskers", age=5, breed="Tabby Cat")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    buddy.add_task(Task("Morning walk", at(7, 30), 30, Priority.HIGH, Recurrence.DAILY))
    buddy.add_task(Task("Vet check-up", at(14, 0), 60, Priority.HIGH))
    whiskers.add_task(Task("Breakfast feeding", at(8, 0), 15, Priority.MEDIUM, Recurrence.DAILY))
    whiskers.add_task(Task("Grooming", at(18, 30), 20, Priority.LOW))

    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule()

    print(f"Today's Schedule for {owner.name} - {datetime.now():%A, %B %d, %Y}")
    print("=" * 60)
    for task in schedule:
        print(
            f"{task.start_time:%H:%M}-{task.end_time:%H:%M}  "
            f"{task.description:<20} {pet_name(task):<10} {task.priority.name}"
        )

    conflicts = scheduler.find_conflicts()
    if conflicts:
        print("\nConflicts:")
        for a, b in conflicts:
            print(f"  '{a.description}' ({pet_name(a)}) overlaps '{b.description}' ({pet_name(b)})")


if __name__ == "__main__":
    main()
