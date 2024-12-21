from datetime import date

import factory

from django.conf import settings
from django.core.management.base import BaseCommand

from tests.factories import histograms_factories, inforecords_factories, station_layout_factories


class Command(BaseCommand):
    help = 'Creates fake data for testing a local development server'

    def handle(*args, **options):
        if not settings.DEBUG:
            raise RuntimeError('Never run this on a production database!!')

        with factory.Faker.override_default_locale('nl_NL'):
            # Inforecords
            countries = [
                inforecords_factories.CountryFactory(number=country_number) for country_number in range(0, 20001, 10000)
            ]
            clusters = [
                inforecords_factories.ClusterFactory(country=country, number=cluster_number + country.number)
                for country in countries
                for cluster_number in range(0, 3001, 1000)
            ]
            subclusters = [
                inforecords_factories.ClusterFactory(
                    country=cluster.country,
                    parent=cluster,
                    number=cluster_number + cluster.number,
                )
                for cluster in clusters
                for cluster_number in range(100, 201, 100)
            ]
            stations = [
                inforecords_factories.StationFactory(cluster=cluster, number=station_number + cluster.number)
                for cluster in clusters + subclusters
                for station_number in range(1, 6)
            ]

            for station in stations:
                inforecords_factories.PcFactory(station=station, name=f'pc{station.number}')

        for station in stations:
            station_layout_factories.StationLayoutFactory(station=station)

        dates = [date(2017, 1, 1), date(2017, 1, 2), date(2017, 2, 10), date(2018, 4, 1)]

        # Histograms and datasets
        network_summaries = [histograms_factories.NetworkSummaryFactory(date=summary_date) for summary_date in dates]

        for network_summary in network_summaries:
            histograms_factories.CoincidencetimeHistogramFactory(network_summary=network_summary)
            histograms_factories.CoincidencenumberHistogramFactory(network_summary=network_summary)

        summaries = [
            histograms_factories.SummaryFactory(station=station, date=summary_date, num_config=1)
            for station in stations
            for summary_date in dates
        ]

        for summary in summaries:
            histograms_factories.AzimuthHistogramFactory(summary=summary)
            histograms_factories.BarometerDatasetFactory(summary=summary)
            histograms_factories.ConfigurationFactory(summary=summary)
            histograms_factories.DetectorTimingOffsetFactory(summary=summary)
            histograms_factories.EventtimeHistogramFactory(summary=summary)
            histograms_factories.PulseheightHistogramFactory(summary=summary)
            histograms_factories.PulseintegralHistogramFactory(summary=summary)
            histograms_factories.SingleshighHistogramFactory(summary=summary)
            histograms_factories.SingleslowHistogramFactory(summary=summary)
            histograms_factories.SinglesratehighDatasetFactory(summary=summary)
            histograms_factories.SinglesratelowDatasetFactory(summary=summary)
            histograms_factories.TemperatureDatasetFactory(summary=summary)
            histograms_factories.ZenithHistogramFactory(summary=summary)
