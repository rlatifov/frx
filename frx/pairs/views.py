from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from telegram import Bot

from frx.settings import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)


class HomeView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('admin:index'))
