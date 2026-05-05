# CampusClip Analytics Tracking Plan — Western University Launch (August 2026)

**Last updated:** 2026-05-05
**Tools:** Mixpanel (primary product analytics) + GA4 (marketing site) + Segment (event routing)
**Coverage:** Mobile app (iOS/Android) + marketing site (campusclip.ca)

---

## Naming Conventions

All events: `object_action` — lowercase, underscores.
All user properties: snake_case.
No PII in event properties (no names, emails, student IDs).

---

## Funnel Stage 1 — Acquisition

These events answer: which channels are bringing students to Western, and which ones convert to downloads?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `marketing_site_visited` | Any pageview on campusclip.ca | `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `page_path`, `referrer` | Attribution baseline — every downstream conversion traces back to this |
| `app_store_link_clicked` | Student taps App Store or Google Play CTA on marketing site | `utm_source`, `utm_medium`, `utm_campaign`, `cta_location` (hero / footer / feature-section), `device_type` | Measures which page sections and channels are driving store visits |
| `app_install_completed` | App opens for the first time (first launch event) | `install_source` (organic / referral / paid / campus_event), `utm_source`, `utm_medium`, `utm_campaign`, `device_os`, `app_version` | The actual download — connect this to the UTM that drove it |
| `referral_link_clicked` | Student opens app from a peer share link | `referrer_user_id` (hashed), `share_surface` (push / in-app / social), `utm_campaign` | Measure organic word-of-mouth vs. incentivised sharing |
| `waitlist_signup_completed` | Pre-launch email capture form submitted | `utm_source`, `utm_medium`, `utm_campaign`, `school_name` (Western) | Build the pre-launch list, track which channels warm up fastest |

---

## Funnel Stage 2 — Activation

These events answer: which new students reach the moment they get the core value of CampusClip within the first session?

**Activation definition for CampusClip:** a student has uploaded at least one syllabus AND joined at least one class.

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `account_created` | Student completes signup (email or SSO) | `signup_method` (email / google / apple), `install_source`, `utm_source`, `session_id` | Top of the activation funnel — every onboarding drop-off is measured against this |
| `onboarding_step_viewed` | Each onboarding screen is displayed | `step_number`, `step_name` (e.g. add_your_classes, upload_syllabus, find_classmates), `is_skipped` | Identifies exactly where students abandon onboarding |
| `onboarding_completed` | Student reaches end of onboarding flow | `steps_completed`, `classes_added_count`, `time_to_complete_seconds` | Baseline completion rate for the entire flow |
| `syllabus_upload_started` | Student taps the camera/upload button | `entry_point` (onboarding / class_detail / home), `class_id` (hashed) | Intent to use the differentiating feature |
| `syllabus_upload_completed` | OCR parse succeeds and assignments populate | `assignments_detected_count`, `class_id` (hashed), `upload_method` (camera / file), `time_to_parse_seconds` | The aha moment. This is the highest-value activation event in the app |
| `syllabus_upload_failed` | OCR fails or timeout | `failure_reason` (bad_image / timeout / unsupported_format), `class_id` (hashed) | Track failure rate to prioritise OCR improvements |
| `class_joined` | Student joins a course in the app | `class_id` (hashed), `class_size_at_join`, `join_method` (search / QR / classmate_invite / course_code), `entry_point` | Each join increases social layer density. Track the join method to optimise discovery |
| `classmate_viewed` | Student views the classmates list in a class | `class_id` (hashed), `classmates_count` | Leading indicator that the social layer has value — students are looking for their people |
| `grade_tracker_opened` | Student opens grade view for a class | `class_id` (hashed), `assignments_populated`, `current_grade_visible` (true/false) | Validates that grade clarity feature is being discovered |
| `assignment_viewed` | Student taps an assignment from their feed | `assignment_id` (hashed), `class_id` (hashed), `days_until_due`, `source` (feed / calendar / grade_tracker) | Measures academic-side engagement beyond syllabus upload |
| `first_week_active` | System event: student opens app on 3 of first 7 days | `days_opened_in_week_1`, `features_used` (array: academic / social / both) | Proxy for whether the student formed a habit in the critical window |

---

## Funnel Stage 3 — Retention

These events answer: which students are forming a real habit, and which ones are fading?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `app_opened` | App becomes active in foreground | `session_number`, `days_since_install`, `days_since_last_open`, `open_source` (direct / push / share_link) | The raw frequency signal. Dropping `days_since_last_open` daily surfaces at-risk users |
| `class_feed_viewed` | Student views the class social feed | `class_id` (hashed), `messages_in_feed`, `time_spent_seconds` | Measures social layer stickiness |
| `message_sent` | Student sends a message in a class chat | `class_id` (hashed), `message_type` (text / poll / resource_share), `recipient_count` | Bi-directional social engagement — high predictor of retention |
| `event_rsvp_completed` | Student RSVPs to a campus event | `event_id` (hashed), `event_type` (club / academic / social), `days_until_event` | Campus event feature discovery |
| `club_viewed` | Student opens a club page | `club_id` (hashed), `entry_point` (discover / class_feed / search) | Measures discovery layer usage |
| `club_followed` | Student follows a club | `club_id` (hashed) | Commitment signal for the social side |
| `assignment_marked_complete` | Student marks an assignment done | `assignment_id` (hashed), `class_id` (hashed), `marked_early` (true if >24h before due) | Academic-side habit signal |
| `grade_recalculated` | Student's grade updates after new marks entered | `class_id` (hashed), `new_grade_value` (bucketed: A/B/C/D/F), `assignments_graded_count` | Validates that grade clarity is a live, maintained feature |
| `push_notification_received` | Push delivered to device | `notification_type`, `campaign_id` | Baseline for notification delivery |
| `push_notification_tapped` | Student taps a push notification | `notification_type`, `campaign_id`, `hours_since_last_open` | Measures notification effectiveness by type |
| `both_sides_active_week` | System event: student uses academic AND social features in same 7-day window | `week_number_since_install`, `academic_events_count`, `social_events_count` | The north star event — see section below |
| `feature_unused_7d` | System event: a feature category has 0 events for 7 days for this user | `feature_category` (academic / social / events / clubs), `days_since_last_use` | Early churn signal — triggers intervention playbook |

---

## Funnel Stage 4 — Referral

These events answer: is organic word-of-mouth growing the network, and which surfaces drive it?

| Event Name | What Triggers It | Properties to Capture | Why It Matters |
|---|---|---|---|
| `share_sheet_opened` | Student taps share / invite from any surface | `share_surface` (class_detail / profile / onboarding / settings), `class_id` (hashed if applicable) | Top of the referral funnel |
| `invite_sent` | Student sends a specific invite (email / link / contact) | `invite_method` (copy_link / contact_invite / social_share), `share_surface`, `recipient_count` | Intent to refer — connect to downstream installs |
| `invite_link_installed` | New user installs via a tracked referral link | `referrer_user_id` (hashed), `time_from_share_to_install_hours` | Closes the referral loop and measures virality |
| `viral_coefficient_computed` | System event (weekly batch): invites sent / active users | — | K-factor proxy — track weekly to see if word-of-mouth is compounding |
| `nps_survey_completed` | In-app NPS prompt answered (day 14 or day 30) | `nps_score`, `nps_comment_provided` (bool), `days_since_install` | Identifies promoters to activate for referrals and detractors to intervene |

---

## The 5 Metrics to Check Every Morning

These are the numbers on the daily dashboard during the Western launch window (August–September 2026). Everything else is context; these are decisions.

### 1. Daily Active Users (DAU) — Target: 70+ by end of September

**Definition:** Unique users who open the app on a given day.
**Why this one:** The most direct measure of whether the network is alive. A static or declining DAU in the first 8 weeks means the social layer never gets density. Check the 7-day rolling average, not just yesterday.

### 2. Day-7 Retention Rate — Target: 40%+

**Definition:** Of students who installed on Day 0, what percentage opened the app again on Day 7.
**Why this one:** The clearest signal of whether CampusClip has formed a habit. Students who make it to Day 7 are dramatically more likely to reach Week 4. If this number is below 30%, the activation sequence needs work before expanding to more campuses.

### 3. Syllabus Upload Completion Rate — Target: 60%+ of accounts created

**Definition:** `syllabus_upload_completed` / `account_created` over the trailing 7 days.
**Why this one:** The syllabus upload is the aha moment. Students who complete it see their academic life populate immediately — they're far less likely to delete the app. A low rate means the feature is discoverable but broken, or discoverable but not compelling enough in the current onboarding flow.

### 4. Both-Sides Active Rate (North Star) — Target: 30%+ of WAU by end of September

**Definition:** Weekly active users who have triggered at least one academic event (syllabus upload, assignment view, grade tracker open) AND at least one social event (message sent, class feed viewed, club followed) in the same 7-day window.
**Why this one:** This is the north star metric. Downloads are vanity, opens are table stakes, but a student using both sides is the one who will not delete the app and will tell their friends. See the dedicated section below for full tracking implementation.

### 5. New Class Joins Per Day — Target: 20+ per day in week 1 of term

**Definition:** Count of `class_joined` events in a given day.
**Why this one:** Class density is the mechanism that makes the social layer feel alive. Each new class join adds someone else's classmates to a shared space. In the first two weeks of term, this number should spike. A flat line means students are not discovering the class system, which is the product's core differentiator.

---

## Tracking the North Star: Academic-Only vs. Both-Sides Students

The product context states this clearly: students who only use one side will undervalue CampusClip. The north star is weekly active users using both sides.

### User Segment Definitions

Define these as Mixpanel user properties, updated on a rolling 7-day window:

| Segment Name | Definition |
|---|---|
| `academic_only` | User has triggered at least one academic event AND zero social events in the last 7 days |
| `social_only` | User has triggered at least one social event AND zero academic events in the last 7 days |
| `both_sides_active` | User has triggered at least one academic event AND at least one social event in the last 7 days — **this is the north star segment** |
| `inactive` | User has not opened the app in the last 7 days |

### Academic Events (qualifying)

- `syllabus_upload_completed`
- `assignment_viewed`
- `assignment_marked_complete`
- `grade_tracker_opened`
- `grade_recalculated`

### Social Events (qualifying)

- `message_sent`
- `class_feed_viewed` (minimum 30 seconds session)
- `club_followed`
- `event_rsvp_completed`
- `classmate_viewed`

### North Star Dashboard Metrics

Track these as a weekly cohort in Mixpanel:

1. **Both-sides rate by install week** — what % of Week 1 installs reached both-sides by Day 14? By Day 30?
2. **Transition funnel** — academic_only → both_sides conversion rate (what triggers the switch to social?)
3. **Retention by segment** — do both_sides users retain at a higher rate than academic_only? (They should. Quantify the delta to justify the product investment in the social layer.)
4. **Both-sides by class size** — do students in larger classes activate the social side faster? (Yes, in theory — but measure it at Western to confirm the threshold.)

### Implementation Note

Fire the `both_sides_active_week` system event as a server-side event every Sunday at midnight ET for each user who qualifies. Set `both_sides_active` as a Mixpanel user property (boolean, recalculated weekly) so it can be used as a cohort filter on every other chart.

---

## UTM Structure for Western Launch

### Naming Convention Rules

- All lowercase
- Underscores within values, no spaces
- Campus identifier always in campaign: `western_` prefix
- Consistent across all team members — use the UTM builder doc, do not freestyle

### Parameter Definitions for Western Launch

| Parameter | Purpose | Values to Use |
|---|---|---|
| `utm_source` | Where the traffic originates | `instagram`, `tiktok`, `meta_ads`, `poster`, `qr_code`, `rep`, `frosh`, `email`, `reddit`, `word_of_mouth` |
| `utm_medium` | The type of channel | `social_organic`, `paid_social`, `out_of_home`, `campus_event`, `email`, `influencer`, `referral` |
| `utm_campaign` | The specific initiative | `western_launch_aug2026`, `western_frosh_week`, `western_class_reps`, `western_clubs_fair`, `western_retargeting` |
| `utm_content` | Differentiates ads or placements | `hero_video`, `story_swipe`, `carousel_academic`, `carousel_social`, `syllabus_demo`, `grade_demo` |
| `utm_term` | Paid search only (not used in social) | Not applicable for launch |

### Channel UTM Examples

**Instagram Organic (class rep post):**
```
utm_source=instagram&utm_medium=social_organic&utm_campaign=western_class_reps&utm_content=syllabus_demo
```

**Frosh Week QR Code (physical poster):**
```
utm_source=qr_code&utm_medium=out_of_home&utm_campaign=western_frosh_week&utm_content=poster_sci_building
```

**Paid Meta Ad (academic creative):**
```
utm_source=meta_ads&utm_medium=paid_social&utm_campaign=western_launch_aug2026&utm_content=carousel_academic
```

**Campus Rep referral link (peer to peer):**
```
utm_source=rep&utm_medium=referral&utm_campaign=western_class_reps&utm_content=rep_firstname
```

**Email to waitlist:**
```
utm_source=email&utm_medium=email&utm_campaign=western_launch_aug2026&utm_content=waitlist_launch_day
```

### Attribution Rules

- Mobile app installs: use AppsFlyer or Branch for deep-link attribution (UTM alone is insufficient on mobile due to app store redirects)
- UTM parameters pass from marketing site → app store link click (captured in GA4) + Branch link (captured in Mixpanel at install)
- Match waitlist email addresses to app installs using hashed email comparison — do not store emails in analytics properties
- All QR codes on campus point to unique Branch links with pre-filled UTM params so offline-to-app attribution is tracked

---

## Privacy Notes

- No PII in any event property (no names, emails, student IDs in raw events)
- User IDs in Mixpanel are randomly generated internal identifiers — not student numbers
- PIPEDA compliance required (CampusClip is Canadian): include consent in onboarding before events fire
- Delete user data capability must be implemented before launch (Mixpanel supports GDPR/PIPEDA deletion via API)
- Class IDs and assignment IDs are hashed before being sent as properties

---

## Validation Checklist Before Launch

- [ ] All events fire in Mixpanel DebugMode on both iOS and Android test devices
- [ ] `both_sides_active_week` server-side event fires correctly for a test user
- [ ] UTM parameters pass through from campusclip.ca to Branch to Mixpanel `install_source` property
- [ ] `syllabus_upload_completed` fires only after OCR succeeds (not on upload start)
- [ ] No duplicate `app_opened` events on app resume vs. cold start
- [ ] Onboarding funnel chart builds correctly in Mixpanel (step 1 → step N with drop-offs visible)
- [ ] Push notification events (`received`, `tapped`) are tied to `campaign_id` in every message
- [ ] User segment properties (academic_only / social_only / both_sides_active / inactive) update weekly via server-side job
