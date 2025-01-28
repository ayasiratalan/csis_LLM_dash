import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

########################
# 1) Domain Explanations
########################
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

########################
# 2) Build ECharts Stacked Bar Option with Larger Fonts
########################
def build_echarts_bar_option(
    x_data,
    series_data,
    chart_title="ECharts Bar",
    x_label="",
    y_label="Percentage"
):
    """
    Returns an 'option' dict for ECharts to create a stacked vertical bar chart 
    with larger and bold axis labels.
    - x_data: categories on the x-axis (e.g., models or actors).
    - series_data: dict { seriesName -> list of values }.
    """
    series_list = []
    for name, values in series_data.items():
        series_list.append({
            "name": name,
            "type": "bar",
            "stack": "total",       # crucial for stacking
            "data": values
        })

    option = {
        "title": {
            "text": chart_title,
            "left": "center",
            "textStyle": {
                "fontSize": 16
            }
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "textStyle": {
                "fontSize": 12
            }
        },
        "legend": {
            "top": 30,
            "textStyle": {
                "fontSize": 12,
                "fontWeight": "bold"
            }
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
            "nameTextStyle": {          # Corrected key from "TextStyle" to "nameTextStyle"
                "fontSize": 14,
                "fontWeight": "bold"    # Added to make x-axis label bold
            },
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold"
            }
        },
        "yAxis": {
            "type": "value",
            "name": y_label,
            "min": 0,
            "max": 100,
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold"    # Added to make y-axis label bold
            },
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold"
            }
        },
        "series": series_list
    }
    return option


########################
# 3) Domain-Level Dashboard
########################
def domain_dashboard():
    try:
        final_dashboard_df = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file 'final_dashboard_df.csv' not found.")
        return

    # Reverse columns so that filters are on the right and plot on the left
    col_plot, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:

                   # Domain
        domain_options = sorted(final_dashboard_df["domain"].unique())
        selected_domain = st.selectbox("Domain", domain_options, key="domain_selectbox")

        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        df_domain = final_dashboard_df[final_dashboard_df["domain"] == selected_domain]

        # Response
        all_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=all_answers,
            key="domain_answers_multiselect"
        )
        df_filtered = df_domain[df_domain["answer"].isin(selected_answers)]

        # Model
        all_models = sorted(df_filtered["model"].unique())
        selected_models = st.multiselect(
            "Models",
            all_models,
            default=all_models,
            key="domain_models_multiselect"
        )
        df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]



        if df_filtered.empty:
            st.warning("No data after filtering.")
            return

    with col_plot:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        # x_data => each model
        x_data = sorted(df_filtered["model"].unique())
        answers = sorted(df_filtered["answer"].unique())
        series_data = {}

        for ans in answers:
            row_values = []
            for mod in x_data:
                sub_df = df_filtered[(df_filtered["model"] == mod) & (df_filtered["answer"] == ans)]
                if len(sub_df) == 0:
                    row_values.append(0)
                else:
                    row_values.append(sub_df["percentage"].mean())
            series_data[ans] = row_values

        option = build_echarts_bar_option(
            x_data,
            series_data,
            chart_title="Response Distribution by LLMs",
            x_label="Model",
            y_label="Percentage"
        )

        st_echarts(options=option, height="400px")


########################
# 4) Country-Level Dashboard
########################
def country_dashboard():
    try:
        final_df = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    # Again, plot on the left, filters on the right
    col_plot, col_filters = st.columns([4, 1], gap="medium")

    with col_filters:
        domain_options = sorted(final_df["domain"].unique())
        selected_domain = st.selectbox("Domain", domain_options, key="country_selectbox")

        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        actor_options = sorted(final_df["actor"].unique())
        selected_actors = st.multiselect(
            "Actor(s)",
            actor_options,
            default=actor_options,
            key="country_actors_multiselect"
        )

        model_options = sorted(final_df["model"].unique())
        selected_models = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=model_options[:3],
            key="country_models_multiselect"
        )
        selected_models = selected_models[:3]

        df_domain = final_df[final_df["domain"] == selected_domain]
        domain_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            domain_answers,
            default=domain_answers,
            key="country_answers_multiselect"
        )

    df_filtered = final_df[
        (final_df["domain"] == selected_domain) &
        (final_df["actor"].isin(selected_actors)) &
        (final_df["model"].isin(selected_models)) &
        (final_df["answer"].isin(selected_answers))
    ].copy()

    if df_filtered.empty:
        st.warning("No data after applying filters.")
        return

    with col_plot:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        num_models = len(selected_models)
        if num_models == 0:
            st.warning("No models selected.")
            return

        model_cols = st.columns(num_models)

        for i, mod in enumerate(selected_models):
            df_model = df_filtered[df_filtered["model"] == mod]
            if df_model.empty:
                with model_cols[i]:
                    st.warning(f"No data for model: {mod}")
                continue

            # x_data => list of actors
            x_data = sorted(df_model["actor"].unique())
            answers = sorted(df_model["answer"].unique())
            series_data = {}

            for ans in answers:
                row_vals = []
                for act in x_data:
                    sub_df = df_model[(df_model["actor"] == act) & (df_model["answer"] == ans)]
                    if len(sub_df) == 0:
                        row_vals.append(0)
                    else:
                        row_vals.append(sub_df["percentage"].mean())
                series_data[ans] = row_vals

            option = build_echarts_bar_option(
                x_data,
                series_data,
                chart_title=mod,
                x_label="Actor",
                y_label="Percentage"
            )

            # Hide legend on subsequent columns for a single legend approach
            if i > 0:
                option["legend"] = {"show": False}

            with model_cols[i]:
                st_echarts(options=option, height="400px")


#######################################
# 5. Main with Preset Buttons
#######################################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    st.info("""
### Using This Dashboard
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking 
of Large Language Models’ preferences in international relations. 
We show **stacked** bars, so each category (model or actor) is a single bar subdivided 
by different response types.

**How to Use the Dashboard:**  
1. **Select Level of Analysis**: Domain-Level or Country-Level (below).  
2. **Filter**: On the right, pick domain, responses, models, etc.  
3. **View**: The left side updates with the stacked bar chart(s).
""")

    # If "analysis_choice" not in session, default "Domain-Level"
    if "analysis_choice" not in st.session_state:
        st.session_state["analysis_choice"] = "Domain-Level"

    # Local radio selection
    analysis_choice_local = st.radio(
        "Select Level of Analysis",
        ["Domain-Level", "Country-Level"],
        index=0 if st.session_state["analysis_choice"] == "Domain-Level" else 1
    )
    # If user changed it, update session
    if analysis_choice_local != st.session_state["analysis_choice"]:
        st.session_state["analysis_choice"] = analysis_choice_local

    # --- 3 columns for the 3 preset buttons ---
    col_a, col_b, col_c = st.columns(3)

    # ------------------ PRESET 1 ------------------
    with col_a:
        if st.button("Pre-set 1: Which model is most likely to recommend escalation (2-choice)?"):
            # Force domain-level
            st.session_state["analysis_choice"] = "Domain-Level"
            # Force domain = Escalation - Two Choice
            st.session_state["domain_domain_val"] = "Escalation - Two Choice"
            # Clear or keep any actor/model/answers as desired.
            # e.g. let answers & models remain whatever user had,
            # or forcibly clear them, etc. Here we do minimal.
            st.experimental_rerun()

    # ------------------ PRESET 2 ------------------
    with col_b:
        if st.button("Pre-set 2: Is China recommended escalatory responses?"):
            # Switch to Country-Level
            st.session_state["analysis_choice"] = "Country-Level"
            # Force domain = Escalation - Two Choice
            st.session_state["country_domain_val"] = "Escalation - Two Choice"
            # Force actor = ["China"]
            st.session_state["country_actors_val"] = ["China"]
            # (Optionally set models if you like, or let user pick.)
            st.experimental_rerun()

    # ------------------ PRESET 3 ------------------
    with col_c:
        if st.button("Pre-set 3: Are models more likely cooperative?"):
            # Domain-level for "Cooperation" domain
            st.session_state["analysis_choice"] = "Domain-Level"
            st.session_state["domain_domain_val"] = "Cooperation"
            st.experimental_rerun()

    # --- Display the selected dashboard ---
    if st.session_state["analysis_choice"] == "Domain-Level":
        domain_dashboard()
    else:
        country_dashboard()





