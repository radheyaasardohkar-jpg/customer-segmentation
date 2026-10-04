import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="👥",
    layout="wide"
)


# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    return pd.read_csv("data/customer_rfm_segments.csv")


df = load_data()


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("🔎 Dashboard Filters")

selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)

min_monetary = st.sidebar.number_input(
    "Minimum Customer Value (£)",
    min_value=0.0,
    value=0.0,
    step=100.0
)

filtered_df = df[
    (df["Segment"].isin(selected_segments)) &
    (df["Monetary"] >= min_monetary)
]

if st.sidebar.button("Reset Filters"):
    st.rerun()


# ==================================================
# DASHBOARD TITLE
# ==================================================

st.title("👥 Customer Segmentation Dashboard")

st.markdown(
    "Analyze customer behavior using "
    "**Recency, Frequency, and Monetary value (RFM)**."
)


# ==================================================
# KPI METRICS
# ==================================================

total_customers = filtered_df["Customer ID"].nunique()

total_revenue = filtered_df["Monetary"].sum()

avg_spending = (
    filtered_df["Monetary"].mean()
    if len(filtered_df) > 0
    else 0
)

total_segments = filtered_df["Segment"].nunique()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Total Customer Value",
    f"£{total_revenue:,.0f}"
)

col3.metric(
    "Average Customer Value",
    f"£{avg_spending:,.0f}"
)

col4.metric(
    "Customer Segments",
    total_segments
)


# ==================================================
# SEGMENT DISTRIBUTION
# ==================================================

st.subheader("📊 Customer Segment Distribution")

if len(filtered_df) > 0:

    segment_counts = (
        filtered_df["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = [
        "Segment",
        "Customers"
    ]

    fig = px.bar(
        segment_counts,
        x="Segment",
        y="Customers",
        title="Customers by Segment",
        text="Customers"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "No customers match the selected filters."
    )


# ==================================================
# FREQUENCY VS MONETARY
# ==================================================

st.subheader("📈 Customer Behavior")

if len(filtered_df) > 0:

    fig = px.scatter(
        filtered_df,
        x="Frequency",
        y="Monetary",
        color="Segment",
        size="Monetary",
        hover_data=[
            "Customer ID",
            "Recency",
            "Frequency",
            "Monetary",
            "Segment"
        ],
        title="Frequency vs Monetary Value"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# RECENCY VS MONETARY
# ==================================================

st.subheader("⏱️ Recency vs Monetary Value")

if len(filtered_df) > 0:

    fig = px.scatter(
        filtered_df,
        x="Recency",
        y="Monetary",
        color="Segment",
        size="Monetary",
        hover_data=[
            "Customer ID",
            "Recency",
            "Frequency",
            "Monetary",
            "Segment"
        ],
        title="Recency vs Monetary Value"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# SEGMENT SUMMARY
# ==================================================

st.subheader("📋 Segment Summary")

if len(filtered_df) > 0:

    segment_summary = (
        filtered_df
        .groupby("Segment")
        .agg(
            Customers=("Customer ID", "count"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Monetary=("Monetary", "mean"),
            Total_Revenue=("Monetary", "sum")
        )
        .round(2)
    )

    st.dataframe(
        segment_summary,
        use_container_width=True
    )


# ==================================================
# CUSTOMER EXPLORER
# ==================================================

st.subheader("🔎 Customer Explorer")

if len(filtered_df) > 0:

    selected_segment = st.selectbox(
        "Select a customer segment",
        sorted(filtered_df["Segment"].unique())
    )

    segment_customers = filtered_df[
        filtered_df["Segment"] == selected_segment
    ]

    st.write(
        f"Customers in this segment: "
        f"**{len(segment_customers):,}**"
    )

    st.dataframe(
        segment_customers.sort_values(
            "Monetary",
            ascending=False
        ),
        use_container_width=True
    )


# ==================================================
# RFM DISTRIBUTIONS
# ==================================================

st.subheader("📊 RFM Distributions")

if len(filtered_df) > 0:

    col1, col2, col3 = st.columns(3)

    with col1:

        fig = px.histogram(
            filtered_df,
            x="Recency",
            title="Recency Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.histogram(
            filtered_df,
            x="Frequency",
            title="Frequency Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col3:

        fig = px.histogram(
            filtered_df,
            x="Monetary",
            title="Monetary Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ==================================================
# PCA CUSTOMER SEGMENT MAP
# ==================================================

st.subheader("🧭 Customer Segment Map")

pca_columns = [
    "PCA1",
    "PCA2"
]

if all(
    column in filtered_df.columns
    for column in pca_columns
):

    if len(filtered_df) > 0:

        fig = px.scatter(
            filtered_df,
            x="PCA1",
            y="PCA2",
            color="Segment",
            hover_data=[
                "Customer ID",
                "Recency",
                "Frequency",
                "Monetary",
                "Segment"
            ],
            title="Customer Segments in 2D"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

else:

    st.info(
        "PCA data is not available in the current dataset."
    )


# ==================================================
# DOWNLOAD FILTERED DATA
# ==================================================

st.subheader("⬇️ Download Customer Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Customer Data",
    data=csv_data,
    file_name="filtered_customer_segments.csv",
    mime="text/csv"
)


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.caption(
    "Customer Segmentation Project | "
    "RFM Analysis + K-Means Clustering + PCA"
)