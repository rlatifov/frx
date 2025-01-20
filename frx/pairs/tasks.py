import asyncio
import logging

from datetime import datetime, timedelta
from decimal import Decimal

from celery.exceptions import Ignore

from frx.celery import app as celery
from frx.pairs.logic import working_hours
from frx.pairs.models import Pair, Rate, Price, LastNotification
from frx.settings import TWELVEDATA_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

from twelvedata import TDClient
from telegram import Bot

logger = logging.getLogger(__name__)


@celery.task(name='get_time_series_from_twelvedata', bind=True)
def get_time_series_from_twelvedata(self):
    # if not working_hours():
    #     raise Ignore('Not working hours. Skipping task')

    split_size = 4
    yesterday_or_friday = datetime.now().date() - timedelta(days=1)
    if yesterday_or_friday.weekday() == 6:
        yesterday_or_friday = yesterday_or_friday - timedelta(days=2)

    symbols = Pair.objects.exclude(
        rates__date=yesterday_or_friday).distinct().values_list('name', flat=True)[:split_size]
    is_single_symbol = len(symbols) == 1

    if not symbols:
        raise Ignore('Yesterday rates are already fetched for all pairs')

    logger.info(f"Fetching exchange rates for pairs: {','.join(symbols)}")
    try:
        twelvedata = TDClient(apikey=TWELVEDATA_API_KEY)
        time_series = twelvedata.time_series(
            symbol=','.join(symbols),
            interval='1day',
            timezone='Asia/Baku',
            outputsize=2
        ).as_json()

        if is_single_symbol:
            pair_name = ','.join(symbols)
            pair, created = Pair.objects.update_or_create(name=pair_name, defaults={'name': pair_name})
            for row in time_series:
                date = datetime.strptime(row['datetime'], '%Y-%m-%d').date()
                if date == yesterday_or_friday:
                    logger.info(f"Updating rates for {pair_name} on {date}")
                    Rate.objects.update_or_create(
                        date=date,
                        pair=pair,
                        defaults={
                            'open': Decimal(row['open']),
                            'high': Decimal(row['high']),
                            'low': Decimal(row['low']),
                            'close': Decimal(row['close'])
                        }
                    )
        else:
            for pair_name, pair_data in time_series.items():
                pair, created = Pair.objects.update_or_create(name=pair_name, defaults={'name': pair_name})
                for row in pair_data:
                    date = datetime.strptime(row['datetime'], '%Y-%m-%d').date()
                    if date == yesterday_or_friday:
                        logger.info(f"Updating rates for {pair_name} on {date}")
                        Rate.objects.update_or_create(
                            date=date,
                            pair=pair,
                            defaults={
                                'open': Decimal(row['open']),
                                'high': Decimal(row['high']),
                                'low': Decimal(row['low']),
                                'close': Decimal(row['close'])
                            }
                        )

    except Exception as e:
        print(f"Error occurred: {e}")
        logger.error(f"Error occurred: {e}")
        self.retry(countdown=120)


@celery.task(name='get_prices_from_twelvedata', bind=True)
def get_prices_from_twelvedata(self):
    if not working_hours():
        raise Ignore('Not working hours. Skipping task')

    split_size = 4
    thirty_minutes_before = datetime.now() - timedelta(minutes=30)
    yesterday_or_friday = datetime.now().date() - timedelta(days=1)
    if yesterday_or_friday.weekday() == 6:
        yesterday_or_friday = yesterday_or_friday - timedelta(days=2)

    symbols = Pair.objects.exclude(
        prices__checked_at__gte=thirty_minutes_before
    ).filter(rates__date=yesterday_or_friday).distinct().values_list('name', flat=True)[:split_size]

    is_single_symbol = len(symbols) == 1

    if not symbols:
        raise Ignore('On last 30 minutes all pairs are checked')

    logger.info(f"Fetching prices for pairs: {','.join(symbols)}")
    try:
        twelvedata = TDClient(apikey=TWELVEDATA_API_KEY)
        prices = twelvedata.price(symbol=','.join(symbols)).as_json()

        for pair_name, pair_data in prices.items():
            pair, created = Pair.objects.update_or_create(name=pair_name, defaults={'name': pair_name})
            price = pair_data if is_single_symbol else pair_data['price']
            logger.info(f"Updating price for {pair_name} on {datetime.now()}")
            Price.objects.create(
                pair=pair,
                price=Decimal(price),
                checked_at=datetime.now(),
            )
            compare_pair_prices.delay(pair_name, price)

    except Exception as e:
        print(f"Error occurred: {e}")
        logger.error(f"Error occurred: {e}")
        self.retry(countdown=120)


@celery.task(name='compare_pair_prices')
def compare_pair_prices(pair_name, price):
    logger.info(f"Comparing pair prices for {pair_name} with price: {price}")

    def calculate_zones(_high, _low, _close):
        zone_center = (_high + _low + _close) / 3
        _z2 = zone_center + (_high - _low)
        _z2_low = zone_center - (_high - _low)
        return round(_z2, 6), round(_z2_low, 6)

    pair = Pair.objects.get(name=pair_name)
    price = Decimal(price)
    yesterday_or_friday = datetime.now().date() - timedelta(days=1)
    if yesterday_or_friday.weekday() == 6:
        yesterday_or_friday = yesterday_or_friday - timedelta(days=2)
    yesterday_rate = pair.rates.filter(date=yesterday_or_friday).first()

    z2, z2_low = calculate_zones(yesterday_rate.high, yesterday_rate.low, yesterday_rate.close)

    if price > z2:
        if not LastNotification.objects.filter(
                pair=pair,
                notification_type=LastNotification.NotificationTypeEnum.Z2,
                date=datetime.now().date()).exists():
            LastNotification.objects.update_or_create(
                pair=pair,
                date=datetime.now().date(),
                defaults={"notification_type": LastNotification.NotificationTypeEnum.Z2})
            msg = f"🚨 {pair_name} crossed above Z2: {z2:.5f}. Current price: {price:.5f}"
            logger.info(msg)
            send_telegram_message.delay(msg)
        else:
            logger.info(f"Already reported: {pair_name} crossed above Z2: {z2:.5f}. Current price: {price:.5f}")
    elif price < z2_low:
        if not LastNotification.objects.filter(
                pair=pair,
                notification_type=LastNotification.NotificationTypeEnum.Z2_LOW,
                date=datetime.now().date()).exists():
            LastNotification.objects.update_or_create(
                pair=pair,
                date=datetime.now().date(),
                defaults={"notification_type": LastNotification.NotificationTypeEnum.Z2_LOW})
            msg = f"🚨 {pair_name} dropped below Z2_low: {z2_low:.5f}. Current price: {price:.5f}"
            logger.info(msg)
            send_telegram_message.delay(msg)
        else:
            logger.info(f"Already reported: {pair_name} dropped below Z2_low: {z2_low:.5f}. Current price: {price:.5f}")


@celery.task(name='send_telegram_message')
def send_telegram_message(message):
    logger.info(f"Sending message to Telegram chat: {message}")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message))
