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
# 2) ECharts Option Builder
###############################################################################
def build_echarts_bar_option(x_data, series_data, chart_title="ECharts Bar", 
                             x_label="", y_label="Percentage"):
    """
    Returns an ECharts 'option' dict for a stacked vertical bar chart 
    with larger/bold axis labels.
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
# 3) Domain-Level Plot (single-run)
###############################################################################
def show_domain_level_plot(df):
    """
    Renders the domain-level chart with filters for answers, models on the right.
    Always defaults to all valid answers/models for the domain.
    """
    # Filters on the right
    dom_col_plot, dom_col_filters = st.columns([3,1], gap="medium")

    with dom_col_filters:
        # All answers
        all_answers = sorted(df["answer"].unique())
        chosen_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=all_answers
        )
        df_filtered = df[df["answer"].isin(chosen_answers)]

        # All models
        all_models = sorted(df_filtered["model"].unique())
        chosen_models = st.multiselect(
            "Models",
            all_models,
            default=all_models
        )
        df_filtered = df_filtered[df_filtered["model"].isin(chosen_models)]

    with dom_col_plot:
        if df_filtered.empty:
            st.warning("No data after filtering.")
            return
        x_data = sorted(df_filtered["model"].unique())
        answers_used = sorted(df_filtered["answer"].unique())

        series_data = {}
        for ans in answers_used:
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

###############################################################################
# 4) Country-Level Plot (single-run)
###############################################################################
def show_country_level_plot(df):
    """
    Renders the country-level chart with filters for actor, models, answers on the right,
    always defaults to all valid for that domain.
    """
    ctry_col_plot, ctry_col_filters = st.columns([3,1], gap="medium")

    with ctry_col_filters:
        all_actors = sorted(df["actor"].unique())
        chosen_actors = st.multiselect(
            "Actor(s)",
            all_actors,
            default=all_actors
        )
        df_filtered = df[df["actor"].isin(chosen_actors)]

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

    with ctry_col_plot:
        if df_filtered.empty:
            st.warning("No data after filtering.")
            return

        final_models = sorted(df_filtered["model"].unique())
        if len(final_models) == 0:
            st.warning("No models available.")
            return

        # side-by-side columns for each model
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

###############################################################################
# 5) Main
###############################################################################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    st.info("""
### Using This Dashboard
- **Filters** on the right, **Plots** on the left.  
- **Preset Buttons** can override domain/actor but you can still change them 
  afterward in the same run.  
- This is single-run: we do not store domain or re-run automatically.  
""")

    # Let the user pick domain-level or country-level
    analysis_choice_local = st.radio("Select Level of Analysis", ["Domain-Level", "Country-Level"])

    # We'll read the data so we can populate domain choices
    try:
        df_domain_all = pd.read_csv("final_dashboard_df.csv")
        domain_level_domains = sorted(df_domain_all["domain"].unique())
    except:
        domain_level_domains = list(DOMAIN_EXPLANATIONS.keys())  # fallback

    try:
        df_country_all = pd.read_csv("country_level_distribution.csv")
        country_level_domains = sorted(df_country_all["domain"].unique())
    except:
        country_level_domains = list(DOMAIN_EXPLANATIONS.keys())

    # We define local variables that the user or presets might override
    final_domain = None
    final_actor = None

    # Three columns for the preset buttons
    c1, c2, c3 = st.columns(3)

    with c1:
        preset1_clicked = st.button("Pre-set 1: Escalation (2 Choice)")
    with c2:
        preset2_clicked = st.button("Pre-set 2: China (Escalation 2 Choice)")
    with c3:
        preset3_clicked = st.button("Pre-set 3: Cooperation")

    # If user clicked a preset, we override final_domain or final_actor
    # We'll also override analysis_choice_local if needed
    if preset1_clicked:
        analysis_choice_local = "Domain-Level"
        final_domain = "Escalation - Two Choice"

    if preset2_clicked:
        analysis_choice_local = "Country-Level"
        final_domain = "Escalation - Two Choice"
        final_actor  = "China"

    if preset3_clicked:
        analysis_choice_local = "Domain-Level"
        final_domain = "Cooperation"

    st.write("---")

    # Now that we've processed presets, let's let the user pick domain from the right side
    # We'll do so in a separate columns block: plot on the left, filters on the right
    # The logic is ephemeral.

    # We'll again define columns so we can put domain selectbox on the right 
    # but the actual chart below
    col_plot, col_filters = st.columns([3,1], gap="medium")

    # We'll store the final domain in a local variable domain_choice that 
    # user can override unless a preset is forcing it
    with col_filters:
        if analysis_choice_local == "Domain-Level":
            # domain-level
            if final_domain is not None:
                # A preset forced it; let user override if they want
                st.markdown(f"**Preset** forced domain = {final_domain}. You can override below.")
                domain_choice = st.selectbox(
                    "Pick domain (override preset if you want)",
                    domain_level_domains,
                    index=domain_level_domains.index(final_domain)
                      if final_domain in domain_level_domains else 0
                )
            else:
                # no preset forcing => user picks
                domain_choice = st.selectbox("Pick domain", domain_level_domains)

            # if user picks different from preset, that overshadow
            final_domain = domain_choice

        else:
            # Country-Level
            if final_domain is not None:
                st.markdown(f"**Preset** forced domain = {final_domain}. You can override below.")
                domain_choice = st.selectbox(
                    "Pick domain (override preset if you want)",
                    country_level_domains,
                    index=country_level_domains.index(final_domain)
                      if final_domain in country_level_domains else 0
                )
            else:
                domain_choice = st.selectbox("Pick domain", country_level_domains)
            final_domain = domain_choice

    # Display
    with col_plot:
        st.subheader(f"**{analysis_choice_local}** scenario, Domain: {final_domain}")
    
    # Now do the final plotting
    if analysis_choice_local == "Domain-Level":
        # Filter domain-level data
        try:
            ddf = pd.read_csv("final_dashboard_df.csv")
        except FileNotFoundError:
            st.error("Missing 'final_dashboard_df.csv'.")
            return

        # Explanation text
        if final_domain in DOMAIN_EXPLANATIONS:
            with col_plot:
                st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        domain_df = ddf[ddf["domain"] == final_domain]
        show_domain_level_plot(domain_df)

    else:
        # Country-Level
        try:
            cdf = pd.read_csv("country_level_distribution.csv")
        except FileNotFoundError:
            st.error("Missing 'country_level_distribution.csv'.")
            return

        # Explanation
        if final_domain in DOMAIN_EXPLANATIONS:
            with col_plot:
                st.markdown(DOMAIN_EXPLANATIONS[final_domain])

        cdf = cdf[cdf["domain"] == final_domain]

        # If a preset forced final_actor = "China", 
        # we do not prevent user from picking new actors. 
        # We'll do a note:
        if final_actor is not None:
            with col_plot:
                st.write(f"Preset suggested actor = {final_actor}, but you may override in the filters.")
        show_country_level_plot(cdf)


if __name__ == "__main__":
    main()
