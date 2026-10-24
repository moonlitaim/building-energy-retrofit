"""Transparent carbon maths and rule-based recommendations (all ESTIMATES)."""
import config


def monthly_emissions(kwh, factor=None):
    factor = config.GRID_EMISSION_FACTOR if factor is None else factor
    return kwh * factor


def emissions_avoided(baseline_kwh, current_kwh, factor=None):
    saved = max(baseline_kwh - current_kwh, 0)
    return monthly_emissions(saved, factor)


HIGH_KWH_PER_PERSON = 150  # rule of thumb, not an official benchmark


def recommendations(building_type, occupants, kwh, prev_kwh, weekend_use,
                    weekend_share, local_aqi, factor=None):
    recs = []
    per_person = kwh / max(occupants, 1)

    if building_type in ("Home", "Apartment") and per_person > HIGH_KWH_PER_PERSON:
        target = kwh * 0.9
        recs.append({
            "kind": "measured",
            "problem": f"Usage is about {per_person:.0f} kWh per person per month, "
                       f"above our {HIGH_KWH_PER_PERSON} kWh rule-of-thumb.",
            "action": "Switch to LED lighting, set the AC to 24-26 C, and unplug idle chargers and TVs.",
            "why": "Cooling, lighting and standby loads are common sources of avoidable use.",
            "measure": "Compare next month's meter reading with this month's.",
            "estimate": f"A 10% cut would save about {kwh - target:.0f} kWh "
                        f"(~{monthly_emissions(kwh - target, factor):.0f} kg CO2) per month.",
        })

    if building_type == "Office" and weekend_use and weekend_share > 0.15:
        saved_kwh = kwh * weekend_share * 0.5
        recs.append({
            "kind": "measured",
            "problem": f"{weekend_share * 100:.0f}% of the office's electricity is used on weekends.",
            "action": "Review lighting, cooling and equipment schedules for weekends and holidays.",
            "why": "Mostly empty buildings still run lights, AC and standby equipment.",
            "measure": "Compare weekend meter readings before and after the schedule change.",
            "estimate": f"Halving weekend use could save about {saved_kwh:.0f} kWh "
                        f"(~{monthly_emissions(saved_kwh, factor):.0f} kg CO2) per month.",
        })

    if prev_kwh and kwh > prev_kwh * 1.1:
        recs.append({
            "kind": "measured",
            "problem": f"Usage rose {((kwh / prev_kwh) - 1) * 100:.0f}% compared with last month.",
            "action": "Check for new appliances, seasonal cooling or heating, or equipment left on.",
            "why": "Finding the cause of a jump is the quickest way to cut it back.",
            "measure": "Track weekly meter readings for a month.",
            "estimate": f"Returning to last month's level would avoid "
                        f"~{emissions_avoided(kwh, prev_kwh, factor):.0f} kg CO2 per month.",
        })

    if local_aqi > 200:
        recs.append({
            "kind": "general",
            "problem": "Local air quality is Poor or worse.",
            "action": "Avoid outdoor exercise at peak hours, use a mask outdoors, and join a community "
                      "tree-planting or dust-control drive.",
            "why": "Fine particles (PM2.5) are linked to breathing and heart problems, and trees and "
                   "less burning of waste can help locally over time.",
            "measure": "Track the AQI trend for your area on the Air Quality tab.",
            "estimate": "Not calculated: the effect on local AQI depends on many factors.",
        })

    if not recs:
        recs.append({
            "kind": "general",
            "problem": "No obvious problem found from the numbers you entered.",
            "action": "Keep tracking monthly usage and try one daily action to build a streak.",
            "why": "Consistent small habits matter more than one-off efforts.",
            "measure": "Watch your monthly kWh on the Impact tab.",
            "estimate": "Not calculated.",
        })
    return recs
