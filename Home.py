import streamlit as st
import plotly.graph_objects as go
from medi_graph.run_graph import run_langgraph_agent_using_sample_data
from pathlib import Path
import time

st.set_page_config(page_title="Therapy Session Analyzer Agent",
                   layout="wide", page_icon=":robot:")
st.title("Therapy Session Analyzer Agent")


if 'analyze_button' in st.session_state and st.session_state.analyze_button == True:
    st.session_state.running = True
else:
    st.session_state.running = False

if "last_data_source" not in st.session_state:
    st.session_state.last_data_source = None

data_source = st.radio(
    "Select Data Source",
    options=["client1", "client2", "client3"],
    index=0,
    horizontal=True,
    format_func=lambda x: f"Client {x[-1]}" if "client" in x else x,
    key="data_source",
    disabled=st.session_state.running
)


@st.cache_data
def get_cached_data(c_id):
    return run_langgraph_agent_using_sample_data(c_id)


# with open("./medi_graph/sample_data/sample_response.json", "r") as f:
#     dummy_data = json.load(f)


analyze_button = st.button(
    "Analyze Session", key="analyze_button",  disabled=st.session_state.running)

if analyze_button:
    with st.spinner("Running agent..."):
        if data_source == st.session_state.last_data_source:
            result = st.session_state.output
        else:
            time.sleep(5)
            result = get_cached_data(data_source)

    if "error" in result:
        st.error(result["error"])
    else:
        st.session_state.output = result
        st.session_state.last_data_source = data_source
        st.rerun()
else:
    if st.session_state.running:
        st.warning("Please wait, the agent is still processing the data.")
    elif st.session_state.last_data_source is None:
        st.info("Please select a data source and click 'Analyze Session' to begin.")

if 'output' in st.session_state:
    result = st.session_state.output
    sessions = result.get("sessions", [])
    st.subheader(f"{result.get('client_id', '-').upper()}")

    cols = st.columns([1, 1, 1, 1])

    cols[0].metric("Diagnosis", result.get('diagnosis', '-'), border=True)
    cols[1].metric("Sessions", len(
        result.get('sessions', [])), border=True)
    cols[2].metric(
        f"Latest {result.get('metric', '-')} score", sessions[-1]["total_score"], border=True)

    cols[3].metric("Status", result.get(
        'progress_status', '-'), border=True)

    st.markdown(
        f"""
        ### Progress Summary
        {result.get('progress_summary', '-')}
        """)

    metric = result.get("metric", "Score")

    st.divider()

    # Trend line chart
    st.markdown("### Total Score Over Sessions")
    if sessions:
        line_data = {
            "Session": [f"Session {s['therapy_session_number']}" for s in sessions],
            "Score": [s.get("total_score") or s.get(f"total_{metric.lower()}_score") for s in sessions],
        }
        st.line_chart(line_data, x="Session", y="Score")
    st.divider()

    # Symptom trend bar chart
    st.markdown("### Symptom Trend Over Sessions")
    if sessions and "estimated_scores" in sessions[0]:
        symptom_keys = list(sessions[0]["estimated_scores"].keys())
        session_labels = [
            f"S{s['therapy_session_number']}" for s in sessions]
        fig = go.Figure()
        for k in symptom_keys:
            fig.add_trace(go.Bar(
                x=session_labels,
                y=[s["estimated_scores"][k] for s in sessions],
                name=k,
                hovertemplate='Session: %{x}<br>' +
                'Symptom: ' + k + '<br>' +
                'Score: %{y}<extra></extra>'
            ))
        fig.update_layout(
            barmode='group',
            xaxis_title="Session",
            yaxis_title="Score",
            margin=dict(l=30, r=30, t=30, b=30),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # Detailed session cards
    st.markdown("### Detailed Session Information")
    for session in sessions:
        with st.expander(f"Session {session['therapy_session_number']}"):
            sess_cols = st.columns([2, 1])
            score = session.get("total_score") or session.get(
                f"total_{metric.lower()}_score")
            sess_cols[0].markdown(f"**{metric} Score:** {score}")
            sess_cols[0].markdown(
                f"**Justification:**\n {session.get('justification', '-')}")
            # Radar chart for symptoms
            if "estimated_scores" in session:
                radar_scores = session["estimated_scores"]
                radar_labels = list(radar_scores.keys())
                radar_values = list(radar_scores.values())
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=radar_values + [radar_values[0]],
                    theta=radar_labels + [radar_labels[0]],
                    fill='toself',
                    name='Symptom Scores',
                    marker=dict(color='#6FA8DC')
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(
                        visible=True, range=[0, 3])),
                    showlegend=False,
                    margin=dict(l=30, r=30, t=30, b=30),
                    height=350
                )
                sess_cols[1].plotly_chart(fig, use_container_width=True)

# else:
#     st.info("Please upload session files or select sample data to begin.")
