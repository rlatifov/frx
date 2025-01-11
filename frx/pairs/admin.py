from django.contrib import admin

from frx.pairs.models import Pair, Rate, Price


class PriceAdmin(admin.ModelAdmin):
    fields = ('pair', 'checked_at', 'price', 'created_at')
    list_display = ('pair', 'checked_at_str', 'price')
    list_filter = ('pair', 'checked_at')
    search_fields = ('pair__name', 'checked_at')
    readonly_fields = ('created_at',)
    ordering = ('-checked_at',)

    @admin.display(description='Checked at')
    def checked_at_str(self, obj):
        return obj.checked_at.strftime('%d.%m.%Y %H:%M:%S')


class RateAdmin(admin.ModelAdmin):
    fields = ('pair', 'date', 'open', 'high', 'low', 'close', 'created_at')
    list_display = ('pair', 'date_str', 'open', 'high', 'low', 'close')
    list_filter = ('pair', 'date')
    search_fields = ('pair__name', 'date')
    readonly_fields = ('created_at',)
    ordering = ('-date',)

    @admin.display(description='Date')
    def date_str(self, obj):
        return obj.date.strftime('%d.%m.%Y')


admin.site.register(Pair)
admin.site.register(Rate, RateAdmin)
admin.site.register(Price, PriceAdmin)
