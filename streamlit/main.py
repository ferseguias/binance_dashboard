#import functions
import sys
sys.path.append('../')
import src.ferseg as fs

#import libraries
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from datetime import date
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
warnings.filterwarnings('ignore')
plt.style.use('dark_background')
plt.rcParams['font.size'] = '10'

#import data
df = pd.read_excel('../database/export_binance/df_new.xlsx', index_col=0)
df_current_prices = pd.read_excel('../database/prices/current_prices.xlsx', index_col=0)
df_hist_prices = pd.read_excel('../database/prices/historical_prices.xlsx')
df_hist_prices.set_index('datetime', inplace=True)

#streamlit code
st.sidebar.image("../binance_image.png", use_column_width=True)
gen_options = st.sidebar.selectbox("What would you like to do?", ["Binance report", "Predictions"])
if gen_options == "Binance report":
    st.sidebar.title("""YOUR BINANCE REPORT""")
    options = st.sidebar.selectbox("Choose your wallet", ["All accounts", "Spot", "Futures", "Binance card"], )
    st.header(gen_options + ' - ' + options)
    if options == 'All accounts':
        #top 5 hondings
        st.write('### Your holdings overview')
        st.write("Top 5 holdings by it's current value in USDT:")
        current_balance = fs.current_balance(df, df_current_prices)
        st.table(current_balance.head(5))
        st.write(f'Current total value (all accounts): {round(current_balance["USDT_value"].sum(), 2)} USDT')
        #fees
        st.write('### Fees paid overview')
        st.write("Accumulated fees paid in USDT (rebates discounted):")
        fig1 = fs.plot_total_fees(df, df_hist_prices)
        st.pyplot(fig1)
        total_fees_paid = fs.total_fees_paid(df, df_hist_prices)
        st.write(f'Total fees paid (to-date): {total_fees_paid} USDT')
        #account activity
        st.write('### Monthly account activity (transaction count)')
        st.write("Count of all transactions per month, including automatic fees charged by the exchange. It's very important to keep track of your trades to avoid overtrading.")
        fig2 = fs.plot_account_activity(df)
        st.pyplot(fig2)
    elif options == 'Spot':
        spot_options = st.sidebar.selectbox("Choose report type", ["Balance overview", "Trades per coin", 'Spot value/funding history'])
        if spot_options == 'Balance overview':
            st.subheader('Balance overview:')
            col1, col2 = st.columns([2, 2])
            #spot balance
            col1.write("##### Spot balance per coin")
            col1.write("###### (top 10 showed)")
            balance_spot = fs.spot_balance(df, df_current_prices)
            col1.table(balance_spot.head(10))
            #plot pie
            col2.write("###### (coins with less than 1.5% share are shown as 'others')")
            fig3 = fs.plot_spot_pie(df, df_current_prices)
            col2.pyplot(fig3)
            st.write(f'Total current value in spot account: {int(balance_spot["USDT_value"].sum())} USDT')
            total_trades_spot = fs.total_trades_spot(df)
            st.write(f"You've made total of {total_trades_spot} trades in your spot account.")
        elif spot_options == 'Trades per coin':
            st.subheader('Trades per coin')
            coins_traded = fs.coins_traded(df)
            x_axis = st.selectbox("Select a coin to plot historic buy/sell orders", (["Choose a coin"] + coins_traded) )
            if x_axis == "Choose a coin":
                st.write("Please choose a coin from the list above...")
            else:
                if x_axis == 'USDT':
                    st.write("USDT trades do not generate plot as exchange ratio is 1.")
                else:
                    fig4 = fs.plot_trades(df, df_hist_prices, x_axis)
                    st.pyplot(fig4)
                    st.write("""### Trade transactions performed on the selected coin""")
                    st.write("Explanation: results are based on selected coin. Dataset below shows all trades performed including amount traded, accumulated holding, transaction price in USDT***, amount paid in USDT and total investment in USDT.")
                    trades_coin = fs.trades_coin(df, df_hist_prices, x_axis)
                    st.table(trades_coin)
                    holding_value = fs.holding_value(df_current_prices, x_axis, trades_coin)
                    st.write(f'{x_axis} trading holding current value = {int(holding_value)} USDT')
                    profit_loss_trade = fs.profit_loss_trade(x_axis, holding_value, trades_coin)
                    st.write(f'{x_axis} trading profit/(loss) = {int(profit_loss_trade)} USDT')
        elif spot_options == 'Spot value/funding history':
            st.subheader('Spot value/funding history')
            st.write('This section shows monthly value in spot account vs total investment in USDT.')
            fig5 = fs.plot_investment_value(df, df_hist_prices)
            st.pyplot(fig5)
            st.write('When blue line is over the yellow line, spot account is considered in profit. When blue line cross yellow line, spot account is considered in loss.')
    elif options == 'Futures':
        st.write("### Futures account overview")
        futures_balance = fs.futures_balance(df, df_hist_prices)
        st.write(f'Current value in futures account: {int(futures_balance.iloc[-1,-1])} USDT')
        st.write('In the plot below you will find in green the total value accumulated per month in futures account. In yellow, the total value invested in futures account.')
        fig6 = fs.plot_futures(df, df_hist_prices)
        st.pyplot(fig6)
        st.write('''### Profit and loss accumulated in USDT per month.''')
        p_l = fs.profit_loss(df, df_hist_prices)
        fig7 = fs.plot_profit_loss(p_l)
        st.pyplot(fig7)
        if p_l[-1] > 0:
            st.write(f"You've made {int(p_l[-1])} USDT of profit in futures account")
        elif p_l[-1] < 0:
            st.write(f"You've lost {-int(p_l[-1])} USDT in futures account")
        else:
            st.write("You are in break even in futures account")
    elif options == 'Binance card':
        st.write('''### Card account overview.''')
        card_balance = fs.card_balance(df, df_current_prices)
        st.write(f'current total value: {round(card_balance["USDT_value"].sum(), 2)} USDT')
        st.table(card_balance)
        st.write('''### Expenses and rewards accumulated.''')
        st.write('''Both plots, expenses and cashback are reflected in transaction coin.''')
        fig8 = fs.plot_expenses_cashback(df, df_current_prices)
        st.pyplot(fig8)
        st.write('''### Card funding transactions.''')
        st.write('''Keep track of funding transactions, regulary the counterparty of these transfers in/out is spot account.''')
        card_funding = fs.card_funding(df)
        st.table(card_funding)
        st.write(f'Total net funding in card account: {int(card_funding["Change"].sum())} EUR')
if gen_options == "Predictions":
    coins = ('- Select pair -', 'BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOT-USD', 'DOGE-USD', 'SHIB-USD', 'AVAX-USD', 'LTC-USD', 'LINK-USD', 'XLM-USD', 'MATIC-USD')  
    coins = sorted(coins)  
    selected_coin = st.sidebar.selectbox("Choose a pair from the list", coins)
    if selected_coin == '- Select pair -':
        st.title('Crypto Forecast App') 
        st.write('Please select a pair from the list...')
    else:
        n_weeks = st.sidebar.slider('Weeks of prediction:', 5, 25, 5)
        plot_comp = st.sidebar.checkbox('Click here to plot forecast components', value=False)
        st.title('Crypto Forecast App')
        st.write(f'### Pair selected {selected_coin}')
        period = n_weeks * 7
        START = "2014-01-01"
        TODAY = date.today().strftime("%Y-%m-%d")
        data = fs.load_data(selected_coin, START, TODAY)
        fig9, fig10 = fs.plot_predictions(data, period, n_weeks)
        st.plotly_chart(fig9, use_container_width=True)
        if plot_comp:
            st.write(f"Forecast components for {selected_coin}")
            st.write(fig10)
        else:
            pass