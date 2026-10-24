"""Seed-to-Forest progression, daily tasks, streaks and badges."""
import datetime as dt

STAGES = [
    ("Seed", 0),
    ("Sapling", 100),
    ("Young Tree", 300),
    ("Mature Tree", 700),
    ("Forest Guardian", 1500),
]
ICONS = {"Seed": "🌰", "Sapling": "🌱", "Young Tree": "🌿",
         "Mature Tree": "🌳", "Forest Guardian": "🌲"}

# photo=True -> needs an in-app camera photo
# kwh=True   -> user enters kWh saved, so CO2 avoided can be calculated
TASKS = {
    "Reduce electricity use (enter kWh saved)": {"xp": 20, "photo": False, "kwh": True},
    "Switch off unused lights and appliances": {"xp": 10, "photo": True, "kwh": False},
    "Walk or cycle instead of driving": {"xp": 15, "photo": False, "kwh": False},
    "Use public transport": {"xp": 15, "photo": False, "kwh": False},
    "Reduce waste / recycle properly": {"xp": 10, "photo": True, "kwh": False},
    "Join a local clean-up": {"xp": 40, "photo": True, "kwh": False},
    "Plant or care for a tree": {"xp": 40, "photo": True, "kwh": False},
}

PHOTO_PROMPTS = {
    "Switch off unused lights and appliances": "Take a photo of the switched-off lights or appliances.",
    "Reduce waste / recycle properly": "Take a photo of your sorted recycling.",
    "Join a local clean-up": "Take a photo of the clean-up area or the bags collected.",
    "Plant or care for a tree": "Take a photo of the tree you planted or cared for.",
}


def stage_for(xp):
    current = STAGES[0]
    for stage in STAGES:
        if xp >= stage[1]:
            current = stage
    idx = STAGES.index(current)
    nxt = STAGES[idx + 1] if idx + 1 < len(STAGES) else (None, None)
    return current[0], current[1], nxt[0], nxt[1]


def progress_to_next(xp):
    _, start, nxt_name, nxt_xp = stage_for(xp)
    if nxt_name is None:
        return 1.0
    return min((xp - start) / (nxt_xp - start), 1.0)


def current_streak(active_days, today=None):
    today = today or dt.date.today()
    day = today if today in active_days else today - dt.timedelta(days=1)
    streak = 0
    while day in active_days:
        streak += 1
        day -= dt.timedelta(days=1)
    return streak


def best_streak(active_days):
    best = run = 0
    prev = None
    for d in sorted(active_days):
        run = run + 1 if prev and d - prev == dt.timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    return best


def badges(log, active_days):
    earned = []
    if log:
        earned.append("🌱 First Step")
    if best_streak(active_days) >= 3:
        earned.append("🔥 3-Day Streak")
    if best_streak(active_days) >= 7:
        earned.append("🏅 7-Day Streak")
    if any("tree" in e["task"].lower() for e in log):
        earned.append("🌳 Tree Friend")
    if any("clean-up" in e["task"].lower() for e in log):
        earned.append("🧹 Clean-up Crew")
    if sum(e.get("kg_co2", 0) for e in log) >= 10:
        earned.append("⚡ 10 kg CO2 Avoided (estimated)")
    return earned
