import re

from faker.providers import BaseProvider
from faker.providers.address import Provider as AddressProvider
from faker.providers.address.nl_NL import Provider as NlAddressProvider


def make_urlsafe(value):
    """Remove all characters that would not be matched by url regex"""
    return re.sub('[^A-Za-z -]+', '', value)


class DataProvider(BaseProvider):
    """Provider for histogram and dataset data"""

    def float(self, min=0., max=100., ndigits=6):
        return round(self.generator.random.uniform(a=min, b=max), ndigits)

    def int_list(self, n=24, **kwargs):
        return [self.random_int(**kwargs) for _ in range(n)]

    def multi_int_list(self, detectors=2, **kwargs):
        return [self.int_list(**kwargs) for _ in range(detectors)]

    def float_list(self, n=600, **kwargs):
        return [self.float(**kwargs) for _ in range(n)]

    def multi_float_list(self, detectors=2, **kwargs):
        return [self.float_list(**kwargs) for _ in range(detectors)]


class UrlSafeProvider(AddressProvider):
    """Provider for safe country and city names"""

    def country_urlsafe(self):
        return make_urlsafe(self.country())

    def city_urlsafe(self):
        return make_urlsafe(self.city())


class NlUrlSafeProvider(NlAddressProvider):
    """Provider for safe country and city names"""

    def country_urlsafe(self):
        return make_urlsafe(self.country())

    def city_urlsafe(self):
        return make_urlsafe(self.city())
