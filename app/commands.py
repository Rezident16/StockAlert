from flask.cli import AppGroup
from app.api.stock_routes import refresh_all_news, refresh_all_patterns, timeframes

# `flask stocks refresh-news` / `flask stocks refresh-patterns` - run these
# on a schedule (cron, Heroku Scheduler, k8s CronJob) instead of relying on
# something hitting the /news and /get_patterns/<id> HTTP routes to keep
# data fresh; those routes still work the same way for backward compatibility.
stock_commands = AppGroup('stocks')


@stock_commands.command('refresh-news')
def refresh_news():
    news = refresh_all_news()
    print(f'Refreshed news: {len(news)} articles processed')


@stock_commands.command('refresh-patterns')
def refresh_patterns():
    for timeframe_id in timeframes:
        refresh_all_patterns(timeframe_id)
    print(f'Refreshed patterns for timeframes: {list(timeframes.values())}')
