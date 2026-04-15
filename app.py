import pandas as pd
import streamlit as st
import altair as alt

# code snippet assisted by ChatGPT

st.set_page_config(page_title="Semmelweis Hand-Washing Case", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("yearly_deaths_by_clinic.csv")
    df["Death Rate (%)"] = (df["Deaths"] / df["Birth"]) * 100
    return df

df = load_data()

st.title("Dr. Ignaz Semmelweis: Hand-Washing and Mortality")
st.write(
    """
    This app visualizes yearly birth and death counts from two maternity clinics associated with
    Dr. Ignaz Semmelweis's work. The goal is to show how mortality patterns changed over time,
    especially around the introduction of hand-washing practices.
    """
)

st.sidebar.header("Explore the data")
selected_clinics = st.sidebar.multiselect(
    "Select clinic(s):",
    options=sorted(df["Clinic"].unique()),
    default=sorted(df["Clinic"].unique())
)

year_range = st.sidebar.slider(
    "Select year range:",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(int(df["Year"].min()), int(df["Year"].max()))
)

filtered_df = df[
    (df["Clinic"].isin(selected_clinics)) &
    (df["Year"].between(year_range[0], year_range[1]))
].copy()

st.subheader("Data preview")
st.dataframe(filtered_df, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Death Rate by Year")
    rate_chart = (
        alt.Chart(filtered_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Death Rate (%):Q", title="Death Rate (%)"),
            color=alt.Color("Clinic:N", title="Clinic"),
            tooltip=["Year", "Clinic", "Birth", "Deaths", alt.Tooltip("Death Rate (%):Q", format=".2f")]
        )
        .properties(height=400)
    )
    handwash_rule = alt.Chart(pd.DataFrame({"Year": [1847]})).mark_rule(strokeDash=[6, 6]).encode(x="Year:O")
    st.altair_chart(rate_chart + handwash_rule, use_container_width=True)
    st.caption("The dashed line marks 1847, the year hand-washing was introduced in the Semmelweis case study.")

with col2:
    st.subheader("Births vs. Deaths")
    metric_df = filtered_df.melt(
        id_vars=["Year", "Clinic"],
        value_vars=["Birth", "Deaths"],
        var_name="Metric",
        value_name="Count"
    )
    metric_chart = (
        alt.Chart(metric_df)
        .mark_bar()
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Count:Q", title="Count"),
            color=alt.Color("Metric:N", title="Metric"),
            column=alt.Column("Clinic:N", title="Clinic"),
            tooltip=["Year", "Clinic", "Metric", "Count"]
        )
        .properties(height=400)
    )
    st.altair_chart(metric_chart, use_container_width=True)

st.subheader("Findings")
st.write(
    """
    The charts show that Clinic 1 had much higher mortality rates than Clinic 2 in the early years,
    but the death rate dropped sharply after 1847. This pattern supports Semmelweis's argument that
    hand-washing significantly reduced maternal deaths and improved patient outcomes.
    """
)

st.subheader("Summary statistics")
summary = (
    filtered_df.groupby("Clinic", as_index=False)
    .agg(
        Total_Births=("Birth", "sum"),
        Total_Deaths=("Deaths", "sum"),
        Avg_Death_Rate_Percent=("Death Rate (%)", "mean")
    )
)
summary["Avg_Death_Rate_Percent"] = summary["Avg_Death_Rate_Percent"].round(2)
st.dataframe(summary, use_container_width=True)
