import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

########################
# 1) Domain Explanations
########################
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation - Three Choice:** This domain focuses on scenarios...
""",
    "Escalation - Two Choice": """
**Escalation - Two Choice:** This domain focuses on scenarios...
""", 
    "Intervention - Two Choice": """
**Intervention:** The Intervention domain tests model preferences...
""",
    "Intervention - Three Choice": """
**Intervention:** The Intervention domain tests model preferences...
""",
    "Cooperation": """
**Cooperation:** Questions in this domain investigate model preferences...
""",
    "Alliance Dynamics": """
**Alliance Dynamics:** States attempt a wide range of activities...
"""
}

########################
# 2) Build ECharts Stacked Bar
########################
def build_echarts_bar_option(
    x_data,
    series_data,
    chart_title="ECharts Bar",
    x_label="",
    y_label="Percentage"
):
    """
    Returns an ECharts 'option' dict for a stacked vertical bar chart 
    with larger and bold axis labels.
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

########################
# 3) Domain-Level Dashboard
########################
def domain_dashboard():
    """
    Renders the domain-level dashboard on the left, with filters on the right.
    Resets the answers/models to all possible whenever a different domain is chosen.
    """
    try:
        df_domain_all = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file 'final_dashboard_df.csv' not found.")
        return

    col_plot, col_filters = st.columns([3,1], gap="medium")

    with col_filters:
        domain_options = sorted(df_domain_all["domain"].unique())

        # If we haven't stored the domain-level choice, init to first
        if "domain_select_val" not in st.session_state:
            st.session_state["domain_select_val"] = domain_options[0]

        old_domain = st.session_state["domain_select_val"]  # store the old domain
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=domain_options.index(old_domain) if old_domain in domain_options else 0
        )
        st.session_state["domain_select_val"] = selected_domain

        # If domain changed, reset answers/models to all for the new domain
        if selected_domain != old_domain:
            new_df = df_domain_all[df_domain_all["domain"] == selected_domain]
            all_answers = sorted(new_df["answer"].unique())
            all_models = sorted(new_df["model"].unique())

            st.session_state["domain_answers_val"] = all_answers  # store all
            st.session_state["domain_models_val"] = all_models    # store all

        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # Now filter the big DF to just that domain
        df_domain = df_domain_all[df_domain_all["domain"] == selected_domain]

        # All possible answers
        domain_answers_options = sorted(df_domain["answer"].unique())
        # If not stored, init
        if "domain_answers_val" not in st.session_state:
            st.session_state["domain_answers_val"] = domain_answers_options

        # Show the multiselect with defaults = session answers
        selected_answers = st.multiselect(
            "Response Types",
            domain_answers_options,
            default=st.session_state["domain_answers_val"]
        )
        # Update session
        st.session_state["domain_answers_val"] = selected_answers

        # Filter by chosen answers
        df_filtered = df_domain[df_domain["answer"].isin(selected_answers)]

        # Models
        domain_models_options = sorted(df_filtered["model"].unique())
        if "domain_models_val" not in st.session_state:
            st.session_state["domain_models_val"] = domain_models_options

        chosen_models = st.multiselect(
            "Models",
            domain_models_options,
            default=st.session_state["domain_models_val"]
        )
        st.session_state["domain_models_val"] = chosen_models

        df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]
        if df_filtered.empty:
            st.warning("No data after filtering.")
            return

    # Plot
    with col_plot:
        st.subheader(f"Distribution of Responses for {selected_domain}")
        x_data = sorted(df_filtered["model"].unique())
        answers = sorted(df_filtered["answer"].unique())

        series_data = {}
        for ans in answers:
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

########################
# 4) Country-Level Dashboard
########################
def country_dashboard():
    """
    Similar logic for country-level. If domain changes, reset actors, models, answers to 'all' for that domain.
    """
    try:
        df_country_all = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    col_plot, col_filters = st.columns([4,1], gap="medium")

    with col_filters:
        domain_options = sorted(df_country_all["domain"].unique())
        if "country_domain_val" not in st.session_state:
            st.session_state["country_domain_val"] = domain_options[0]

        old_domain = st.session_state["country_domain_val"]
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=domain_options.index(old_domain) if old_domain in domain_options else 0
        )
        st.session_state["country_domain_val"] = selected_domain

        # If domain changed, reset everything to 'all' for the new domain
        if selected_domain != old_domain:
            new_df = df_country_all[df_country_all["domain"] == selected_domain]
            st.session_state["country_actors_val"]  = sorted(new_df["actor"].unique())
            st.session_state["country_models_val"]  = sorted(new_df["model"].unique())
            st.session_state["country_answers_val"] = sorted(new_df["answer"].unique())

        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # Now filter big DF
        df_domain = df_country_all[df_country_all["domain"] == selected_domain]

        # Actors
        domain_actor_options = sorted(df_domain["actor"].unique())
        if "country_actors_val" not in st.session_state:
            st.session_state["country_actors_val"] = domain_actor_options
        chosen_actors = st.multiselect(
            "Actor(s)",
            domain_actor_options,
            default=st.session_state["country_actors_val"]
        )
        st.session_state["country_actors_val"] = chosen_actors

        # Models
        domain_models_options = sorted(df_domain["model"].unique())
        if "country_models_val" not in st.session_state:
            st.session_state["country_models_val"] = domain_models_options[:3]
        chosen_models = st.multiselect(
            "Model(s) (max 3)",
            domain_models_options,
            default=st.session_state["country_models_val"]
        )[:3]
        st.session_state["country_models_val"] = chosen_models

        # Answers
        domain_answers_options = sorted(df_domain["answer"].unique())
        if "country_answers_val" not in st.session_state:
            st.session_state["country_answers_val"] = domain_answers_options
        chosen_answers = st.multiselect(
            "Response Types",
            domain_answers_options,
            default=st.session_state["country_answers_val"]
        )
        st.session_state["country_answers_val"] = chosen_answers

    # Filter
    df_filtered = df_country_all[
        (df_country_all["domain"] == selected_domain) &
        (df_country_all["actor"].isin(st.session_state["country_actors_val"])) &
        (df_country_all["model"].isin(st.session_state["country_models_val"])) &
        (df_country_all["answer"].isin(st.session_state["country_answers_val"]))
    ].copy()

    if df_filtered.empty:
        st.warning("No data after applying filters.")
        return

    with col_plot:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        num_models = len(st.session_state["country_models_val"])
        if num_models == 0:
            st.warning("No models selected.")
            return

        model_cols = st.columns(num_models)
        for i, mod in enumerate(st.session_state["country_models_val"]):
            df_model = df_filtered[df_filtered["model"] == mod]
            if df_model.empty:
                with model_cols[i]:
                    st.warning(f"No data for model: {mod}")
                continue

            x_data = sorted(df_model["actor"].unique())
            answers = sorted(df_model["answer"].unique())
            series_data = {}
            for ans in answers:
                sub_actors = df_model[df_model["answer"] == ans]
                row_vals = []
                for act in x_data:
                    sub_df = sub_actors[sub_actors["actor"] == act]
                    row_vals.append(sub_df["percentage"].mean() if len(sub_df)>0 else 0)
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

    # By default, domain-level if not in session
    if "analysis_choice" not in st.session_state:
        st.session_state["analysis_choice"] = "Domain-Level"

    # local radio
    analysis_choice_local = st.radio(
        "Select Level of Analysis",
        ["Domain-Level", "Country-Level"],
        index=0 if st.session_state["analysis_choice"] == "Domain-Level" else 1
    )
    if analysis_choice_local != st.session_state["analysis_choice"]:
        st.session_state["analysis_choice"] = analysis_choice_local

    # 3 columns for 3 preset buttons
    col_a, col_b, col_c = st.columns(3)

    # -- Preset 1: Domain-Level => Escalation - Two Choice
    with col_a:
        if st.button("Pre-set 1: Escalation (2 Choice)"):
            st.session_state["analysis_choice"] = "Domain-Level"
            st.session_state["domain_select_val"] = "Escalation - Two Choice"
            # We'll reset domain-level answers & models next run
            st.experimental_rerun()

    # -- Preset 2: Country-Level => Escalation - Two Choice, Actor=China
    with col_b:
        if st.button("Pre-set 2: China Escalation (2 Choice)"):
            st.session_state["analysis_choice"] = "Country-Level"
            st.session_state["country_domain_val"] = "Escalation - Two Choice"
            st.session_state["country_actors_val"] = ["China"]
            st.experimental_rerun()

    # -- Preset 3: Domain-Level => Cooperation
    with col_c:
        if st.button("Pre-set 3: Cooperation"):
            st.session_state["analysis_choice"] = "Domain-Level"
            st.session_state["domain_select_val"] = "Cooperation"
            st.experimental_rerun()

    # Show chosen dashboard
    if st.session_state["analysis_choice"] == "Domain-Level":
        domain_dashboard()
    else:
        country_dashboard()


if __name__ == "__main__":
    main()
