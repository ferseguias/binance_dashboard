import streamlit as st
import pandas as pd
import finac as f

st.sidebar.title("""Python accounting CRM""")

options = st.sidebar.selectbox("Welcome, let's get started! What would you like to do?", ["How does it work", "Add new account", "View all accounts"])

st.header(options)

if options ==  "How does it work":
    st.write("""This is a simple CRM for accounting. You can add new accounts, view all accounts, and edit them.""")
elif options == "Add new account":
    st.write("""Single/ mass upload?""")
    

    account = st.text_input('Account name:', value="")
    asset = st.text_input('Asset:', value="")
    tp = st.text_input('Type:', value="")
    note = st.text_input('Note:', value="")

    f.init('/tmp/test.db')
    f.core.account_create(account=account, asset=asset, tp=tp, note=note)
elif options == "View all accounts":
    st.write("""These are the accounts you have added""")