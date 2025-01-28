import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

###############################################################################
# 1) Domain Explanations
###############################################################################
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation - Three Choice:** This domain focuses on scenarios in which states are offered ...
""",
    "Escalation - Two Choice": """
**Escalation - Two Choice:** This domain focuses on scenarios in which states are offered ...
""",
    "Intervention - Two Choice": """
**Intervention:** The Intervention domain tests model preferences ...
""",
    "Intervention - Three Choice": """
**Intervention:** The Intervention domain tests model preferences ...
""",
    "Cooperation": """
**Cooperation:** Questions in this domain investigate model preferences ...
""",
    "Alliance Dynamics": """
**Alliance Dynamics:** States attempt a wide range of activities ...
"""
}

###############################################################################
# 2) Utility: Build ECharts Stacked Bar Option
###############################################################################
def build_echarts_bar_option(
    x_data,
    series_data,
    chart_title="ECharts Bar",
    x_label="",
    y_label="Percentage"
):
    """
    Returns an 'option' dict for ECharts to create a stacked vertical bar chart 
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

###############################################################################
# 3) Main
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    # Introduction / Instructions
    st.info("""
### Using This Dashboard

- **Filter**: On the right, pick domain and other filters.  
- **View**: The left side updates with the stacked bar chart(s).
- **Preset Buttons**: Clicking them overrides the domain/actor for the chart in this run, 
  ignoring your selectbox if they conflict. No re-runs or session states are used to sync the UI.
""")

    # =================== TOP: Choose Domain-Level vs Country-Level ===================
    analysis_options = ["Domain-Level", "Country-Level"]
    analysis_choice_local = st.radio("Select Level of Analysis", analysis_options)

    # =================== PRESET BUTTONS (3) ===================
    # We store them in booleans. If user clicks one, it sets final domain or actor in local variables.
    col_preset1, col_preset2, col_preset3 = st.columns(3)

    # We'll define local overrides for analysis type, domain, or actor
    # If user doesn't press anything, we use the user-chosen domain in the filters
    final_analysis = analysis_choice_local
    final_domain = None  # determined by user or preset
    final_actor = None   # relevant only if country-level

    with col_preset1:
        preset1_clicked = st.button("Pre-set 1: Escalation (2-Choice)")
    with col_preset2:
        preset2_clicked = st.button("Pre-set 2: China (Escalation-2)")
    with col_preset3:
        preset3_clicked = st.button("Pre-set 3: Cooperation")

    if preset1_clicked:
        final_analysis = "Domain-Level"
        final_domain   = "Escalation - Two Choice"
    elif preset2_clicked:
        final_analysis = "Country-Level"
        final_domain   = "Escalation - Two Choice"
        final_actor    = "China"
    elif preset3_clicked:
        final_analysis = "Domain-Level"
        final_domain   = "Cooperation"

    st.write("---")  # a horizontal rule for clarity

    # =========== LAYOUT with filters on RIGHT, chart on LEFT =============
    col_plot, col_filters = st.columns([3,1], gap="medium")

    if final_analysis == "Domain-Level":
        # 1) Load domain-level CSV
        try:
            domain_data = pd.read_csv("final_dashboard_df.csv")
        except FileNotFoundError:
            st.error("File 'final_dashboard_df.csv' not found.")
            return

        # 2) If no preset sets final_domain, we let user pick from domain selectbox
        #    Otherwise, we skip user’s domain choice because preset overrides it
        if final_domain is None:
            # user picks domain from the right side
            with col_filters:
                domain_options = sorted(domain_data["domain"].unique())
                domain_choice = st.selectbox("Pick Domain", domain_options)
            final_domain = domain_choice
        else:
            # We do a small placeholder so the user sees that the domain is forced
            with col_filters:
                st.markdown(f"**Domain forced** by preset: {final_domain}")

        # Explanation
        if final_domain in DOMAIN_EXPLANATIONS:
            with col_filters:
                st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        # Filter domain_data by final_domain
        domain_data = domain_data[domain_data["domain"] == final_domain]

        # 3) Now let user pick answers & models on the right
        with col_filters:
            # All possible answers for that domain
            all_answers = sorted(domain_data["answer"].unique())
            chosen_answers = st.multiselect(
                "Response Types",
                all_answers,
                default=all_answers
            )
            df_filtered = domain_data[domain_data["answer"].isin(chosen_answers)]

            # All possible models
            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect(
                "Models",
                all_models,
                default=all_models
            )
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

        # Plot on the left
        with col_plot:
            st.subheader(f"**Domain-Level**: {final_domain}")
            if df_filtered.empty:
                st.warning("No data after these filters.")
            else:
                x_data = sorted(df_filtered["model"].unique())
                used_answers = sorted(df_filtered["answer"].unique())
                series_data = {}
                for ans in used_answers:
                    row_vals = []
                    for m in x_data:
                        sub_df = df_filtered[(df_filtered["model"] == m) & (df_filtered["answer"] == ans)]
                        row_vals.append(sub_df["percentage"].mean() if len(sub_df)>0 else 0)
                    series_data[ans] = row_vals
                option = build_echarts_bar_option(
                    x_data=x_data,
                    series_data=series_data,
                    chart_title="Response Distribution by LLMs",
                    x_label="Model",
                    y_label="Percentage"
                )
                st_echarts(options=option, height="400px")

    else:
        # =========== Country-Level logic =============
        try:
            country_data = pd.read_csv("country_level_distribution.csv")
        except FileNotFoundError:
            st.error("File 'country_level_distribution.csv' not found.")
            return

        if final_domain is None:
            with col_filters:
                domain_options = sorted(country_data["domain"].unique())
                domain_choice = st.selectbox("Pick Domain", domain_options)
            final_domain = domain_choice
        else:
            with col_filters:
                st.markdown(f"**Domain forced** by preset: {final_domain}")

        # Explanation
        if final_domain in DOMAIN_EXPLANATIONS:
            with col_filters:
                st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        # Filter by domain
        country_data = country_data[country_data["domain"] == final_domain]

        with col_filters:
            # If preset set final_actor, we override user choice
            all_actors = sorted(country_data["actor"].unique())
            if final_actor is None:
                chosen_actors = st.multiselect("Actor(s)", all_actors, default=all_actors)
            else:
                # domain forced, actor forced
                st.markdown(f"**Actor forced** by preset: {final_actor}")
                chosen_actors = [final_actor]  # override
            df_filtered = country_data[country_data["actor"].isin(chosen_actors)]

            # Next, models
            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect("Models", all_models, default=all_models[:3])
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

            # Then answers
            all_answers = sorted(df_filtered["answer"].unique())
            chosen_answers = st.multiselect("Response Types", all_answers, default=all_answers)
            df_filtered = df_filtered[df_filtered["answer"].isin(chosen_answers)]

        with col_plot:
            st.subheader(f"**Country-Level**: {final_domain}")
            if df_filtered.empty:
                st.warning("No data after these filters.")
            else:
                # Plot side-by-side columns for each model
                final_models = sorted(df_filtered["model"].unique())
                model_cols = st.columns(len(final_models))

                for i, mod in enumerate(final_models):
                    sub_df_m = df_filtered[df_filtered["model"] == mod]
                    if sub_df_m.empty:
                        with model_cols[i]:
                            st.warning(f"No data for model: {mod}")
                        continue

                    x_data = sorted(sub_df_m["actor"].unique())
                    used_answers = sorted(sub_df_m["answer"].unique())
                    series_data = {}
                    for ans in used_answers:
                        sub_df_ans = sub_df_m[sub_df_m["answer"] == ans]
                        row_vals = []
                        for act in x_data:
                            sub_df_act = sub_df_ans[sub_df_ans["actor"] == act]
                            row_vals.append(sub_df_act["percentage"].mean() if len(sub_df_act)>0 else 0)
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


if __name__ == "__main__":
    main()
