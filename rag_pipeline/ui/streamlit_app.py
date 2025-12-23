"""
Streamlit UI for Cement RAG
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Cement Industry RAG Assistant",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Cement Industry RAG Assistant")
st.write("Ask questions about cement company conference calls")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    companies = st.multiselect(
        "Filter by Companies",
        options=[
            "ACC Limited", "Ambuja Cements", "UltraTech Cement",
            "Shree Cement", "Dalmia Bharat Ltd", "Grasim Industries"
        ]
    )
    
    date_range = st.date_input("Date Range", value=[])
    
    top_k = st.slider("Number of results", 1, 10, 5)

# Main chat interface
query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query:
        with st.spinner("Searching..."):
            # TODO: Implement RAG query
            st.write("Response will appear here")
            
            with st.expander("View Sources"):
                st.write("Source documents will appear here")
    else:
        st.warning("Please enter a question")

# Sample questions
st.sidebar.header("Sample Questions")
sample_questions = [
    "What was ACC's EBITDA margin in Q3 2024?",
    "Compare capacity utilization across companies",
    "What are the key industry trends?"
]

for q in sample_questions:
    if st.sidebar.button(q):
        st.rerun()
