import csv

from django.db.models import QuerySet
from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse


# Экспорт данных в формате CSV
class ExportAsCSVMixin:
    def export_csv(self, request: HttpRequest, query_set: QuerySet):
        # Экспортируем все доступные поля моделей, они доступны в meta
        meta: Options = self.model._meta
        # Получаем список из строк как называются поля этой модели
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}-export.csv'

        csv_writer = csv.writer(response)

        # Записываем заголовки
        csv_writer.writerows(field_names)

        for obj in query_set:
            csv_writer.writerow([getattr(obj, field) for field in field_names])

        return response
