"""
=============================================================================
Capstone Project - Data Science
PHASE 1: WEB SCRAPING SCRIPT
Domain: Fitness & Wellness Apps (Google Play Store)

What this script does:
  1. Searches the Google Play Store using a list of fitness-related terms
  2. Collects app-level metadata for every unique app found
  3. Collects a batch of recent user reviews for each app
  4. Saves two RAW (unclean) CSV files:
       - raw_apps.csv     -> one row per app
       - raw_reviews.csv  -> one row per review

No login is required. This uses the public, unofficial `google-play-scraper`
library, which reads the same public app listing pages a normal user would
see in a browser - no scraping of login-gated or private content.

NOTE: This script must be run on a machine with normal internet access to
play.google.com. It will not run inside a locked-down sandbox.
=============================================================================
"""

import csv
import time
from google_play_scraper import search, app as app_details, reviews, Sort

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------

# NOTE: The Python `google-play-scraper` library does not offer a
# "similar apps" lookup (unlike its Node.js counterpart), so instead of
# expanding from a small seed set, we cast a much wider net of search
# terms up front - covering workout types, equipment, body parts, diets,
# and fitness sub-audiences - so de-duplicated results realistically
# clear 1,000+ unique apps.
SEARCH_TERMS = [
    # General fitness / tracking
    "fitness tracker", "workout planner", "step counter", "calorie counter",
    "macro tracker", "water reminder", "sleep tracker", "fitness challenge",
    "30 day fitness challenge", "workout log",
    # Workout types
    "HIIT workout", "home workout", "gym workout", "bodyweight workout",
    "calisthenics", "crossfit", "strength training app", "cardio workout",
    "full body workout", "functional training",
    # Body-part specific
    "ab workout", "core workout", "leg workout", "arm workout",
    "back workout", "chest workout",
    # Equipment specific
    "dumbbell workout", "kettlebell workout", "resistance bands workout",
    "treadmill workout", "rowing machine app",
    # Yoga / mindfulness / recovery
    "yoga app", "pilates app", "stretching app", "meditation app",
    "mindfulness app", "breathing exercises app", "foam rolling",
    "flexibility training", "recovery app",
    # Cardio / outdoor
    "running tracker", "walking app", "cycling tracker", "swimming tracker",
    "dance workout", "zumba app", "boxing workout", "martial arts training",
    "sports training app",
    # Diet / nutrition
    "weight loss app", "weight gain app", "muscle building app",
    "bodybuilding app", "intermittent fasting", "keto diet app",
    "vegan diet app", "nutrition planner",
    # Trainer / personalized
    "personal trainer app", "workout planner women", "workout planner men",
    "senior fitness app", "prenatal fitness app", "kids fitness app",
    "gym membership app", "fitness community app",
    "senior fitness app", "prenatal fitness app", "kids fitness app",
    "gym membership app", "fitness community app",
    # Extra buffer terms
    "ab roller workout", "resistance training", "cardio blast",
    "fitness for beginners", "no equipment workout", "wall pilates",
    "barre workout", "trx workout", "plyometric training",
    "fitness goal tracker", "hydration tracker", "posture correction app",
    "fat burning workout", "toning workout", "fitness quotes motivation",
    "ab roller workout", "resistance training", "cardio blast",
    "fitness for beginners", "no equipment workout", "wall pilates",
    "barre workout", "trx workout", "plyometric training",
    "fitness goal tracker", "hydration tracker", "posture correction app",
    "fat burning workout", "toning workout", "fitness motivation app",
    "fitness for seniors", "postnatal fitness", "athlete training app",
    "sports performance app", "injury recovery app", "physical therapy app",
    "workout music app", "gym finder app", "personal record tracker",
    "fitness journal", "body recomposition app",
]

RESULTS_PER_TERM = 100      # max results google-play-scraper returns per search term
REVIEWS_PER_APP = 40        # number of recent reviews to pull per app
COUNTRY = "us"
LANG = "en"

RAW_APPS_CSV = "data/raw/raw_apps.csv"
RAW_REVIEWS_CSV = "data/raw/raw_reviews.csv"

APP_FIELDS = [
    "app_id", "title", "developer", "category", "score", "ratings",
    "installs", "minInstalls", "price", "free", "containsAds",
    "offersIAP", "size", "androidVersion", "released", "updated",
    "contentRating", "description",
]

REVIEW_FIELDS = [
    "app_id", "review_id", "userName", "score", "at", "content",
    "thumbsUpCount", "appVersion",
]


# -----------------------------------------------------------------------
# STEP 1: SEARCH -> COLLECT UNIQUE APP IDS
# -----------------------------------------------------------------------

def collect_app_ids():
    """Run each search term and collect a de-duplicated set of app IDs."""
    seen_ids = set()

    for term in SEARCH_TERMS:
        print(f"Searching: '{term}' ...")
        try:
            results = search(
                term,
                lang=LANG,
                country=COUNTRY,
                n_hits=RESULTS_PER_TERM,
            )
        except Exception as e:
            print(f"  ! Search failed for '{term}': {e}")
            continue

        new_ids = 0
        for r in results:
            app_id = r.get("appId")
            if app_id and app_id not in seen_ids:   # skip None/empty IDs
                seen_ids.add(app_id)
                new_ids += 1

        print(f"  -> {len(results)} results, {new_ids} new unique apps "
              f"(running total: {len(seen_ids)})")

        time.sleep(1)  # be polite between requests

    return list(seen_ids)


# -----------------------------------------------------------------------
# STEP 2: FETCH FULL APP DETAILS FOR EACH APP ID
# -----------------------------------------------------------------------

def fetch_app_details(app_ids):
    """Fetch full metadata for each app ID. Returns a list of dicts."""
    apps_data = []

    for i, app_id in enumerate(app_ids, 1):
        d = None
        for attempt in range(3):
            try:
                d = app_details(app_id, lang=LANG, country=COUNTRY)
                break
            except Exception as e:
                time.sleep(3)
        if d is None:
            print(f"  ! Giving up on {app_id} after 3 attempts")
            continue

        apps_data.append({
            "app_id": app_id,
            "title": d.get("title"),
            "developer": d.get("developer"),
            "category": d.get("genre"),
            "score": d.get("score"),
            "ratings": d.get("ratings"),
            "installs": d.get("installs"),
            "minInstalls": d.get("minInstalls"),
            "price": d.get("price"),
            "free": d.get("free"),
            "containsAds": d.get("containsAds"),
            "offersIAP": d.get("offersIAP"),
            "size": d.get("size"),
            "androidVersion": d.get("androidVersion"),
            "released": d.get("released"),
            "updated": d.get("updated"),
            "contentRating": d.get("contentRating"),
            "description": (d.get("description") or "").replace("\n", " ").strip(),
        })

        if i % 25 == 0:
            print(f"  Fetched details for {i}/{len(app_ids)} apps...")

        time.sleep(0.3)  # be polite between requests

    return apps_data


# -----------------------------------------------------------------------
# STEP 3: FETCH REVIEWS FOR EACH APP
# -----------------------------------------------------------------------

def fetch_reviews(app_ids):
    """Fetch a batch of recent reviews for each app. Returns a list of dicts."""
    reviews_data = []

    for i, app_id in enumerate(app_ids, 1):
        try:
            result, _ = reviews(
                app_id,
                lang=LANG,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=REVIEWS_PER_APP,
            )
        except Exception as e:
            print(f"  ! Failed to fetch reviews for {app_id}: {e}")
            continue

        for r in result:
            reviews_data.append({
                "app_id": app_id,
                "review_id": r.get("reviewId"),
                "userName": r.get("userName"),
                "score": r.get("score"),
                "at": r.get("at"),
                "content": (r.get("content") or "").replace("\n", " ").strip(),
                "thumbsUpCount": r.get("thumbsUpCount"),
                "appVersion": r.get("appVersion"),
            })

        if i % 25 == 0:
            print(f"  Fetched reviews for {i}/{len(app_ids)} apps...")

        time.sleep(0.3)  # be polite between requests

    return reviews_data


# -----------------------------------------------------------------------
# STEP 4: SAVE TO CSV
# -----------------------------------------------------------------------

def save_csv(filename, fieldnames, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows -> {filename}")


# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------

def main():
    print("=" * 60)
    print("STEP 1: Collecting unique app IDs across search terms")
    print("=" * 60)
    app_ids = collect_app_ids()
    print(f"\nTotal unique apps found: {len(app_ids)}\n")

    print("=" * 60)
    print("STEP 2: Fetching app details")
    print("=" * 60)
    apps_data = fetch_app_details(app_ids)

    print("\n" + "=" * 60)
    print("STEP 3: Fetching reviews")
    print("=" * 60)
    reviews_data = fetch_reviews(app_ids)

    print("\n" + "=" * 60)
    print("STEP 4: Saving raw CSV files")
    print("=" * 60)
    save_csv(RAW_APPS_CSV, APP_FIELDS, apps_data)
    save_csv(RAW_REVIEWS_CSV, REVIEW_FIELDS, reviews_data)

    print("\nDone. Raw data ready for cleaning in the next script.")


if __name__ == "__main__":
    main()