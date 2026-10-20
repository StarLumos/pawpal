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
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
