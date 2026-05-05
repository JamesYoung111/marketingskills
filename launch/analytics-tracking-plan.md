# CampusClip Analytics Tracking Plan — Western University Launch (August 2026)

**Last updated:** 2026-05-05
**Tools:** Mixpanel (primary product analytics) + GA4 (marketing site) + Segment (event routing) + Branch (mobile attribution)
**Coverage:** Mobile app (iOS/Android) + marketing site (campusclip.ca)

---

## Naming Conventions

All events: `object_action` — lowercase, underscores, no spaces or special characters.
All user properties: `snake_case`.
No PII in any event property (no names, emails, student IDs in raw events).
All class IDs, assignment IDs, and user references in properties are hashed internal identifiers.

---

## Funnel Stage 1 — Acquisition

These events answer: which channels are bringing students to Western, and which convert to downloads?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `marketing_site_visited` | Any pageview on campusclip.ca | `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `page_path`, `referrer`, `device_type` | Attribution baseline — every downstream conversion traces back to this touchpoint |
| `app_store_link_clicked` | Student taps App Store or Google Play CTA on marketing site | `utm_source`, `utm_medium`, `utm_campaign`, `cta_location` (hero / feature_section / footer / nav), `device_type`, `os` | Measures which page sections and channels drive store visits; surfaces underperforming CTAs |
| `app_install_completed` | App opens for the first time after install (first-ever foreground event) | `install_source` (organic / referral / paid / campus_event / qr_code / frosh_week), `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `device_os`, `app_version`, `branch_attribution_matched` (bool) | The actual download — this is the conversion; connect to the UTM and Branch link that drove it |
| `referral_link_clicked` | Student opens the app from a peer share link | `referrer_user_id` (hashed), `share_surface` (push / in-app / social / sms), `utm_campaign`, `time_from_share_to_click_hours` | Measures organic word-of-mouth strength; K-factor input |
| `waitlist_signup_completed` | Pre-launch email capture form submitted on campusclip.ca | `utm_source`, `utm_medium`, `utm_campaign`, `school_name` (western), `page_path` | Builds pre-launch list; tracks which channels warm up fastest before August |

---

## Funnel Stage 2 — Activation

These events answer: which new students reach the moment they actually get the value of CampusClip — and where does everyone else drop off?

**Activation definition for CampusClip:** a student has completed at least one syllabus upload AND joined at least one class. Both conditions must be true. Students who only do one of the two have not experienced the product's compound value.

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `account_created` | Student completes signup (email or SSO) | `signup_method` (email / google / apple), `install_source`, `utm_source`, `utm_campaign`, `session_id`, `time_from_install_to_signup_seconds` | Top of the activation funnel — all onboarding drop-off is measured as a share of this |
| `onboarding_step_viewed` | Each onboarding screen renders | `step_number`, `step_name` (e.g. `add_your_classes`, `upload_syllabus`, `find_classmates`, `enable_notifications`), `is_skipped` (bool) | Pinpoints exactly where students abandon onboarding — fix the biggest drop-off first |
| `onboarding_completed` | Student lands on the main home screen after finishing onboarding | `steps_completed`, `steps_skipped`, `classes_added_count`, `syllabus_uploaded` (bool), `time_to_complete_seconds` | Baseline onboarding completion rate; segment by upload_completed to see activation gap |
| `syllabus_upload_started` | Student taps the camera or file upload button on the syllabus screen | `entry_point` (onboarding / class_detail / home_prompt / assignment_tab), `class_id` (hashed) | Measures intent to use the differentiating feature; gap between started and completed reveals OCR friction |
| `syllabus_upload_completed` | OCR parse succeeds and at least one assignment populates in the calendar | `assignments_detected_count`, `class_id` (hashed), `upload_method` (camera / file_import), `time_to_parse_seconds`, `entry_point` | **The aha moment.** This is the highest-value activation event in the entire app. Students who hit this are dramatically more likely to retain. |
| `syllabus_upload_failed` | OCR fails, times out, or returns zero assignments | `failure_reason` (bad_image / timeout / unsupported_format / zero_assignments_detected), `class_id` (hashed), `upload_method` | Tracks the size of the OCR failure problem to prioritise engineering improvements before launch |
| `class_joined` | Student joins a course in the app | `class_id` (hashed), `class_size_at_join`, `join_method` (search / qr_code / classmate_invite / course_code / browse), `entry_point`, `is_first_class` (bool) | Each join adds density to the social layer; track join method to optimise discovery mechanics |
| `classmate_viewed` | Student opens the classmates list inside a class | `class_id` (hashed), `classmates_count`, `days_since_class_joined` | Signals the social layer has value — students are looking for their people |
| `grade_tracker_opened` | Student opens the grade view for a class | `class_id` (hashed), `assignments_populated_count`, `current_grade_visible` (bool), `days_since_syllabus_upload` | Validates grade clarity feature is being discovered and used beyond the upload moment |
| `assignment_viewed` | Student taps an assignment from their feed, calendar, or grade tracker | `assignment_id` (hashed), `class_id` (hashed), `days_until_due`, `source` (feed / calendar / grade_tracker / widget), `is_overdue` (bool) | Measures academic-side engagement depth beyond the initial syllabus upload |
| `first_week_active` | System event: student opens the app on 3 or more of their first 7 days post-install | `days_opened_in_week_1`, `features_used` (array: academic / social / both), `syllabus_uploaded` (bool), `classes_joined_count` | Most reliable early habit proxy; segment by features_used to see which early activations predict 30-day retention |

---

## Funnel Stage 3 — Retention

These events answer: which students are forming a real habit, and which ones are fading before the social layer reaches density?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `app_opened` | App becomes active in foreground | `session_number`, `days_since_install`, `days_since_last_open`, `open_source` (direct / push_notification / share_link / widget), `user_segment` (academic_only / social_only / both_sides_active / inactive) | The raw frequency signal; `days_since_last_open` > 4 is the leading churn indicator |
| `class_feed_viewed` | Student opens and views the social feed inside a class | `class_id` (hashed), `messages_in_feed`, `time_spent_seconds`, `scrolled_past_fold` (bool) | Primary social layer engagement event; low time_spent on a non-empty feed suggests content quality issue |
| `message_sent` | Student sends a message in a class chat | `class_id` (hashed), `message_type` (text / poll / resource_share / reaction), `class_size` | Bi-directional social engagement — the strongest predictor of long-term retention in this app |
| `event_rsvp_completed` | Student RSVPs to a campus event | `event_id` (hashed), `event_type` (club / academic / orientation / social), `days_until_event`, `entry_point` (discover / class_feed / notification) | Campus events feature discovery; RSVP signals intent to show up, which re-engages lapsed users |
| `club_viewed` | Student opens a club page | `club_id` (hashed), `entry_point` (discover / class_feed / search / notification) | Measures the discovery layer usage; funnel to club_followed |
| `club_followed` | Student follows a club | `club_id` (hashed), `club_size_at_follow`, `entry_point` | Commitment signal for the social side; creates recurring notification hooks |
| `assignment_marked_complete` | Student taps the complete checkbox on an assignment | `assignment_id` (hashed), `class_id` (hashed), `days_until_due` (negative = late), `marked_early` (bool: >24h before due) | Academic habit signal; regular completions correlate strongly with next-week retention |
| `grade_recalculated` | Grade updates after a student enters new marks | `class_id` (hashed), `new_grade_bucket` (A / B / C / D / F), `assignments_graded_count`, `course_completion_pct` | Validates grade clarity is a maintained, live feature — not just a one-time onboarding novelty |
| `push_notification_received` | Push notification delivered to device | `notification_type` (churn_risk / assignment_due / classmate_joined / event_reminder / win_back), `campaign_id`, `days_since_last_open` | Delivery baseline; pairing with tapped gives open rate per notification type |
| `push_notification_tapped` | Student taps a push notification | `notification_type`, `campaign_id`, `hours_since_last_open`, `user_segment` | Measures each notification type's effectiveness; surfaces which campaigns re-engage vs. annoy |
| `both_sides_active_week` | System event (server-side, every Sunday midnight ET): user qualifies as both_sides_active for the current 7-day window | `week_number_since_install`, `academic_events_count`, `social_events_count`, `consecutive_both_sides_weeks` | **The north star event.** See dedicated section below. |
| `feature_unused_7d` | System event: a feature category has zero qualifying events for a user in the past 7 days | `feature_category` (academic / social / events / clubs), `days_since_last_use`, `user_segment` | Early churn signal — feeds directly into the intervention playbook in churn-prevention.md |
| `in_app_notification_dismissed` | Student dismisses an in-app nudge or banner without tapping | `notification_type`, `campaign_id`, `times_shown` | Signals over-messaging or irrelevant targeting; cap at 2 dismissals then suppress |

---

## Funnel Stage 4 — Referral

These events answer: is organic word-of-mouth growing the Western network, and which surfaces and students are driving it?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `share_sheet_opened` | Student taps share / invite from any surface | `share_surface` (class_detail / profile / onboarding_prompt / settings / assignment_tab), `class_id` (hashed, if applicable), `days_since_install` | Top of the referral funnel; shows which surfaces organically surface sharing intent |
| `invite_sent` | Student sends a specific invite via copy_link, contact, or social | `invite_method` (copy_link / contact_invite / social_share / sms), `share_surface`, `recipient_count`, `days_since_install` | Intent to refer — connect to downstream installs to compute per-channel referral rate |
| `invite_link_installed` | New user installs the app from a tracked referral link (Branch attribution) | `referrer_user_id` (hashed), `time_from_share_to_install_hours`, `install_source` (referral), `utm_campaign` | Closes the referral loop; the data for computing the K-factor |
| `viral_coefficient_computed` | System event (weekly batch): total invites sent / active users for the week | `k_factor_estimate`, `week_number`, `total_installs_from_referral` | K-factor proxy — track weekly during the launch window to see if word-of-mouth is self-sustaining |
| `nps_survey_completed` | In-app NPS prompt answered (triggered at Day 14, or Day 7 for highly active users) | `nps_score`, `nps_comment_provided` (bool), `days_since_install`, `user_segment`, `classes_joined_count` | Identifies promoters for referral activation; NPS < 7 triggers intervention before they fade |

---

## The 5 Metrics to Check Every Morning

These are the numbers on the daily dashboard during the Western launch window (August–September 2026). Everything else is context; these are decisions.

### 1. Daily Active Users (DAU) — Target: 70+ by end of September

**Definition:** Unique users who trigger `app_opened` on a given day.
**Dashboard view:** 7-day rolling average + yesterday's number side by side.
**Why this one:** The most direct measure of whether the network is alive. A flat or declining DAU in the first 8 weeks means the social layer never reaches density, and the January expansion to Guelph and Laurier will be built on a hollow foundation. The 7-day average smooths out weekday/weekend patterns that are pronounced in a student app.

### 2. Day-7 Retention Rate — Target: 40%+

**Definition:** Of all students who installed on Day 0 of a given cohort, what percentage opened the app on Day 7 (±1 day window).
**Dashboard view:** Rolling cohort table — D1, D3, D7, D14, D30 retention by install week.
**Why this one:** The single clearest signal of whether CampusClip formed a habit. Students who make it to Day 7 are dramatically more likely to reach Week 4. If Day-7 retention is below 30% entering September, the activation sequence needs rework before any expansion. High Day-1, low Day-7 is a specific pattern: students are curious but not convinced — activation problem. Low Day-1 and low Day-7 is a distribution problem.

### 3. Syllabus Upload Completion Rate — Target: 60%+ of account creates

**Definition:** `syllabus_upload_completed` events / `account_created` events over the trailing 7 days.
**Dashboard view:** Rolling 7-day rate with a 30-day trend line.
**Why this one:** The syllabus upload is the aha moment. Students who complete it see their academic life populate immediately — they are far less likely to delete the app. A rate below 40% is a red flag: students are either not reaching the feature in onboarding, the OCR is failing too often, or the feature is not compelling enough in context. Watch `syllabus_upload_failed` events in parallel to distinguish the failure mode.

### 4. Both-Sides Active Rate — Target: 30%+ of WAU by end of September

**Definition:** Weekly active users who have triggered at least one qualifying academic event AND at least one qualifying social event in the same 7-day window (the `both_sides_active` user property = true).
**Dashboard view:** Percentage of all WAU who are `both_sides_active`, tracked weekly.
**Why this one:** This is the north star metric. Downloads are vanity, opens are table stakes, but a student using both sides is the one who will not delete the app and will tell their friends. A student on one side only is at risk. See the full implementation in the section below.

### 5. New Class Joins Per Day — Target: 20+ per day in weeks 1–2 of term

**Definition:** Count of `class_joined` events on a given day.
**Dashboard view:** Daily bar chart with a 7-day rolling average.
**Why this one:** Class density is the mechanism that makes the social layer feel alive. Each new class join adds another student to a shared social space, increasing the chance that any individual student opens the app and finds someone they know. In the first two weeks of term, this should spike sharply as students finalise their schedules. A flat line means students are not discovering the class system — the product's core differentiator and the hook that makes everything else work.

---

## Tracking the North Star: Academic-Only vs. Both-Sides Students

The product context is explicit: students who only use one side will undervalue CampusClip and are at risk of deleting it. The north star is weekly active users using both sides.

### User Segment Definitions

These are Mixpanel user properties, recalculated every Sunday midnight ET via a server-side job and set on each user profile. They are used as cohort filters on every other chart in the dashboard.

| Segment Name | Definition |
|---|---|
| `academic_only` | ≥1 academic event AND 0 social events in the last 7 days |
| `social_only` | ≥1 social event AND 0 academic events in the last 7 days |
| `both_sides_active` | ≥1 academic event AND ≥1 social event in the last 7 days — **the north star segment** |
| `inactive` | 0 qualifying events of any kind in the last 7 days |

### Qualifying Academic Events

- `syllabus_upload_completed`
- `assignment_viewed`
- `assignment_marked_complete`
- `grade_tracker_opened`
- `grade_recalculated`

### Qualifying Social Events

- `message_sent`
- `class_feed_viewed` (minimum 20 seconds on screen to filter accidental opens)
- `club_followed`
- `event_rsvp_completed`
- `classmate_viewed`

### North Star Dashboard Charts

Track all four of these as weekly cohorts in Mixpanel:

1. **Both-sides rate by install week** — what % of each week's installs reached `both_sides_active` by Day 14? By Day 30? (This measures onboarding and activation quality over time.)
2. **Transition funnel** — `academic_only` → `both_sides_active` conversion rate. What triggers the switch? Use Mixpanel's funnel with `class_joined` and `message_sent` as intermediate steps.
3. **Retention by segment** — do `both_sides_active` users retain at Day 14 and Day 30 at a higher rate than `academic_only` users? They should. Quantify the delta — it is the single most important internal argument for investing in the social layer.
4. **Both-sides rate by class size** — do students in larger classes activate the social side faster? Segment `both_sides_active` rate by `class_size_at_join` buckets (1–5, 6–15, 16–30, 30+). This tells you the minimum viable class density threshold for the social layer to feel alive.

### Implementation Note

The `both_sides_active_week` system event fires server-side for each qualifying user every Sunday at midnight ET. Simultaneously, a server-side job writes `user_segment` and `both_sides_active` (boolean) to each user's Mixpanel profile. These profile properties are the source of truth for all segment-level reporting. Do not attempt to derive this in Mixpanel client-side — the weekly recalculation must be server-authoritative to be reliable across sessions and devices.

---

## UTM Structure for Western Launch

### Naming Convention Rules

- All lowercase, no exceptions
- Underscores within values, no spaces or hyphens within a value
- Campus identifier always included in campaign as a prefix: `western_`
- All UTM values agreed in advance and listed in the UTM registry spreadsheet — no freeform values during launch

### Parameter Definitions

| Parameter | Purpose | Allowed Values (Western Launch) |
|---|---|---|
| `utm_source` | Where traffic originates | `instagram`, `tiktok`, `meta_ads`, `poster`, `qr_code`, `campus_rep`, `frosh_week`, `email`, `reddit`, `direct` |
| `utm_medium` | The channel type | `social_organic`, `paid_social`, `out_of_home`, `campus_event`, `email`, `influencer`, `referral` |
| `utm_campaign` | The initiative | `western_launch_aug2026`, `western_frosh_week`, `western_class_reps`, `western_clubs_fair`, `western_retargeting` |
| `utm_content` | Differentiates creatives or placements | `hero_video`, `story_swipe`, `carousel_academic`, `carousel_social`, `syllabus_demo`, `grade_demo`, `poster_sci_building`, `poster_ucc`, `poster_library` |

### UTM Examples by Channel

**Instagram organic (class rep post):**
```
utm_source=instagram&utm_medium=social_organic&utm_campaign=western_class_reps&utm_content=syllabus_demo
```

**Frosh Week QR code on physical poster (Science Building):**
```
utm_source=qr_code&utm_medium=out_of_home&utm_campaign=western_frosh_week&utm_content=poster_sci_building
```

**Paid Meta ad (academic creative, launch campaign):**
```
utm_source=meta_ads&utm_medium=paid_social&utm_campaign=western_launch_aug2026&utm_content=carousel_academic
```

**Campus rep referral link (peer-to-peer):**
```
utm_source=campus_rep&utm_medium=referral&utm_campaign=western_class_reps&utm_content=rep_firstname
```

**Email to waitlist (launch day):**
```
utm_source=email&utm_medium=email&utm_campaign=western_launch_aug2026&utm_content=waitlist_launch_day
```

**TikTok organic (grade demo video):**
```
utm_source=tiktok&utm_medium=social_organic&utm_campaign=western_launch_aug2026&utm_content=grade_demo
```

### Mobile Attribution Rules

UTM parameters alone are insufficient for mobile app attribution due to the App Store redirect gap. Use Branch for all app install attribution:

- Every UTM-tagged link to the App Store or Google Play is a Branch deep link. Branch captures the UTM parameters and passes them through on first app open as `install_source` properties in Mixpanel.
- All physical QR codes on campus point to unique Branch links with pre-filled UTM params. This is the only way to track offline-to-app conversion.
- Match waitlist signups to app installs using hashed email comparison. Never store raw emails in analytics event properties.
- Branch attribution window: 7-day click-through, 24-hour view-through for any paid campaigns.

---

## Privacy and Compliance Notes

- No PII in any event property: no names, email addresses, student IDs, or IP addresses
- User IDs in Mixpanel are randomly generated internal identifiers — not student numbers
- PIPEDA compliance required (CampusClip is Canadian): consent must be obtained in onboarding before any events fire; the analytics SDK must not initialise until consent is confirmed
- User data deletion: Mixpanel's GDPR/PIPEDA deletion API must be wired to the account deletion flow before launch
- Data retention: configure Mixpanel to 24-month retention; do not accumulate indefinitely
- Class IDs, assignment IDs, and any course references in event properties are hashed before transmission

---

## Pre-Launch Validation Checklist

- [ ] All events fire in Mixpanel DebugView on both iOS and Android test devices
- [ ] `both_sides_active_week` server-side event fires correctly for a test user and writes the `user_segment` profile property
- [ ] UTM parameters pass through from campusclip.ca → Branch link → Mixpanel `install_source` property on first app open
- [ ] `syllabus_upload_completed` fires only after OCR succeeds and assignments populate (not on `syllabus_upload_started`)
- [ ] No duplicate `app_opened` events on app resume vs. cold start
- [ ] Onboarding funnel chart in Mixpanel shows all steps from `account_created` to `onboarding_completed` with visible drop-offs
- [ ] Push notification events (`received`, `tapped`) carry `campaign_id` on every send
- [ ] User segment properties recalculate correctly on the Sunday midnight job with a test user who crosses segments
- [ ] `feature_unused_7d` system event fires for a test user who has not triggered qualifying events for 7 days
- [ ] PIPEDA consent check: confirm analytics SDK does not initialise before consent screen is accepted
