import os
import psycopg
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from metrics import calculate_unavailability_rate

load_dotenv("infra/.env")
st.set_page_config(
    page_title="Citi Bike Availability Analytics",
    layout="wide"
)

st.title("Citi Bike Availability Analytics")
st.markdown(
    "Analyzing bicycle availability across New York City's "
    "Citi Bike station network."
)
st.divider()
st.subheader("Overview")

try:
    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="mobility",
        user="mobility",
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (
                        WHERE eligible_snapshots > 0
                    ) AS stations_analyzed,
                    COALESCE(SUM(eligible_snapshots), 0),
                    COALESCE(SUM(zero_bike_snapshots), 0)
                FROM dbt_mobility.mart_station_unavailability
            """)
            stations, eligible, zero_bikes = cursor.fetchone()

            cursor.execute("""
                SELECT
                    station_name,
                    eligible_snapshots,
                    zero_bike_snapshots,
                    unavailability_rate_pct
                FROM dbt_mobility.mart_station_unavailability
                WHERE has_minimum_sample = TRUE
                  AND eligible_snapshots > 0
                ORDER BY unavailability_rate_pct DESC NULLS LAST,
                         eligible_snapshots DESC
                LIMIT 20
            """)

            top_stations = pd.DataFrame(
                cursor.fetchall(),
                columns=[
                    "station_name",
                    "eligible_snapshots",
                    "zero_bike_snapshots",
                    "unavailability_rate_pct"
                ]
            )

            cursor.execute("""
                SELECT
                    hour_of_day,
                    eligible_observations,
                    zero_bike_observations,
                    unavailability_rate_pct
                FROM dbt_mobility.mart_hourly_unavailability
                WHERE eligible_observations > 0
                ORDER BY hour_of_day
            """)

            hourly_data = pd.DataFrame(
                cursor.fetchall(),
                columns=[
                    "hour_of_day",
                    "eligible_observations",
                    "zero_bike_observations",
                    "unavailability_rate_pct"
                ]
            )

            cursor.execute("""
                SELECT
                    quality_category,
                    observation_count,
                    percentage_of_total
                FROM dbt_mobility.mart_station_data_quality
                ORDER BY observation_count DESC
            """)

            quality_data = pd.DataFrame(
                cursor.fetchall(),
                columns=[
                    "quality_category",
                    "observation_count",
                    "percentage_of_total"
                ]
            )

            cursor.execute("""
                SELECT
                    MIN(collected_at_utc),
                    MAX(collected_at_utc),
                    COUNT(DISTINCT collected_at_utc),
                    COUNT(DISTINCT (
                        collected_at_utc AT TIME ZONE 'America/New_York'
                    )::date)
                FROM raw.station_status
            """)

            first_snapshot, last_snapshot, total_snapshots, days_observed = (
                cursor.fetchone()
            )

    unavailability_rate = calculate_unavailability_rate(
        zero_bikes,
        eligible
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Stations Analyzed",
        f"{stations:,}"
    )

    col2.metric(
        "Eligible Observations",
        f"{eligible:,}"
    )

    col3.metric(
        "Zero-Bike Observations",
        f"{zero_bikes:,}"
    )

    col4.metric(
        "Unavailability Rate",
        f"{unavailability_rate:.2f}%"
    )

    st.caption(
        "Unavailability represents the percentage of eligible "
        "snapshots with zero available bicycles, not continuous downtime."
    )

    st.divider()
    st.subheader("Stations by Unavailability Rate")

    if not top_stations.empty:
        top_stations["unavailability_rate_pct"] = (
            top_stations["unavailability_rate_pct"].astype(float)
        )

        top_n = st.selectbox(
            "Number of stations to display",
            options=[5, 10, 15, 20],
            index=1
        )

        display_stations = (
            top_stations
            .nlargest(top_n, "unavailability_rate_pct")
            .sort_values("unavailability_rate_pct")
        )

        fig = px.bar(
            display_stations,
            x="unavailability_rate_pct",
            y="station_name",
            orientation="h",
            labels={
                "unavailability_rate_pct": "Unavailability Rate",
                "station_name": "Station"
            },
            hover_data=[
                "eligible_snapshots",
                "zero_bike_snapshots"
            ]
        )

        fig.update_traces(
            texttemplate="%{x:.2f}%",
            textposition="outside"
        )

        fig.update_layout(
            height=480,
            xaxis_range=[0, 100],
            xaxis_ticksuffix="%",
            yaxis_title=None
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No station data available.")

    st.divider()
    st.subheader("Unavailability Rate by Hour")

    if not hourly_data.empty:
        hourly_data["unavailability_rate_pct"] = (
            hourly_data["unavailability_rate_pct"].astype(float)
        )

        fig_hourly = px.line(
            hourly_data,
            x="hour_of_day",
            y="unavailability_rate_pct",
            markers=True,
            labels={
                "hour_of_day": "Hour of Day (New York Time)",
                "unavailability_rate_pct": "Unavailability Rate"
            },
            hover_data=[
                "eligible_observations",
                "zero_bike_observations"
            ]
        )

        fig_hourly.update_layout(
            height=450,
            xaxis=dict(dtick=1),
            yaxis=dict(ticksuffix="%", rangemode="tozero")
        )

        st.plotly_chart(fig_hourly, use_container_width=True)

    else:
        st.info("No hourly availability data available.")

    st.divider()
    st.subheader("Key Findings")

    if not top_stations.empty and not hourly_data.empty:

        highest_station = top_stations.loc[
            top_stations["unavailability_rate_pct"].idxmax()
        ]

        peak_hour = hourly_data.loc[
            hourly_data["unavailability_rate_pct"].idxmax()
        ]

        st.markdown(f"""
        **Station with the highest observed unavailability:**

        - {highest_station['station_name']}
        - Unavailability rate: **{highest_station['unavailability_rate_pct']:.2f}%**
        - Eligible observations: {int(highest_station['eligible_snapshots']):,}

        **Hour with the highest observed unavailability:**

        - **{int(peak_hour['hour_of_day']):02d}:00 (New York Time)**
        - Unavailability rate: **{peak_hour['unavailability_rate_pct']:.2f}%**

        **Business Implication:**

        These results highlight potential priorities for bicycle
        rebalancing operations, particularly at stations with high
        observed unavailability rates and during peak unavailability hours.
                """)

        st.caption(
            "Findings are based on sampled station observations. "
            "They do not represent continuous station downtime "
            "or establish long-term availability patterns."
        )

        st.divider()
    st.subheader("Data Quality Overview")

    if not quality_data.empty:
        quality_data["percentage_of_total"] = (
            quality_data["percentage_of_total"].astype(float)
        )

        fig_quality = px.bar(
            quality_data,
            x="percentage_of_total",
            y="quality_category",
            orientation="h",
            labels={
                "percentage_of_total": "Percentage of Observations",
                "quality_category": "Quality Category"
            },
            hover_data=["observation_count"]
        )

        fig_quality.update_layout(
            height=400,
            xaxis_range=[0, 100],
            xaxis_ticksuffix="%",
            yaxis_title=None,
            showlegend=False
        )

        st.plotly_chart(
            fig_quality,
            use_container_width=True
        )

        quality_table = quality_data.rename(
            columns={
                "quality_category": "Category",
                "observation_count": "Observations",
                "percentage_of_total": "Percentage (%)"
            }
        )

        st.dataframe(
            quality_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Observations": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Percentage (%)": st.column_config.NumberColumn(
                    format="%.2f%%"
                )
            }
        )

        st.caption(
            "Observation distribution by data quality category, "
            "based on the dbt data quality model."
        )

    else:
        st.info("No data quality information available.")

    st.subheader("Data Coverage")

    if first_snapshot and last_snapshot:
        st.info(
            f"**Observation Period (UTC):** "
            f"{first_snapshot:%Y-%m-%d} to "
            f"{last_snapshot:%Y-%m-%d} | "
            f"**Snapshots:** {total_snapshots:,} | "
            f"**Days Observed:** {days_observed}"
        )

        st.caption(
            "Coverage refers to raw snapshots loaded into PostgreSQL. "
            "Observations may be incomplete or unevenly distributed "
            "across dates and hours."
        )

except (psycopg.Error, KeyError) as error:
    st.error(f"Database connection failed: {error}")