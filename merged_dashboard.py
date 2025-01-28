import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

########################################
# 1) Domain Explanations (Your Text)
########################################
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation - Three Choice:** ...
""",
    "Escalation - Two Choice": """
**Escalation - Two Choice:** ...
""",
    "Intervention - Two Choice": """
**Intervention:** ...
""",
    "Intervention - Three Choice": """
**Intervention:** ...
""",
    "Cooperation": """
**Cooperation:** ...
""",
    "Alliance Dynamics": """
**Alliance Dynamics:** ...
"""
}

########################################
# 2) ECharts Bar Option (Stacked)
########################################
def build_echarts_bar_option(x_data, series_data, chart_title="ECharts Bar", 
                             x_label="", y_label="Percentage"):
    """
    Returns an ECharts 'option' dict for a stacked vertical bar chart 
    with bold axis labels. 
    """
    series_list = []
    for name, values in series_data.items():
        series_list.append({
            "name": name,
            "type": "bar",
            "stack": "total",
            "data": values
        })
    option = {
        "title": {
            "text": chart_title,
            "left": "center",
            "textStyle": {"fontSize": 16}
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "textStyle": {"fontSize": 12}
        },
        "legend": {
            "top": 30,
            "textStyle": {"fontSize": 12, "fontWeight": "bold"}
        },
        "grid": {
            "left": "5%",
            "right": "5%",
            "bottom": "10%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "name": x_label,
            "data": x_data,
            "nameTextStyle": {"fontSize": 14, "fontWeight": "bold"},
            "axisLabel": {"fontSize": 12, "fontWeight": "bold"}
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "min": 0,
            "max": 100,
            "nameTextStyle": {"fontSize": 14, "fontWeight": "bold"},
            "axisLabel": {"fontSize": 12, "fontWeight": "bold"}
        },
        "series": series_list
    }
    return option

########################################
# 3) Domain-Level Plot Logic (Local)
########################################
def show_domain_level_plot(domain_df):
    """
    Renders the domain-level chart. We assume domain_df is already filtered to 
    exactly the chosen domain and chosen answers/models.
    """
    if domain_df.empty:
        st.warning("No data after filtering.")
        return
    # Let user pick from all possible answers in this domain
    all_answers = sorted(domain_df["answer"].unique())
    selected_answers = st.multiselect(
        "Response Types",
        all_answers,
        default=all_answers  # always show all for new domain
    )
    df_filtered = domain_df[domain_df["answer"].isin(selected_answers)]

    # Then let user pick from all possible models
    all_models = sorted(df_filtered["model"].unique())
    chosen_models = st.multiselect(
        "Models",
        all_models,
        default=all_models  # always show all for new domain
    )
    df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]
    if df_filtered.empty:
        st.warning("No data after filtering.")
        return

    # Build final chart
    x_data = sorted(df_filtered["model"].unique())
    answers_used = sorted(df_filtered["answer"].unique())
    series_data = {}
    for ans in answers_used:
        row_values = []
        for m in x_data:
            sub_df = df_filtered[(df_filtered["model"] == m) & (df_filtered["answer"] == ans)]
            row_values.append(sub_df["percentage"].mean() if len(sub_df) > 0 else 0)
        series_data[ans] = row_values

    option = build_echarts_bar_option(
        x_data=x_data,
        series_data=series_data,
        chart_title="Response Distribution by LLMs",
        x_label="Model",
        y_label="Percentage"
    )
    st_echarts(options=option, height="400px")


########################################
# 4) Country-Level Plot Logic (Local)
########################################
def show_country_level_plot(country_df):
    """
    Renders the country-level chart. We assume country_df is already filtered to 
    exactly the chosen domain. 
    """
    if country_df.empty:
        st.warning("No data for domain.")
        return

    # Let user pick from all possible actors in domain
    all_actors = sorted(country_df["actor"].unique())
    chosen_actors = st.multiselect(
        "Actor(s)",
        all_actors,
        default=all_actors  # always show all for new domain
    )
    df_filtered = country_df[country_df["actor"].isin(chosen_actors)]

    # Let user pick from all possible models
    all_models = sorted(df_filtered["model"].unique())
    chosen_models = st.multiselect(
        "Model(s)",
        all_models,
        default=all_models[:3]
    )
    df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

    # Let user pick from all possible answers
    all_answers = sorted(df_filtered["answer"].unique())
    chosen_answers = st.multiselect(
        "Response Types",
        all_answers,
        default=all_answers
    )
    df_filtered = df_filtered[df_filtered["answer"].isin(chosen_answers)]

    if df_filtered.empty:
        st.warning("No data after filtering.")
        return

    # Build final chart with side-by-side columns for each model
    final_models = sorted(df_filtered["model"].unique())
    model_cols = st.columns(len(final_models))

    for i, mod in enumerate(final_models):
        sub_df_m = df_filtered[df_filtered["model"] == mod]
        if sub_df_m.empty:
            with model_cols[i]:
                st.warning(f"No data for model: {mod}")
            continue

        x_data = sorted(sub_df_m["actor"].unique())
        answers_used = sorted(sub_df_m["answer"].unique())
        series_data = {}
        for ans in answers_used:
            row_vals = []
            sub_df_ans = sub_df_m[sub_df_m["answer"] == ans]
            for act in x_data:
                sub_df_act = sub_df_ans[sub_df_ans["actor"] == act]
                row_vals.append(sub_df_act["percentage"].mean() if len(sub_df_act) > 0 else 0)
            series_data[ans] = row_vals

        option = build_echarts_bar_option(
            x_data=x_data,
            series_data=series_data,
            chart_title=mod,
            x_label="Actor",
            y_label="Percentage"
        )
        if i > 0:
            option["legend"] = {"show": False}
        with model_cols[i]:
            st_echarts(options=option, height="400px")


########################################
# 5) Main with Preset Buttons (No rerun)
########################################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    st.info("""
### Using This Dashboard
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking 
of Large Language Models’ preferences in international relations. 
It always shows all valid response types and models for your chosen domain. 
Pressing a preset button overrides your domain/actor choice in this run.
""")

    # Let user choose Domain-Level or Country-Level (no session usage)
    analysis_options = ["Domain-Level", "Country-Level"]
    analysis_choice_local = st.radio("Select Level of Analysis", analysis_options)

    # Let user pick domain from the selectbox
    # We'll load the data to get domain_options dynamically
    # but let's do a small approach for the user:
    # We'll just read from file if it’s quick, or define a local domain_options for demonstration
    try:
        df_domain_all = pd.read_csv("final_dashboard_df.csv")
        domain_all_options = sorted(df_domain_all["domain"].unique())
    except:
        # fallback if the file is missing
        domain_all_options = sorted(list(DOMAIN_EXPLANATIONS.keys()))
    selected_domain_local = st.selectbox("Domain", domain_all_options)

    # For country-level domain, we will also load the country distribution
    try:
        df_country_all = pd.read_csv("country_level_distribution.csv")
        country_domain_all_options = sorted(df_country_all["domain"].unique())
    except:
        country_domain_all_options = sorted(list(DOMAIN_EXPLANATIONS.keys()))

    # 3 columns for preset buttons
    c1, c2, c3 = st.columns(3)

    # We create local variables for final domain and possibly actor
    final_analysis = analysis_choice_local
    final_domain = selected_domain_local
    final_actor = None  # only used if country-level

    # ========== PRESET 1 ==========
    with c1:
        if st.button("Pre-set 1: Escalation (2 Choice)"):
            # Force Domain-Level & domain= "Escalation - Two Choice"
            final_analysis = "Domain-Level"
            final_domain = "Escalation - Two Choice"

    # ========== PRESET 2 ==========
    with c2:
        if st.button("Pre-set 2: China Escalation (2 Choice)"):
            final_analysis = "Country-Level"
            final_domain = "Escalation - Two Choice"
            final_actor = "China"  # We'll override in code below

    # ========== PRESET 3 ==========
    with c3:
        if st.button("Pre-set 3: Cooperation"):
            final_analysis = "Domain-Level"
            final_domain = "Cooperation"

    st.write("---")

    # Now we do the actual data loading & plotting logic using final_analysis, final_domain, final_actor

    # -------------- Domain-Level --------------
    if final_analysis == "Domain-Level":
        st.subheader(f"**Domain-Level** → Domain: *{final_domain}*")

        # Load the domain-level CSV again
        try:
            domain_df = pd.read_csv("final_dashboard_df.csv")
        except FileNotFoundError:
            st.error("Missing domain-level 'final_dashboard_df.csv'.")
            return

        # Filter domain
        domain_df = domain_df[domain_df["domain"] == final_domain]
        # Show explanation
        if final_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        # Now do the domain-level plot
        show_domain_level_plot(domain_df)

    # -------------- Country-Level --------------
    else:
        st.subheader(f"**Country-Level** → Domain: *{final_domain}*")

        # Load the country-level CSV
        try:
            country_df = pd.read_csv("country_level_distribution.csv")
        except FileNotFoundError:
            st.error("Missing 'country_level_distribution.csv'.")
            return

        # Filter domain
        country_df = country_df[country_df["domain"] == final_domain]
        # Show explanation
        if final_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        # If preset 2 was pressed => final_actor= "China", we can forcibly subset
        # but let's allow the user to see the full UI. We'll do it as part of the main logic
        # or we do a local approach. For demonstration, let's forcibly filter if final_actor is set:
        if final_actor is not None:
            # Only keep "China"
            country_df = country_df[country_df["actor"] == final_actor]

        show_country_level_plot(country_df)


if __name__ == "__main__":
    main()
