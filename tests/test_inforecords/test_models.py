from django.test import TestCase

from ..factories import inforecords_factories


class TestProfession(TestCase):
    def test_str(self):
        profession = inforecords_factories.ProfessionFactory()
        self.assertEqual(profession.description, str(profession))


class TestContactInformation(TestCase):
    def test_type(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        self.assertEqual('no owner', contact_info.type)

    def test_type_with_contact(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        inforecords_factories.ContactFactory(contactinformation=contact_info)
        self.assertEqual('Contact', contact_info.type)

    def test_type_with_station(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        inforecords_factories.StationFactory(
            number=1, cluster__number=0, cluster__country__number=0, contactinformation=contact_info
        )
        self.assertEqual('Station', contact_info.type)

    def test_contact_owner(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        self.assertEqual('no owner', contact_info.contact_owner)

    def test_contact_owner_with_contact(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        contact = inforecords_factories.ContactFactory(contactinformation=contact_info)
        self.assertEqual(str(contact), contact_info.contact_owner)

    def test_contact_owner_with_station(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        station = inforecords_factories.StationFactory(
            number=1, cluster__number=0, cluster__country__number=0, contactinformation=contact_info
        )
        self.assertEqual(str(station), contact_info.contact_owner)

    def test_contact_owner_with_contact_and_station(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        contact = inforecords_factories.ContactFactory(contactinformation=contact_info)
        station = inforecords_factories.StationFactory(
            number=1, cluster__number=0, cluster__country__number=0, contactinformation=contact_info
        )
        self.assertEqual(f'{contact}, {station}', contact_info.contact_owner)

    def test_contact_owner_with_multiple_contacts(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        contact = inforecords_factories.ContactFactory(surname='A', contactinformation=contact_info)
        contact2 = inforecords_factories.ContactFactory(surname='B', contactinformation=contact_info)
        self.assertEqual(f'{contact}, {contact2}', contact_info.contact_owner)

    def test_str(self):
        contact_info = inforecords_factories.ContactInformationFactory()
        self.assertEqual(
            ' '.join([contact_info.city, contact_info.street_1, contact_info.email_work]), str(contact_info)
        )


class TestContact(TestCase):
    def test_str(self):
        contact = inforecords_factories.ContactFactory()
        self.assertEqual(contact.name, str(contact))

    def test_email_work(self):
        contact = inforecords_factories.ContactFactory()
        self.assertEqual(contact.contactinformation.email_work, contact.email_work)


class TestCountry(TestCase):
    def test_str(self):
        country = inforecords_factories.CountryFactory(number=0)
        self.assertEqual(country.name, str(country))


class TestCluster(TestCase):
    def test_str(self):
        cluster = inforecords_factories.ClusterFactory(number=0, country__number=0)
        self.assertEqual(cluster.name, str(cluster))


class TestStation(TestCase):
    def test_str(self):
        station = inforecords_factories.StationFactory(number=0, cluster__number=0, cluster__country__number=0)
        self.assertEqual(f'{station.number:5d}: {station.name}', str(station))

    def test_number_of_detectors(self):
        station = inforecords_factories.StationFactory(number=0, cluster__number=0, cluster__country__number=0)
        self.assertEqual(4, station.number_of_detectors())


class TestPcType(TestCase):
    def test_str(self):
        pc_type = inforecords_factories.PcTypeFactory()
        self.assertEqual(pc_type.description, str(pc_type))


class TestPc(TestCase):
    def test_str(self):
        station = inforecords_factories.StationFactory(number=0, cluster__number=0, cluster__country__number=0)
        pc = inforecords_factories.PcFactory(station=station)
        self.assertEqual(pc.name, str(pc))
