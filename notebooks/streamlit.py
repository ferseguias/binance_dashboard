import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

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
st.sidebar.title("""Choose your wallet""")

options = st.sidebar.selectbox("Choose your wallet", ["All accounts", "Spot", "Futures", "Card"])

st.header(options)

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
    st.write("Top 10 holdings by it's current value in USDT:")
    st.table(current_balance.head(10))

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

    fig = plt.figure(figsize=(12, 6))
    sns.lineplot(x='year_month', y='total_value_accum', data=join)
    st.pyplot(fig)

    st.write(f'Total fees paid (to-date): {round(join.iloc[-1,-1], 2)} USDT')

    st.write(' ### Monthly account activity (transaction count)')
    st.write("Count of all transactions per month, including automatic fees charged by the exchange. It's very important to keep track of your trades to avoid overtrading.")
    account_activity = df.copy()
    account_activity['UTC_Time'] = account_activity['UTC_Time'].apply(lambda x: x.strftime('%Y-%m'))
    account_activity = account_activity.groupby('UTC_Time').count()
    account_activity.reset_index(inplace=True)

    fig = plt.figure(figsize=(12, 6))
    sns.barplot(x='UTC_Time', y='Change', data=account_activity)
    plt.ylabel('Transaction_count');

    st.pyplot(fig)

elif options == 'Spot':
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
    
    col1.subheader("Spot balance per coin")
    col1.write("(top 10 showed)")
    col1.table(balance_spot.head(10))

    col2.subheader("Spot account pie chart")

    pie = balance_spot.reset_index()
    pie['percentage'] = pie['USDT_value'] / pie['USDT_value'].sum()
    pie = pie.drop(['Change', 'USDT_price', 'USDT_value'], axis=1)
    others = pie.loc[pie['percentage'] < 0.015]
    pie.drop(others.index, inplace=True)
    others = {'Coin':'others', 'percentage': others['percentage'].sum()}
    pie = pie.append(others, ignore_index=True)

    fig = plt.figure(figsize=(20, 20))
    plt.pie(pie['percentage'], labels=pie['Coin'], autopct='%1.1f%%')

    col2.write("(relevant balances)")
    col2.pyplot(fig)
    
    st.write("### Select a coin to plot historic buy/sell orders")

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

        price_name = coin + 'USDT'
        buy_name = coin + '_buy'
        sell_name = coin + '_sell'

        temp = df_hist_prices[[price_name, buy_name, sell_name]]
        temp = temp.loc[(temp[buy_name] > 0) | (temp[sell_name] < 0)]

        temp[buy_name] = temp[buy_name].apply(lambda x: 1 if x > 0 else np.nan)
        temp[sell_name] = temp[sell_name].apply(lambda x: 1 if x < 0 else np.nan)
        temp[buy_name] = temp[buy_name] * temp[price_name]
        temp[sell_name] = temp[sell_name] * temp[price_name]

        fig = plt.figure(figsize=(12, 6))
        sns.lineplot(x=df.index, y=price_name, data=df, color='blue')
        sns.lineplot(x=temp.index, y=buy_name, data=temp, color='g', marker='o', label='buy', linestyle='')
        sns.lineplot(x=temp.index, y=sell_name, data=temp, color='r', marker='o', label='sell', linestyle='');
        plt.legend()
        st.pyplot(fig)
        
    coins_traded = list(trades.reset_index()['Coin'].unique())
    x_axis = st.selectbox("Choose a coin", (["Choose a coin"] + coins_traded) )

    if  x_axis == "Choose a coin":    
            st.write("Please choose a coin from the list")
    else:
        plot_trades(df_hist_prices, x_axis)

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
    fig = plt.figure(figsize=(12, 6))
    sns.lineplot(x=join.index, y='total_value_accum', data=join, label = 'total futures value accum in USDT')
    sns.lineplot(x=join_inv.index, y='total_value_accum', data=join_inv, label = 'total futures funding accum in USDT')

    st.write(f'Current value in futures account: {int(join.iloc[-1,-1])} USDT')
    st.write('In the plot below you will find in green the total value accumulated per month in futures account. In yellow, the total value invested in futures account.')
    st.pyplot(fig)

    st.write('''### Profit and loss accumulated in USDT per month.''')
    
    p_l = join['total_value_accum'] - join_inv['total_value_accum']
    
    if p_l[-1] > 0:
        st.write(f"You've made {int(p_l[-1])} USDT of profit in futures account")
        fig = plt.figure(figsize=(12, 6))
        sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='green')
    elif p_l[-1] < 0:
        st.write(f"You've lost {-int(p_l[-1])} USDT in futures account")
        fig = plt.figure(figsize=(12, 6))
        sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='red')
    else:
        st.write("You are in break even in futures account")
        fig = plt.figure(figsize=(12, 6))
        sns.lineplot(x=p_l.index, y=p_l, label = 'Profit or (loss)', color='blue')

    st.pyplot(fig)