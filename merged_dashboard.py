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
# 2) Build ECharts Stacked Bar Option with Larger Fonts
########################
def build_echarts_bar_option(
    x_data,
    series_data,
    chart_title="ECharts Bar",
    x_label="",
    y_label="Percentage"
):
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
# 3) Domain-Level Dashboard (with intersection fix)
########################
def domain_dashboard():
    try:
        final_dashboard_df = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file 'final_dashboard_df.csv' not found.")
        return

    # Plot (left), Filters (right)
    col_plot, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:
        # Domain
        domain_options = sorted(final_dashboard_df["domain"].unique())
        if "domain_select_val" not in st.session_state:
            st.session_state["domain_select_val"] = domain_options[0]

        # The user’s actual pick:
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=domain_options.index(st.session_state["domain_select_val"])
              if st.session_state["domain_select_val"] in domain_options else 0
        )
        st.session_state["domain_select_val"] = selected_domain

        # Explanation
        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        df_domain = final_dashboard_df[final_dashboard_df["domain"] == selected_domain]

        # Response
        all_answers = sorted(df_domain["answer"].unique())
        if "domain_answers_val" not in st.session_state:
            st.session_state["domain_answers_val"] = all_answers

        # Intersect to avoid "value not in options" error
        valid_answers = list(set(st.session_state["domain_answers_val"]).intersection(all_answers))
        selected_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=valid_answers
        )
        st.session_state["domain_answers_val"] = selected_answers

        df_filtered = df_domain[df_domain["answer"].isin(selected_answers)]

        # Model
        all_models = sorted(df_filtered["model"].unique())
        if "domain_models_val" not in st.session_state:
            st.session_state["domain_models_val"] = all_models

        valid_models = list(set(st.session_state["domain_models_val"]).intersection(all_models))
        selected_models = st.multiselect(
            "Models",
            all_models,
            default=valid_models
        )
        st.session_state["domain_models_val"] = selected_models

        df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]

        if df_filtered.empty:
            st.warning("No data after filtering.")
            return

    with col_plot:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        x_data = sorted(df_filtered["model"].unique())
        answers = sorted(df_filtered["answer"].unique())
        series_data = {}
        for ans in answers:
            row_values = []
            for mod in x_data:
                sub_df = df_filtered[(df_filtered["model"] == mod) & (df_filtered["answer"] == ans)]
                row_values.append(sub_df["percentage"].mean() if len(sub_df)>0 else 0)
            series_data[ans] = row_values

        option = build_echarts_bar_option(
            x_data=x_data,
            series_data=series_data,
            chart_title="Response Distribution by LLMs",
            x_label="Model",
            y_label="Percentage"
        )
        st_echarts(options=option, height="400px")

########################
# 4) Country-Level Dashboard (with intersection fix)
########################
def country_dashboard():
    try:
        final_df = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    col_plot, col_filters = st.columns([4,1], gap="medium")

    with col_filters:
        # Domain
        domain_options = sorted(final_df["domain"].unique())
        if "country_domain_val" not in st.session_state:
            st.session_state["country_domain_val"] = domain_options[0]

        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=domain_options.index(st.session_state["country_domain_val"])
              if st.session_state["country_domain_val"] in domain_options else 0
        )
        st.session_state["country_domain_val"] = selected_domain

        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        df_domain = final_df[final_df["domain"] == selected_domain]

        # Actors
        actor_options = sorted(df_domain["actor"].unique())
        if "country_actors_val" not in st.session_state:
            st.session_state["country_actors_val"] = actor_options
        valid_actors = list(set(st.session_state["country_actors_val"]).intersection(actor_options))
        selected_actors = st.multiselect(
            "Actor(s)",
            actor_options,
            default=valid_actors
        )
        st.session_state["country_actors_val"] = selected_actors

        # Models
        model_options = sorted(df_domain["model"].unique())
        if "country_models_val" not in st.session_state:
            st.session_state["country_models_val"] = model_options[:3]
        valid_models = list(set(st.session_state["country_models_val"]).intersection(model_options))
        selected_models = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=valid_models
        )[:3]
        st.session_state["country_models_val"] = selected_models

        # Answers
        answer_options = sorted(df_domain["answer"].unique())
        if "country_answers_val" not in st.session_state:
            st.session_state["country_answers_val"] = answer_options
        valid_answers = list(set(st.session_state["country_answers_val"]).intersection(answer_options))
        selected_answers = st.multiselect(
            "Response Types",
            answer_options,
            default=valid_answers
        )
        st.session_state["country_answers_val"] = selected_answers

    # Filter
    df_filtered = final_df[
        (final_df["domain"] == st.session_state["country_domain_val"]) &
        (final_df["actor"].isin(st.session_state["country_actors_val"])) &
        (final_df["model"].isin(st.session_state["country_models_val"])) &
        (final_df["answer"].isin(st.session_state["country_answers_val"]))
    ].copy()

    if df_filtered.empty:
        st.warning("No data after applying filters.")
        return

    with col_plot:
        st.subheader(f"Distribution of Responses for {st.session_state['country_domain_val']}")

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
                sub_actors = df_model[(df_model["answer"] == ans)]
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

    # Preset 1: Domain-Level = "Escalation - Two Choice"
    with col_a:
        if st.button("Pre-set 1: Escalation (2 Choice)"):
            st.session_state["analysis_choice"] = "Domain-Level"
            st.session_state["domain_select_val"] = "Escalation - Two Choice"
            # Clear or keep answers, e.g.:
            st.experimental_rerun()

    # Preset 2: Country-Level = "Escalation - Two Choice" + actor=China
    with col_b:
        if st.button("Pre-set 2: China Escalation (2 Choice)"):
            st.session_state["analysis_choice"] = "Country-Level"
            st.session_state["country_domain_val"] = "Escalation - Two Choice"
            st.session_state["country_actors_val"] = ["China"]
            st.experimental_rerun()

    # Preset 3: Domain-Level = "Cooperation"
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

