from tkinter import Button
from turtle import color
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

#located in .py file
#streamlit run myfile.py

#[theme]
#base="dark"
#backgroundColor="#2f2f2f"
#secondaryBackgroundColor="#2f2f2f"
#font="monospace"

#imports
df = pd.read_excel('../database/export_binance/df_new.xlsx', index_col=0)
df_current_prices = pd.read_excel('../database/prices/current_prices.xlsx', index_col=0)
df_hist_prices = pd.read_excel('../database/prices/historical_prices.xlsx')
df_hist_prices.set_index('datetime', inplace=True)

#streamlit code
st.sidebar.image("../binance_image.png", use_column_width=True)

gen_options = st.sidebar.selectbox("What would you like to do?", ["Binance report", "Predictions"])

#st.header(gen_options)

if gen_options == "Binance report":

    st.sidebar.title("""YOUR BINANCE REPORT""")

    options = st.sidebar.selectbox("Choose your wallet", ["All accounts", "Spot", "Futures", "Binance card"])

    st.header(gen_options + ' - ' + options)

    if options == 'All accounts':
        #total account balance per coin, enhanced with a current price in USDT
        current_balance = df.groupby('Coin').sum()['Change']
        holding_prices = []
        for i in current_balance.index:
            if i == 'USDT':
                holding_prices.append(1)
            elif i == 'WETH':
                try:
                    price = df_current_prices.loc[df_current_prices['symbol'] == ('ETH' + 'USDT')]['price'].values[0]
                    holding_prices.append(price)
                except:
                    holding_prices.append(np.nan)
            else:
                try:
                    price = df_current_prices.loc[df_current_prices['symbol'] == (i + 'USDT')]['price'].values[0]
                    holding_prices.append(price)
                except:
                    holding_prices.append(np.nan)
        current_balance = pd.DataFrame(current_balance)
        current_balance['USDT_price'] = holding_prices
        current_balance['USDT_value'] = holding_prices * current_balance['Change']
        current_balance.sort_values(by='USDT_value', ascending=False, inplace=True)
        current_balance = current_balance.loc[current_balance['USDT_value'] > 1]
        current_balance.reset_index(inplace=True)

        st.write(' ### Your holdings overview')
        st.write("Top 5 holdings by it's current value in USDT:")
        st.table(current_balance.head(5))

        st.write(f'Current total value (all accounts): {round(current_balance["USDT_value"].sum(), 2)} USDT')

        st.write(' ### Fees paid overview')
        st.write("Accumulated fees paid in USDT (rebates discounted):")

        #get monthly fees paid per coin
        fees = df.loc[(df['Operation'] == 'Fee') | (df['Operation'] == 'Funding Fee') | (df['Operation'] == 'Referrer rebates')| (df['Operation'] == 'Commission Rebate')]
        fees['year_month'] = fees['UTC_Time'].dt.strftime('%Y-%m')
        fees_monthly_bal = fees.groupby(['year_month', 'Coin']).sum()['Change'].reset_index()
        fees_monthly_bal = fees_monthly_bal.pivot(index='year_month', columns='Coin', values='Change').fillna(0)

        end_dates = []
        for i in fees_monthly_bal.index:
            if i.split('-')[1] == '02':
                end_dates.append(i + '-28')
            elif i.split('-')[1] == '01' or i.split('-')[1] == '03' or i.split('-')[1] == '05' or i.split('-')[1] == '07' or i.split('-')[1] == '08' or i.split('-')[1] == '10' or i.split('-')[1] == '12':
                end_dates.append(i + '-31')
            else:
                end_dates.append(i + '-30')
        monthly_prices = df_hist_prices.loc[end_dates].reset_index()
        monthly_prices['datetime'] = monthly_prices['datetime'].dt.strftime('%Y-%m')
        monthly_prices.set_index('datetime', inplace=True)

        #join prices and balances to get value in USDT
        join = fees_monthly_bal.join(monthly_prices, how='outer')
        for i in fees_monthly_bal.columns:
            if i == 'USDT':
                pass
            else:
                name_price = i + 'USDT'
                join[i] = join[i] * join[name_price]
        join.drop(monthly_prices.columns, axis=1, inplace=True)
        join['total_value'] = -join.sum(axis=1)
        join['total_value_accum'] = join['total_value'].cumsum()

        fig = plt.figure(figsize=(12, 3))
        sns.lineplot(x='year_month', y='total_value_accum', data=join)
        st.pyplot(fig)

        st.write(f'Total fees paid (to-date): {round(join.iloc[-1,-1], 2)} USDT')

        st.write(' ### Monthly account activity (transaction count)')
        st.write("Count of all transactions per month, including automatic fees charged by the exchange. It's very important to keep track of your trades to avoid overtrading.")
        account_activity = df.copy()
        account_activity['UTC_Time'] = account_activity['UTC_Time'].apply(lambda x: x.strftime('%Y-%m'))
        account_activity = account_activity.groupby('UTC_Time').count()
        account_activity.reset_index(inplace=True)

        fig = plt.figure(figsize=(12, 3))
        sns.barplot(x='UTC_Time', y='Change', data=account_activity)
        plt.ylabel('Transaction_count');

        st.pyplot(fig)

    elif options == 'Spot':

        spot_options = st.sidebar.selectbox("Choose report type", ["Balance overview", "Trades per coin", 'Spot value/funding history'])

        if spot_options == 'Balance overview':
            st.subheader('Balance overview:')
            #spot balance per coin, enhanced with a current price in USDT
            df_spot = df.loc[df['Account'] == 'Spot']
            balance_spot = df_spot.groupby('Coin').sum()['Change']
            holding_prices = []
            for i in balance_spot.index:
                if i == 'USDT':
                    holding_prices.append(1)
                else:
                    try:
                        price = df_current_prices.loc[df_current_prices['symbol'] == (i + 'USDT')]['price'].values[0]
                        holding_prices.append(price)
                    except:
                        holding_prices.append(np.nan)
            balance_spot = pd.DataFrame(balance_spot)
            balance_spot['USDT_price'] = holding_prices
            balance_spot['USDT_value'] = holding_prices * balance_spot['Change']
            print(f'current total value: {round(balance_spot["USDT_value"].sum(), 2)} USDT')
            balance_spot.sort_values(by='USDT_value', ascending=False, inplace=True)
            balance_spot = balance_spot.loc[balance_spot['USDT_value'] > 1]
            
            col1, col2 = st.columns([2, 2])
            
            col1.write("##### Spot balance per coin")
            col1.write("###### (top 10 showed)")
            col1.table(balance_spot.head(10))

            col2.write("##### Spot account pie chart")

            pie = balance_spot.reset_index()
            pie['percentage'] = pie['USDT_value'] / pie['USDT_value'].sum()
            pie = pie.drop(['Change', 'USDT_price', 'USDT_value'], axis=1)
            others = pie.loc[pie['percentage'] < 0.015]
            pie.drop(others.index, inplace=True)
            others = {'Coin':'others', 'percentage': others['percentage'].sum()}
            pie = pie.append(others, ignore_index=True)

            fig = plt.figure(figsize=(5, 5))
            plt.pie(pie['percentage'], autopct='%1.1f%%', startangle=90, pctdistance=1.2)
            plt.legend(loc='upper left', labels=pie['Coin'], bbox_to_anchor=(-0.1, 1.1))

            col2.write("###### (coins with less than 1.5% share is shown as 'others')")
            col2.pyplot(fig)

            st.write(f'Total current value in spot account: {int(balance_spot["USDT_value"].sum())} USDT')

            #number of total trades
            df_spot = df.loc[df['Account'] == 'Spot']
            balance_spot = df_spot.groupby('Coin').sum()['Change']
            total_trades = df_spot[df_spot['Operation'].isin(['Buy', 'Large OTC Trading', 'Sell', 'Small assets exchange BNB', 'Transaction Related'])]
            total_trades = total_trades.groupby('UTC_Time').agg({'Operation': 'count'}).reset_index()
            total_trades['Operation'] = 1
            total_trades = total_trades['Operation'].sum()
            st.write(f"You've made total of {total_trades} trades in your spot account.")
        
        elif spot_options == 'Trades per coin':
            st.subheader('Trades per coin')

            #get trade related operations
            trades = df.loc[((df['Operation'] == 'Buy')) | ((df['Operation'] == 'Sell')) | ((df['Operation'] == 'Large OTC trading')) | ((df['Operation'] == 'Small assets exchange BNB')) | ((df['Operation'] == 'Transaction Related'))]
            #separate columns for buy and sell and cut time from datetime
            trades['buy'] = trades['Change'].apply(lambda x: x if x > 0 else np.nan)
            trades['sell'] = trades['Change'].apply(lambda x: x if x < 0 else np.nan)
            trades['UTC_Time'] = trades['UTC_Time'].apply(lambda x: x.strftime('%Y-%m-%d'))
            trades = trades[['UTC_Time', 'buy', 'sell', 'Coin']].set_index('UTC_Time').sort_values(by=['Coin', 'buy'])
            #delete duplicated dates
            trades = trades.reset_index().groupby(['UTC_Time', 'Coin']).agg({'buy': 'sum', 'sell': 'sum'}).reset_index().sort_values(by=['Coin', 'UTC_Time'])
            trades = trades.replace(0,np.nan)
            trades['UTC_Time'] = pd.to_datetime(trades['UTC_Time'])
            trades.set_index('UTC_Time', inplace=True)

            #integrate historical prices with trades
            for i in trades['Coin'].unique():
                buy_name = i + '_buy'
                sell_name = i + '_sell'
                temp = trades.loc[trades['Coin'] == i]
                temp[buy_name] = temp['buy']
                temp[sell_name] = temp['sell']
                temp.drop(['Coin', 'buy', 'sell'], axis=1, inplace=True)
                df_hist_prices = pd.merge(df_hist_prices, temp, how='outer', left_index=True, right_index=True)

            #plot trades and prices (input coin name)
            def plot_trades(df, coin):
                if coin == 'USDT':
                    st.write("USDT trades do not generate plot as exchange ratio is 1.")
                else:
                    price_name = coin + 'USDT'
                    buy_name = coin + '_buy'
                    sell_name = coin + '_sell'

                    temp = df_hist_prices[[price_name, buy_name, sell_name]]
                    temp = temp.loc[(temp[buy_name] > 0) | (temp[sell_name] < 0)]

                    temp[buy_name] = temp[buy_name].apply(lambda x: 1 if x > 0 else np.nan)
                    temp[sell_name] = temp[sell_name].apply(lambda x: 1 if x < 0 else np.nan)
                    temp[buy_name] = temp[buy_name] * temp[price_name]
                    temp[sell_name] = temp[sell_name] * temp[price_name]

                    fig = plt.figure(figsize=(12, 3))
                    sns.lineplot(x=df.index, y=price_name, data=df, color='white')
                    sns.lineplot(x=temp.index, y=buy_name, data=temp, color='g', marker='o',   label='buy', linestyle='', markersize=10)
                    sns.lineplot(x=temp.index, y=sell_name, data=temp, color='r', marker='o', label='sell', linestyle='', markersize=10);
                    plt.legend()
                    st.pyplot(fig)

            coins_traded = list(trades.reset_index()['Coin'].unique())
            x_axis = st.selectbox("Select a coin to plot historic buy/sell orders", (["Choose a coin"] + coins_traded) )

            if  x_axis == "Choose a coin":    
                    st.write("Please choose a coin from the list above...")
            else:
                plot_trades(df_hist_prices, x_axis)

            if x_axis == "Choose a coin":
                pass
            else:
                st.write("""### Trade transactions performed on the selected coin""")
                st.write("Explanation: results are based on selected coin. Dataset below shows all trades performed including amount traded, accumulated holding, transaction price in USDT***, amount paid in USDT and total investment in USDT.")
                            
                if x_axis == "USDT":
                    trades_coin = trades.loc[trades['Coin'] == x_axis].reset_index()
                    trades_coin = trades_coin.fillna(0)
                    trades_coin['amount_traded'] = trades_coin['buy'] + trades_coin['sell']
                    trades_coin.drop(['buy', 'sell'], axis=1, inplace=True)
                    trades_coin['UTC_Time'] = trades_coin['UTC_Time'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    trades_coin['buy_sell'] = trades_coin['amount_traded'].apply(lambda x: "buy" if x > 0 else "sell")
                    trades_coin['accum_balance'] = trades_coin['amount_traded'].cumsum()
                    trades_coin = trades_coin.reindex(columns=['UTC_Time', 'Coin', 'buy_sell', 'amount_traded', 'accum_balance'])
                    trades_coin['trade_USDT'] = trades_coin['amount_traded']
                    trades_coin['accum_inv_USDT'] = trades_coin['trade_USDT'].cumsum()
                elif x_axis == "WETH":
                    trades_coin = trades.loc[trades['Coin'] == x_axis].reset_index()
                    trades_coin = trades_coin.fillna(0)
                    trades_coin['amount_traded'] = trades_coin['buy'] + trades_coin['sell']
                    trades_coin.drop(['buy', 'sell'], axis=1, inplace=True)
                    trades_coin['UTC_Time'] = trades_coin['UTC_Time'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    trades_coin['buy_sell'] = trades_coin['amount_traded'].apply(lambda x: "buy" if x > 0 else "sell")
                    trades_coin['accum_balance'] = trades_coin['amount_traded'].cumsum()
                    trades_coin = trades_coin.reindex(columns=['UTC_Time', 'Coin', 'buy_sell', 'amount_traded', 'accum_balance'])
                    trade_price = pd.DataFrame(df_hist_prices.loc[trades_coin['UTC_Time'].unique(), ('ETH' + 'USDT')])
                    trade_price.reset_index(inplace=True)
                    trades_coin['price'] = trade_price[('ETH' + 'USDT')]
                    trades_coin['trade_USDT'] = trades_coin['amount_traded'] * trades_coin['price']
                    trades_coin['accum_inv_USDT'] = trades_coin['trade_USDT'].cumsum()
                else:
                    trades_coin = trades.loc[trades['Coin'] == x_axis].reset_index()
                    trades_coin = trades_coin.fillna(0)
                    trades_coin['amount_traded'] = trades_coin['buy'] + trades_coin['sell']
                    trades_coin.drop(['buy', 'sell'], axis=1, inplace=True)
                    trades_coin['UTC_Time'] = trades_coin['UTC_Time'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    trades_coin['buy_sell'] = trades_coin['amount_traded'].apply(lambda x: "buy" if x > 0 else "sell")
                    trades_coin['accum_balance'] = trades_coin['amount_traded'].cumsum()
                    trades_coin = trades_coin.reindex(columns=['UTC_Time', 'Coin', 'buy_sell', 'amount_traded', 'accum_balance'])
                    trade_price = pd.DataFrame(df_hist_prices.loc[trades_coin['UTC_Time'].unique(), (x_axis + 'USDT')])
                    trade_price.reset_index(inplace=True)
                    trades_coin['price'] = trade_price[(x_axis + 'USDT')]
                    trades_coin['trade_USDT'] = trades_coin['amount_traded'] * trades_coin['price']
                    trades_coin['accum_inv_USDT'] = trades_coin['trade_USDT'].cumsum()

                st.table(trades_coin)
                
                if x_axis == "WETH":
                    holding_value = df_current_prices.loc[df_current_prices['symbol'] == ('ETH' + 'USDT')].iloc[-1,-1] * trades_coin['accum_balance'].iloc[-1]
                    st.write(f'{x_axis} trading holding current value = {int(holding_value)} USDT')
                    profit_loss_trade = holding_value - trades_coin['accum_inv_USDT'].iloc[-1]
                    st.write(f'BTC trading profit/(loss) = {int(profit_loss_trade)} USDT')
                elif x_axis == "USDT":
                    holding_value = trades_coin['accum_balance'].iloc[-1]
                    st.write(f'{x_axis} trading holding current value = {int(holding_value)} USDT')
                    profit_loss_trade = holding_value - trades_coin['accum_inv_USDT'].iloc[-1]
                    st.write(f'{x_axis} trading profit/(loss) = {int(profit_loss_trade)} USDT')
                else:            
                    holding_value = df_current_prices.loc[df_current_prices['symbol'] == (x_axis + 'USDT')].iloc[-1,-1] * trades_coin['accum_balance'].iloc[-1]
                    st.write(f'{x_axis} trading holding current value = {int(holding_value)} USDT')
                    profit_loss_trade = holding_value - trades_coin['accum_inv_USDT'].iloc[-1]
                    st.write(f'{x_axis} trading profit/(loss) = {int(profit_loss_trade)} USDT')
        elif spot_options == 'Spot value/funding history':
            st.subheader('Spot value/funding history')
            st.write('This section shows monthly value in spot account vs total investment in USDT.')

            df_spot = df.loc[df['Account'] == 'Spot']
            df_spot['year_month'] = df_spot['UTC_Time'].dt.strftime('%Y-%m')
            monthly_bal = df_spot.groupby(['year_month', 'Coin']).sum()['Change'].reset_index()
            monthly_bal = monthly_bal.pivot(index='year_month', columns='Coin', values='Change').fillna(0)
            monthly_bal = monthly_bal.cumsum()

            #import month-end prices for all coins in USDT
            df_hist_prices = pd.read_excel('../database/prices/historical_prices.xlsx')
            df_hist_prices.set_index('datetime', inplace=True)

            end_dates = []
            for i in monthly_bal.index:
                if i.split('-')[1] == '02':
                    end_dates.append(i + '-28')
                elif i.split('-')[1] == '01' or i.split('-')[1] == '03' or i.split('-')[1] == '05' or i.split('-')[1] == '07' or i.split('-')[1] == '08' or i.split('-')[1] == '10' or i.split('-')[1] == '12':
                    end_dates.append(i + '-31')
                else:
                    end_dates.append(i + '-30')
            monthly_prices = df_hist_prices.loc[end_dates].reset_index()
            monthly_prices['datetime'] = monthly_prices['datetime'].dt.strftime('%Y-%m')
            monthly_prices.set_index('datetime', inplace=True)

            #join prices and balances to get value in USDT
            join = monthly_bal.join(monthly_prices, how='outer')
            for i in monthly_bal.columns:
                if i == 'USDT':
                    pass
                else:
                    name_price = i + 'USDT'
                    join[i] = join[i] * join[name_price]
            join.drop(monthly_prices.columns, axis=1, inplace=True)
            join['total_value'] = join.sum(axis=1)
            
            investmenst = df_spot.loc[(df_spot['Operation'] == 'Deposit') | (df_spot['Operation'] == 'Withdraw') | (df_spot['Operation'] == 'transfer_in') | (df_spot['Operation'] == 'transfer_out')]
            inv_monthly_bal = investmenst.groupby(['year_month', 'Coin']).sum()['Change'].reset_index()
            inv_monthly_bal = inv_monthly_bal.pivot(index='year_month', columns='Coin', values='Change').fillna(0)
            #inv_monthly_bal = inv_monthly_bal.cumsum()

            col = []
            for i in inv_monthly_bal.columns.drop('USDT'):
                name_price = i + 'USDT'
                col.append(name_price)
                
            end_dates = []
            for i in inv_monthly_bal.index:
                if i.split('-')[1] == '02':
                    end_dates.append(i + '-28')
                elif i.split('-')[1] == '01' or i.split('-')[1] == '03' or i.split('-')[1] == '05' or i.split('-')[1] == '07' or i.split('-')[1] == '08' or i.split('-')[1] == '10' or i.split('-')[1] == '12':
                    end_dates.append(i + '-31')
                else:
                    end_dates.append(i + '-30')
            inv_monthly_prices = df_hist_prices.loc[end_dates].reset_index()
            inv_monthly_prices['datetime'] = inv_monthly_prices['datetime'].dt.strftime('%Y-%m')
            inv_monthly_prices.set_index('datetime', inplace=True)
            inv_monthly_prices = inv_monthly_prices.loc[:,col]

            join_inv = inv_monthly_bal.join(inv_monthly_prices, how='outer')
            for i in inv_monthly_bal.columns:
                if i == 'USDT':
                    pass
                else:
                    name_price = i + 'USDT'
                    join_inv[i] = join_inv[i] * join_inv[name_price]
            join_inv.drop(inv_monthly_prices.columns, axis=1, inplace=True)
            join_inv['total_value'] = join_inv.sum(axis=1)
            join_inv['total_value'] = join_inv['total_value'].cumsum()

            #plot monthly balance in USDT and investment in USDT
            fig = plt.figure(figsize=(12, 4))
            sns.lineplot(x=join.index, y='total_value', data=join, label='spot balance in USDT')
            sns.lineplot(x=join_inv.index, y='total_value', data=join_inv, label='total funding in USDT')
            st.pyplot(fig)

            st.write('When blue line is over the yellow line, spot account is considered in profit. When blue line cross yellow line, spot account is considered in loss.')

    elif options == 'Futures':
        st.write("### Futures account overview")
        
        df_futures = df.loc[df['Account'] == 'USDT-Futures']
        df_futures['year_month'] = df_futures['UTC_Time'].dt.strftime('%Y-%m')
        futures_monthly_bal = df_futures.groupby(['year_month', 'Coin']).sum()['Change'].reset_index()
        futures_monthly_bal = futures_monthly_bal.pivot(index='year_month', columns='Coin', values='Change').fillna(0)

        end_dates = []
        for i in futures_monthly_bal.index:
            if i.split('-')[1] == '02':
                end_dates.append(i + '-28')
            elif i.split('-')[1] == '01' or i.split('-')[1] == '03' or i.split('-')[1] == '05' or i.split('-')[1] == '07' or i.split('-')[1] == '08' or i.split('-')[1] == '10' or i.split('-')[1] == '12':
                end_dates.append(i + '-31')
            else:
                end_dates.append(i + '-30')
        monthly_prices = df_hist_prices.loc[end_dates].reset_index()
        monthly_prices['datetime'] = monthly_prices['datetime'].dt.strftime('%Y-%m')
        monthly_prices.set_index('datetime', inplace=True)

        #join prices and balances to get value in USDT
        join = futures_monthly_bal.join(monthly_prices, how='outer')
        for i in futures_monthly_bal.columns:
            if i == 'USDT':
                pass
            else:
                name_price = i + 'USDT'
                join[i] = join[i] * join[name_price]
        join.drop(monthly_prices.columns, axis=1, inplace=True)
        join['total_value'] = join.sum(axis=1)
        join['total_value_accum'] = join['total_value'].cumsum()

        funding = df_futures.loc[(df_futures['Operation'] == 'transfer_in') | (df_futures['Operation'] == 'transfer_out')]
        funding['year_month'] = funding['UTC_Time'].dt.strftime('%Y-%m')
        futures_inv_monthly_bal = funding.groupby(['year_month', 'Coin']).sum()['Change'].reset_index()
        futures_inv_monthly_bal = futures_inv_monthly_bal.pivot(index='year_month', columns='Coin', values='Change').fillna(0)
        
        end_dates = []
        for i in futures_inv_monthly_bal.index:
            if i.split('-')[1] == '02':
                end_dates.append(i + '-28')
            elif i.split('-')[1] == '01' or i.split('-')[1] == '03' or i.split('-')[1] == '05' or i.split('-')[1] == '07' or i.split('-')[1] == '08' or i.split('-')[1] == '10' or i.split('-')[1] == '12':
                end_dates.append(i + '-31')
            else:
                end_dates.append(i + '-30')
        monthly_prices = df_hist_prices.loc[end_dates].reset_index()
        monthly_prices['datetime'] = monthly_prices['datetime'].dt.strftime('%Y-%m')
        monthly_prices.set_index('datetime', inplace=True)

        #join prices and balances to get value in USDT
        join_inv = futures_inv_monthly_bal.join(monthly_prices, how='outer')
        for i in futures_inv_monthly_bal.columns:
            if i == 'USDT':
                pass
            else:
                name_price = i + 'USDT'
                join_inv[i] = join_inv[i] * join_inv[name_price]
        join_inv.drop(monthly_prices.columns, axis=1, inplace=True)
        join_inv['total_value'] = join_inv.sum(axis=1)
        join_inv['total_value_accum'] = join_inv['total_value'].cumsum()

        #plot monthly futures account value in USDT and investment in USDT
        fig = plt.figure(figsize=(12, 3))
        sns.lineplot(x=join.index, y='total_value_accum', data=join, label = 'total futures value accum in USDT')
        sns.lineplot(x=join_inv.index, y='total_value_accum', data=join_inv, label = 'total futures funding accum in USDT')

        st.write(f'Current value in futures account: {int(join.iloc[-1,-1])} USDT')
        st.write('In the plot below you will find in green the total value accumulated per month in futures account. In yellow, the total value invested in futures account.')
        st.pyplot(fig)

        st.write('''### Profit and loss accumulated in USDT per month.''')
        
        p_l = join['total_value_accum'] - join_inv['total_value_accum']
        
        if p_l[-1] > 0:
            st.write(f"You've made {int(p_l[-1])} USDT of profit in futures account")
            fig = plt.figure(figsize=(12, 3))
            sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='green')
        elif p_l[-1] < 0:
            st.write(f"You've lost {-int(p_l[-1])} USDT in futures account")
            fig = plt.figure(figsize=(12, 3))
            sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='red')
        else:
            st.write("You are in break even in futures account")
            fig = plt.figure(figsize=(12, 3))
            sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='blue')

        st.pyplot(fig)
    elif options == 'Binance card':
        st.write('''### Card account overview.''')

        df_card = df.loc[df['Account'] == 'Card']
        card_balance = pd.DataFrame(df_card.groupby('Coin').sum()['Change'])

        holding_prices = []
        for i in card_balance.index:
            if i == 'USDT':
                holding_prices.append(1)
            else:
                try:
                    price = df_current_prices.loc[df_current_prices['symbol'] == (i + 'USDT')]['price'].values[0]
                    holding_prices.append(price)
                except:
                    holding_prices.append(np.nan)
        card_balance = pd.DataFrame(card_balance)
        card_balance['USDT_price'] = holding_prices
        card_balance['USDT_value'] = holding_prices * card_balance['Change']
        print(f'current total value: {round(card_balance["USDT_value"].sum(), 2)} USDT')
        card_balance.sort_values(by='USDT_value', ascending=False, inplace=True)
        card_balance = card_balance.loc[card_balance['USDT_value'] > 1]
        st.table(card_balance)


        st.write('''### Expenses and rewards accumulated.''')
        st.write('''Both plots, expenses and cashback are reflected in transaction coin.''')



        expenses = df_card.loc[df_card['Operation'] == 'Binance Card Spending']
        expenses['year_month'] = expenses['UTC_Time'].dt.strftime('%Y-%m')
        expenses = expenses.pivot_table(index='year_month', columns='Coin', values='Change', aggfunc=np.sum)

        rewards = df_card.loc[df_card['Operation'] == 'Card Cashback']
        rewards['year_month'] = rewards['UTC_Time'].dt.strftime('%Y-%m')
        rewards = rewards.pivot_table(index='year_month', columns='Coin', values='Change', aggfunc=np.sum)

        fig, ax = plt.subplots(2, 1, figsize = (8,5))
        ax = ax.flat
        sns.lineplot(data=expenses.cumsum()*-1, ax = ax[0], legend=True, palette='GnBu_d', linewidth=1.5)
        ax[0].set_title('Binance Card Spending')
        ax[0].set_ylabel('Amount')
        sns.lineplot(data=rewards.cumsum(), ax = ax[1], legend=True, palette='YlOrRd', linewidth=1.5)
        ax[1].set_title('Card Cashback')
        ax[1].set_ylabel('Amount')
        plt.tight_layout()
        
        st.pyplot(fig)

        st.write('''### Card funding transactions.''')
        st.write('''Keep track of funding transactions, regulary the counterparty of these transfers in/out is spot account.''')

        funding_card = pd.DataFrame(df_card.loc[(df_card['Operation'] == 'transfer_in') | (df_card['Operation'] == 'transfer_out')])
        funding_card['year_month'] = funding_card['UTC_Time'].dt.strftime('%Y-%m')
        funding_card = funding_card.groupby(['Coin', 'year_month']).sum()['Change'].reset_index()

        st.table(funding_card)

        st.write(f'Total net funding in card account: {int(funding_card["Change"].sum())} EUR')


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

        period = n_weeks * 7
        START = "2014-01-01"
        TODAY = date.today().strftime("%Y-%m-%d")

        st.title('Crypto Forecast App')


   
        st.write(f'### Pair selected {selected_coin}')

        @st.cache
        def load_data(ticker):
            data = yf.download(ticker, START, TODAY)
            data.reset_index(inplace=True)
            return data

        data = load_data(selected_coin)

        #st.subheader('Raw data')
        #st.write(data.tail())

        # Predict forecast with Prophet.
        df_train = data[['Date','Close']]
        df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

        # Show and plot forecast
        #st.subheader('Forecast data')
        #st.write(forecast.tail())
        
        fig1 = plot_plotly(m, forecast)
        fig1.update_layout(title=f'Forecast plot for {n_weeks} weeks (fbPROPHET)', xaxis_title='Date', yaxis_title='Price')
        fig1.update_xaxes(rangeselector_activecolor='orange')
        fig1.update_xaxes(rangeselector_bgcolor='black')
        
        st.plotly_chart(fig1, use_container_width=True)

        if plot_comp:
            st.write(f"Forecast components for {selected_coin}")
            fig2 = m.plot_components(forecast)
            st.write(fig2)
        else:
            pass