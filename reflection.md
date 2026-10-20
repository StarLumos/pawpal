# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
3 core actions a user should be able to perform:
    1. add owner/pet information
    2. add events/tasks (like scheduling a walk)
    3. generate daily schedule/seeing today's tasks

- Owner class
--> name (str)
--> pets (list of Pet objects)
==> add pet
==> remove pet
==> list all pets & their info

- Pet class (inheritance from Owner)
--> name (str)
--> age (int)
--> breed (str)
--> owner (Owner object)
--> tasks to be carried out for this pet (list of Task objects)
==> add tasks
==> remove tasks
==> list tasks

- Task class (inheritance from Pet)
--> description (str)
--> time stamp (str)
--> duration (int for minutes)
--> completion status
--> priority (low, medium, high)
==> mark_complete

- Scheduler class
--> list of tasks to be carried out (list of Task objects)
==> retrieve all tasks for multiple pets
==> filter/organize tasks for multiple pets

- What classes did you include, and what responsibilities did you assign to each?
I included four key classes: Owner, Pet, Task, and Scheduler, and their responsibilities can be viewed through their methods. For example, owners can add or remove a pet, as well as list all of their pets. 

**b. Design changes**

- Did your design change during implementation?
Yes, my design did change during implementation because there were several missing relationships and logic bottlenecks.
- If yes, describe at least one change and why you made it.
One of the big changes I made is in the ability to call back the name of the pet that a certain task is to be carried for. It was important for Task to know what its Pet is so that tasks that read the same aren't mixed up for several different pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler considers start time, duration, priority, and the owner's available hours. It also skips completed tasks and flags tasks that overlap, even across different pets.
- How did you decide which constraints mattered most?
Time mattered most because the owner can only do one thing at a time, so the schedule is sorted chronologically and conflicts are checked across all pets. Priority only breaks ties when two tasks start at the same time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler reports conflicts instead of resolving them. It doesn't move or drop overlapping tasks, and `build_schedule` simply leaves out tasks outside the owner's available hours.
- Why is that tradeoff reasonable for this scenario?
The owner knows their routine best, so it's safer to point out overlaps and let them decide than to silently reshuffle their pet care.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI to turn my UML into class skeletons, implement the core logic, and write docstrings and README summaries.
- What kinds of prompts or questions were most helpful?
Small, specific requests that pointed at a file or method worked best, such as "add 1-line docstrings to my methods in pawpal_system.py".

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I revised the design after the first pass because the classes were missing relationships, such as Task needing to know its Pet.
- How did you evaluate or verify what the AI suggested?
I checked the code against my UML, ran the sample schedule in `main.py`, and wrote tests for task completion and task addition.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I wrote an automated pytest suite covering the core behaviors: marking a task complete, adding a task to a pet, and sorting tasks chronologically (with priority breaking ties at the same start time). I also tested recurring tasks (completing a daily task creates the next one, late completions skip past occurrences, completing twice doesn't duplicate, non-recurring tasks spawn nothing) and conflict detection (same start time for one pet and across pets, back-to-back tasks not conflicting, completed tasks ignored, chained overlaps reporting only the real pairs). Finally, I tested `build_schedule` excluding completed and out-of-hours tasks, plus empty inputs and tasks that cross midnight.
- Why were these tests important?
The scheduler is the heart of the app and its bugs are quiet: a wrong sort order or a missed overlap still produces a schedule that looks fine. The tests pin down the rules I decided on, so I could change the code (and the UI on top of it) without breaking them unnoticed.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Very confident for normal use: a single owner's day with a handful of tasks across a few pets. The main paths and many edge cases are covered, and the tests pass.
- What edge cases would you test next if you had more time?
One test already shows a known gap: a zero-duration task that starts at another task's start time is flagged inconsistently. Next I would test tasks that span midnight (currently treated as never available), daylight saving changes, recurrence other than daily, and many pets with heavily overlapping tasks. I would also test the Streamlit UI flow, since the tests only cover the logic classes.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with how the backend and the UI ended up connected. The scheduling logic (sorting, filtering, recurring tasks, conflict detection) lives in `pawpal_system.py` and is tested on its own, and the Streamlit app just calls it. The final UML diagram, the README walkthrough, and the test suite also make the project easy to understand and trust.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would let the scheduler suggest a fix for conflicts (such as the next free slot) while still leaving the decision to the owner. I would also save data between sessions, handle tasks that cross midnight, support more recurrence options than daily, and clean up the original design where Pet and Task were described as inheriting from Owner and Pet. They are really "has-a" relationships (an owner has pets, a pet has tasks), which composition models better.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is fast at producing code, but I still have to own the design. The best results came when I decided the structure and rules first (the UML, what counts as a conflict, what the scheduler should and shouldn't do) and then gave the AI small, specific tasks. Checking its output against my design, running it, and testing it is what caught the missing relationships and edge cases.
