import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(
    page_title="Tennis Analytics Dashboard",
    page_icon="🎾",
    layout="wide"
)

# --- DB Connection ---
@st.cache_resource
def get_connection():
    return sqlite3.connect(
        r"C:\labmentrix internship\FINAL_PROJECT\tennis.db",
        check_same_thread=False
    )

conn = get_connection()

# --- Sidebar Navigation ---
st.sidebar.title("🎾 Tennis Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate to",
    ["🏠 Home", "🏆 Competitions", "🏟️ Venues & Complexes", "📊 Player Rankings"]
)

# ============================================================
# HOME PAGE
# ============================================================
if page == "🏠 Home":
    st.title("🎾 Tennis Data Analytics Dashboard")
    st.markdown("**Project 11 — SportRadar API | SQLite | Streamlit**")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    total_competitions = pd.read_sql_query("SELECT COUNT(*) as c FROM competitions", conn).iloc[0,0]
    total_venues = pd.read_sql_query("SELECT COUNT(*) as c FROM venues", conn).iloc[0,0]
    total_complexes = pd.read_sql_query("SELECT COUNT(*) as c FROM complexes", conn).iloc[0,0]
    total_competitors = pd.read_sql_query("SELECT COUNT(DISTINCT competitor_id) as c FROM competitors", conn).iloc[0,0]

    col1.metric("🏆 Competitions", f"{total_competitions:,}")
    col2.metric("🏟️ Venues", f"{total_venues:,}")
    col3.metric("🏢 Complexes", f"{total_complexes:,}")
    col4.metric("👤 Competitors", f"{total_competitors:,}")

    st.markdown("---")
    st.subheader("📌 About This Project")
    st.markdown("""
    This dashboard analyzes **professional tennis data** fetched from the **SportRadar Tennis API**.

    **Data includes:**
    - 🏆 6,572 competitions across multiple categories
    - 🏟️ 3,975 venues across 764 complexes worldwide
    - 👤 1,000 ranked professional tennis players

    **Tech Stack:** Python · SportRadar API · SQLite · Pandas · Streamlit · Plotly

    **Use the sidebar** to explore Competitions, Venues, and Player Rankings.
    """)

    st.markdown("---")
    st.subheader("🌍 Top 5 Countries by Venues")
    df_home = pd.read_sql_query("""
        SELECT country_name, COUNT(*) as total_venues
        FROM venues
        GROUP BY country_name
        ORDER BY total_venues DESC
        LIMIT 5
    """, conn)
    fig = px.bar(df_home, x="country_name", y="total_venues",
                 color="total_venues", color_continuous_scale="teal",
                 labels={"country_name": "Country", "total_venues": "Venues"})
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# COMPETITIONS PAGE
# ============================================================
elif page == "🏆 Competitions":
    st.title("🏆 Competitions Analysis")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Browse", "📊 Charts", "🔍 Search"])

    with tab1:
        st.subheader("All Competitions")
        df_comp = pd.read_sql_query("""
            SELECT c.competition_id, c.competition_name, c.gender,
                   c.type, cat.category_name
            FROM competitions c
            LEFT JOIN categories cat ON c.category_id = cat.category_id
            LIMIT 500
        """, conn)
        st.dataframe(df_comp, use_container_width=True, height=400)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Competitions by Gender")
            df_gender = pd.read_sql_query("""
                SELECT gender, COUNT(*) as count
                FROM competitions
                GROUP BY gender
            """, conn)
            fig1 = px.pie(df_gender, names="gender", values="count",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Top 10 Categories")
            df_cat = pd.read_sql_query("""
                SELECT cat.category_name, COUNT(*) as comp_count
                FROM competitions c
                JOIN categories cat ON c.category_id = cat.category_id
                GROUP BY cat.category_name
                ORDER BY comp_count DESC
                LIMIT 10
            """, conn)
            fig2 = px.bar(df_cat, x="comp_count", y="category_name",
                          orientation="h", color="comp_count",
                          color_continuous_scale="blues")
            fig2.update_layout(yaxis=dict(autorange="reversed"), height=400)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Competition Types Distribution")
        df_type = pd.read_sql_query("""
            SELECT type, COUNT(*) as count
            FROM competitions
            WHERE type IS NOT NULL
            GROUP BY type
            ORDER BY count DESC
            LIMIT 10
        """, conn)
        fig3 = px.bar(df_type, x="type", y="count",
                      color="count", color_continuous_scale="purples")
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.subheader("🔍 Search Competitions")
        search = st.text_input("Enter competition name keyword:")
        if search:
            df_search = pd.read_sql_query(f"""
                SELECT c.competition_name, c.gender, c.type,
                       cat.category_name
                FROM competitions c
                LEFT JOIN categories cat ON c.category_id = cat.category_id
                WHERE c.competition_name LIKE '%{search}%'
                LIMIT 100
            """, conn)
            st.write(f"Found **{len(df_search)}** results:")
            st.dataframe(df_search, use_container_width=True)

# ============================================================
# VENUES & COMPLEXES PAGE
# ============================================================
elif page == "🏟️ Venues & Complexes":
    st.title("🏟️ Venues & Complexes Analysis")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🌍 By Country", "🏢 Complexes", "🔍 Search Venues"])

    with tab1:
        st.subheader("Top 15 Countries by Number of Venues")
        df_country = pd.read_sql_query("""
            SELECT country_name, COUNT(*) as total_venues
            FROM venues
            GROUP BY country_name
            ORDER BY total_venues DESC
            LIMIT 15
        """, conn)
        fig = px.bar(df_country, x="total_venues", y="country_name",
                     orientation="h", color="total_venues",
                     color_continuous_scale="teal")
        fig.update_layout(yaxis=dict(autorange="reversed"), height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Venues Data Table")
        df_v = pd.read_sql_query("""
            SELECT venue_name, city_name, country_name, timezone
            FROM venues
            ORDER BY country_name
            LIMIT 200
        """, conn)
        st.dataframe(df_v, use_container_width=True, height=350)

    with tab2:
        st.subheader("Top 15 Complexes by Venue Count")
        df_cx = pd.read_sql_query("""
            SELECT c.complex_name, COUNT(v.venue_id) as venue_count
            FROM complexes c
            JOIN venues v ON c.complex_id = v.complex_id
            GROUP BY c.complex_name
            ORDER BY venue_count DESC
            LIMIT 15
        """, conn)
        fig2 = px.bar(df_cx, x="venue_count", y="complex_name",
                      orientation="h", color="venue_count",
                      color_continuous_scale="oranges")
        fig2.update_layout(yaxis=dict(autorange="reversed"), height=500)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("🔍 Search Venues by Country")
        countries = pd.read_sql_query("""
            SELECT DISTINCT country_name FROM venues
            ORDER BY country_name
        """, conn)["country_name"].tolist()

        selected = st.selectbox("Select a country:", countries)
        if selected:
            df_sel = pd.read_sql_query(f"""
                SELECT v.venue_name, v.city_name, c.complex_name, v.timezone
                FROM venues v
                LEFT JOIN complexes c ON v.complex_id = c.complex_id
                WHERE v.country_name = '{selected}'
                ORDER BY v.city_name
            """, conn)
            st.write(f"**{len(df_sel)} venues** found in {selected}")
            st.dataframe(df_sel, use_container_width=True, height=400)

# ============================================================
# PLAYER RANKINGS PAGE
# ============================================================
elif page == "📊 Player Rankings":
    st.title("📊 Player Rankings Analysis")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🥇 Top Players", "🌍 By Country", "📈 Points Analysis"])

    with tab1:
        st.subheader("Top Ranked Players")
        top_n = st.slider("Show Top N players:", 10, 100, 25)
        df_top = pd.read_sql_query(f"""
            SELECT DISTINCT cr.rank, c.name, c.country, cr.points, cr.competitions_played
            FROM competitor_rankings cr
            JOIN competitors c ON cr.competitor_id = c.competitor_id
            ORDER BY cr.rank ASC, cr.points DESC
            LIMIT {top_n}
        """, conn)
        st.dataframe(df_top, use_container_width=True, height=400)

        fig = px.bar(df_top.head(20), x="name", y="points",
                     color="country", title="Top 20 Players by Points")
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Countries by Player Count")
            df_c = pd.read_sql_query("""
                SELECT country, COUNT(DISTINCT competitor_id) as player_count
                FROM competitors
                GROUP BY country
                ORDER BY player_count DESC
                LIMIT 10
            """, conn)
            fig1 = px.pie(df_c, names="country", values="player_count",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Avg Points by Country (min 3 players)")
            df_avg = pd.read_sql_query("""
                SELECT c.country, ROUND(AVG(cr.points), 0) as avg_points,
                       COUNT(DISTINCT c.competitor_id) as player_count
                FROM competitors c
                JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
                GROUP BY c.country
                HAVING player_count >= 3
                ORDER BY avg_points DESC
                LIMIT 10
            """, conn)
            fig2 = px.bar(df_avg, x="avg_points", y="country",
                          orientation="h", color="avg_points",
                          color_continuous_scale="greens")
            fig2.update_layout(yaxis=dict(autorange="reversed"), height=400)
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Points Distribution")
        df_pts = pd.read_sql_query("""
            SELECT DISTINCT cr.points, c.name, c.country
            FROM competitor_rankings cr
            JOIN competitors c ON cr.competitor_id = c.competitor_id
        """, conn)
        fig3 = px.histogram(df_pts, x="points", nbins=50,
                            color_discrete_sequence=["#00b4d8"],
                            title="Distribution of Player Points")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Points Range Buckets")
        df_bucket = pd.read_sql_query("""
            SELECT
                CASE
                    WHEN points >= 5000 THEN '5000+'
                    WHEN points >= 2000 THEN '2000-4999'
                    WHEN points >= 1000 THEN '1000-1999'
                    WHEN points >= 500  THEN '500-999'
                    WHEN points >= 100  THEN '100-499'
                    ELSE 'Below 100'
                END as points_range,
                COUNT(DISTINCT competitor_id) as competitor_count
            FROM competitor_rankings
            GROUP BY points_range
            ORDER BY MIN(points) DESC
        """, conn)
        fig4 = px.bar(df_bucket, x="points_range", y="competitor_count",
                      color="competitor_count", color_continuous_scale="reds")
        st.plotly_chart(fig4, use_container_width=True)