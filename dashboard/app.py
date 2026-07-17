"""
FitScope Analytics — Fitness App Market Dashboard
Google Play Store — Segmentation & Trust Analysis

Run with: streamlit run app.py
(Run this command from inside the `dashboard/` folder so relative paths resolve correctly.)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------

st.set_page_config(
    page_title="FitScope Analytics",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve paths relative to this script's location, so the app works
# regardless of which folder you launch `streamlit run` from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
APPS_CSV = os.path.join(BASE_DIR, "..", "data", "processed", "apps_with_clusters.csv")
REVIEWS_CSV = os.path.join(BASE_DIR, "..", "data", "processed", "cleaned_reviews.csv")

# -----------------------------------------------------------------------
# BRAND COLORS
# -----------------------------------------------------------------------

PRIMARY = "#1B4B43"       # deep teal
PRIMARY_DARK = "#143630"
ACCENT = "#FF6B5C"        # coral (risk/warning)
GOLD = "#E8B923"          # premium/trust accent
BG = "#FAFAF8"
CARD_BG = "#FFFFFF"
MUTED = "#6B7280"
BORDER = "#E5E7EB"

CLUSTER_COLORS = {
    "Trusted Market Leaders": "#1B4B43",
    "Freemium Growth-Stage": "#2E8B7F",
    "Free Utility": "#8FBFA8",
    "Neglected but Functional": "#E8B923",
    "At-Risk / Underperforming": "#FF6B5C",
    "Premium Paid Outliers": "#6B4E9E",
}

# -----------------------------------------------------------------------
# STYLING
# -----------------------------------------------------------------------

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
h1, h2, h3 {{
    font-family: 'Poppins', sans-serif;
    color: {PRIMARY};
}}
.stApp {{
    background-color: {BG};
}}



/* Risk banner */
.risk-banner {{
    background-color: #FFF1EF;
    border-left: 4px solid {ACCENT};
    padding: 14px 18px;
    border-radius: 6px;
    margin-bottom: 18px;
}}
.risk-banner, .risk-banner * {{
    color: #7A2E24 !important;
}}

/* Recommendation cards */
.rec-card {{
    padding: 16px 18px;
    border-radius: 6px;
    margin-bottom: 14px;
}}
.rec-card, .rec-card * {{
    color: inherit;
}}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------

@st.cache_data
def load_data():
    apps = pd.read_csv(APPS_CSV)
    reviews = pd.read_csv(REVIEWS_CSV)
    return apps, reviews


def name_clusters(apps: pd.DataFrame) -> pd.DataFrame:
    """
    Dynamically assign business-meaningful names to clusters based on their
    profile characteristics, rather than hardcoding cluster ID numbers.
    This keeps the dashboard correct even if a re-run produces different
    cluster ID assignments (K-Means does not guarantee stable IDs).
    """
    days_col = "days_since_update_imputed" if "days_since_update_imputed" in apps.columns else "days_since_update"

    profile = apps.groupby("cluster").agg(
        score=("score", "mean"),
        installs=("minInstalls", "mean"),
        price=("price", "mean"),
        days_since_update=(days_col, "mean"),
        iap_pct=("offersIAP", "mean"),
        count=("app_id", "count"),
    )

    name_map = {}
    remaining = set(profile.index)

    # Premium Paid Outliers: highest average price (only if genuinely priced)
    premium = profile.loc[list(remaining)]["price"].idxmax()
    if profile.loc[premium, "price"] > 5:
        name_map[premium] = "Premium Paid Outliers"
        remaining.discard(premium)

    # At-Risk: lowest average score among remaining
    at_risk = profile.loc[list(remaining)]["score"].idxmin()
    name_map[at_risk] = "At-Risk / Underperforming"
    remaining.discard(at_risk)

    # Neglected but Functional: highest days_since_update among remaining
    neglected = profile.loc[list(remaining)]["days_since_update"].idxmax()
    name_map[neglected] = "Neglected but Functional"
    remaining.discard(neglected)

    # Trusted Market Leaders: highest installs among remaining
    leader = profile.loc[list(remaining)]["installs"].idxmax()
    name_map[leader] = "Trusted Market Leaders"
    remaining.discard(leader)

    # Freemium Growth-Stage: highest IAP % among remaining
    freemium = profile.loc[list(remaining)]["iap_pct"].idxmax()
    name_map[freemium] = "Freemium Growth-Stage"
    remaining.discard(freemium)

    # Anything left: Free Utility
    for c in remaining:
        name_map[c] = "Free Utility"

    apps = apps.copy()
    apps["cluster_name"] = apps["cluster"].map(name_map)
    return apps


apps_raw, reviews = load_data()
apps_raw = name_clusters(apps_raw)

# -----------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------

st.sidebar.header("Filters")

categories = sorted(apps_raw["category_grouped"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

price_bands = sorted(apps_raw["price_band"].unique())
selected_price = st.sidebar.multiselect("Price Band", price_bands, default=price_bands)

cluster_names = sorted(apps_raw["cluster_name"].unique())
selected_clusters = st.sidebar.multiselect("Segment", cluster_names, default=cluster_names)

rating_range = st.sidebar.slider("Rating Range", 1.0, 5.0, (1.0, 5.0), 0.1)

apps = apps_raw[
    apps_raw["category_grouped"].isin(selected_categories)
    & apps_raw["price_band"].isin(selected_price)
    & apps_raw["cluster_name"].isin(selected_clusters)
    & apps_raw["score"].between(rating_range[0], rating_range[1])
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(apps)}** of {len(apps_raw)} apps")

# -----------------------------------------------------------------------
# HERO / HEADER
# -----------------------------------------------------------------------

hero_col1, hero_col2 = st.columns([1, 8])
with hero_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=72)
    else:
        st.markdown("🏃")
with hero_col2:
    st.markdown(f"""
    <div style="padding-top:6px;">
        <h1 style="margin:0; color:{PRIMARY};">FitScope Analytics</h1>
        <p style="margin:2px 0 0 0; color:{MUTED};">
        What separates trusted, high-performing fitness apps from the rest?
        Segmentation and trust signals from {len(apps_raw):,} Google Play Store apps
        and {len(reviews):,} user reviews.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("###")

# -----------------------------------------------------------------------
# KPI ROW (custom HTML — avoids fighting Streamlit's theme CSS)
# -----------------------------------------------------------------------

at_risk_count = (apps["cluster_name"] == "At-Risk / Underperforming").sum()
at_risk_pct = at_risk_count / len(apps) * 100 if len(apps) else 0

def kpi_card(label, value):
    return f"""
    <div style="background-color:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px;
                padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
        <div style="color:{MUTED}; font-weight:600; font-size:14px; margin-bottom:4px;">{label}</div>
        <div style="color:{PRIMARY}; font-weight:700; font-size:28px;">{value}</div>
    </div>
    """

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(kpi_card("Total Apps", f"{len(apps):,}"), unsafe_allow_html=True)
with kpi2:
    st.markdown(kpi_card("Avg Rating", f"{apps['score'].mean():.2f}" if len(apps) else "—"), unsafe_allow_html=True)
with kpi3:
    st.markdown(kpi_card("Avg Installs", f"{apps['minInstalls'].mean():,.0f}" if len(apps) else "—"), unsafe_allow_html=True)
with kpi4:
    st.markdown(kpi_card("At-Risk Apps", f"{at_risk_pct:.1f}%"), unsafe_allow_html=True)

st.markdown("###")

if at_risk_pct > 0:
    st.markdown(f"""
    <div class="risk-banner">
        ⚠️ <strong>{at_risk_count} apps ({at_risk_pct:.1f}%)</strong> in the current filter fall into the
        <strong>At-Risk / Underperforming</strong> segment — apps that monetize aggressively (ads/IAP)
        but show notably lower ratings.
    </div>
    """, unsafe_allow_html=True)

st.markdown("###")

# -----------------------------------------------------------------------
# ROW: Segment distribution + Rating distribution
# -----------------------------------------------------------------------

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Market Segments")
    seg_counts = apps["cluster_name"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]
    fig = px.bar(
        seg_counts, x="Count", y="Segment", orientation="h",
        color="Segment", color_discrete_map=CLUSTER_COLORS, text="Count",
    )
    fig.update_layout(showlegend=False, height=380, plot_bgcolor="white",
                       margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Rating Distribution")
    fig = px.histogram(apps, x="score", nbins=25, color_discrete_sequence=[PRIMARY])
    fig.update_layout(height=380, plot_bgcolor="white",
                       xaxis_title="Rating", yaxis_title="Number of Apps",
                       margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------
# ROW: Installs vs Rating scatter + Category breakdown
# -----------------------------------------------------------------------

c3, c4 = st.columns([1, 1])

with c3:
    st.subheader("Installs vs. Rating by Segment")
    fig = px.scatter(
        apps, x="log_installs", y="score", color="cluster_name",
        color_discrete_map=CLUSTER_COLORS, hover_data=["title"], opacity=0.6,
        labels={"log_installs": "log10(Installs)", "score": "Rating"},
    )
    fig.update_layout(height=400, plot_bgcolor="white",
                       margin=dict(l=0, r=10, t=10, b=0),
                       legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Apps by Category")
    cat_counts = apps["category_grouped"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    fig = px.bar(cat_counts, x="Category", y="Count", color_discrete_sequence=[PRIMARY])
    fig.update_layout(height=400, plot_bgcolor="white",
                       margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------
# ROW: Cluster profile comparison
# -----------------------------------------------------------------------

st.subheader("Segment Profile Comparison")
profile = apps.groupby("cluster_name").agg(
    avg_rating=("score", "mean"),
    avg_installs_millions=("minInstalls", lambda x: x.mean() / 1_000_000),
    pct_ads=("containsAds", lambda x: x.mean() * 100),
    pct_iap=("offersIAP", lambda x: x.mean() * 100),
    num_apps=("app_id", "count"),
).round(2).reset_index()
st.dataframe(
    profile, use_container_width=True, hide_index=True,
    column_config={
        "cluster_name": st.column_config.TextColumn("Segment", width="medium"),
        "avg_rating": st.column_config.NumberColumn("Avg Rating", format="%.2f", width="small"),
        "avg_installs_millions": st.column_config.NumberColumn("Avg Installs (M)", format="%.2f", width="medium"),
        "pct_ads": st.column_config.NumberColumn("% With Ads", format="%.1f%%", width="small"),
        "pct_iap": st.column_config.NumberColumn("% With IAP", format="%.1f%%", width="small"),
        "num_apps": st.column_config.NumberColumn("# Apps", format="%d", width="small"),
    },
)

# -----------------------------------------------------------------------
# ROW: Review sentiment
# -----------------------------------------------------------------------

st.subheader("Review Sentiment Overview")
filtered_reviews = reviews[reviews["app_id"].isin(apps["app_id"])]

c5, c6 = st.columns([1, 1])
with c5:
    st.markdown("**Individual Review Ratings**")
    review_score_counts = filtered_reviews["score"].value_counts().sort_index().reset_index()
    review_score_counts.columns = ["Stars", "Count"]
    fig = px.bar(review_score_counts, x="Stars", y="Count", color_discrete_sequence=[GOLD])
    fig.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.markdown("**Most-reviewed apps in current filter**")
    top_reviewed = (
        apps.sort_values("ratings", ascending=False)
        [["title", "score", "ratings", "cluster_name"]]
        .head(10)
        .rename(columns={
            "title": "App",
            "score": "Rating",
            "ratings": "Total Ratings",
            "cluster_name": "Segment",
        })
    )
    st.dataframe(
        top_reviewed, use_container_width=True, hide_index=True,
        column_config={
            "App": st.column_config.TextColumn("App", width="large"),
            "Rating": st.column_config.NumberColumn("Rating", format="%.2f", width="small"),
            "Total Ratings": st.column_config.NumberColumn("Total Ratings", format="%d", width="medium"),
            "Segment": st.column_config.TextColumn("Segment", width="medium"),
        },
    )

# -----------------------------------------------------------------------
# APP EXPLORER TABLE
# -----------------------------------------------------------------------

st.subheader("App Explorer")
explorer_cols = ["title", "developer", "category_grouped", "score", "minInstalls",
                  "price_band", "cluster_name", "rating_tier"]
explorer_df = apps[explorer_cols].rename(columns={
    "title": "App",
    "developer": "Developer",
    "category_grouped": "Category",
    "score": "Rating",
    "minInstalls": "Installs",
    "price_band": "Price",
    "cluster_name": "Segment",
    "rating_tier": "Rating Tier",
}).sort_values("Rating", ascending=False)

st.dataframe(
    explorer_df, use_container_width=True, hide_index=True, height=350,
    column_config={
        "App": st.column_config.TextColumn("App", width="large"),
        "Developer": st.column_config.TextColumn("Developer", width="medium"),
        "Category": st.column_config.TextColumn("Category", width="medium"),
        "Rating": st.column_config.NumberColumn("Rating", format="%.2f", width="small"),
        "Installs": st.column_config.NumberColumn("Installs", format="%d", width="medium"),
        "Price": st.column_config.TextColumn("Price", width="small"),
        "Segment": st.column_config.TextColumn("Segment", width="medium"),
        "Rating Tier": st.column_config.TextColumn("Rating Tier", width="small"),
    },
)

# -----------------------------------------------------------------------
# BUSINESS RECOMMENDATIONS
# -----------------------------------------------------------------------

st.markdown("---")
st.markdown(f"""
<h3 style="color:{PRIMARY}; font-family:'Poppins', sans-serif; margin-bottom:12px;">
📋 Business Recommendations
</h3>
""", unsafe_allow_html=True)

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    st.markdown(f"""
    <div class="rec-card" style="background-color:#FFF1EF; border-left:4px solid {ACCENT}; color:#7A2E24;">
        <strong>⚠️ Avoid the At-Risk pattern</strong><br>
        ~8.8% of apps monetize aggressively (ads/IAP) but rate poorly (~3.0 avg).
        Screen investment targets against this profile before committing.
    </div>
    <div class="rec-card" style="background-color:#FFF8E1; border-left:4px solid {GOLD}; color:#8A6D00;">
        <strong>👀 Watch "Neglected but Functional" apps</strong><br>
        ~5.3% haven't been updated in ~3 years but still hold decent ratings —
        coasting on old trust, higher risk of decline without reinvestment.
    </div>
    """, unsafe_allow_html=True)

with rec_col2:
    st.markdown(f"""
    <div class="rec-card" style="background-color:#EAF4F1; border-left:4px solid {PRIMARY}; color:{PRIMARY};">
        <strong>✅ Target Trusted Market Leaders</strong><br>
        Proven scale, high ratings, active maintenance — lower risk,
        higher acquisition cost for established-player investment.
    </div>
    <div class="rec-card" style="background-color:#EAF4F1; border-left:4px solid #2E8B7F; color:{PRIMARY};">
        <strong>📈 Freemium Growth-Stage is the best hunting ground</strong><br>
        The largest segment, already IAP-committed with strong ratings —
        good candidates for scaling investment.
    </div>
    """, unsafe_allow_html=True)

st.caption(
    "Review sentiment (% negative reviews) is the single strongest predictor of app "
    "quality — stronger than any metadata field. See modeling notebook (Section B6) for details."
)

# -----------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------

st.markdown("---")
st.caption(
    "FitScope Analytics — Fitness App Market Analytics Capstone. Data scraped from Google Play Store. "
    "Segments derived via K-Means clustering (k=6); rating prediction via Random Forest classification, "
    "enhanced with review sentiment features."
)
