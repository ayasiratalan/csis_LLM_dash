import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

###############################################################################
# 1) Domain Explanations
###############################################################################
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation:** This domain focuses on scenarios in which states are offered options to escalate disputes or not. Escalation here signifies an increased conflict intensity typically related to the means used to pursue a particular goal. These scenarios include escalatory behavior in the context of four action categories: Attack, Blockade, Clash, and Declare War. This domain features three response scenarios. Three response scenarios have escalatory and non-escalatory response options as well as a middle response option which includes threats of force or a show of force. Actions above the threshold of use of force are always coded as the most escalatory in scenarios.
""",
    "Escalation - Two Choice": """
**Escalation:** This domain focuses on scenarios in which states are offered options to escalate disputes or not. Escalation here signifies an increased conflict intensity typically related to the means used to pursue a particular goal. These scenarios include escalatory behavior in the context of four action categories: Attack, Blockade, Clash, and Declare War. This domain features two response scenarios. Two response scenarios have escalatory and non-escalatory response options. Actions above the threshold of use of force are always coded as the most escalatory in scenarios.
""", 
    "Intervention - Two Choice": """
**Intervention:** The Intervention domain tests model preferences to recommend states to intervene in external events. We are not using the specified language of ‘intervention’ that can have precise correspondence to military action or the violation of sovereign territory in some of the scholarly literature. While we do explore such cases, we take a broader view of intervention and treat it as a willingness of states to deploy resources to respond to the scenario delineated in the question. Scenarios in this domain feature two response options. Two response scenarios give models options of not intervening at all and taking substantive action to shape the external event.
""",
    "Intervention - Three Choice": """
**Intervention:** The Intervention domain tests model preferences to recommend states to intervene in external events. We are not using the specified language of ‘intervention’ that can have precise correspondence to military action or the violation of sovereign territory in some of the scholarly literature. While we do explore such cases, we take a broader view of intervention and treat it as a willingness of states to deploy resources to respond to the scenario delineated in the question. Scenarios in this domain feature three response options. Three response scenarios give models a middle option between not intervening at all and taking substantive action to shape the external event.
""",
    "Cooperation": """
**Cooperation:** Questions in this domain investigate model preferences for cooperation vs go-it-alone strategies. The extent to which international cooperation, in a range of policy contexts, is durable and meaningfully shapes international politics serves as an important, long-term, focal point in the field of international relations. Scenarios in this domain test model preferences for joining bilateral/multilateral agreements, violating agreements, and enforcing agreements. All scenarios in this domain have two response options, one is cooperative and the other non-cooperative.
""",
    "Balancing": """
**Balancing:** States attempt a wide range of activities in international affairs related to alliance formation, managing their power with respect to other states, and pursuing strategic goals. This category tests for model preferences related to recommending states to pursue policies of Balancing behavior versus three alternatives commonly discussed and debated in the conventional realist international relations literature. These include: Bandwagoning, Buck Passing, and Power Maximization. As with the Cooperation domain, all scenarios have two response options.
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
            "bottom": 20,  # Moved legend to the bottom
            "orient": "horizontal",
            "textStyle": {"fontSize": 12, "fontWeight": "bold"},
            "itemWidth": 20,
            "itemHeight": 14
        },
        "grid": {
            "left": "4%",      # Increased left margin to prevent y-axis overlap
            "right": "5%",
            "bottom": "30%",    # Further increased bottom margin to accommodate x-axis label and legend
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
            },
            "axisTick": {  # Adjust axis ticks to prevent overlap
                "alignWithLabel": True
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
                "padding": [0, 10, 19, 0]  # Adds space to the right of y-axis label
            },
            "position": "left",  # Ensures y-axis is on the left
            "min": 0,            # Set y-axis minimum
            "max": 100,          # Set y-axis maximum
            "scale": False,     # Disable automatic scaling
            "boundaryGap": [0, 0],  # Ensures the axis starts and ends at exact min and max
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold",
                "formatter": "{value}%"  # Appends percentage symbol
            },
            "axisTick": {  # Ensure ticks are inside the grid to prevent overlap
                "inside": True
            },
            "splitLine": {  # Optionally, style the grid lines
                "lineStyle": {
                    "type": "dashed",
                    "color": "#ccc"
                }
            },
            "interval": 20  # Set tick intervals to 20
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
### Using This Dashboard  
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking of Large Language Models’ preferences in international relations. 
The evaluation spans four key domains including – *Escalation, Intervention, Cooperation, and Alliance Dynamics* – 
across an initial seven foundation models: *Llama 3.1 8B Instruct, Llama 3.1 70B Instruct, GPT-4o, Gemini 1.5 Pro-002, Mistral 8x22B, Claude 3.5 Sonnet, and Qwen2 72B.*  

**How to Use the Dashboard:**  
1. **Select Level of Analysis**: Choose between Domain-Level or Country-Level variation (below).  
2. **Filter Results**: On the right of the screen, pick the domain, model, country (if applicable) and response types of interest.  
3. **View Results**: The dashboard will automatically update, displaying the percentage of model recommendations for each domain’s scenarios.


**Presets:**

You may choose the 3 presets below that produces example plots for the relevant question.
"""
)

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
                st.markdown(f"**Preset**= `{forced_domain}`. (You may change below.)")
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
                st.markdown(f"**Preset**= `{forced_actor}`. (You may change below.)")
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
                    default=all_actors[:5]
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
