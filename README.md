# final_project_ironhack_binance_dashboard

![portada](https://www.criptoinversion.org/wp-content/uploads/2020/11/Binance-dobla-su-apoyo-al-ecosistema-del-etereo.png)

# Objetive 🎯
In my personal opinion, investors struggle on having their investment transaction history updated or in many cases they just give up on that!

It's really important to keep track of your porfolio and properly analize your performance to learn from past experiences.

Having all transactions on hand, is possible to provide balances for different operations such as total funding, total account profit/loss, total fees paid, etc.

This is why I've created a stremlit dashboard with most relevant information for Binance Crypto Exchange investors.

# Data sources 📊
As most investment platforms, Binance Crypto Exchange gives the possibility to their users to download their transactions history in file.csv. This is where all it all starts... 

Simple steps:
1. Log in into your Binance account
2. "Wallet" --> "Overview"
3. "Transaction history"
4. "Generate all statements" --> Select dates (from the first transaction)
5. Do not mark "Hide transfer record"
6. Download .csv file

This file.csv contains the following columns:
1. User_ID: your account id
2. UTC_Time: transaction UTC time
3. Account: your account type (Spot, Futures, Binance Card, etc)
4. Operation: operation type (Buy, Sell, Deposit, Withdraw, etc)
5. Coin: transaction coin
6. Change: transaction amount
7. Remark: extra comments

As file.csv cointains confidential information, I've created simulated file.csv for this project. All transactions are fake.

Additionally, to get current prices and historic prices for all coins included in the file.csv, I've used Binance API (API_KEY and SECRET_KEY are needed)

# Streamlit dashboard structure 📦
a) Binance report: this is the main area where you can explore all data analized per account (Spot, Futures and Binance Card).

- Spot: you can choose from different reports in this section such as "Overview", "Trades per coin", and "Spot value/funding history".

- Futures: here you can check your trading performance in futures account.

- Binance Card: keep track of your expenses and cashback received.

b) Predictions: as an extra information for users, I've created a simple price prediction model using Prophet. Here you can choose prediction period and a coin from a fixed list to plot predictions and components.
