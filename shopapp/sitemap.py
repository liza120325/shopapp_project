from django.contrib.sitemaps import Sitemap

from .models import Product

class ShopSitemap(Sitemap):
    '''Карта сайта'''

    changefreq = 'monthly' # как часто меняем инфо на ресурсе
    priority = 0.5 # 1 (единица) говорит, что наша страница самая главная,
    # и она должна быть выше остальных в поисковой системе в рамках нашего сайта

    def items(self):
        '''Метод возвращает список всех объектов'''
        return Product.objects.filter(archive=False).order_by('name')

    def lastmod(self, object: Product):
        '''Когда последний раз обновлялся продукт'''
        return object.date_produced

