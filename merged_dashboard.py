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
    "Alliance Dynamics": """
**Alliance Dynamics:** States attempt a wide range of activities in international affairs related to alliance formation, managing their power with respect to other states, and pursuing strategic goals. This category tests for model preferences related to recommending states to pursue policies of Balancing behavior versus three alternatives commonly discussed and debated in the conventional realist international relations literature. These include: Bandwagoning, Buck Passing, and Power Maximization. As with the Cooperation domain, all scenarios have two response options.
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
            "left": "4%",      
            "right": "5%",
            "bottom": "10%",    # Increased bottom margin to accommodate rotated labels
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "name": x_label,
            "nameLocation": "middle",
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold",
                "padding": [10, 0, 0, 0]
            },
            "data": x_data,
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold",
                "rotate": 20,        # Rotate labels by 45 degrees
                "interval": 0        # Show all labels
            },
            "axisTick": {  
                "alignWithLabel": True
            }
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "nameLocation": "middle",
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold",
                "rotate": 90,
                "padding": [0, 10, 19, 0]
            },
            "position": "left",
            "min": 0,
            "max": 100,
            "scale": False,
            "boundaryGap": [0, 0],
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold",
                "formatter": "{value}%" 
            },
            "axisTick": {  
                "inside": True
            },
            "splitLine": {  
                "lineStyle": {
                    "type": "dashed",
                    "color": "#ccc"
                }
            },
            "interval": 20  
        },
        "series": series_list
    }
    
    return option


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
    # -----------------
    # 1) Preset Buttons
    # -----------------
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        preset1 = st.button("Pre-set 1: Which model is most likely to recommend escalation?")
    with col_p2:
        preset2 = st.button("Pre-set 2: Is China recommended escalatory responses?")
    with col_p3:
        preset3 = st.button("Pre-set 3: Do models offer more cooperative recommendations?")

    # Default is None unless a preset is pressed
    forced_domain = None
    forced_actor = None

    # If preset1 is clicked, set forced_domain
    if preset1:
        forced_domain = "Escalation - Two Choice"
        analysis_choice = "Domain-Level"
    elif preset2:
        forced_domain = "Escalation - Two Choice"
        forced_actor = "China"
        analysis_choice = "Country-Level"
    elif preset3:
        forced_domain = "Cooperation"
        analysis_choice = "Domain-Level"
    else:
        # If no preset clicked, let user pick the analysis type
        analysis_options = ["Domain-Level", "Country-Level"]
        analysis_choice = st.radio("Select Level of Analysis", analysis_options)

    st.write("---")

    col_plot, col_filters = st.columns([3,1], gap="medium")

    # -------------------------
    # 2) Domain-Level Analysis
    # -------------------------
    if analysis_choice == "Domain-Level":
        try:
            df_domain_all = pd.read_csv("final_dashboard_df.csv")
        except FileNotFoundError:
            st.error("Could not find 'final_dashboard_df.csv'.")
            return

        with col_filters:
            domain_options = sorted(df_domain_all["domain"].unique())
            
            # If a forced domain was set from a preset,
            # make that the DEFAULT value in the selectbox
            if forced_domain and forced_domain in domain_options:
                st.markdown(f"**Preset** selected: `{forced_domain}` (you can still override below).")
                default_index = domain_options.index(forced_domain)
            else:
                default_index = 0  # or whatever you want if forced_domain not valid
                
            domain_choice = st.selectbox(
                "Pick Domain", 
                domain_options, 
                index=default_index
            )

        with col_plot:
            # Always show an explanation for the chosen domain
            st.subheader(f"**Domain-Level**: {domain_choice}")
            explanation_text = DOMAIN_EXPLANATIONS.get(
                domain_choice, 
                "_No explanation available for this domain (check spelling!)._"
            )
            st.markdown(explanation_text)

        # Additional filtering
        domain_data = df_domain_all[df_domain_all["domain"] == domain_choice]
        with col_filters:
            all_answers = sorted(domain_data["answer"].unique())
            chosen_answers = st.multiselect(
                "Response Types",
                all_answers,
                default=all_answers
            )
            df_filtered = domain_data[domain_data["answer"].isin(chosen_answers)]

            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect(
                "Models",
                all_models,
                default=all_models
            )
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

        # Plot
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
                        sub_df = df_filtered[
                            (df_filtered["model"] == m) & 
                            (df_filtered["answer"] == ans)
                        ]
                        # take mean or 0 if no row
                        row_vals.append(
                            sub_df["percentage"].mean() if not sub_df.empty else 0
                        )
                    series_data[ans] = row_vals

                option = build_echarts_bar_option(
                    x_data=x_data,
                    series_data=series_data,
                    chart_title="Response Distribution by LLMs",
                    x_label="Model",
                    y_label="Percentage"
                )
                st_echarts(options=option, height="400px")

    # --------------------------
    # 3) Country-Level Analysis
    # --------------------------
    else:
        try:
            df_country_all = pd.read_csv("country_level_distribution.csv")
        except FileNotFoundError:
            st.error("Could not find 'country_level_distribution.csv'.")
            return

        with col_filters:
            domain_options = sorted(df_country_all["domain"].unique())
            
            if forced_domain and forced_domain in domain_options:
                st.markdown(f"**Preset** selected: `{forced_domain}` (you can still override below).")
                default_index = domain_options.index(forced_domain)
            else:
                default_index = 0

            domain_choice = st.selectbox("Pick Domain", domain_options, index=default_index)

        with col_plot:
            st.subheader(f"**Country-Level**: {domain_choice}")
            explanation_text = DOMAIN_EXPLANATIONS.get(
                domain_choice, 
                "_No explanation available for this domain (check spelling!)._"
            )
            st.markdown(explanation_text)

        cdf = df_country_all[df_country_all["domain"] == domain_choice]

        with col_filters:
            all_actors = sorted(cdf["actor"].unique())
            # If forced_actor from a preset
            if forced_actor and forced_actor in all_actors:
                st.markdown(f"**Preset** selected: `{forced_actor}` (you can still override below).")
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

            all_models = sorted(df_filtered["model"].unique())
            chosen_models = st.multiselect(
                "Models",
                all_models,
                default=all_models[:3]
            )
            df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

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
                model_cols = st.columns(len(final_models)) if final_models else []
                
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
                            row_vals.append(sub_df_act["percentage"].mean() if not sub_df_act.empty else 0)
                        series_data[ans] = row_vals

                    option = build_echarts_bar_option(
                        x_data=x_data,
                        series_data=series_data,
                        chart_title=mod,
                        x_label="Actor",
                        y_label="Percentage"
                    )
                    # Hide legend after the first plot if you want
                    if i > 0:
                        option["legend"] = {"show": False}
                    
                    with model_cols[i]:
                        st_echarts(options=option, height="400px")

if __name__ == "__main__":
    main()
