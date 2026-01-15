import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="🎯 AI Meeting Assistant",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    .meeting-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
    }
    .action-item {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'meetings' not in st.session_state:
    st.session_state.meetings = []

# HARDCODED API KEY (for testing - remove before deploying publicly!)
API_KEY = "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"

def analyze_meeting(transcript, meeting_type):
    """Analyze meeting transcript"""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=API_KEY
    )
    
    prompts = {
        "full_summary": """
Analyze this meeting transcript and provide a comprehensive summary.

TRANSCRIPT:
{transcript}

Provide:

1. **Meeting Summary** (2-3 sentences)

2. **Key Discussion Points** (5-7 bullet points)

3. **Decisions Made** (numbered list)

4. **Action Items** (Format: "• Task | Person | Deadline")

5. **Next Steps**

Be concise and actionable.
""",
        "action_items": """
Extract all action items from this meeting.

TRANSCRIPT:
{transcript}

For each action item provide:
- ✅ Task description
- 👤 Person responsible (if mentioned)
- 📅 Deadline (if mentioned)
- 🔥 Priority: High/Medium/Low

Format as bullet points.
""",
        "quick_notes": """
Create quick meeting notes.

TRANSCRIPT:
{transcript}

Provide:
1. **One-line summary**
2. **Top 3 key points**
3. **Immediate actions**
4. **Next meeting topics**
""",
        "participant_insights": """
Analyze participants.

TRANSCRIPT:
{transcript}

For each person:
- Name
- Main points raised
- Commitments
"""
    }
    
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert meeting facilitator."),
        ("human", prompts[meeting_type])
    ])
    
    chain = template | llm
    response = chain.invoke({"transcript": transcript})
    
    return response.content

# HEADER
st.title("🎯 AI Meeting Assistant")
st.markdown("### Transform meeting transcripts into actionable insights")

# SIDEBAR
with st.sidebar:
    
    
    st.markdown("### 📊 Stats")
    st.metric("Meetings Analyzed", len(st.session_state.meetings))
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.meetings = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Features
    
    ✅ Full Summary
    ✅ Action Items
    ✅ Quick Notes
    ✅ Participant Analysis
    """)

# MAIN CONTENT
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown('<div class="meeting-card">', unsafe_allow_html=True)
    st.subheader("📝 Meeting Details")
    
    meeting_title = st.text_input(
        "Meeting Title",
        placeholder="e.g., Q1 Planning Meeting"
    )
    
    meeting_date = st.date_input("Date", datetime.now())
    
    transcript = st.text_area(
        "Paste meeting transcript:",
        height=300,
        placeholder="""Example:
John: We need to finalize Q1 roadmap.
Sarah: I'll update specs by Wednesday.
Mike: Let's review on Friday."""
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("🎯 Analysis Type")
    analysis_type = st.radio(
        "Choose:",
        ["full_summary", "action_items", "quick_notes", "participant_insights"],
        format_func=lambda x: {
            "full_summary": "📋 Full Summary",
            "action_items": "✅ Action Items",
            "quick_notes": "⚡ Quick Notes",
            "participant_insights": "👥 Participants"
        }[x]
    )
    
    # ANALYZE BUTTON
    if st.button("🚀 Analyze Meeting", type="primary", use_container_width=True):
        if not transcript:
            st.warning("⚠️ Please paste a meeting transcript")
        elif not meeting_title:
            st.warning("⚠️ Please enter a meeting title")
        else:
            try:
                with st.spinner("🔍 Analyzing meeting..."):
                    analysis = analyze_meeting(transcript, analysis_type)
                    
                    st.session_state.meetings.insert(0, {
                        'title': meeting_title,
                        'date': meeting_date.strftime("%Y-%m-%d"),
                        'type': analysis_type,
                        'analysis': analysis,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    st.success("✅ Analysis complete!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col2:
    st.subheader("📊 Analysis Results")
    
    if st.session_state.meetings:
        latest = st.session_state.meetings[0]
        
        st.markdown(f"""
        <div class="meeting-card">
            <h2>📅 {latest['title']}</h2>
            <p>Date: {latest['date']} | Analyzed: {latest['timestamp']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(latest['analysis'])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 Download TXT",
                f"# {latest['title']}\n\n{latest['analysis']}",
                file_name="meeting_notes.txt"
            )
        with col_b:
            st.download_button(
                "📊 Download JSON",
                json.dumps(latest, indent=2),
                file_name="meeting_data.json"
            )
    else:
        st.info(" Analyze a meeting to see results here")

# HISTORY
if len(st.session_state.meetings) > 0:
    st.markdown("---")
    st.subheader("📚 Recent Meetings")
    
    for i, meeting in enumerate(st.session_state.meetings[:3]):
        with st.expander(f"📅 {meeting['title']} - {meeting['date']}"):
            st.markdown(meeting['analysis'][:300] + "...")

# SAMPLE TRANSCRIPT
with st.expander("📝 Try Sample Transcript"):
    if st.button("Load Sample"):
        st.code("""Sarah (PM): Let's review Q1 roadmap. Three major features to discuss.

John (Tech): Feature A needs 6 weeks. Can we split into phases?

Emma (Design): Phase 1 in 3 weeks, Phase 2 later?

Sarah: Good idea. John, send breakdown by Wednesday.

John: Will do by Wednesday EOD.

Mike (Marketing): Need 2 weeks before launch for campaigns.

Sarah: Noted. Emma, share mockups by Thursday.

Emma: No problem. I'll deliver Thursday.

Sarah: Feature B is top priority. John, can you deliver?

John: Yes, can deliver in 2 weeks if we start today.

Sarah: Perfect. Start today. I'll check in Monday.

Mike: I'll start drafting campaigns now.

Sarah: Great teamwork everyone. Meeting adjourned.""")
        st.info("☝️ Copy this sample and paste it in the transcript box")

# Footer
st.markdown("---")
st.markdown("**Built with:** Streamlit • Groq • LangChain")