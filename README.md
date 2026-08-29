# StockAlert

A read-only, StockTwits-style dashboard for tracking a watchlist of stocks: live price/candlestick charts, TA-Lib pattern detection, FinBERT-scored news sentiment, and a rule-based BUY/SELL/NEUTRAL technical signal - all backed by the Alpaca Markets API.

## Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Flask-SocketIO, SQLite (Postgres in production)
- **Frontend**: React 17 (Create React App via CRACO), Redux + Redux-Thunk, React Router, Recharts, Tailwind CSS, socket.io-client
- **Data/ML**: Alpaca Markets API (bars, snapshots, news, options), TA-Lib (candlestick patterns), FinBERT (`yiyanghkust/finbert-tone`) for news sentiment
- **Cache**: Redis (put/call ratio rolling history)

## Running it locally

Requires Python 3.9+, Node, and Redis running locally.

```bash
# 1. Configure environment
cp .env.example .env
# fill in API_KEY / API_SECRET (Alpaca) at minimum - see comments in .env.example

# 2. Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask seed all
flask run                     # http://localhost:5000

# 3. Redis (separate terminal)
redis-server

# 4. Frontend (separate terminal)
cd react-app
npm install
npm start                     # http://localhost:3000
```

No Google OAuth credentials needed for local dev - use the "Continue as Demo" button (logs in as the seeded demo user; disabled in production).

To pull in real pattern/news/sentiment data for the seeded stocks:

```bash
flask stocks refresh-patterns
flask stocks refresh-news
```

## What was initially built

The original app (models, auth, and core data pipeline) shipped before any AI-assisted work on this repo:

- User accounts + Google OAuth login
- Stock/News/Pattern models and seed data
- Fetching bars from Alpaca and detecting candlestick patterns with TA-Lib, deduped and persisted to the DB
- Fetching news per stock and scoring it with FinBERT
- Per-stock price chart
- WebSocket-driven live updates when new patterns/news are caught
- Redis caching for pattern lookups
- Initial styling

## New functionality co-created with Claude

The following were net-new features designed and built collaboratively in this repo (excluding refactors, bug fixes, cleanup, and improvements to functionality that already existed in some form):

- **BUY/SELL/NEUTRAL technical signal** - a rule-based read-only signal (price vs. moving averages, RSI, MACD, put/call ratio) ported from a separate trading-bot project and generalized to run on any stock. Scales its moving-average windows to match the selected chart timeframe (1D through 5Y) and surfaces every bullish/bearish flag that fired, not just whichever side decided the final call.
- **Indicator breakdown table** - a color-coded (green/red/amber) table showing each individual indicator behind the signal - price trend, RSI, MACD, put/call ratio - so a mixed reading (e.g. bullish trend but bearish MACD) is visible at a glance instead of collapsing into one badge.

## TODO

- Watchlist management (add/remove stocks from the UI)
- Pattern detection currently only runs on-demand (a page hitting `GET /api/stocks/get_patterns/<id>`, or someone manually running `flask stocks refresh-patterns`) - there's no scheduler wiring it up. Before going live this needs a real recurring job (cron, a hosting platform's scheduler, a k8s CronJob, etc.) driving `flask stocks refresh-patterns` on an interval, instead of relying on page loads to trigger it.
