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
3. Account: your account type (Spot, Futures, Binance Card, etc.)
4. Operation: operation type (Buy, Sell, Deposit, Withdraw, etc.)
5. Coin: transaction coin
6. Change: transaction amount
7. Remark: extra comments

As file.csv cointains confidential information, I've simulated file.csv for this project. All transactions are fake.

# Notebooks 📒
All accounts/wallets analysis included in streamlit are detailed in notebooks folder. However, there is a src folder which incudes all functions imported for streamlit.py file.

Explore "get_current_prices.ipynb" and "get_interval_prices.ipynb" to get current prices and historic prices for all coins included in the file.csv. It requires Binance API (API_KEY and SECRET_KEY).

# Streamlit dashboard structure 📦
1. Binance report: this is the main area where you can explore all data analized per account (Spot, Futures and Binance Card).

    - Spot: you can choose from different reports in this section such as "Overview", "Trades per coin", and "Spot value/funding history".

    - Futures: here you can check your trading performance in futures account.

    - Binance Card: keep track of your expenses and cashback received.

2. Predictions: as an extra information for users, I've created a simple price prediction model using Prophet. Here you can choose prediction period and a coin from a fixed list to plot predictions and components.

Check out the next section to have a better look of streamlit dashboard...

# Streamlit walk around 🚶🏽‍♂️
Click on image below to watch the video:
[![Watch the video](https://raw.githubusercontent.com/ferseguias/final_project_ironhack/main/images/youtube_image.png)](https://www.youtube.com/watch?v=vvlb0zWMCUw)

# Scope limitations and next steps ⏭
- Prices database used daily frequency, however, price changes every second. To obtain sharpen figures, prices database should have frequence per second.

- All kind of transactions possible are not taken into account. For those unknown transactions, code should be updated.

- Once the product is fully develop, the idea is to ask users for their file.csv to show them their personal dashboard. That file.csv must be stored with no user identification to analize users trading transactions and create prediction models. If your are a Binance Exchange user and you would like to contribute with the project, share with me your file.csv extracted from the plattform (delete user id to keep it confidential). In return you will have your binance report with all your info shown in dashboard. Thanks!

# Tools 🔧
[streamlit](https://docs.streamlit.io/)

[pandas](https://pandas.pydata.org/)

[binance API](https://binance-docs.github.io/apidocs/spot/en/#change-log)

[yahoo finance](https://pypi.org/project/yfinance/)

[matplotlib](https://matplotlib.org/)

[seaborn](https://seaborn.pydata.org/)

[plotly](https://plotly.com/python/)

[fbPROPHET](https://facebook.github.io/prophet/docs/quick_start.html)

# Disclaimer
Prediction prices should not be used as investment advice by any means.

DYOR do your own research / NFA not financial advice / XD