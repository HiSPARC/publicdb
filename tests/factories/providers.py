from faker.providers import BaseProvider


class DataProvider(BaseProvider):
    """Provider for histogram and dataset data"""

    def int_list(self, n=24, **kwargs):
        return [self.random_int(**kwargs) for _ in range(n)]

    def float_list(self, n=600, min=0, max=100):
        return [self.generator.random.uniform(a=min, b=max) for _ in range(n)]

    def multi_float_list(self, detectors=2, n=600, min=0, max=100):
        return [self.float_list(n, min, max) for _ in range(detectors)]
