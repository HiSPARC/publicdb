import re

from faker.providers import BaseProvider


def make_urlsafe(value):
    """Remove all characters that would not be matched by url regex"""
    return re.sub('[^A-Za-z -]+', '', value)


class DataProvider(BaseProvider):
    """Provider for histogram and dataset data"""

    def float(self, min=0., max=100.):
        return self.generator.random.uniform(a=min, b=max)

    def int_list(self, n=24, **kwargs):
        return [self.random_int(**kwargs) for _ in range(n)]

    def float_list(self, n=600, **kwargs):
        return [self.float(**kwargs) for _ in range(n)]

    def multi_float_list(self, detectors=2, **kwargs):
        return [self.float_list(**kwargs) for _ in range(detectors)]

    def country_urlsafe(self):
        return make_urlsafe(self.country())

    def city_urlsafe(self):
        return make_urlsafe(self.city())
