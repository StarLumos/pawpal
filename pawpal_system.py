from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    description: str
    time_stamp: str
    duration: int
    priority: str
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    age: int
    breed: str
    owner: Optional[Owner] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def list_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def list_pets(self) -> List[Pet]:
        pass


@dataclass
class Scheduler:
    tasks: List[Task] = field(default_factory=list)

    def get_all_tasks(self, pets: List[Pet]) -> List[Task]:
        pass

    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        pass
