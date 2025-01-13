from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from telegram import Bot

from frx.settings import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)


class HomeView(TemplateView):
    def get(self, request, *args, **kwargs):
        # from django.http import HttpResponse
        # from datetime import datetime, timedelta
        # from frx.pairs.models import Pair
        # from frx.pairs.tasks import get_time_series_from_twelvedata
        # split_size = 4
        # yesterday = datetime.now().date() - timedelta(days=1)
        # symbols = Pair.objects.exclude(
        #     rates__date=yesterday).distinct().values_list('name', flat=True)[:split_size]
        # get_time_series_from_twelvedata()
        # return HttpResponse('123')
        return HttpResponseRedirect(reverse('admin:index'))
