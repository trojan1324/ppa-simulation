import streamlit as st
import pandas as pd
import graphviz
import plotly.express as px

# --- CONFIGURATION & UX SETUP ---
st.set_page_config(page_title="Personal Projects Analysis", layout="wide", page_icon="🧭")

# Custom CSS for "Brilliant UX"
st.markdown("""
<style>
    .main { background-color: #f9fbfd; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .project-card { 
        padding: 20px; 
        background: white; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-left: 5px solid #4A90E2;
        margin-bottom: 15px;
    }
    h1 { color: #2C3E50; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #34495E; }
    .highlight { color: #4A90E2; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'projects' not in st.session_state: st.session_state.projects = []
if 'ratings' not in st.session_state: st.session_state.ratings = {}
if 'values' not in st.session_state: st.session_state.values = {}
if 'matrix' not in st.session_state: st.session_state.matrix = pd.DataFrame()

# --- HELPER FUNCTIONS ---
def calculate_factors(ratings):
    # Based on Little's 5 Factors
    stress = (ratings.get('Difficulty', 0) + ratings.get('Challenge', 0) + (10 - ratings.get('Competence', 0))) / 3
    meaning = (ratings.get('Importance', 0) + ratings.get('Value Congruency', 0) + ratings.get('Self-Identity', 0)) / 3
    efficacy = (ratings.get('Progress', 0) + ratings.get('Control', 0) + ratings.get('Outcome', 0)) / 3
    structure = (ratings.get('Control', 0) + ratings.get('Time Adequacy', 0)) / 2
    community = (ratings.get('Visibility', 0) + ratings.get('Support', 0)) / 2
    return {'Stress': stress, 'Meaning': meaning, 'Efficacy': efficacy, 'Structure': structure, 'Community': community}

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🧭 PPA Simulator")
    st.caption("Dr. Brian Little | Organizational Behavior")
    st.divider()
    step = st.radio("Current Phase:", 
        ["1. Elicitation (The List)", 
         "2. Appraisal (The Rating)", 
         "3. Laddering (The Values)", 
         "4. Cross-Impact (The System)", 
         "5. Leadership Dashboard"])
    
    st.info(f"**Active Projects:** {len(st.session_state.projects)}")
    
    # Reset Button for students to restart
    if st.button("Reset Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- PHASE 1: ELICITATION ---
if step == "1. Elicitation (The List)":
    st.title("Phase 1: The Brain Dump")
    st.markdown("""
    **Objective:** Identify the "extended sets of personally salient action" in your life[cite: 254]. 
    These can range from daily maintenance ("Walk the dog") to defining life goals ("Become a CEO").
    
    *Input at least 8-10 projects to get a valid system analysis.*
    """)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("add_project", clear_on_submit=True):
            new_proj = st.text_input("I am currently trying to...", placeholder="e.g., Pass Accounting, Fix my relationship, Lose 10lbs")
            submitted = st.form_submit_button("Add Project")
            if submitted and new_proj:
                if new_proj not in [p['name'] for p in st.session_state.projects]:
                    st.session_state.projects.append({'name': new_proj})
                    # Initialize default ratings
                    st.session_state.ratings[new_proj] = {d: 5 for d in 
                        ['Importance', 'Difficulty', 'Visibility', 'Control', 'Responsibility', 'Time Adequacy', 
                         'Outcome', 'Self-Identity', 'Others View', 'Value Congruency', 'Progress', 'Challenge', 
                         'Absorption', 'Support', 'Competence', 'Autonomy']}
                    st.success(f"Added: {new_proj}")
                    st.rerun()

    with col2:
        st.subheader("Your Portfolio")
        if not st.session_state.projects:
            st.caption("No projects yet.")
        for i, p in enumerate(st.session_state.projects):
            with st.expander(f"{i+1}. {p['name']}", expanded=False):
                if st.button(f"Delete '{p['name']}'", key=f"del_{i}"):
                    st.session_state.projects.pop(i)
                    del st.session_state.ratings[p['name']]
                    st.rerun()

# --- PHASE 2: APPRAISAL ---
elif step == "2. Appraisal (The Rating)":
    st.title("Phase 2: Project Appraisal")
    st.markdown("Rate your projects to uncover the hidden structure of your life.")
    
    if not st.session_state.projects:
        st.warning("Please add projects in Phase 1 first.")
    else:
        proj_names = [p['name'] for p in st.session_state.projects]
        selected = st.selectbox("Select Project to Rate:", proj_names)
        
        if selected:
            r = st.session_state.ratings[selected]
            st.markdown(f"<div class='project-card'><h3>📝 Rating: {selected}</h3></div>", unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs(["Meaning", "Structure", "Community", "Efficacy & Stress"])
            
            with tab1:
                st.caption("Does this project matter?")
                r['Importance'] = st.slider("Importance (0-10)", 0, 10, r['Importance'])
                r['Value Congruency'] = st.slider("Consistent with your values?", 0, 10, r['Value Congruency'])
                r['Self-Identity'] = st.slider("Is this 'typical' of you?", 0, 10, r['Self-Identity'])
            
            with tab2:
                st.caption("Are you in the driver's seat?")
                colA, colB = st.columns(2)
                with colA:
                    r['Control'] = st.slider("How much control do you have?", 0, 10, r['Control'])
                    r['Responsibility'] = st.slider("How responsible are you?", 0, 10, r['Responsibility'])
                with colB:
                    r['Time Adequacy'] = st.slider("Do you have enough time?", 0, 10, r['Time Adequacy'])
                    r['Autonomy'] = st.slider("Are you doing this freely?", 0, 10, r['Autonomy'])

            with tab3:
                st.caption("Who sees this?")
                r['Visibility'] = st.slider("How visible is this to others?", 0, 10, r['Visibility'])
                r['Support'] = st.slider("How much support do you get?", 0, 10, r['Support'])
                r['Others View'] = st.slider("Do others think this is important?", 0, 10, r['Others View'])

            with tab4:
                st.caption("The cost vs. benefit")
                colC, colD = st.columns(2)
                with colC:
                    r['Difficulty'] = st.slider("Difficulty", 0, 10, r['Difficulty'])
                    r['Challenge'] = st.slider("Challenge", 0, 10, r['Challenge'])
                    r['Absorption'] = st.slider("Absorption (Flow)", 0, 10, r['Absorption'])
                with colD:
                    r['Progress'] = st.slider("Progress so far", 0, 10, r['Progress'])
                    r['Competence'] = st.slider("Do you feel capable?", 0, 10, r['Competence'])
                    r['Outcome'] = st.slider("Likelihood of success", 0, 10, r['Outcome'])

            st.session_state.ratings[selected] = r
            st.success("Ratings saved automatically.")

# --- PHASE 3: LADDERING ---
elif step == "3. Laddering (The Values)":
    st.title("Phase 3: The 'Why' Ladder")
    st.markdown("""
    Use the **Laddering Technique** [cite: 113] to connect your daily tasks to higher values.
    Ask: *"Why am I doing this?"* until you reach a core value.
    """)
    
    if not st.session_state.projects:
        st.warning("Go back to Phase 1.")
    else:
        # Find top 3 most important projects
        sorted_projs = sorted(st.session_state.projects, key=lambda x: st.session_state.ratings[x['name']]['Importance'], reverse=True)
        top_3 = sorted_projs[:3]
        
        for p in top_3:
            name = p['name']
            st.subheader(f"🪜 Laddering: {name}")
            val = st.text_input(f"Why is '{name}' important to you? (e.g., 'To feel secure', 'To be loved')", 
                                key=f"why_{name}", 
                                value=st.session_state.values.get(name, ""))
            if val:
                st.session_state.values[name] = val

# --- PHASE 4: CROSS-IMPACT ---
elif step == "4. Cross-Impact (The System)":
    st.title("Phase 4: System Impact")
    st.markdown("""
    Analyze how your projects affect each other[cite: 102].
    * **+1 (Green):** Helping each other.
    * **-1 (Red):** Hindering/Conflict.
    * **0:** Neutral.
    """)
    
    names = [p['name'] for p in st.session_state.projects]
    if len(names) < 2:
        st.warning("Need at least 2 projects.")
    else:
        if st.session_state.matrix.shape != (len(names), len(names)):
            st.session_state.matrix = pd.DataFrame(0, index=names, columns=names)
        
        st.session_state.matrix = st.data_editor(
            st.session_state.matrix,
            column_config={n: st.column_config.NumberColumn(n, min_value=-1, max_value=1, step=1) for n in names},
            height=400,
            use_container_width=True
        )

# --- PHASE 5: DASHBOARD ---
elif step == "5. Leadership Dashboard":
    st.title("🎓 Executive System Audit")
    
    if not st.session_state.projects:
        st.error("No data.")
    else:
        # Prepare Data
        data = []
        for p in st.session_state.projects:
            name = p['name']
            factors = calculate_factors(st.session_state.ratings[name])
            factors['Name'] = name
            factors['Core Value'] = st.session_state.values.get(name, "N/A")
            data.append(factors)
        df = pd.DataFrame(data)
        
        # 1. VISUALIZE SYSTEM
        st.subheader("1. Your Project Ecology Map")
        colA, colB = st.columns([3, 1])
        with colA:
            graph = graphviz.Digraph()
            graph.attr(rankdir='LR', bgcolor='transparent')
            
            # Draw Nodes
            for _, row in df.iterrows():
                # Color node by stress (Red = High Stress, Blue = Low Stress)
                color = "#E74C3C" if row['Stress'] > 6 else "#3498DB"
                graph.node(row['Name'], row['Name'], style='filled', fillcolor=color, fontcolor='white', shape='box')
            
            # Draw Edges
            mat = st.session_state.matrix
            for p1 in mat.index:
                for p2 in mat.columns:
                    if p1 != p2:
                        val = mat.loc[p1, p2]
                        if val == 1: graph.edge(p1, p2, color='#2ECC71', penwidth='2') # Green
                        if val == -1: graph.edge(p1, p2, color='#E74C3C', penwidth='2', style='dashed') # Red
            
            st.graphviz_chart(graph, use_container_width=True)
        
        with colB:
            st.info("System Key")
            st.markdown("""
            * **Blue Box:** Healthy Project
            * **Red Box:** High Stress Project
            * **Green Line:** Synergy
            * **Red Dashed Line:** Conflict
            """)

        st.divider()

        # 2. BURNOUT MATRIX (Scatter Plot)
        st.subheader("2. The Meaning vs. Stress Matrix")
        fig = px.scatter(df, x="Stress", y="Meaning", color="Efficacy", size="Community", 
                         hover_data=["Name", "Core Value"], text="Name",
                         title="High Stress + Low Meaning = Burnout Risk",
                         labels={"Stress": "System Stress", "Meaning": "Personal Meaning"},
                         color_continuous_scale="RdYlGn")
        
        # Add Quadrant Backgrounds
        fig.add_hrect(y0=0, y1=5, fillcolor="red", opacity=0.05, layer="below")
        fig.add_hrect(y0=5, y1=10, fillcolor="green", opacity=0.05, layer="below")
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

        # 3. REPORT CARD
        st.subheader("3. Project Metrics")
        st.dataframe(df.set_index("Name")[['Stress', 'Meaning', 'Efficacy', 'Structure', 'Core Value']].style.background_gradient(cmap='RdYlGn', subset=['Efficacy', 'Meaning', 'Structure']).background_gradient(cmap='RdYlGn_r', subset=['Stress']))

        # 4. EXPORT FOR ASSIGNMENT
        st.divider()
        st.subheader("4. Submission Export")
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label="Download Analysis (CSV)",
            data=csv,
            file_name='my_personal_projects.csv',
            mime='text/csv',
        )
