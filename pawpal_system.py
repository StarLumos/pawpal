from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from typing import List, Optional, Tuple


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"

    def interval(self) -> Optional[timedelta]:
        """Time between occurrences, or None if the task doesn't repeat."""
        if self is Recurrence.DAILY:
            return timedelta(days=1)
        if self is Recurrence.WEEKLY:
            return timedelta(weeks=1)
        return None


# eq=False on all entities: equality is identity, so removing one of two
# identical-looking tasks/pets removes the right one and the Pet <-> Owner
# cycle can't recurse through __eq__.
@dataclass(eq=False)
class Task:
    description: str
    start_time: datetime
    duration: int  # minutes
    priority: Priority = Priority.MEDIUM
    recurrence: Recurrence = Recurrence.NONE
    completed: bool = False
    pet: Optional[Pet] = field(default=None, repr=False)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def end_time(self) -> datetime:
        """When the task finishes (start time plus duration)."""
        return self.start_time + timedelta(minutes=self.duration)

    def overlaps(self, other: Task) -> bool:
        """True if this task's time window overlaps the other's."""
        return self.start_time < other.end_time and other.start_time < self.end_time

    def mark_complete(self) -> Optional[Task]:
        """Mark done; if recurring, create and attach the next occurrence."""
        self.completed = True
        step = self.recurrence.interval()
        if step is None:
            return None
        next_task = Task(
            description=self.description,
            start_time=self.start_time + step,
            duration=self.duration,
            priority=self.priority,
            recurrence=self.recurrence,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task


@dataclass(eq=False)
class Pet:
    name: str
    age: int
    breed: str
    owner: Optional[Owner] = field(default=None, repr=False)
    tasks: List[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, detaching it from any previous pet."""
        if task.pet is not None and task.pet is not self:
            task.pet.remove_task(task)
        if not any(t is task for t in self.tasks):
            self.tasks.append(task)
        task.pet = self

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        self.tasks = [t for t in self.tasks if t is not task]
        if task.pet is self:
            task.pet = None

    def list_tasks(self) -> List[Task]:
        """A copy of this pet's task list."""
        return list(self.tasks)


@dataclass(eq=False)
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    contact: str = ""
    available_start: int = 0  # hour of day, 0-23
    available_end: int = 24  # hour of day, 1-24
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, detaching it from any previous owner."""
        if pet.owner is not None and pet.owner is not self:
            pet.owner.remove_pet(pet)
        if not any(p is pet for p in self.pets):
            self.pets.append(pet)
        pet.owner = self

    def remove_pet(self, pet: Pet) -> None:
        """Detach a pet from this owner."""
        self.pets = [p for p in self.pets if p is not pet]
        if pet.owner is self:
            pet.owner = None

    def list_pets(self) -> List[Pet]:
        """A copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> List[Task]:
        """Every pet's tasks together."""
        return [t for pet in self.pets for t in pet.list_tasks()]

    def is_available(self, task: Task) -> bool:
        """True if the task falls within the owner's daily available hours."""
        day = task.start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        window_start = day + timedelta(hours=self.available_start)
        window_end = day + timedelta(hours=self.available_end)
        return window_start <= task.start_time and task.end_time <= window_end


@dataclass
class Scheduler:
    """Builds a schedule from an Owner's pets; tasks live only on the pets."""

    owner: Owner

    def get_all_tasks(self) -> List[Task]:
        """Every task across the owner's pets."""
        return self.owner.get_all_tasks()

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        pet: Optional[Pet] = None,
        completed: Optional[bool] = None,
        min_priority: Optional[Priority] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Task]:
        """Tasks matching all given criteria; omitted criteria are ignored."""
        result = self.get_all_tasks() if tasks is None else list(tasks)
        if pet is not None:
            result = [t for t in result if t.pet is pet]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if min_priority is not None:
            result = [t for t in result if t.priority >= min_priority]
        if start is not None:
            result = [t for t in result if t.start_time >= start]
        if end is not None:
            result = [t for t in result if t.start_time < end]
        return result

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Chronological; higher priority first when start times tie."""
        return sorted(tasks, key=lambda t: (t.start_time, -t.priority))

    def find_conflicts(
        self, tasks: Optional[List[Task]] = None
    ) -> List[Tuple[Task, Task]]:
        """Overlapping pairs. The owner can only do one thing at a time, so
        this checks across all pets, not just within one."""
        ordered = self.sort_tasks(self.get_all_tasks() if tasks is None else tasks)
        conflicts: List[Tuple[Task, Task]] = []
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 :]:
                if b.start_time >= a.end_time:
                    break  # sorted by start, so nothing later can overlap a
                conflicts.append((a, b))
        return conflicts

    def build_schedule(self) -> List[Task]:
        """Pending tasks in order, limited to the owner's available hours."""
        pending = self.filter_tasks(completed=False)
        return self.sort_tasks([t for t in pending if self.owner.is_available(t)])
