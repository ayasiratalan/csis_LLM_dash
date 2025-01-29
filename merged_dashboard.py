import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

###############################################################################
# 1) Domain Explanations
###############################################################################
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

###############################################################################
# 2) Build ECharts Bar Option
###############################################################################
def build_echarts_bar_option(x_data, series_data,
                             chart_title="ECharts Bar",
                             x_label="", y_label="Percentage"):
    """Returns an ECharts 'option' dict for a stacked vertical bar chart."""
    
    # Construct the series list for ECharts
    series_list = []
    for name, values in series_data.items():
        series_list.append({
            "name": name,
            "type": "bar",
            "stack": "total",
            "data": values
        })

    # Define the ECharts option dictionary
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
            "left": "15%",      # Increased left margin for y-axis label
            "right": "5%",
            "bottom": "20%",    # Increased bottom margin for x-axis label
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "name": x_label,
            "nameLocation": "middle",  # Centers the x-axis label
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold",
                "padding": [10, 0, 0, 0]  # Adds space above the x-axis label
            },
            "data": x_data,
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold",
                "rotate": 0  # Keeps x-axis labels horizontal; adjust if needed
            }
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "nameLocation": "middle",  # Centers the y-axis label vertically
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold",
                "rotate": 90,  # Rotates y-axis label for vertical alignment
                "padding": [0, 10, 0, 0]  # Adds space to the right of y-axis label
            },
            "position": "left",  # Ensures y-axis is on the left
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold"
            }
        },
        "series": series_list
    }
    
    return option



###############################################################################
# 3) MAIN
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    st.info("""
**How to Use**  
- Choose Domain-Level or Country-Level below.  
- Optional: click a preset button to force a domain (and actor in preset 2).  
- Then pick your final domain, actor, or filters in the UI to override if desired.  
- The final chart is determined by whichever domain/actor you set *last*.
""")

    # Step A: Choose analysis (Domain or Country)
    analysis_options = ["Domain-Level", "Country-Level"]
    analysis_choice = st.radio("Select Level of Analysis", analysis_options)

    # Step B: Three Preset Buttons
    # We store them in local booleans if pressed
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        preset1 = st.button("Preset 1: Escalation - Two Choice")
    with col_p2:
        preset2 = st.button("Preset 2: China Escalation - Two Choice")
    with col_p3:
        preset3 = st.button("Preset 3: Cooperation")

    # local variables to store forced domain / actor from presets
    forced_domain = None
    forced_actor  = None

    if preset1:
        forced_domain = "Escalation - Two Choice"
        analysis_choice = "Domain-Level"  # override
    if preset2:
        forced_domain = "Escalation - Two Choice"
        forced_actor  = "China"
        analysis_choice = "Country-Level"
    if preset3:
        forced_domain = "Cooperation"
        analysis_choice = "Domain-Level"

    st.write("---")

    # Step C: We put domain selection on the right, final plotting on the left
    col_plot, col_filters = st.columns([3,1], gap="medium")

    # ....................
    # If Domain-Level
    if analysis_choice == "Domain-Level":
        # Attempt to load domain-level CSV
        try:
            df_domain_all = pd.read_csv("final_dashboard_df.csv")
        except FileNotFoundError:
            st.error("Could not find 'final_dashboard_df.csv'.")
            return

        # Step 1: The user can pick domain. If we have forced_domain from a preset, 
        # we show a note and let them override in the same run if they want.
        with col_filters:
            domain_options = sorted(df_domain_all["domain"].unique())
            if forced_domain is not None:
                st.markdown(f"**Preset** forced domain = `{forced_domain}`. (You may override below.)")
                if forced_domain not in domain_options:
                    # If forced domain isn't in domain_options, just append or fallback
                    domain_options = [forced_domain] + domain_options
                domain_choice = st.selectbox(
                    "Pick Domain",
                    domain_options,
                    index=domain_options.index(forced_domain) if forced_domain in domain_options else 0
                )
            else:
                domain_choice = st.selectbox("Pick Domain", domain_options)

        # Step 2: domain_data => filter
        domain_data = df_domain_all[df_domain_all["domain"] == domain_choice]

        # Step 3: Explanation
        with col_plot:
            st.subheader(f"**Domain-Level**: {domain_choice}")
            if domain_choice in DOMAIN_EXPLANATIONS:
                st.markdown(DOMAIN_EXPLANATIONS[domain_choice])

        # Step 4: Now we do final filters for answers, models on the right, 
        # and plot on the left. We'll do it in the same columns but user can choose 
        # after the domain is selected or overridden.
        with col_filters:
            # All possible answers
            all_answers = sorted(domain_data["answer"].unique())
            chosen_answers = st.multiselect(
                "Response Types",
                all_answers,
                default=all_answers
            )
            df_filtered = domain_data[domain_data["answer"].isin(chosen_answers)]

            # Models
            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect(
                "Models",
                all_models,
                default=all_models
            )
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

        # Plot on col_plot
        with col_plot:
            if df_filtered.empty:
                st.warning("No data after filtering.")
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


    # ....................
    # If Country-Level
    else:
        try:
            df_country_all = pd.read_csv("country_level_distribution.csv")
        except FileNotFoundError:
            st.error("Could not find 'country_level_distribution.csv'.")
            return

        # Domain
        with col_filters:
            domain_options = sorted(df_country_all["domain"].unique())
            if forced_domain is not None:
                st.markdown(f"**Preset** forced domain = `{forced_domain}`. (You may override below.)")
                if forced_domain not in domain_options:
                    domain_options = [forced_domain] + domain_options
                domain_choice = st.selectbox(
                    "Pick Domain",
                    domain_options,
                    index=domain_options.index(forced_domain) if forced_domain in domain_options else 0
                )
            else:
                domain_choice = st.selectbox("Pick Domain", domain_options)

        cdf = df_country_all[df_country_all["domain"] == domain_choice]

        # Explanation
        with col_plot:
            st.subheader(f"**Country-Level**: {domain_choice}")
            if domain_choice in DOMAIN_EXPLANATIONS:
                st.markdown(DOMAIN_EXPLANATIONS[domain_choice])

        # Now let user pick actor, models, answers
        with col_filters:
            all_actors = sorted(cdf["actor"].unique())
            # If forced_actor from preset, we do note & let user override
            if forced_actor is not None and forced_actor in all_actors:
                st.markdown(f"**Preset** forced actor = `{forced_actor}`. (You may override below.)")
                # We'll put forced_actor as default in the multiselect
                if forced_actor not in all_actors:
                    all_actors = [forced_actor] + all_actors
                chosen_actors = st.multiselect(
                    "Actor(s)",
                    all_actors,
                    default=[forced_actor] 
                )
            else:
                chosen_actors = st.multiselect(
                    "Actor(s)",
                    all_actors,
                    default=all_actors
                )
            df_filtered = cdf[cdf["actor"].isin(chosen_actors)]

            # Models
            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect(
                "Models",
                all_models,
                default=all_models[:3]
            )
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

            # Answers
            all_answers = sorted(df_filtered["answer"].unique())
            chosen_answers = st.multiselect(
                "Response Types",
                all_answers,
                default=all_answers
            )
            df_filtered = df_filtered[df_filtered["answer"].isin(chosen_answers)]

        with col_plot:
            if df_filtered.empty:
                st.warning("No data after filtering.")
            else:
                final_models = sorted(df_filtered["model"].unique())
                if len(final_models) == 0:
                    st.warning("No models found.")
                else:
                    model_cols = st.columns(len(final_models))
                    for i, mod in enumerate(final_models):
                        df_mod = df_filtered[df_filtered["model"] == mod]
                        if df_mod.empty:
                            with model_cols[i]:
                                st.warning(f"No data for model: {mod}")
                            continue
                        x_data = sorted(df_mod["actor"].unique())
                        used_answers = sorted(df_mod["answer"].unique())
                        series_data = {}
                        for ans in used_answers:
                            sub_df_ans = df_mod[df_mod["answer"] == ans]
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
