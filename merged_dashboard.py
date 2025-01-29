import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

DOMAIN_EXPLANATIONS = {
    "Escalation - Three Choice": "...",
    "Escalation - Two Choice": "...",
    "Intervention - Two Choice": "...",
    "Intervention - Three Choice": "...",
    "Cooperation": "...",
    "Balancing": "..."
}

def build_echarts_bar_option(...):
    # your existing code
    return option

def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    # -----------------
    # 1) Preset Buttons
    # -----------------
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        preset1 = st.button("Preset 1: Escalation - Two Choice")
    with col_p2:
        preset2 = st.button("Preset 2: China Escalation - Two Choice")
    with col_p3:
        preset3 = st.button("Preset 3: Cooperation")

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
