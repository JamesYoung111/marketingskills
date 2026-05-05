# CampusClip Onboarding Flow — Western University Launch

*CRO Specialist Deliverable | August 2026 Launch*

---

## The Signup Flow: Download to First Meaningful Action

### Design Principle

Every screen before the aha moment is a tax. The signup flow exists to collect only what is required to deliver value — nothing more. All personalization, profile completion, and feature discovery is deferred until after the student has experienced something real.

Target: download to first meaningful action in under 4 minutes.

---

### Screen-by-Screen Flow

**Screen 0 — App Store → Download**

No friction here. The download is the first conversion. Nothing blocks it.

---

**Screen 1 — Welcome**

> *"Your whole uni life, in one place."*
>
> Classes. Grades. Classmates. Everything that actually matters this semester.
>
> [**Get started**]
>
> *Already have an account? Sign in*

**What to ask:** Nothing. One tap.

**What to skip:** Feature tours, permission requests, explainer carousels. Do not explain the product here. Show it instead.

---

**Screen 2 — Account Creation**

Single screen. Three fields maximum.

> **Create your account**
>
> [Full name]
> [Email] ← default to their school email if possible via keyboard suggestion
> [Password]
>
> Or [**Continue with Google**] (primary, above the fold)
> Or [**Continue with Apple**]
>
> *By continuing you agree to our Terms and Privacy Policy.*
>
> [**Create account**]

**What to ask:** Name, email, password — or social auth.

**What to skip:** Phone number, year of study, program, profile photo. Collect these later via progressive profiling once they are inside.

**What to defer:** Every personalization question. You will ask these after the aha moment, when they have a reason to care.

**CTA:** "Create account" — not "Sign up free," not "Join CampusClip." Direct and transactional.

---

**Screen 3 — School Confirmation**

One tap. Pre-selected based on launch context.

> **Your campus**
>
> [Western University ✓]
>
> *Not your school? Other schools coming soon — we'll let you know.*
>
> [**That's me**]

**What to ask:** Confirm campus only.

**What to skip:** Asking them to search or type. Western is the only campus at launch. Pre-select it. Do not make them do work to confirm what you already know.

**What to defer:** Other campus selection (not relevant at launch).

---

**Screen 4 — Notification Permission**

iOS and Android require a native permission prompt. Frame it before the prompt fires.

> **Stay on top of things**
>
> CampusClip will let you know when an assignment is due, when a classmate posts in your class, and when something's happening on campus.
>
> These are actually useful. Not spam.
>
> [**Turn on notifications**]
>
> *Maybe later*

**When it fires:** After account creation, before they enter the product. Do not ask mid-session.

**Copy rationale:** The phrase "actually useful" directly names the objection (students are notification-fatigued). It signals self-awareness without being sycophantic.

---

**Screen 5 — The Prompt That Delivers the Aha Moment**

This is not a tutorial. This is the product doing the thing.

> **Add your first class**
>
> Photograph your syllabus and we'll pull out every assignment, due date, and grade weight automatically.
>
> Or just type your course code if you don't have it handy.
>
> [**Scan a syllabus**] ← primary
> [**Enter course code manually**] ← secondary

**What to ask:** Their first class, right now.

**What to skip:** Any explanation of how it works. Show the result instead. The scan takes 15 seconds. Let the experience explain itself.

**Why this is Screen 5 and not later:** The syllabus scan is the aha moment. Deferring it to a checklist or a second session means most students will never do it. Put it in the critical path.

---

**Screen 6 — Result Screen (post-scan)**

This is the moment. The app has just done something no other app does.

> **There's your class.**
>
> [Displays: Course name, instructor, list of assignments, grade weights, due dates — all parsed from the photo]
>
> *Check anything that looks wrong.*
>
> [**Looks good**]

If OCR misses something, offer a quick edit. But the student does not need to re-enter everything — just correct the errors. A partial result that is mostly right is still remarkable.

---

**Screen 7 — Classmates Prompt**

The social layer activates here, immediately after the academic layer delivers value.

> **Your classmates are in here too.**
>
> [Shows 2–3 profile previews, even if just placeholder silhouettes for now]
>
> See who else is in [Course Name]. Post a question. Find a study partner.
>
> [**See my class**]
>
> *I'll check later*

**What to skip:** Asking them to add friends from their contacts. That is a different app's behavior. CampusClip's social layer is class-native — it does not need an address book import.

---

**First Meaningful Action Achieved.**

The student has scanned their syllabus, seen their assignments auto-populate, and discovered their classmates exist in the same space. Total time from download: under 4 minutes if scan is smooth, 6–7 minutes if they type manually.

---

## The Aha Moment

### What It Is

**Seeing your first syllabus parsed.**

The moment a student photographs their syllabus and watches every assignment, weight, and due date appear — organized, labeled, and already in their calendar — is the only moment in the product that cannot be replicated by anything else they already use.

This is the moment that makes a student say "okay, this is actually useful."

It works because:
- It is effortless (one photo, 15 seconds)
- The output is immediately practical (due dates, grade weights)
- It removes something they hated doing (manual calendar entry)
- It is surprising — they did not expect it to be that fast or that accurate

### How to Get Them There Within the First Session

**Do not put it behind a checklist.** Put the syllabus scan in the critical path of onboarding — Screen 5, right after account creation and notifications. Every step before it should be fast enough that a student does not put the phone down.

**Handle the "I don't have my syllabus" case gracefully.** Some students open the app before classes start or before they've been handed a syllabus. For these students:

- Offer "Enter course code manually" as a fallback
- Show a preview of what the parsed syllabus view looks like ("Here's what it'll look like once you add it")
- Set a Day 1 reminder: "Your syllabus reminder is set for the first week of class."

**Handle the cold start case for the scan.** If OCR quality is imperfect, show the partial result and let them confirm or edit. A mostly-right result is still dramatically faster than typing everything manually. Never fail silently — if the scan produces nothing, say so and offer the manual path immediately.

---

## The Cold Start Solution

### The Problem

A student at Western opens CampusClip in early August 2026. There are 10 registered users. The app is technically live but socially empty. This is the highest-risk moment in the launch.

If the app feels like a ghost town, the student will delete it before the social layer ever becomes useful. The cold start problem is not a technical problem — it is a perception problem.

### What They Should See

**Not emptiness. Anticipation.**

The product needs to communicate: *this is real, it is coming, and you are here at the right time.*

---

**Cold Start State — Class Feed**

> **[Course Code] — Western University**
>
> You're one of the first students in this class on CampusClip.
>
> Your assignments are set up. When your classmates join, they'll be right here.
>
> [**Invite classmates**] ← generates a shareable link with the course pre-filled
>
> *[First name], be the person who gets everyone organized this semester.*

**Design rationale:** The framing "one of the first" transforms emptiness into status. This student is not looking at a failed product — they are early. The CTA "invite classmates" gives them an action that directly addresses their concern (no one is here yet) and activates the growth loop.

---

**Cold Start State — Campus Feed**

> **Western University**
>
> [Shows 2–3 upcoming campus events — pulled from public sources, pre-seeded by the team, or submitted by the founding user cohort]
>
> [Shows a count: "14 students are already on CampusClip at Western"]
>
> *More joining every day. Add your classes to be there when they do.*

**The number matters.** Even 14 is more compelling than 0. Keep this number real — never inflate it. Update it in near-real-time. Students will share the screenshot when they see it grow.

---

**Cold Start State — Club Discovery**

If the clubs directory is empty, pre-seed it before launch with the top 20–30 Western clubs, pulled from public university sources. Even if no club members are on the app yet, a student can follow a club and be notified when it activates.

> **[Club Name] — not on CampusClip yet**
>
> We've added them so you can follow along when they join.
>
> [**Follow**]
>
> *We'll notify you when [Club Name] posts their first update.*

This turns absence into anticipation. The student is not looking at a blank directory — they are seeing organizations they recognize, and they are one step ahead when those clubs do activate.

---

**Pre-seeded content strategy for launch week**

Before August launch, the CampusClip team should manually seed:
- All Western course codes for Fall 2026 (public information)
- Top 30 Western clubs with names, descriptions, and social links
- 5–10 upcoming campus events for September
- A "Western Class of 2026" community space as a default join for all new users

Even with 10 real users, the app should not look like it was launched yesterday. It should look like it was built for Western.

---

## Onboarding Copy — Screen by Screen

### Welcome Screen

> **Your whole uni life, in one place.**
>
> Classes. Grades. Classmates. Everything that actually matters this semester.
>
> [Get started]

---

### Account Creation Screen

> **Create your account**
>
> [Full name] — placeholder: *Taylor Wilson*
> [Email] — placeholder: *you@uwo.ca*
> [Password] — placeholder: *At least 8 characters*
>
> [Continue with Google]
> [Continue with Apple]
>
> [Create account]
>
> *By continuing you agree to our [Terms] and [Privacy Policy].*

---

### School Confirmation Screen

> **Your campus**
>
> [Western University ✓]
>
> *Other schools coming soon.*
>
> [That's me]

---

### Notification Permission Pre-Prompt

> **Stay on top of things**
>
> We'll let you know when an assignment is coming up, when a classmate posts, and when something's happening on campus.
>
> These are actually useful. Not spam.
>
> [Turn on notifications]
> *Maybe later*

---

### Syllabus Scan Prompt

> **Add your first class**
>
> Photograph your syllabus and we'll pull out every assignment, due date, and grade weight — automatically.
>
> Or just type your course code if you don't have it yet.
>
> [Scan a syllabus]
> [Enter course code manually]

---

### Post-Scan Result Screen

> **There's your class.**
>
> [Parsed course name, assignments, weights, due dates]
>
> *Anything look off? Tap to edit.*
>
> [Looks good]

---

### Classmates Prompt

> **Your classmates are in here too.**
>
> [Profile previews or placeholder avatars for the class]
>
> See who else is in [Course Code]. Post a question. Find a study partner.
>
> [See my class]
> *I'll check later*

---

### Empty State — No Classmates Yet

> You're one of the first in [Course Code] on CampusClip.
>
> Your assignments are set. When your classmates join, they'll be right here.
>
> [Invite classmates]

---

### Empty State — No Upcoming Events

> Nothing on campus this week — but that changes fast.
>
> [Browse clubs] or [Add another class]

---

### Empty State — Grade Tracker (no assignments graded yet)

> Your grades will show up here as you complete assignments.
>
> You're tracking [X] assignments in [Course Name].
>
> Right now: nothing graded yet — which means nothing to stress about.

---

### First Prompt After Completing Onboarding

Shown as an in-app card on the home screen, session 1, after the first class is added:

> **You're set up for [Course Code].**
>
> Add your other classes to see your full semester at a glance — and to find classmates across all of them.
>
> [Add another class]
> *Do it later*

---

## The First 7 Days — Email and In-App Sequence

### Trigger Logic

Emails and nudges are behavior-triggered, not time-based by default. A student who adds three classes on day one should not receive the "add your first class" prompt on day three. The sequence adapts based on what they have and have not done.

**Activation gates:**
- Gate 1: Account created
- Gate 2: First class added (syllabus scanned or course code entered)
- Gate 3: Second class added
- Gate 4: First classmate interaction (post, reply, or profile view)
- Gate 5: App opened on day 3 or later without a push notification

---

### Day 0 — Immediately After Signup

**Channel:** Email (sent within 2 minutes of account creation)

**Subject:** `You're in. Here's what to do first.`

**Body:**

> Hey [First name],
>
> Your CampusClip account is live. You're one of the first students at Western on it.
>
> One thing to do right now: photograph your syllabus. Takes about 15 seconds and it pulls every assignment and due date out automatically. No typing required.
>
> You can do it from the app right now.
>
> — The CampusClip team
>
> P.S. Add more than one class and you'll start to see how it all fits together.

**If they have already scanned a syllabus:** Skip this email. Trigger the Day 1 "add another class" nudge instead.

---

### Day 1 — Morning (if syllabus not yet scanned)

**Channel:** Push notification

> **[First name], your first assignment is one scan away.**
>
> Photograph your syllabus and CampusClip does the rest.

**If syllabus was scanned:** Fire this instead:

> **[Course Code] has [X] assignments this semester.**
>
> Add your other classes to see the full picture.

---

### Day 1 — Evening (if Gate 2 not reached)

**Channel:** Email

**Subject:** `Still works if your syllabus isn't ready yet`

**Body:**

> Hey [First name],
>
> If you haven't got your syllabus yet, that's fine — most professors don't post them until the first week of class.
>
> You can add your course code now and scan the syllabus when it drops. CampusClip will remind you.
>
> Or, if you want to see what the parsed version looks like before yours is ready, [here's a preview].
>
> Either way, we'll be here.
>
> — CampusClip

---

### Day 2 — Classmate Discovery (if Gate 2 reached, Gate 4 not reached)

**Channel:** Push notification

> **[X] students are in [Course Code] on CampusClip.**
>
> Tap to see who else is in your class.

**Channel:** In-app card on home screen

> **Your classmates are here.**
>
> [X] students in [Course Code] are already on CampusClip. See who they are — or post a question to break the ice.
>
> [See my class]

---

### Day 3 — Grade Tracker Introduction (if Gate 2 reached)

**Channel:** In-app tooltip, shown once on first open of day 3

> **Your grade is always calculated.**
>
> Every assignment you mark as done updates your running average automatically. No spreadsheet needed.
>
> [Got it]

**Channel:** Email (only if not opened app on day 2)

**Subject:** `Your grade is already in here`

**Body:**

> Hey [First name],
>
> Once you add your assignments, CampusClip keeps a running grade for every course — weighted correctly, updated every time you submit something.
>
> No more waiting for Canvas to post marks. No more guessing where you stand.
>
> Open the app and take a look.
>
> — CampusClip

---

### Day 4 — Second Class Nudge (if only one class added)

**Channel:** Push notification

> **One class in. How many are you actually taking?**
>
> Add the rest and see your whole semester in one place.

**Channel:** Email (only if not opened app on day 3 or 4)

**Subject:** `You're only seeing part of the picture`

**Body:**

> Hey [First name],
>
> Right now CampusClip only knows about one of your classes. Most students are taking four or five.
>
> Add the rest of your courses and you'll see everything — all your assignments, all your grades, all your classmates — without switching tabs or checking different apps.
>
> [Add your courses]
>
> — CampusClip

---

### Day 5 — Campus Events Discovery

**Channel:** In-app card (shown on first open, once)

> **What's on at Western this week**
>
> [List of 2–3 seeded events]
>
> *Clubs and events from across campus, all in one place.*
>
> [Explore campus]

---

### Day 7 — Re-engagement (if Gate 5 not reached — student has not opened on day 3 or later)

**Channel:** Email

**Subject:** `Your classmates are already using it`

**Body:**

> Hey [First name],
>
> A few things have happened in [Course Code] since you signed up.
>
> [If data is available: "[N] classmates have joined. [M] assignments have been tracked."]
>
> [If no data yet: "Your classes are set up and ready — your assignments, your grade tracker, your classmates."]
>
> The semester is about to start. Might as well have it all in one place.
>
> [Open CampusClip]
>
> — CampusClip

**Subject line alternatives to test:**
- `You've got [X] assignments due in the next two weeks`
- `[First name], here's what's happening in [Course Code]`
- `The app that knows your GPA before your professor does`

---

### Day 7 — Milestone Celebration (if all activation gates reached)

**Channel:** In-app toast notification

> **You've got [X] classes, [Y] assignments tracked, and [Z] classmates in CampusClip.**
>
> This is what it looks like when your uni life is actually in one place.

---

## Churn Risk Moments — The Three Danger Points

### Danger Point 1: Empty App on First Open (No Social Density)

**When it happens:** The student opens the app, navigates to the class feed or campus section, and sees nothing. No posts. No classmates. No events. The social layer is completely empty.

**Why they churn:** The product promised a social layer. What they got is a grade tracker with a blank feed. The gap between the promise and the experience is enough to delete the app.

**How to prevent it:**

Never show a genuinely empty screen. Every empty state needs forward momentum:
- "You're one of the first here" (status, not failure)
- A count of users that is already nonzero (even 8 is real)
- A clear action that produces an outcome (invite classmates, add a class, follow a club)
- Pre-seeded content — events, club listings, university-wide announcements — so the campus section never looks dead

Before launch, seed the campus feed with:
- The top 5 "most asked" questions about Western (academic calendar, drop dates, etc.)
- Upcoming events from the Western public calendar
- A pinned post from CampusClip that reads like a student wrote it, not a company

The first student who opens the app to an empty campus feed and sees a pinned post saying "Welcome to CampusClip at Western — you're here before everyone else. Add your classes and invite your coursemates." will feel differently than one who sees a blank screen.

---

### Danger Point 2: The Syllabus Scan Fails or Feels Like Too Much Effort

**When it happens:** The student tries to scan their syllabus. Either the OCR fails (produces garbled or incomplete results) or the student does not have the syllabus on hand and decides to skip it — and then never comes back to it.

**Why they churn:** The syllabus scan is the aha moment. If it does not happen — either because of a technical failure or a deferred "I'll do it later" that becomes never — the student has no experience of core value. They saw a sign-up flow and a blank calendar. There is nothing to come back for.

**How to prevent it:**

For OCR failures:
- Never fail silently. If the scan produces poor results, say so immediately: "That one was hard to read. Here's what we got — tap anything that looks wrong." Show partial results. Even 60% correct is useful.
- Offer a retry (rescan) and a manual entry path in the same screen, not as a modal sequence.
- If scan fails entirely: "The lighting might be off — try a flat surface. Or, enter your course code and we'll remind you to scan later."

For the "I'll do it later" skip:
- Do not let the skip disappear into the void. When a student skips the scan, set a reminder for Day 1 of classes: "Your classes start [date]. Scan your syllabus now and you're set for the semester."
- Show the ghost of the value they did not get: "When you scan [Course Code], all [N] assignments will appear here automatically." — N can be estimated from course type. Show the preview state.

For the "I don't have my syllabus yet" case:
- Add the course code now. Set a smart reminder for the first day of classes.
- Do not ask them to come back and remember on their own. The app should do that for them.

---

### Danger Point 3: Coming Back on Day 2 or 3 and Finding Nothing New

**When it happens:** The student set up their classes, saw their assignments, and felt good. Then they opened the app on day two and nothing had changed. No new posts from classmates. No new assignments. No reason to open again tomorrow.

**Why they churn:** The habit loop has not formed. Academic tracking is high-value but low-frequency — a student does not need to check their grade tracker three times a day. Without the social layer activating (posts, classmate activity, events), there is no pull to open the app again.

**How to prevent it:**

Build the re-open hook into the first session:
- After the student adds their first class, show an upcoming due date: "Your first assignment is in [X days]. We'll remind you the day before." Now there is an appointment in their future that CampusClip owns.
- After the student visits the class feed, show them a prompt to post: "Be the first to post in [Course Code]. Introduce yourself or ask a question." The first student who posts creates content for everyone who opens after them.

Use notifications strategically on day 2 and 3:
- Only fire a push if there is something real to show. Not a generic "Come back!" — a specific "Someone posted in [Course Code]" or "Your assignment [name] is due in 3 days."
- If nothing real has happened, use a quiet in-app card when they open, not a push. The goal is to reward opening, not to interrupt.

Make the grade tracker feel alive even before grades exist:
- Show the empty grade tracker with the structure in place: course name, assignments listed, grade weight breakdown. It should feel like a prepared dashboard, not an empty page.
- Add a subtle motivational state: "All assignments tracked. 0% of the semester complete. You're on top of it."

Anchor the habit to a recurring behavior they already have:
- Day 3 in-app prompt: "Before your first class tomorrow, check your assignments here. Takes 10 seconds." This pairs the app open with a behavior (checking before class) that already exists in the student's routine.

---

## Summary — The Funnel That Needs to Hold

| Step | Target | Risk |
|---|---|---|
| Download → Account created | >80% | Friction in signup form |
| Account created → Notifications enabled | >60% | Generic permission framing |
| Notifications enabled → First class added | >75% | Student doesn't have syllabus |
| First class added → Aha moment (syllabus parsed) | >65% | OCR failure, skips to manual |
| Aha moment → Returns day 3+ | >45% | Empty social feed, no habit loop |
| Day 7 → Both sides of app in use | >30% | Single-feature use only |

The conversion that matters most is not download to signup. It is first class added to day-7 active user with both academic and social engagement. Every decision in this document is oriented toward that final step.

---

*Prepared for CampusClip Western University launch, August 2026.*
