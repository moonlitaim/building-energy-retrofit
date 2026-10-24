"""EcoSphere prototype. Run with:  streamlit run app.py"""
import datetime as dt
import html as _html

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import carbon
import config
import data
import gamification as gm
import theme
from model import load_data, run_model

st.set_page_config(page_title="EcoSphere", page_icon="🌱", layout="wide")

# ---------- palette ----------
FOREST = "#0f3d2e"
LEAF = "#2e9e5b"
LIME = "#b7e36a"
TEAL = "#1fb5a8"
AMBER = "#f2b134"
ALERT = "#e8590c"
MUTED = "#9aa5a0"
CPCB = [("Good", 50, "#00b050"), ("Satisfactory", 50, "#92d050"),
        ("Moderate", 100, "#f2c200"), ("Poor", 100, "#ff9900"),
        ("Very poor", 100, "#e8403a"), ("Severe", 100, "#a30000")]



def html(s: str):
    """Render HTML safely through markdown (strips indentation and blank lines)."""
    st.markdown("\n".join(l.strip() for l in s.strip().splitlines() if l.strip()),
                unsafe_allow_html=True)


def esc(x) -> str:
    return _html.escape(str(x))


def css_color(c) -> str:
    """Accept a hex string or an (r, g, b[, a]) sequence from data.aqi_band."""
    if isinstance(c, str):
        return c
    try:
        r, g, b, *_ = c
        return f"rgb({int(r)},{int(g)},{int(b)})"
    except Exception:
        return LEAF


def section(icon, title, sub=""):
    html(f'<div class="sec"><div class="sec-ic">{icon}</div><div><h2>{esc(title)}</h2>'
         f'<p>{esc(sub)}</p></div></div>')


def show(chart):
    """Altair chart that works across Streamlit versions."""
    chart = (chart.configure_view(strokeWidth=0).configure(background="transparent")
             .configure_axis(labelColor="#1d4a38", titleColor="#1d4a38",
                             gridColor="rgba(15,61,46,0.10)", domainColor="rgba(15,61,46,0.25)")
             .configure_legend(labelColor="#1d4a38"))
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:
        st.altair_chart(chart, use_container_width=True)


def bar_gradient():
    return alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                        stops=[alt.GradientStop(color=LEAF, offset=0),
                               alt.GradientStop(color=LIME, offset=1)])


def gauge_html(aqi, label, colour):
    frac = min(max(float(aqi) / 500, 0), 1)
    off = 251.33 * (1 - frac)
    return (f'<div class="gauge"><svg viewBox="0 0 200 110">'
            f'<path class="g-track" d="M 20 100 A 80 80 0 0 1 180 100"/>'
            f'<path class="g-fill" d="M 20 100 A 80 80 0 0 1 180 100" '
            f'style="stroke:{colour};--off:{off:.2f}"/></svg>'
            f'<div class="g-num">{int(aqi)}</div>'
            f'<div class="g-lbl" style="color:{colour}">{esc(label)}</div></div>')


def scale_html(aqi):
    pos = min(max(float(aqi) / 500, 0), 1) * 100
    segs = "".join(f'<div style="flex:{w};background:{c}" title="{n}"></div>' for n, w, c in CPCB)
    return (f'<div class="scale">{segs}<div class="mark" style="--pos:{pos:.1f}%">▼</div></div>'
            f'<div class="scale-lbl"><span>0</span><span>100</span><span>200</span>'
            f'<span>300</span><span>400</span><span>500</span></div>')


def journey_html(xp, current):
    parts = []
    for i, (name, need) in enumerate(gm.STAGES):
        cls = "step done" if xp >= need else "step"
        if name == current:
            cls += " now"
        if i:
            parts.append(f'<div class="line{" done" if xp >= need else ""}"></div>')
        parts.append(f'<div class="{cls}"><div class="bubble">{gm.ICONS[name]}</div>'
                     f'<div class="nm">{esc(name)}</div><div class="xp">{need} XP</div></div>')
    return f'<div class="journey">{"".join(parts)}</div>'


# ---------- session state ----------
def init_state():
    ss = st.session_state
    ss.setdefault("xp", 0)
    ss.setdefault("active_days", set())
    ss.setdefault("log", [])
    ss.setdefault("posts", data.sample_posts())
    ss.setdefault("liked", set())
    ss.setdefault("factor", config.GRID_EMISSION_FACTOR)
    ss.setdefault("last_carbon", None)


init_state()
ss = st.session_state
today = dt.date.today()
st.markdown(theme.CSS, unsafe_allow_html=True)


def xp_today():
    return sum(e["xp"] for e in ss.log if e["date"] == today)


def load_demo_history():
    for back, task, xp, kg in [
        (2, "Walk or cycle instead of driving", 15, 0.0),
        (1, "Reduce electricity use (enter kWh saved)", 20, 4.1),
    ]:
        day = today - dt.timedelta(days=back)
        ss.active_days.add(day)
        ss.log.append({"date": day, "task": task, "xp": xp, "kg_co2": kg})
        ss.xp += xp


# ---------- celebrations (answer the user's action) ----------
if "levelup" in ss:
    st.balloons()
    st.toast(f"Level up! You grew into a {ss.pop('levelup')}.", icon="🎉")
if "toast" in ss:
    st.toast(ss.pop("toast"), icon="🌱")

# ---------- sidebar ----------
neighbourhoods = data.sample_neighbourhoods()
stage, _, nxt, nxt_xp = gm.stage_for(ss.xp)
streak = gm.current_streak(ss.active_days, today)

with st.sidebar:
    st.title("🌱 EcoSphere")
    st.caption("Prototype. Sample data only.")
    area = st.selectbox("Your neighbourhood", neighbourhoods["name"])
    html(f'<div class="side-tree">{gm.ICONS[stage]}</div>')
    st.subheader(stage)
    st.progress(gm.progress_to_next(ss.xp))
    st.caption(f"{ss.xp} XP" + (f" / {nxt_xp} XP to {nxt}" if nxt else " (max stage)"))
    st.metric("Current streak", f"{streak} days")
    if st.button("Load demo history"):
        if not ss.log:
            load_demo_history()
        st.rerun()
    st.caption("Location privacy: this prototype only uses neighbourhood-level "
               "areas, never your exact position.")

# ---------- hero ----------
hero_row = neighbourhoods[neighbourhoods["name"] == area].iloc[0]
h_label, h_colour, _ = data.aqi_band(hero_row["aqi"])
html(theme.ambient_html())
html(theme.hero_html(
    icon=gm.ICONS[stage], stage=stage, xp=ss.xp, streak=streak, area=area,
    aqi=hero_row["aqi"], aqi_label=h_label, aqi_colour=css_color(h_colour),
    co2_kg=sum(e["kg_co2"] for e in ss.log)))
components.html(theme.CTA_HTML, height=64)

tabs = st.tabs(["Air quality", "Carbon estimate", "Daily actions", "Community",
                "Building retrofit", "My impact"])

# ---------- tab 1: air quality ----------
with tabs[0]:
    section("🌫️", "Local air quality", f"Latest readings for {area}")
    row = neighbourhoods[neighbourhoods["name"] == area].iloc[0]
    label, colour, advice = data.aqi_band(row["aqi"])
    colour = css_color(colour)

    g_col, m_col = st.columns([1, 2], vertical_alignment="center")
    with g_col:
        html(gauge_html(row["aqi"], label, colour))
    with m_col:
        c2, c3, c4 = st.columns(3)
        c2.metric("PM2.5 (µg/m³)", row["pm25"])
        c3.metric("PM10 (µg/m³)", row["pm10"])
        c4.metric("NO₂ (µg/m³)", row["no2"])
        st.info(f"**{label}.** {advice}")
        html(scale_html(row["aqi"]))
    st.caption("Source: SIMULATED sample data for the demo. AQI bands follow the "
               "Indian CPCB scale.")

    live = st.checkbox("Try live pollutant data (needs OPENWEATHER_API_KEY)")
    if live:
        result = data.get_live_aqi(row["lat"], row["lon"])
        if result is None:
            st.warning("Live data is unavailable (no API key set, or the request failed). "
                       "Showing sample data instead.")
        else:
            st.success("Live pollutant readings (OpenWeather, µg/m³):")
            st.json(result)
            st.caption("OpenWeather's 1-5 index is not the Indian AQI, so only raw "
                       "pollutant values should be compared.")

    st.subheader("Pollution map")
    st.map(neighbourhoods, latitude="lat", longitude="lon", color="color", size="size")
    st.caption("Dot colour shows the AQI band. Google Maps Platform is a planned upgrade.")

    st.subheader("Compare neighbourhoods")
    aqi_chart = alt.Chart(neighbourhoods).mark_bar(cornerRadiusEnd=8, height=24).encode(
        y=alt.Y("name:N", sort="-x", title=None),
        x=alt.X("aqi:Q", title="AQI", scale=alt.Scale(domain=[0, 500])),
        color=alt.Color("aqi:Q", legend=None, scale=alt.Scale(
            type="threshold", domain=[51, 101, 201, 301, 401], range=[c for _, _, c in CPCB])),
        opacity=alt.condition(alt.datum["name"] == area, alt.value(1), alt.value(0.5)),
        tooltip=["name", "aqi", "band"],
    )
    show(aqi_chart)
    st.dataframe(neighbourhoods[["name", "aqi", "band", "pm25", "pm10", "no2", "o3"]],
                 width="stretch", hide_index=True)

# ---------- tab 2: carbon estimate ----------
with tabs[1]:
    section("⚡", "Carbon emission estimate", "Estimated CO₂ = electricity used (kWh) × grid emission factor")
    st.caption("This is an estimate, not a measurement.")
    col_a, col_b = st.columns(2)
    with col_a:
        btype = st.selectbox("Building type", ["Home", "Apartment", "Office"])
        occupants = st.number_input("Number of occupants", 1, 500, 4)
        kwh = st.number_input("This month's electricity (kWh)", 0.0, 100000.0, 420.0, step=10.0)
        prev_kwh = st.number_input("Last month's electricity (kWh)", 0.0, 100000.0, 380.0, step=10.0)
    with col_b:
        weekend_use = st.checkbox("Office is used on weekends", value=False,
                                  disabled=(btype != "Office"))
        weekend_share = st.slider("Share of usage on weekends", 0, 60, 25,
                                  disabled=(btype != "Office")) / 100
        with st.expander("Emission factor (assumption)"):
            ss.factor = st.number_input("kg CO₂ per kWh", 0.1, 1.5, float(ss.factor), step=0.01)
            st.caption("Placeholder value. Replace it with your region's latest official figure.")

    co2 = carbon.monthly_emissions(kwh, ss.factor)
    change = ((kwh / prev_kwh) - 1) * 100 if prev_kwh else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated CO₂ this month", f"{co2:.0f} kg",
              f"{change:+.0f}% vs last month", delta_color="inverse")
    m2.metric("Per person", f"{co2 / occupants:.0f} kg")
    m3.metric("Emission factor used", f"{ss.factor} kg/kWh")
    ss.last_carbon = {"kwh": kwh, "prev_kwh": prev_kwh, "co2": co2}

    # tree-equivalent graphic (rough rule of thumb: ~21 kg CO2 absorbed per tree per year)
    tree_years = co2 / 21
    shown = min(max(round(tree_years), 1), 40)
    more = f" +{round(tree_years) - shown} more" if round(tree_years) > shown else ""
    html(f'<div class="trees">{"🌳" * shown}{more}</div>')
    st.caption(f"Roughly {tree_years:.0f} tree-years of growth to absorb this month's estimate "
               "(rule of thumb of about 21 kg CO₂ per mature tree per year; real values vary).")

    st.subheader("Recommendations")
    local_aqi = float(neighbourhoods[neighbourhoods["name"] == area]["aqi"].iloc[0])
    for rec in carbon.recommendations(btype, occupants, kwh, prev_kwh,
                                      weekend_use, weekend_share, local_aqi, ss.factor):
        tag = "Based on your numbers" if rec["kind"] == "measured" else "General guidance"
        with st.expander(f"{rec['problem']}  ·  {tag}", expanded=True):
            st.markdown(f"**What to do:** {rec['action']}")
            st.markdown(f"**Why it may help:** {rec['why']}")
            st.markdown(f"**How we'll measure it:** {rec['measure']}")
            st.markdown(f"**Estimated improvement:** {rec['estimate']}")

# ---------- tab 3: daily actions ----------
with tabs[2]:
    section("✅", "Daily actions", "Small habits, steady growth")
    if "flash" in ss:
        st.success(ss.pop("flash"))
    st.progress(min(xp_today() / config.DAILY_XP_CAP, 1.0),
                text=f"Today: {xp_today()} / {config.DAILY_XP_CAP} XP")
    st.caption("The daily cap rewards steady effort, not spam.")
    task_name = st.selectbox("Choose today's action", list(gm.TASKS))
    task = gm.TASKS[task_name]

    tags = [f"⚡ +{task['xp']} XP"]
    if task["photo"]:
        tags.append("📷 Photo needed")
    if task["kwh"]:
        tags.append("💡 Enter kWh saved")
    html("".join(f'<span class="tag">{esc(t)}</span>' for t in tags))

    photo = None
    kwh_saved = 0.0
    if task["photo"]:
        st.write(gm.PHOTO_PROMPTS[task_name])
        photo = st.camera_input("Take a photo (camera only, no gallery uploads)")
        st.caption("Camera capture makes reuse of old photos harder, but it cannot prove an "
                   "action really happened. A full version would add moderation and reporting.")
    if task["kwh"]:
        kwh_saved = st.number_input("kWh saved compared with your usual use", 0.0, 1000.0, 2.0, step=0.5)
    share = st.checkbox("Share with my neighbourhood feed", value=True)

    if st.button("Complete action", type="primary"):
        done_today = [e["task"] for e in ss.log if e["date"] == today]
        remaining = config.DAILY_XP_CAP - xp_today()
        if task["photo"] and photo is None:
            st.error("This action needs a photo taken with the camera.")
        elif task_name in done_today:
            st.warning("You already logged this action today. Try a different one.")
        elif remaining <= 0:
            st.info("You've hit today's XP cap. Come back tomorrow to keep your streak growing.")
        else:
            xp_gain = min(task["xp"], remaining)
            kg = carbon.monthly_emissions(kwh_saved, ss.factor) if task["kwh"] else 0.0
            old_stage = gm.stage_for(ss.xp)[0]
            ss.xp += xp_gain
            ss.active_days.add(today)
            ss.log.append({"date": today, "task": task_name, "xp": xp_gain, "kg_co2": kg})
            if share:
                ss.posts.insert(0, {"id": len(ss.posts) + 1, "author": "You", "area": area,
                                    "text": task_name, "xp": xp_gain, "likes": 0})
            msg = f"+{xp_gain} XP."
            if kg:
                msg += f" Estimated {kg:.1f} kg CO₂ avoided (kWh saved × emission factor)."
            ss.flash = msg
            ss.toast = msg
            new_stage = gm.stage_for(ss.xp)[0]
            if new_stage != old_stage:
                ss.levelup = new_stage
            st.rerun()  # refresh the sidebar XP and streak

    st.subheader("Badges")
    earned = gm.badges(ss.log, ss.active_days)
    if earned:
        html("".join(f'<span class="badge">{esc(b)}</span>' for b in earned))
    else:
        st.write("Complete your first action to earn a badge.")

    st.subheader("Seed to Forest")
    html(journey_html(ss.xp, stage))

# ---------- tab 4: community ----------
with tabs[3]:
    section("🏘️", "Community feed", "See what your neighbours are doing")
    scope = st.radio("Show", ["My neighbourhood", "Everyone"], horizontal=True)
    posts = [p for p in ss.posts if scope == "Everyone" or p["area"] == area]
    if not posts:
        st.info("No posts in your neighbourhood yet. Complete an action and share it!")
    for p in posts:
        with st.container(border=True):
            st.markdown(f"**{p['author']}** · {p['area']} · +{p['xp']} XP")
            st.write(p["text"])
            liked = p["id"] in ss.liked
            likes = p["likes"] + (1 if liked else 0)
            if st.button(f"{'❤️' if liked else '🤍'} {likes}", key=f"like_{p['id']}"):
                ss.liked.symmetric_difference_update({p["id"]})
                st.rerun()
    st.caption("Prototype feed. Posts reset when you refresh the page. A full version needs "
               "accounts, moderation and report buttons.")

    st.subheader("Neighbourhood leaderboard (sample)")
    board = pd.DataFrame({
        "Neighbourhood": ["🥇 Lake View Society", "🥈 Green Park Colony", "🥉 Market Road", "Old Town"],
        "Community XP": [1240, 980, 760, 410],
    })
    base = alt.Chart(board).encode(
        y=alt.Y("Neighbourhood:N", sort=None, title=None),
        x=alt.X("Community XP:Q", title=None, axis=None))
    bars = base.mark_bar(cornerRadiusEnd=10, height=30, color=LEAF)
    labels = base.mark_text(align="left", dx=6, fontWeight="bold").encode(text="Community XP:Q")
    show(bars + labels)

# ---------- tab 5: building retrofit ----------
with tabs[4]:
    section("🏢", "Building energy retrofit finder",
            "Buildings using far more energy than predicted are retrofit candidates")
    st.write("A machine-learning model predicts how much energy each building should use. "
             "Buildings using far more than predicted are flagged as retrofit candidates.")

    @st.cache_data(show_spinner="Training the energy model...")
    def get_results():
        return run_model(load_data())

    result, score = get_results()
    threshold = st.slider("Flag buildings using more than this % above predicted", 10, 60, 20)
    result = result.copy()
    result["status"] = result["excess_pct"].apply(
        lambda x: "Retrofit candidate" if x > threshold else "OK")
    candidates = result[result["status"] == "Retrofit candidate"].sort_values(
        "excess_pct", ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Buildings analysed", len(result))
    c2.metric("Retrofit candidates", len(candidates))
    c3.metric("Model R² score", f"{score:.2f}")

    st.subheader("Predicted vs actual energy use (kWh)")
    lo = float(min(result["predicted_kwh"].min(), result["actual_kwh"].min()))
    hi = float(max(result["predicted_kwh"].max(), result["actual_kwh"].max()))
    dots = alt.Chart(result).mark_circle(size=70, opacity=0.75).encode(
        x=alt.X("predicted_kwh:Q", title="Predicted kWh", scale=alt.Scale(zero=False)),
        y=alt.Y("actual_kwh:Q", title="Actual kWh", scale=alt.Scale(zero=False)),
        color=alt.Color("status:N", legend=alt.Legend(title=None, orient="top"),
                        scale=alt.Scale(domain=["OK", "Retrofit candidate"], range=[LEAF, ALERT])),
        tooltip=["building_id", "building_type", "predicted_kwh", "actual_kwh",
                 alt.Tooltip("excess_pct:Q", format=".1f")],
    )
    diag = alt.Chart(pd.DataFrame({"v": [lo, hi]})).mark_line(
        strokeDash=[6, 6], color=MUTED).encode(x="v:Q", y="v:Q")
    show((diag + dots).interactive())
    st.caption("Dots above the dashed line use more energy than the model predicts.")

    st.subheader("Top 10 buildings to retrofit first")
    if len(candidates):
        top = candidates.head(10)
        top_chart = alt.Chart(top).mark_bar(cornerRadiusEnd=8, height=22).encode(
            y=alt.Y("building_id:N", sort="-x", title=None),
            x=alt.X("excess_pct:Q", title="% above predicted"),
            color=alt.Color("excess_pct:Q", legend=None,
                            scale=alt.Scale(range=[AMBER, ALERT])),
            tooltip=["building_id", alt.Tooltip("excess_pct:Q", format=".1f")],
        )
        show(top_chart)
    else:
        st.info("No buildings exceed this threshold. Try lowering it.")
    st.dataframe(candidates[["building_id", "building_type", "floor_area", "age",
                             "predicted_kwh", "actual_kwh", "excess_pct"]],
                 width="stretch", hide_index=True)
    st.caption("Uses SIMULATED building data. Retrain on a real dataset (for example "
               "ASHRAE Great Energy Predictor) for real results.")

# ---------- tab 6: my impact ----------
with tabs[5]:
    section("🌍", "My impact", "Your logged actions so far")
    if not ss.log:
        st.info("Nothing logged yet. Complete an action, or click 'Load demo history' in the sidebar.")
    else:
        log_df = pd.DataFrame(ss.log)
        total_kg = log_df["kg_co2"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Actions completed", len(log_df))
        c2.metric("Estimated CO₂ avoided", f"{total_kg:.1f} kg")
        c3.metric("Best streak", f"{gm.best_streak(ss.active_days)} days")
        st.caption("CO₂ avoided counts only actions where you entered kWh saved "
                   "(kWh × emission factor). Photo and travel actions earn XP but are "
                   "not converted to CO₂. This is an estimate, not a measured change "
                   "in the atmosphere.")

        st.subheader("XP per day")
        xp_df = log_df.groupby("date", as_index=False)["xp"].sum()
        xp_df["date"] = pd.to_datetime(xp_df["date"])
        xp_chart = alt.Chart(xp_df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X("date:T", timeUnit="yearmonthdate", title=None),
            y=alt.Y("xp:Q", title="XP"),
            color=alt.value(bar_gradient()),
            tooltip=[alt.Tooltip("date:T", title="Date"), "xp"],
        )
        show(xp_chart)
        st.subheader("Activity history")
        st.dataframe(log_df.sort_values("date", ascending=False),
                     width="stretch", hide_index=True)

    if ss.last_carbon:
        st.subheader("Electricity: last month vs this month")
        lc = ss.last_carbon
        this_colour = ALERT if lc["kwh"] > lc["prev_kwh"] else LEAF
        kwh_df = pd.DataFrame({"Month": ["Last month", "This month"],
                               "kWh": [lc["prev_kwh"], lc["kwh"]]})
        kwh_chart = alt.Chart(kwh_df).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10,
                                               size=70).encode(
            x=alt.X("Month:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("kWh:Q"),
            color=alt.Color("Month:N", legend=None,
                            scale=alt.Scale(domain=["Last month", "This month"],
                                            range=[MUTED, this_colour])),
            tooltip=["Month", "kWh"],
        )
        show(kwh_chart)