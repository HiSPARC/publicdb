import datetime


class YearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        year = int(value)
        if 2004 <= year <= datetime.date.today().year:
            return year

        raise ValueError(f'Value {year} is not an allowed year')

    def to_url(self, value):
        return f'{value:4}'


class MonthConverter:
    regex = '[0-9]{1,2}'

    def to_python(self, value):
        month = int(value)
        if 1 <= month <= 12:
            return month

        raise ValueError(f'Value {month} is not a valid month')

    def to_url(self, value):
        return str(value)


class DateConverter:
    regex = '[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}'

    def to_python(self, value):
        date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
        if datetime.date(2004, 1, 1) <= date <= datetime.date.today():
            return date

        raise ValueError(f'Value {date} is not an allowed date')

    def to_url(self, value):
        return f'{value:%Y/%-m/%-d}'
