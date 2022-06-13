import streamlit as st
import pandas as pd

#located in .py file
#streamlit run myfile.py

st.sidebar.title("""    """)

options = st.sidebar.selectbox("Welcome, let's get started! What would you like to do?", ["How does it work", "Add new account", "View all accounts"])

st.header(options)