import streamlit as st
import pandas as pd
import plotly.express as px

# Define domain explanations
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


#####################
# 1) DOMAIN DASHBOARD
#####################
def domain_dashboard():
    # Load the domain-level DataFrame (columns: domain, model, answer, percentage)
    try:
        final_dashboard_df = pd.read_csv("final_dashboard_df.csv")
    except FileNotFoundError:
        st.error("Domain-level data file 'final_dashboard_df.csv' not found.")
        return

    col_main, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:
       

        # Extract response types based on domain only
        df_domain = final_dashboard_df[final_dashboard_df["domain"] == selected_domain]
        all_answers = sorted(df_domain["answer"].unique())

        # Response selection - unique key
        selected_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=all_answers,
            key="domain_answers_multiselect"  # unique key
        )

         # Domain selection - unique key
        domain_options = sorted(final_dashboard_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=0,
            key="domain_selectbox_dashboard"  # unique key
        )

        # Display domain explanation if available
        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # Now filter by responses
        df_filtered = df_domain[df_domain["answer"].isin(selected_answers)]

        # Model selection - unique key
        all_models = sorted(df_filtered["model"].unique())
        selected_models = st.multiselect(
            "Models",
            all_models,
            default=all_models,
            key="domain_models_multiselect"  # unique key
        )
        df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]

        if df_filtered.empty:
            st.warning("No data after filtering by model(s) and response(s).")
            return

    with col_main:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        fig = px.bar(
            df_filtered,
            x="model",
            y="percentage",
            color="answer",
            orientation="v",
            title="Response Distribution by LLMs",
            hover_data=["percentage"],
            labels={"percentage": "Percentage", "model": "Model", "answer": "Answer"}
        )
        fig.update_layout(yaxis=dict(range=[0, 100]))

        st.plotly_chart(fig, use_container_width=True)


#######################
# 2) COUNTRY DASHBOARD
#######################
def country_dashboard():
    # Load your country-level DataFrame (domain, actor, model, answer, percentage)
    try:
        final_df = pd.read_csv("country_level_distribution.csv")
    except FileNotFoundError:
        st.error("Country-level data file 'country_level_distribution.csv' not found.")
        return

    col_main, col_filters = st.columns([4, 1], gap="medium")

    with col_filters:
        # Domain selection - unique key
        domain_options = sorted(final_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            key="country_selectbox_dashboard"  # unique key
        )

        # Display domain explanation if available
        if selected_domain in DOMAIN_EXPLANATIONS:
            st.markdown(DOMAIN_EXPLANATIONS[selected_domain])

        # Actors - unique key
        actor_options = sorted(final_df["actor"].unique())
        selected_actors = st.multiselect(
            "Actor(s) (max 5)",
            options=actor_options,
            default=actor_options,
            key="country_actors_multiselect"  # unique key
        )

        # Models (max 3) - unique key
        model_options = sorted(final_df["model"].unique())
        selected_models = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=model_options[:3],
            key="country_models_multiselect"  # unique key
        )
        selected_models = selected_models[:3]  # enforce max of 3

        # Answers - unique key
        # Extract all answers based on domain only
        df_domain = final_df[final_df["domain"] == selected_domain]
        domain_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            options=domain_answers,
            default=domain_answers,
            key="country_answers_multiselect"  # unique key
        )

    # Further filter
    df_filtered = final_df[
        (final_df["domain"] == selected_domain) &
        (final_df["actor"].isin(selected_actors)) &
        (final_df["model"].isin(selected_models)) &
        (final_df["answer"].isin(selected_answers))
    ].copy()

    with col_main:
        if df_filtered.empty:
            st.warning("No data after applying filters.")
            return

        st.subheader(f"Distribution of Responses for {selected_domain}")

        num_models = len(selected_models)
        if num_models == 0:
            st.warning("No models selected.")
            return

        # side-by-side columns for each model
        model_cols = st.columns(num_models)

        for i, model_name in enumerate(selected_models):
            df_model = df_filtered[df_filtered["model"] == model_name]
            if df_model.empty:
                with model_cols[i]:
                    st.warning(f"No data for model: {model_name}")
                continue

            # vertical bar chart: x=actor, y=percentage
            fig = px.bar(
                df_model,
                x="actor",
                y="percentage",
                color="answer",
                title=model_name,  # just the model name
                hover_data=["percentage"],
                labels={
                    "actor": "Actor",
                    "percentage": "Percentage",
                    "answer": "Answer"
                }
            )

            fig.update_layout(
                yaxis=dict(range=[0, 100]),
                width=400,
                height=400,
                margin=dict(r=150)  # space on the right
            )

            # Single legend on the first plot
            if i == 0:
                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.25  # adjust this value as needed to position the legend
                    )
                )
            else:
                fig.update_layout(showlegend=False)

            with model_cols[i]:
                st.plotly_chart(fig, use_container_width=False)


#######################
# 3) MAIN App
#######################
def main():
    # Set page layout to wide
    st.set_page_config(layout="wide")
    st.title("LLM Bias Dashboard")

    # Instruction Section in a Framed Box
    st.info(""" 
### Using This Dashboard  
This interactive dashboard presents results from CSIS and Scale AI’s benchmarking of Large Language Models’ preferences in international relations. 
The evaluation spans four key domains including – *Escalation, Intervention, Cooperation, and Alliance Dynamics* – 
across an initial seven foundation models: *Llama 3.1 8B Instruct, Llama 3.1 70B Instruct, GPT-4o, Gemini 1.5 Pro-002, Mistral 8x22B, Claude 3.5 Sonnet, and Qwen2 72B.*  

**How to Use the Dashboard:**  
1. **Select Level of Analysis**: Choose between Domain-Level or Country-Level variation (below).  
2. **Filter Results**: On the right of the screen, pick the domain, model, country (if applicable) and response types of interest.  
3. **View Results**: The dashboard will automatically update, displaying the percentage of model recommendations for each domain’s scenarios.
""")

    # Replace tabs with a radio button
    dashboard_choice = st.radio(
        "Select Level of Analysis",
        ["Domain-Level", "Country-Level"],
        key="dashboard_radio_choice"
    )

    # Show the desired dashboard based on the radio choice
    if dashboard_choice == "Domain-Level":
        domain_dashboard()
    else:
        country_dashboard()


if __name__ == "__main__":
    main()
