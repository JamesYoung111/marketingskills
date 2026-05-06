# CampusClip App Screenshots

Drop real app screenshots here. These are used as starting frames for Kling
image-to-video generation — the ad videos will literally animate FROM the
real app UI, making them look authentic and professional.

## File naming

| File | Screen |
|------|--------|
| `screenshot_01_dashboard.png` | Dashboard — Academic Performance rings + My Classes |
| `screenshot_02_class_detail.png` | Class detail — Assignments, grades, exams |
| `screenshot_03_clubs.png` | Clubs tab — My Clubs + Discover Clubs |
| `screenshot_04_club_page.png` | Individual club — Discussion/Chat/Events/Members |
| `screenshot_05_feed.png` | Feed — Club posts, likes, comments |
| `screenshot_06_calendar.png` | Calendar — April 2026, Track your academic journey, Group Case Assignment card |
| `screenshot_07_search.png` | Search/Explore — Trending Students + Popular Clubs |
| `screenshot_08_profile.png` | Profile — James Young, 2nd Year BMOS Finance, Western University |

## After adding screenshots

Re-run the GitHub Actions workflow with batch = `product` or `all`.
The video generator will pick up screenshots from this folder and pass them
to Kling's start_image parameter so videos animate from real app screens.
