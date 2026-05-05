# Churn Prevention Playbook — CampusClip

*Western University Launch — August 2026*

---

## At-Risk Signals: What Predicts a Delete in the First 7 Days

These behaviours in the first week are the strongest predictors of a student deleting CampusClip:

| Signal | Window | Risk level |
|---|---|---|
| Downloaded but never completed signup | 2 hours post-download | Critical |
| Completed signup but skipped syllabus upload | 24 hours post-signup | High |
| Opened app once, never returned | 48 hours post-signup | High |
| Joined zero classes | 48 hours post-signup | High |
| Opened social feed, saw no classmates, closed immediately | First session | High |
| No second open within 72 hours | 72 hours post-signup | Medium |
| Only used academic side, never engaged social | 7 days post-signup | Medium |

---

## Intervention Playbook

### Signal 1: Downloaded, never completed signup
**Trigger:** App opened but signup not completed within 2 hours

**Push notification (2 hours after download):**
> your campus is already in here

**Push notification (24 hours, if still no signup):**
> takes 45 seconds. your classes are waiting.

**Action:** If no signup after 48 hours, suppress further notifications — they've churned at install. Don't spam them into a permanent mute.

---

### Signal 2: Signed up, skipped syllabus upload
**Trigger:** Completed account creation but skipped or exited the syllabus prompt

**Push notification (same day, evening):**
> photo your syllabus → your whole semester appears. try it before class tomorrow

**Push notification (next morning, 8am):**
> first class today? snap your syllabus on the way in. 20 seconds.

**In-app empty state (every time they open without uploading):**
> Your semester starts here.
> Photograph your syllabus and we'll pull out every assignment, due date, and grade weight automatically.
> [Scan syllabus] [I don't have it yet → remind me first day of class]

---

### Signal 3: Opened once, never returned
**Trigger:** No second open within 48 hours of first session

**Push notification (48 hours):**
> 12 Western students joined their classes today. yours might be in there.

**Push notification (72 hours, if still no return):**
> your PSYCH 1000 class has 8 people in it now
*(Use the actual class they enrolled in. If no class joined, use the most popular first-year course at Western.)*

**Email (72 hours):**

Subject: you left before the good part

> Hey [Name],
>
> Most students open CampusClip, look around, and think "okay, but where's my stuff?"
>
> Fair. The app gets useful the second you photograph your syllabus and join your classes. Before that it's just an empty room.
>
> Here's what takes 2 minutes:
> 1. Open CampusClip
> 2. Tap + → Scan syllabus (point your camera at it)
> 3. Join your classes
>
> That's it. Your assignments appear, your classmates are there, and your grade stays calculated all semester.
>
> — CampusClip

---

### Signal 4: Opened social feed, saw no classmates, closed
**Trigger:** Visited the social/classmates tab but spent less than 10 seconds and left

**This is the cold start churn moment — the highest risk scenario at launch.**

**In-app immediate response (fires if they try to leave):**
> Western is just getting started on CampusClip.
> You're one of the first students here — the students who join now are the ones who shape how their campus uses it.
> [Invite a classmate] [Keep exploring]

**Push notification (next day):**
> 3 more students from your PSYCH 1000 class joined last night

**Strategy note:** The pre-seeding plan (course pages, club pages, campus events) must be executed before August launch to ensure no student ever opens to a completely empty feed. Even 10 pre-populated posts per major class page is enough to create the impression of activity.

---

### Signal 5: No engagement with social side after 7 days
**Trigger:** Student has used grade tracking and syllabus features but never visited classmates or social feed

**Push notification (day 7):**
> you've got your grades sorted. did you know your classmates are already here?

**In-app prompt (appears on home screen day 8):**
> 5 people in your PSYCH 1000 class are already connected.
> See who's there → [View classmates]

---

## Win-Back Sequence: Gone 14 Days Without Opening

If a student hasn't opened the app in 14 days, they are churning. This is the recovery sequence.

**Day 14 — Push notification:**
> your grades are waiting (and one assignment is due soon)

**Day 14 — Email:**

Subject: you have an assignment due in 4 days

> Hey [Name],
>
> Quick heads up — based on your [Course Name] syllabus, you have [Assignment Name] due [Date].
>
> You set this up in CampusClip a few weeks ago. Just thought you'd want to know.
>
> [Open CampusClip]

*(If no syllabus was uploaded, fall back to: "Your classmates have been active this week.")*

---

**Day 17 — Push notification (if still no open):**
> midterms are coming. your grades are already calculated.

**Day 21 — Final email:**

Subject: still here if you need it

> Hey [Name],
>
> We're not going to keep nudging you.
>
> CampusClip is here when you need it — especially around midterms when keeping track of everything gets harder.
>
> Your syllabus data is still there. Your classmates are still there. Whenever you're ready.
>
> [Open CampusClip]

**Day 21 — Suppress all further push notifications.** Do not spam a disengaged user. If they come back organically, re-enter the normal engagement flow.

---

## Cold Start Churn: The Specific August–September Problem

Students who download during launch week are the highest churn risk because the network is thin. Standard retention tactics assume the product already delivers social value. Here it doesn't yet.

**The strategy: buy time with academic value while the network builds.**

If a student's social feed is empty, ensure the academic side is immediately, undeniably useful:
- Syllabus upload should work perfectly from day one — this is the fallback value prop
- Grade calculator must be accurate — if it miscalculates, trust is gone instantly
- Due date reminders must fire reliably — one missed assignment kills the product

**The bridge message (fires on day 5 for students not yet seeing social activity):**

Push:
> the academic stuff saves you time every week. the social side gets better as more of your campus joins. stick around — Western is growing fast.

**The density milestone notification (fires when a class hits 10 members):**

Push:
> your [Course Name] class just hit 10 students on CampusClip. go say hi.

This notification is one of the most important in the entire product during the launch window — it signals that the cold start is ending.

---

## Dunning: Failed Payments

*(For future monetisation — not applicable at free launch. Implement before any paid tier is introduced.)*

When a payment fails:
- Day 1: In-app banner only, no notification — most retries succeed automatically
- Day 3: Email with one-tap payment update link
- Day 5: Push notification: "keep your [feature] — update your payment"
- Day 7: Final email before downgrade
- Day 8: Downgrade to free, send "you've been moved to free plan" email with reactivation CTA

---

## Metrics to Watch

| Metric | Target | Alert threshold |
|---|---|---|
| Day 1 retention | >60% | <45% |
| Day 7 retention | >35% | <25% |
| Day 30 retention | >20% | <15% |
| Syllabus upload rate (within 48hrs of signup) | >50% | <35% |
| Class join rate (within 48hrs of signup) | >70% | <50% |
| Both-sides activation (academic + social used in first week) | >30% | <20% |
