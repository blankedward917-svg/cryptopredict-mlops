# Crypto INR Data Processing

## Coins Used

The following cryptocurrencies are included in this dataset:

- Dogecoin (DOGE)
- Ripple (XRP)
- Polygon (MATIC)
- Bitcoin (BTC)
- Ethereum (ETH)
- Litecoin (LTC)
- Bitcoin Cash (BCH)
- Binance Coin (BNB)
- Polkadot (DOT)
- Chainlink (LINK)

## Data Collection

The data for each cryptocurrency is collected from CoinDesk's API endpoints:

- Hourly data: `/index/cc/v1/historical/hours`
- Daily data: `/index/cc/v1/historical/days`

Each request includes parameters such as:

- `instrument` (e.g., BTC-USD, DOGE-USD)
- `market` (e.g., cadli)
- `aggregate` (1 hour or 1 day)
- `to_ts` (timestamp until which data is fetched)
- `limit` (maximum number of records per request)

The data includes the following columns:

- `UNIT`
- `TIMESTAMP`
- `TYPE`
- `MARKET`
- `INSTRUMENT`
- `OPEN`
- `HIGH`
- `LOW`
- `CLOSE`
- `DATE` (converted from timestamp)

Data is fetched in batches (e.g., 2000 hours or 2000 days) and combined sequentially to cover the full historical range.

## Data Cleaning: Removing Values Less Than ₹1

After fetching and combining the data for each coin, the dataset is cleaned by removing rows where the price in INR is less than 1 rupee.

- Columns checked: `OPEN`, `HIGH`, `LOW`, `CLOSE`
- Rows where any of these columns have a value less than 1 are removed.
- The filtered data is saved into separate CSV files for each coin and can also be merged into a single dataset for analysis.

This ensures that all records in the final dataset represent meaningful price points above ₹1, avoiding extremely low or invalid data points.

