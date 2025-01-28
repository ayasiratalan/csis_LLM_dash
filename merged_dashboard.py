import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

#######################################
# 1. Domain Explanations (Unchanged)
#######################################
DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": """
**Escalation - Three Choice:** This domain focuses on scenarios in which states are offered...
""",
    "Escalation - Two Choice": """
**Escalation - Two Choice:** This domain focuses on scenarios in which states are offered...
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

#######################################
# 2. Build ECharts Bar Option
#######################################
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
            "nameTextStyle": {
                "fontSize": 14,
                "fontWeight": "bold"
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
                "fontWeight": "bold"
            },
            "axisLabel": {
                "fontSize": 12,
                "fontWeight": "bold"
            }
        },
        "series": series_list
    }
    return option

#######################################
# 3. Domain-Level Dashboard
#######################################
def domain_dashboard():
    try:
        df_domain_all = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file not found.")
        return

    col_plot, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:
        # Domain
        domain_options = sorted(df_domain_all["domain"].unique())
        if "domain_domain_val" not in st.session_state:
            st.session_state["domain_domain_val"] = domain_options[0]
        domain_val = st.selectbox(
            "Domain", 
            domain_options,
            index=domain_options.index(st.session_state["domain_domain_val"]) 
              if st.session_state["domain_domain_val"] in domain_options else 0
        )
        st.session_state["domain_domain_val"] = domain_val

        # Explanation
        if domain_val in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[domain_val])

        # Filter by domain
        df_domain = df_domain_all[df_domain_all["domain"] == domain_val]

        # Response Types
        answer_options = sorted(df_domain["answer"].unique())
        if "domain_answers_val" not in st.session_state:
            st.session_state["domain_answers_val"] = answer_options

        # Intersect to avoid invalid defaults
        valid_answers = list(set(st.session_state["domain_answers_val"]).intersection(answer_options))
        answers_val = st.multiselect(
            "Response Types",
            answer_options,
            default=valid_answers
        )
        st.session_state["domain_answers_val"] = answers_val

        df_filtered = df_domain[df_domain["answer"].isin(answers_val)]

        # Models
        model_options = sorted(df_filtered["model"].unique())
        if "domain_models_val" not in st.session_state:
            st.session_state["domain_models_val"] = model_options

        valid_models = list(set(st.session_state["domain_models_val"]).intersection(model_options))
        models_val = st.multiselect(
            "Models",
            model_options,
            default=valid_models
        )
        st.session_state["domain_models_val"] = models_val

        df_filtered = df_filtered[df_filtered["model"].isin(models_val)]
        if df_filtered.empty:
            st.warning("No data after filtering.")
            return


    with col_plot:
        st.subheader(f"Distribution of Responses for {st.session_state['domain_domain_val']}")

        # Build chart
        x_data = sorted(df_filtered["model"].unique())
        answers = sorted(df_filtered["answer"].unique())

        series_data = {}
        for ans in answers:
            row_vals = []
            for mod in x_data:
                sub_df = df_filtered[(df_filtered["model"] == mod) & (df_filtered["answer"] == ans)]
                if len(sub_df) == 0:
                    row_vals.append(0)
                else:
                    row_vals.append(sub_df["percentage"].mean())
            series_data[ans] = row_vals

        option = build_echarts_bar_option(
            x_data=x_data,
            series_data=series_data,
            chart_title="Response Distribution by LLMs",
            x_label="Model",
            y_label="Percentage"
        )
        st_echarts(options=option, height="400px")

#######################################
# 4. Country-Level Dashboard
#######################################
def country_dashboard():
    # Load country-level data
    try:
        df_country_all = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    col_plot, col_filters = st.columns([4,1], gap="medium")

    with col_filters:
        # Domain
        domain_options = sorted(df_country_all["domain"].unique())

        if "country_domain_val" not in st.session_state:
            st.session_state["country_domain_val"] = domain_options[0]
        domain_val = st.selectbox(
            "Domain",
            domain_options,
            index=domain_options.index(st.session_state["country_domain_val"]) 
              if st.session_state["country_domain_val"] in domain_options else 0
        )
        if domain_val != st.session_state["country_domain_val"]:
            st.session_state["country_domain_val"] = domain_val

        if st.session_state["country_domain_val"] in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[st.session_state["country_domain_val"]])

        df_domain = df_country_all[df_country_all["domain"] == st.session_state["country_domain_val"]]

        # Actors
        actor_options = sorted(df_domain["actor"].unique())
        if "country_actors_val" not in st.session_state:
            st.session_state["country_actors_val"] = actor_options  # all by default
        actors_val = st.multiselect(
            "Actor(s)",
            actor_options,
            default=st.session_state["country_actors_val"]
        )
        st.session_state["country_actors_val"] = actors_val

        # Models (max 3)
        model_options = sorted(df_domain["model"].unique())
        if "country_models_val" not in st.session_state:
            st.session_state["country_models_val"] = model_options[:3]
        models_val = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=st.session_state["country_models_val"]
        )
        # enforce max 3
        models_val = models_val[:3]
        st.session_state["country_models_val"] = models_val

        # Response types
        answer_options = sorted(df_domain["answer"].unique())
        if "country_answers_val" not in st.session_state:
            st.session_state["country_answers_val"] = answer_options
        answers_val = st.multiselect(
            "Response Types",
            answer_options,
            default=st.session_state["country_answers_val"]
        )
        st.session_state["country_answers_val"] = answers_val

    df_filtered = df_country_all[
        (df_country_all["domain"] == st.session_state["country_domain_val"]) &
        (df_country_all["actor"].isin(st.session_state["country_actors_val"])) &
        (df_country_all["model"].isin(st.session_state["country_models_val"])) &
        (df_country_all["answer"].isin(st.session_state["country_answers_val"]))
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
                row_vals = []
                for act in x_data:
                    sub_df = df_model[(df_model["actor"] == act) & (df_model["answer"] == ans)]
                    if len(sub_df) == 0:
                        row_vals.append(0)
                    else:
                        row_vals.append(sub_df["percentage"].mean())
                series_data[ans] = row_vals

            option = build_echarts_bar_option(
                x_data=x_data,
                series_data=series_data,
                chart_title=mod,
                x_label="Actor",
                y_label="Percentage"
            )
            # hide legend except first
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
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking...
""")

    # If "analysis_choice" not in session, default "Domain-Level"
    if "analysis_choice" not in st.session_state:
        st.session_state["analysis_choice"] = "Domain-Level"

    # We do not set a key, store the user's local choice:
    analysis_choice_local = st.radio(
        "Select Level of Analysis",
        ["Domain-Level", "Country-Level"],
        index=0 if st.session_state["analysis_choice"]=="Domain-Level" else 1
    )
    # If user changed it, update session
    if analysis_choice_local != st.session_state["analysis_choice"]:
        st.session_state["analysis_choice"] = analysis_choice_local

    # 3 columns for the preset buttons
    col_a, col_b, col_c = st.columns(3)

    # Pre-set 1
    with col_a:
        if st.button("Pre-set 1: Escalation (Two Choice)"):
            # "Which model is most likely to recommend escalatory courses... 2 response Escalation domain"
            # Force domain-level approach
            st.session_state["analysis_choice"] = "Domain-Level"
            # Force domain
            st.session_state["domain_domain_val"] = "Escalation - Two Choice"
            # Optionally clear or set responses / models if you want
            st.session_state["domain_answers_val"] = ["Use of Force","No Use of Force","Refused to Answer"]

            
            st.rerun()

    # Pre-set 2
    with col_b:
        if st.button("Pre-set 2: China (Escalation - Two Choice)"):
            # "Is China the country most likely to be recommended escalatory responses?"
            st.session_state["analysis_choice"] = "Country-Level"
            st.session_state["country_domain_val"] = "Escalation - Two Choice"
            # Force actor
            st.session_state["country_actors_val"] = ["China"]
            # Force models
            st.session_state["country_models_val"] = ["Llama 3.1 8B Instruct", "GPT-4o"]
            st.rerun()

    # Pre-set 3
    with col_c:
        if st.button("Pre-set 3: Cooperation"):
            # "Are any models more likely to prefer cooperative...?"
            st.session_state["analysis_choice"] = "Domain-Level"
            st.session_state["domain_domain_val"] = "Cooperation"
            st.session_state["domain_answers_val"] = ["Cooperative","Non-Cooperative","Refused to Answer"]

            st.rerun()

    # Now show the dashboard based on st.session_state["analysis_choice"]
    if st.session_state["analysis_choice"] == "Domain-Level":
        domain_dashboard()
    else:
        country_dashboard()

if __name__ == "__main__":
    main()
