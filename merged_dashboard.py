import streamlit as st
import pandas as pd
import plotly.express as px

#####################
# 1) DOMAIN DASHBOARD
#####################
def domain_dashboard():
    st.subheader("Domain-Level Dashboard")

    # Load the domain-level DataFrame (columns: domain, model, answer, percentage)
    final_dashboard_df = pd.read_csv("final_dashboard_df.csv")

    col_main, col_filters = st.columns([3, 1], gap="medium")

    with col_filters:
        # Domain selection - unique key
        domain_options = sorted(final_dashboard_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            index=0,
            key="domain_selectbox_dashboard"  # unique key
        )

        # Filter by domain
        df_filtered = final_dashboard_df[final_dashboard_df["domain"] == selected_domain].copy()
        if df_filtered.empty:
            st.warning("No data available for the selected domain.")
            return

        # Model selection - unique key
        all_models = sorted(df_filtered["model"].unique())
        selected_models = st.multiselect(
            "Models",
            all_models,
            default=all_models,
            key="domain_models_multiselect"  # unique key
        )
        df_filtered = df_filtered[df_filtered["model"].isin(selected_models)]

        # Response selection - unique key
        all_answers = sorted(df_filtered["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            all_answers,
            default=all_answers,
            key="domain_answers_multiselect"  # unique key
        )
        df_filtered = df_filtered[df_filtered["answer"].isin(selected_answers)]

        if df_filtered.empty:
            st.warning("No data after filtering by model(s) and response(s).")
            return

    with col_main:
        st.subheader(f"Distribution of Responses for {selected_domain}")

        fig = px.bar(
            df_filtered,
            x="percentage",
            y="model",
            color="answer",
            orientation="v",
            title="Model vs. Response Distribution",
            hover_data=["percentage"],
            labels={"percentage": "Percentage", "model": "Model", "answer": "Answer"}
        )
        fig.update_layout(xaxis=dict(range=[0, 100]))

        st.plotly_chart(fig, use_container_width=True)


#######################
# 2) COUNTRY DASHBOARD
#######################
def country_dashboard():
    st.subheader("Country-Level Dashboard")

    # Load your country-level DataFrame (domain, actor, model, answer, percentage)
    final_df = pd.read_csv("country_level_distribution.csv")

    col_main, col_filters = st.columns([4, 1], gap="medium")

    with col_filters:
        # Domain selection - unique key
        domain_options = sorted(final_df["domain"].unique())
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            key="country_selectbox_dashboard"  # unique key
        )

        # Filter data to selected domain
        df_domain = final_df[final_df["domain"] == selected_domain].copy()
        if df_domain.empty:
            st.warning("No data available for this domain.")
            return

        # Actors - unique key
        actor_options = sorted(df_domain["actor"].unique())
        selected_actors = st.multiselect(
            "Actor(s)",
            options=actor_options,
            default=actor_options,
            key="country_actors_multiselect"  # unique key
        )

        # Models (max 3) - unique key
        model_options = sorted(df_domain["model"].unique())
        selected_models = st.multiselect(
            "Model(s) (max 3)",
            model_options,
            default=model_options[:3],
            key="country_models_multiselect"  # unique key
        )
        selected_models = selected_models[:3]

        # Answers - unique key
        domain_answers = sorted(df_domain["answer"].unique())
        selected_answers = st.multiselect(
            "Response Types",
            options=domain_answers,
            default=domain_answers,
            key="country_answers_multiselect"  # unique key
        )

    # Filter further
    df_filtered = df_domain[
        (df_domain["actor"].isin(selected_actors)) &
        (df_domain["model"].isin(selected_models)) &
        (df_domain["answer"].isin(selected_answers))
    ].copy()

    with col_main:
        if df_filtered.empty:
            st.warning("No data after applying filters.")
            return

        st.subheader("Response Distribution")

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

            # Single legend on the first plot if you want:
            if i == 0:
                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation='v',
                        yanchor='middle',
                        y=0.5,
                        xanchor='left',
                        x=1.25
                    )
                )
            else:
                fig.update_layout(showlegend=False)

            with model_cols[i]:
                st.plotly_chart(fig, use_container_width=False)


#######################
# 3) MAIN App with Tabs
#######################
def main():
    st.set_page_config(layout="wide")
    st.title("LLM IR Unified Dashboard")

    tab1, tab2 = st.tabs(["Domain-Level", "Country-Level"])

    with tab1:
        domain_dashboard()

    with tab2:
        country_dashboard()


if __name__ == "__main__":
    main()
