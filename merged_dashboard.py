import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

# ---------------------------------------------------
# 1. Domain explanations
# ---------------------------------------------------
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation - Three Choice:** This domain focuses on scenarios in which states are offered options to escalate disputes or not. Escalation here signifies an increased conflict intensity typically related to the means used to pursue a particular goal. These scenarios include escalatory behavior in the context of four action categories: Attack, Blockade, Clash, and Declare War. This domain features three response scenarios. Three response scenarios have escalatory and non-escalatory response options as well as a middle response option which includes threats of force or a show of force. Actions above the threshold of use of force are always coded as the most escalatory in scenarios.
""",
    "Escalation - Two Choice": """
**Escalation - Two Choice:** This domain focuses on scenarios in which states are offered options to escalate disputes or not. Escalation here signifies an increased conflict intensity typically related to the means used to pursue a particular goal. These scenarios include escalatory behavior in the context of four action categories: Attack, Blockade, Clash, and Declare War. This domain features two response scenarios. Two response scenarios have escalatory and non-escalatory response options. Actions above the threshold of use of force are always coded as the most escalatory in scenarios.
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


# ---------------------------------------------------
# 2. Utility: Build ECharts option for a simple bar chart
# ---------------------------------------------------
def build_echarts_bar_option(
    x_data,      # list of x-axis categories (e.g. models or actors)
    series_data, # dict { series_name -> list of values in x_data order }
    chart_title="ECharts Bar",
    x_label="",
    y_label="Percentage"
):
    """
    Returns an 'option' dict for ECharts to create a vertical bar chart with
    multiple series. Each series_name in series_data is displayed as a separate
    color-coded bar category. x_data is the list of categories on the x-axis.
    series_data is a dict mapping from e.g. 'answer' to a list of numeric values
    that align with x_data.

    Example:
      x_data = ["GPT-4o", "Claude 3.5 Sonnet", "Llama 3.1 70B Instruct"]
      series_data = {
         "Use of Force": [50, 40, 60],
         "No Use of Force": [50, 60, 40]
      }
    """
    # Convert into series for echarts
    # Each key in series_data is a 'series' in the bar chart
    series_list = []
    for name, values in series_data.items():
        series_list.append({
            "name": name,
            "type": "bar",
            "data": values
        })

    option = {
        "title": {
            "text": chart_title,
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "legend": {
            "top": 30  # place legend below title
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
            "data": x_data
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "min": 0,
            "max": 100
        },
        "series": series_list
    }
    return option


# ---------------------------------------------------
# 3) DOMAIN DASHBOARD
# ---------------------------------------------------
def domain_dashboard():
    try:
        final_dashboard_df = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file 'final_dashboard_df.csv' not found.")
        return

    col_main, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:
        # 1. Domain selection
        domain_options = sorted(final_dashboard_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=0,
            key="domain_selectbox_dashboard"
        )

        # 2. Explanation
        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # 3. Filter by domain
        df_domain = final_dashboard_df[final_dashboard_df["domain"] == selected_domain]
        # 4. Response filter
        all_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=all_answers,
            key="domain_answers_multiselect"
        )
        df_filtered = df_domain[df_domain["answer"].isin(selected_answers)]

        # 5. Model filter
        all_models = sorted(df_filtered["model"].unique())
        selected_models = st.multiselect(
            "Models",
            all_models,
            default=all_models,
            key="domain_models_multiselect"
        )
        df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]

        if df_filtered.empty:
            st.warning("No data after filtering by model(s) and response(s).")
            return

    # Build the ECharts bar data
    st.subheader(f"Distribution of Responses for {selected_domain}")

    # x_data = list of models in the final filtered data
    x_data = sorted(df_filtered["model"].unique())

    # We group by 'answer' to produce multiple series
    # For each answer, we want a list of percentages in x_data order
    answers = sorted(df_filtered["answer"].unique())

    # Construct series_data
    series_data = {}
    for ans in answers:
        # For each model in x_data
        # We'll find the average or sum of percentages?
        # Typically we have direct "percentage" row for each (model, answer).
        # We'll do a quick approach: df_filtered might have multiple rows for the same (model,answer)
        # We'll just take the mean. Or if your data only has one row per combo, you can just take .iloc[0].
        row_values = []
        for mod in x_data:
            sub_df = df_filtered[(df_filtered["model"] == mod) & (df_filtered["answer"] == ans)]
            if len(sub_df) == 0:
                row_values.append(0)
            else:
                row_values.append(sub_df["percentage"].mean())  # or sum
        series_data[ans] = row_values

    # Build ECharts 'option'
    option = build_echarts_bar_option(
        x_data=x_data,
        series_data=series_data,
        chart_title="Response Distribution by LLMs",
        x_label="Model",
        y_label="Percentage"
    )

    # Render ECharts in col_main
    from streamlit_echarts import st_echarts
    st_echarts(options=option, height="400px")


# ---------------------------------------------------
# 4) COUNTRY DASHBOARD
# ---------------------------------------------------
def country_dashboard():
    try:
        final_df = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    col_main, col_filters = st.columns([4, 1], gap="medium")

    with col_filters:
        # Domain
        domain_options = sorted(final_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            key="country_selectbox_dashboard"
        )

        # Explanation
        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # Actors
        actor_options = sorted(final_df["actor"].unique())
        selected_actors = st.multiselect(
            "Actor(s)",
            actor_options,
            default=actor_options,
            key="country_actors_multiselect"
        )

        # Models (max 3)
        model_options = sorted(final_df["model"].unique())
        selected_models = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=model_options[:3],
            key="country_models_multiselect"
        )
        selected_models = selected_models[:3]

        # Answers: domain-based
        df_domain = final_df[final_df["domain"] == selected_domain]
        domain_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            domain_answers,
            default=domain_answers,
            key="country_answers_multiselect"
        )

    # Filter
    df_filtered = final_df[
        (final_df["domain"] == selected_domain) &
        (final_df["actor"].isin(selected_actors)) &
        (final_df["model"].isin(selected_models)) &
        (final_df["answer"].isin(selected_answers))
    ].copy()

    if df_filtered.empty:
        st.warning("No data after applying filters.")
        return

    st.subheader(f"Distribution of Responses for {selected_domain}")

    # Build side-by-side columns
    num_models = len(selected_models)
    if num_models == 0:
        st.warning("No models selected.")
        return

    model_cols = st.columns(num_models)

    # We'll create a separate ECharts chart for each model
    for i, mod in enumerate(selected_models):
        df_model = df_filtered[df_filtered["model"] == mod]
        if df_model.empty:
            with model_cols[i]:
                st.warning(f"No data for model: {mod}")
            continue

        # x_data = list of actors
        x_data = sorted(df_model["actor"].unique())
        # series_data = { answer -> [list of percentages for each actor in x_data order] }
        answers = sorted(df_model["answer"].unique())
        series_data = {}
        for ans in answers:
            row_values = []
            for act in x_data:
                sub_df = df_model[(df_model["actor"] == act) & (df_model["answer"] == ans)]
                if len(sub_df) == 0:
                    row_values.append(0)
                else:
                    row_values.append(sub_df["percentage"].mean())
            series_data[ans] = row_values

        # Build ECharts option
        option = build_echarts_bar_option(
            x_data=x_data,
            series_data=series_data,
            chart_title=mod,   # just the model name
            x_label="Actor",
            y_label="Percentage"
        )

        # If we want to show a single legend only on the first plot:
        # We'll remove the legend from subsequent plots. We can do so by modifying 'option'
        if i > 0:
            option["legend"] = {"show": False}
            option["title"]["left"] = "center"

        # Render
        with model_cols[i]:
            st_echarts(options=option, height="400px")


# ---------------------------------------------------
# 5) MAIN
# ---------------------------------------------------
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    # Instruction Box
    st.info("""
### Using This Dashboard
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking 
of Large Language Models’ preferences in international relations. 
The evaluation spans four key domains including – **Escalation, Intervention, Cooperation, 
and Alliance Dynamics** – across an initial seven foundation models: **Llama 3.1 8B Instruct, 
Llama 3.1 70B Instruct, GPT-4o, Gemini 1.5 Pro-002, Mistral 8x22B, Claude 3.5 Sonnet, 
and Qwen2 72B.**

**How to Use the Dashboard:**
1. **Select Level of Analysis**: Choose between Domain-Level or Country-Level variation (below).
2. **Filter Results**: On the right, pick the domain, model, country (if applicable), 
   and response types of interest.
3. **View Results**: The dashboard automatically updates, showing each domain’s scenario distribution 
   of model recommendations.
""")

    # Instead of tabs, let's do a radio for domain-level or country-level
    choice = st.radio(
        "Select Level of Analysis",
        ["Domain-Level", "Country-Level"],
        key="analysis_choice"
    )

    if choice == "Domain-Level":
        domain_dashboard()
    else:
        country_dashboard()


if __name__ == "__main__":
    main()
