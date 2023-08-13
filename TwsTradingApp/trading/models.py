from django.contrib.auth.models import User
from django.core import validators, exceptions
from django.db import models


class Strategy(models.Model):
    EMINI_SP500 = "ES (E-mini S&P 500)"
    EMINI_NASDAQ = "NQ (E-mini Nasdaq 100)"
    CRUDE_OIL = "CL (Crude Oil)"
    NATURAL_GAS = "NG (Natural Gas)"

    SYMBOL = (
        (EMINI_SP500, EMINI_SP500),
        (EMINI_NASDAQ, EMINI_NASDAQ),
        (CRUDE_OIL, CRUDE_OIL),
        (NATURAL_GAS, NATURAL_GAS)
    )

    name = models.CharField(max_length=100)
    parameter1 = models.IntegerField(null=True, blank=True)
    parameter2 = models.IntegerField(null=True, blank=True)
    parameter3 = models.IntegerField(null=True, blank=True)

    strategy_description = models.TextField(null=True, blank=True)
    parameters_description = models.TextField(null=True, blank=True)

    symbol = models.CharField(
        null=True,
        blank=True,
        choices=SYMBOL,
    )


class HistoricalData(models.Model):
    ticker = models.CharField(max_length=10)
    time = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    # unique_together ensures that I don't store duplicate data for the same future and timestamp
    class Meta:
        unique_together = ('ticker', 'time')


class BacktestResults(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    parameter_values = models.JSONField()
    pnl_results = models.JSONField()
    finish_time = models.DateTimeField(auto_now_add=True)


class Portfolio(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    parameter_values = models.JSONField()
    results_id = models.IntegerField()
    deployed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


def validate_only_alphanumeric(value):
    for ch in value:
        if not ch.isalnum() and ch != '_':
            raise exceptions.ValidationError('Ensure this value contains only letters, numbers, and underscore.')


# TODO: Do I need Profile, when we use class based views and all goes to auth_user in db...
class Profile(models.Model):

    MAX_LEN_USERNAME = 15
    MIN_LEN_USERNAME = 3
    MAX_LEN_LEVEL = 15

    JUNIOR_TRADER = "Junior Trader"
    SENIOR_TRADER = "Senior Trader"

    LEVELS = (
        (JUNIOR_TRADER, JUNIOR_TRADER),
        (SENIOR_TRADER, SENIOR_TRADER)
    )

    username = models.CharField(
        max_length=MAX_LEN_USERNAME,
        null=False,
        blank=False,
        validators=([
            validators.MinLengthValidator(MIN_LEN_USERNAME),
            validate_only_alphanumeric
        ])
    )

    email = models.EmailField(
        null=False,
        blank=False,
    )

    level = models.CharField(
        max_length=MAX_LEN_LEVEL,
        null=False,
        blank=False,
        choices=LEVELS
    )


