from django import forms
from django.forms import fields, models, widgets
from django.contrib.formtools.wizard import FormWizard
from django.contrib.admin.helpers import AdminForm
from django_publicdb.inforecords.models import *
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.shortcuts import render_to_response
from django.utils.datastructures import SortedDict

#The following forms are used in the form wizards
#Some are used in multiple wizards


#form to be used for creating main clusters.
class ClusterForm(forms.Form):
    form_name = 'create new main cluster'
    cluster_name = forms.CharField(max_length=70, label='Cluster Name')
    cluster_country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label='new country', label='country', required=False)
    cluster_url = forms.URLField(label='url', required=False)


#form to be used for creating subclusters. Contains no country field.
# Contains a parentfield containing only clusters that do not have a parent.
class SubClusterForm(forms.Form):
    form_name = 'create new subcluster'
    subcluster_name = forms.CharField(max_length=70, label='Cluster Name')
    parent = forms.ModelChoiceField(queryset=Cluster.objects.filter(parent=None), empty_label=None, label='parent cluster')
    subcluster_url = forms.URLField(label='url', required=False)


#form to be used for creating a country. Country number is not required and
# if no number is given should be created by country.save()
class CountryForm(forms.Form):
    form_name = 'Create new country'
    country_name = forms.CharField(max_length=70, label='Country Name')
    country_number = forms.IntegerField()


#form for the creation of a contact.
class ContactForm(forms.Form):
    form_name = 'Create new contact'
    contact_first_name = forms.CharField(max_length=40, label='First Name')
    contact_prefix_surname = forms.CharField(max_length=10, label='Prefix surname', required=False)
    contact_surname = forms.CharField(max_length=40, label='Surname')
    #empty_label is used so as a way to see if the profession form should be shown by the wizard
    contact_profession = forms.ModelChoiceField(queryset=Profession.objects.all(), empty_label='new profession', label='profession', required=False)
    contact_title = forms.CharField(max_length=20, label='Title', required=False)
    contact_street_1 = forms.CharField(max_length=40, label='street')
    contact_street_2 = forms.CharField(max_length=40, label='street', required=False)
    contact_postalcode = forms.CharField(max_length=6, label='postalcode')
    contact_city = forms.CharField(max_length=40, label='city')
    contact_pobox = forms.CharField(max_length=9, label='pobox', required=False)
    contact_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
    contact_pobox_city = forms.CharField(max_length=40, label='pobox City', required=False)
    contact_phone_work = forms.CharField(max_length=20, label='Phone Work')
    contact_phone_home = forms.CharField(max_length=20, label='Phone Home', required=False)
    contact_fax = forms.CharField(max_length=20, label='Fax', required=False)
    contact_email_work = forms.EmailField(label='Email Work')
    contact_email_private = forms.EmailField(label='Email Private', required=False)
    contact_url = forms.URLField(label='url', required=False)


#another form for the creation of a contact. This is to make it easier to work with wizards that need multiple contacts to be created.
#the different field names make it easier to keep track of which information you are using in the wizard.
class StationContactForm(forms.Form):
    form_name = 'create new contact'
    stationcontact_first_name = forms.CharField(max_length=40, label='First Name')
    stationcontact_prefix_surname = forms.CharField(max_length=10, label='Prefix surname', required=False)
    stationcontact_surname = forms.CharField(max_length=40, label='Surname')
    #empty_label is used so as a way to see if the profession form should be shown by the wizard
    stationcontact_profession = forms.ModelChoiceField( queryset=Profession.objects.all(), empty_label='new profession', label='profession', required=False)
    stationcontact_title = forms.CharField(max_length=20, label='title', required=False)
    stationcontact_street_1 = forms.CharField(max_length=40, label='street')
    stationcontact_street_2 = forms.CharField(max_length=40, label='street', required=False)
    stationcontact_postalcode = forms.CharField(max_length=6, label='postalcode')
    stationcontact_city = forms.CharField(max_length=40, label='city')
    stationcontact_pobox = forms.CharField(max_length=9, label='pobox', required=False)
    stationcontact_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
    stationcontact_pobox_city = forms.CharField(max_length=40, label='pobox City', required=False)
    stationcontact_phone_work = forms.CharField(max_length=20, label='Phone Work')
    stationcontact_phone_home = forms.CharField(max_length=20, label='Phone Home', required=False)
    stationcontact_fax = forms.CharField(max_length=20, label='Fax', required=False)
    stationcontact_email_work = forms.EmailField(label='Email Work')
    stationcontact_email_private = forms.EmailField(label='Email Private', required=False)
    stationcontact_url = forms.URLField(label='url', required=False)


#a form for the creation of a station.Contains two possible contacts and a booleanfield so you can use the main contact as the ict contact.
class StationForm(forms.Form):
    form_name = 'Create new station'
    station_name = forms.CharField(max_length=40, label='name')
    station_cluster = forms.ModelChoiceField(queryset=Cluster.objects.all(), empty_label=None, label='cluster')
    station_street_1 = forms.CharField(max_length=40, label='street')
    station_street_2 = forms.CharField(max_length=40, label='street', required=False)
    station_postalcode = forms.CharField(max_length=6, label='postalcode')
    station_city = forms.CharField(max_length=40, label='city')
    station_pobox = forms.CharField(max_length=9, label='pobox', required=False)
    station_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
    station_pobox_city = forms.CharField(max_length=40, label='pobox City', required=False)
    station_phone_work = forms.CharField(max_length=20, label='Phone Work')
    station_phone_home = forms.CharField(max_length=20, label='Phone Home', required=False)
    station_fax = forms.CharField(max_length=20, label='Fax', required=False)
    station_email_work = forms.EmailField(label='Email Work')
    station_email_private = forms.EmailField(label='Email Private', required=False)
    station_url = forms.URLField(label='url', required=False)
    station_password = forms.CharField(max_length=40, label='password')
    station_infopage = forms.URLField(label='infopage', required=False)
    station_contact = forms.ModelChoiceField(queryset=Contact.objects.all(), empty_label='Nieuwe contactpersoon', label='contactpersoon', required=False)
    station_contact_is_ict = forms.BooleanField(label='Contact is also ICT contact', required=False)
    station_ict_contact = forms.ModelChoiceField(queryset=Contact.objects.all(), empty_label='gelijk aan contact of nieuw contactpersoon', label='ICT contactpersoon', required=False)


#two professionforms again to make it easier to know which information you are using in a wizard with multiple contacts.
class ProfessionForm(forms.Form):
    form_name = 'create new profession'
    profession_description = forms.CharField(max_length=40, label='profession')


class ICTProfessionForm(forms.Form):
    form_name = 'create new profession'
    ICTprofession_description = forms.CharField(max_length=40, label='profession')


#A tweaked formwizard for the creation of a new station.
#This wizard should be called with the following forms in this order:
# StationForm, StationContactForm, ProfessionForm, ContactForm, ICTProfessionForm
#If called with other forms or in an other order the wizard wont work correctly.
#The stationcontact form is used for the main contact
#The contact form is used for the ict contact.
class StationWizard(FormWizard):
    @property

    #this is needed for integration in the admin tool.
    def __name__(self):
        return self.__class__.__name__

    #what to do when the wizard is finished
    def done(self, request, form_list):
        #all given data is verified and stored in data
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
            #create the contact information for the station itself.
            #any fields left blank will be left blank.
            #required fields need to be required in the form.
            station_contact_information = ContactInformation(
                    street_1=data['station_street_1'],
                    street_2=data['station_street_2'],
                    postalcode=data['station_postalcode'],
                    city=data['station_city'],
                    pobox=data['station_pobox'],
                    pobox_postalcode=data['station_pobox_postalcode'],
                    pobox_city=data['station_pobox_city'],
                    phone_work=data['station_phone_work'],
                    phone_home=data['station_phone_home'],
                    fax=data['station_fax'],
                    email_work=data['station_email_work'],
                    email_private=data['station_email_private'],
                    url=data['station_url'])
        station_contact_information.save()
        #If no stationcontact was given(empty_label=create new contact).
        #the stationcontact form is used.
        #create and save the contact contact information.
        #the form used for the main contact is the stationcontact form.
        if data['station_contact'] == None:
            contact_contact_information = ContactInformation(
                    street_1=data['stationcontact_street_1'],
                    street_2=data['stationcontact_street_2'],
                    postalcode=data['stationcontact_postalcode'],
                    city=data['stationcontact_city'],
                    pobox=data['stationcontact_pobox'],
                    pobox_postalcode=data['stationcontact_pobox_postalcode'],
                    pobox_city=data['stationcontact_pobox_city'],
                    phone_work=data['stationcontact_phone_work'],
                    phone_home=data['stationcontact_phone_home'],
                    fax=data['stationcontact_fax'],
                    email_work=data['stationcontact_email_work'],
                    email_private=data['stationcontact_email_private'],
                    url=data['stationcontact_url'])
            contact_contact_information.save()
            #if no profession was given(empty_label=create new profession).
            if data['stationcontact_profession']==None:
                profession = Profession(
                        description=data['profession_description'])
                profession.save()
            #otherwise the use the profession from the stationcontact form
            else:
                profession = data['stationcontact_profession']
                #we now have all the information to create and save the stationcontact.
            stationcontact = Contact(
                    profession=profession,
                    title=data['stationcontact_title'],
                    first_name=data['stationcontact_first_name'],
                    prefix_surname=data['stationcontact_prefix_surname'],
                    surname=data['stationcontact_surname'],
                    contactinformation=contact_contact_information)
            stationcontact.save()
        #if a stationcontact was given then this is the contact.
        else:
            stationcontact = data['station_contact']
        #if no ict contact was given and the boolean station_contact_is_ist is False. The contact form was used for ict contact.
        #the contact information for the ict contact is saved. The form used for the ict contact is the contact form.
        if (data['station_ict_contact'] == None and
            data['station_contact_is_ict'] == False):
            ICT_contact_information = ContactInformation(
                    street_1=data['contact_street_1'],
                    street_2=data['contact_street_2'],
                    postalcode=data['contact_postalcode'],
                    city=data['contact_city'],
                    pobox=data['contact_pobox'],
                    pobox_postalcode=data['contact_pobox_postalcode'],
                    pobox_city=data['contact_pobox_city'],
                    phone_work=data['contact_phone_work'],
                    phone_home=data['contact_phone_home'],
                    fax=data['contact_fax'],
                    email_work=data['contact_email_work'],
                    email_private=data['contact_email_private'],
                    url=data['contact_url'])
            ICT_contact_information.save()
            #if no profession was given the ict_profession form was used.
            if data['contact_profession']==None:
                ictprofession = Profession(
                        description=data['ICTprofession_description'])
                ictprofession.save()
            else:
                ictprofession = data['contact_profession']
            #we can now create and save the ict contact.
            station_ict_contact = Contact(
                    profession=ictprofession,
                    title=data['contact_title'],
                    first_name=data['contact_first_name'],
                    prefix_surname=data['contact_prefix_surname'],
                    surname=data['contact_surname'],
                    contactinformation=ICT_contact_information)
            station_ict_contact.save()
        #the boolean station_contact_is_ict is true so we use the stationcontact created above as ict contact.
        elif data['station_contact_is_ict']:
            station_ict_contact = stationcontact
        #the ict contact was given in the form so we use that ict contact.
        else:
            station_ict_contact = data['station_ict_contact']
        #we now have all the information we need to create and save the station
        #the station number is generated in station.save()
        station = Station(
                name=data['station_name'],
                contactinformation=station_contact_information,
                cluster=data['station_cluster'],
                contact=stationcontact,
                ict_contact=station_ict_contact,
                password=data['station_password'],
                info_page=data['station_infopage'])
        station.save()
        #we now create a dictionary containing all the fields form the forms actually used in the wizard so we can show a summary.
        #forms that were skipped are not in form_list and so are not included in the summary.
        #and we add station number because it is not in any form.
        modeldata = GetModelData(form_list)
        modeldata.insert(0,'Station Number', station.number)
        response = {"modeldata":modeldata}
        return render_to_response('summary.html', response)

    #the following is called at the start of every step including the first step.
    def process_step(self, request, form, step):
        #with form.is_valid we check if we have completed a step. In the first step the form is not yet filled so invalid.
        #if the form is filled incorrectly the wizard will show it again and we should not do anything here.
        if form.is_valid():
            #first we check which form was just filled.
            formtype = form.__class__.__name__
            if formtype=='StationForm':
                #if station_contact is not empty we do not need the stationcontact form and profession form.
                #we will remove those form the form_list so they will not be used.
                #I also check to see if it is actually present so we do not get an error trying to remove it.
                if (form.cleaned_data['station_contact']!=None and
                    StationContactForm in self.form_list):
                    self.form_list.remove(StationContactForm)
                    self.form_list.remove(ProfessionForm)
                #If station_ict_contact is not empty contact form and ict profession form can be removed.
                if (form.cleaned_data['station_ict_contact']!=None and
                    ContactForm in self.form_list):
                    self.form_list.remove(ContactForm)
                    self.form_list.remove(ICTProfessionForm)
                #If station_contact_is_ict is true we can also remove contact form and ict profession form.
                if (form.cleaned_data['station_contact_is_ict']==True and
                    ContactForm in self.form_list):
                    self.form_list.remove(ContactForm)
                    self.form_list.remove(ICTProfessionForm)
            if formtype=='StationContactForm':
                #in stationcontactform we only need to check if profession is empty and remove the profession form if it is not.
                if (form.cleaned_data['stationcontact_profession']!=None and
                    ProfessionForm in self.form_list):
                    self.form_list.remove(ProfessionForm)
            if formtype=='ContactForm':
                #same goes for the contactform
                if (form.cleaned_data['contact_profession']!=None and
                    ICTProfessionForm in self.form_list):
                    self.form_list.remove(ICTProfessionForm)

    #this gives the wizard the context expected by the admin app.
    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin
        opts = Station._meta
        self.extra_context.update({
                'title': 'Add %s' % force_unicode(opts.verbose_name),
                'current_app': admin.admin_site.name,
                'has_change_permission': admin.has_change_permission(request),
                'add': True,
                'opts': opts,
                'root_path': admin.admin_site.root_path,
                'app_label': opts.app_label})

    #this renders the wizard.
    #formtype is a string with the name of the current form.
    #This is overwritten here for the contact forms so the user can see which he is using
    #the forms are rendered as Adminforms
    def render_template(self, request, form, previous_fields, step, context=None):
        formtype = form.form_name
        if form.__class__.__name__=='StationContactForm':
            formtype='Create new contact (main)'
        if form.__class__.__name__=='ContactForm':
            formtype='Create new contact (ICT)'
        form = AdminForm(form,
                         [(formtype, {'fields': form.base_fields.keys()})], {})
        context = context or {}
        context.update({'media': self._model_admin.media + form.media})
        return super(StationWizard, self).render_template(request, form,
                                                          previous_fields,
                                                          step, context)


class ContactWizard(FormWizard):
    @property

    #this is needed for intergration in the admin tool.
    def __name__(self):
        return self.__class__.__name__

    #what to do when the wizard is finished
    def done(self, request, form_list):
        #all given data is verified and stored in data
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        #first we create and save the contact information.
        #if a field in the form was empty is will be created empty here.
        #validation and requiring fields is done in the form
        contact_information = ContactInformation(
                street_1=data['contact_street_1'],
                street_2=data['contact_street_2'],
                postalcode=data['contact_postalcode'],
                city=data['contact_city'],
                pobox=data['contact_pobox'],
                pobox_postalcode=data['contact_pobox_postalcode'],
                pobox_city=data['contact_pobox_city'],
                phone_work=data['contact_phone_work'],
                phone_home=data['contact_phone_home'],
                fax=data['contact_fax'],
                email_work=data['contact_email_work'],
                email_private=data['contact_email_private'],
                url=data['contact_url'])
        contact_information.save()
        #if no contact_profession was given the profession form was show
        #we use this form to create a new contact
        if data['contact_profession']==None:
            profession = Profession(description=data['profession_description'])
            profession.save()
        #or we use the given profession
        else:
            profession = data['contact_profession']
        #we can now create and save the new contact.
        contact = Contact(
                profession=profession,
                title=data['contact_title'],
                first_name=data['contact_first_name'],
                prefix_surname=data['contact_prefix_surname'],
                surname=data['contact_surname'],
                contactinformation=contact_information)
        contact.save()
        #we now create a dictionary containing all the fields form the forms actually used in the wizard so we can show a summary.
        #forms that were skipped are not in form_list and so are not included in the summary.
        modeldata = GetModelData(form_list)
        response = {"modeldata":modeldata}
        return render_to_response('summary.html', response)

        #the following is called at the start of every step including the first step.
    def process_step(self, request, form, step):
        #with form.is_valid we check if we have completed a step. In the first step the form is not yet filled so invalid.
        #if the form is filled incorrectly the wizard will show it again and we should not do anything here.
        if form.is_valid():
            #first we check which form was just filled.
            formtype = form.__class__.__name__
            if formtype=='ContactForm':
            #if contactprofession is not empy we donot need to show the profession form
            #we remove it form the form_list
                if (form.cleaned_data['contact_profession']!=None and
                    ProfessionForm in self.form_list):
                    self.form_list.remove(ProfessionForm)

    #this gives the wizard the context expected by the admin app.
    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin
        opts = Contact._meta
        self.extra_context.update({
                'title': 'Add %s' % force_unicode(opts.verbose_name),
                'current_app': admin.admin_site.name,
                'has_change_permission': admin.has_change_permission(request),
                'add': True, 'opts': opts,
                'root_path': admin.admin_site.root_path,
                'app_label': opts.app_label})

        #this renders the wizard.
        #the forms are rendered as Adminforms
    #formtype is a string describing the current form which is printed in the template
    def render_template(self, request, form, previous_fields, step, context=None):
        formtype = form.form_name
        form = AdminForm(form,
                         [(formtype, {'fields': form.base_fields.keys()})], {})
        context = context or {}
        context.update({'media': self._model_admin.media + form.media})
        return super(ContactWizard, self).render_template(request, form,
                                                          previous_fields,
                                                          step, context)

#the subcluster wizard did not need to be a formwizard, but it is implemented as a wizard to keep single approach.
class SubClusterWizard(FormWizard):
    @property
    #this is needed for integration in the admin tool.
    def __name__(self):
        return self.__class__.__name__
    #what to do when the wizard is finished
    def done(self, request, form_list):
        #all given data is verified and stored in data
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        #there is only one form so we can create and save the cluster.
        #the number is none because it will be created by subcluster.save
        subcluster = Cluster(name=data['subcluster_name'], number=None,
                             parent=data['parent'],
                             country=data['parent'].country,
                             url=data['subcluster_url'])
        subcluster.save()
        #we get all the fields form the form and use them for a summary.
        #we manualy add the clusternumber
        modeldata = GetModelData(form_list)
        modeldata.insert(0,'clusternumber', subcluster.number)
        response = {"modeldata": modeldata}
        return render_to_response('summary.html', response)

    #this gives the wizard the context expected by the admin app.
    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin
        opts = Cluster._meta
        self.extra_context.update({
                'title': 'Add %s' % force_unicode(opts.verbose_name),
                'current_app': admin.admin_site.name,
                'has_change_permission': admin.has_change_permission(request),
                'add': True, 'opts': opts,
                'root_path': admin.admin_site.root_path,
                'app_label': opts.app_label})

        #this renders the wizard.
        #the forms are rendered as Adminforms
    #form type is a string describing the current form which is printed in the template
    def render_template(self, request, form, previous_fields, step, context=None):
        formtype = form.form_name
        form = AdminForm(form,
                         [(formtype,{'fields': form.base_fields.keys()})], {})
        context = context or {}
        context.update({'media': self._model_admin.media + form.media})
        return super(SubClusterWizard, self).render_template(request, form,
                                                             previous_fields,
                                                             step, context)

class ClusterWizard(FormWizard):
    @property
    #this is needed for intergration in the admin tool.
    def __name__(self):
        return self.__class__.__name__
        #what to do when the wizard is finished
    def done(self, request, form_list):
        #all given data is verified and stored in data
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        #If no country is given then the contryform was shown and we use it to create a new country
        #If no countrynumber is given it will be created by country.save()
        if data['cluster_country']==None:
            country = Country(name=data['country_name'],
                              number=data['country_number'])
        else:
            country = data['cluster_country']
        country.save()
        #we can now create and save the cluster
        #it is a main cluster so it has no parent
        #the number is generated by cluster.save()
        cluster = Cluster(name=data['cluster_name'], number=None,
                          parent=None, country=country,
                          url=data['cluster_url'])
        cluster.save()

        #we now create a dictionary containing all the fields form the forms actually used in the wizard so we can show a summary.
        #forms that were skipped are not in form_list and so are not included in the summary.
        #manually add clusternumber to summary
        modeldata = GetModelData(form_list)
        modeldata.insert(0,'Clusternumber', cluster.number)
        response = {"modeldata":modeldata}
        return render_to_response('summary.html', response)

    def process_step(self, request, form, step):
        #with form.is_valid we check if we have completed a step. In the first step the form is not yet filled so invalid.
        #if the form is filled incorrectly the wizard will show it again and we should not do anything here.
        if form.is_valid():
            #first we check which form was just filled.
            formtype = form.__class__.__name__
            if formtype=='ClusterForm':
            #if cluster_contry is not empty we do not need to show the country form
            #we remove it from the form_list
                if (form.cleaned_data['cluster_country']!=None and
                    CountryForm in self.form_list):
                    self.form_list.remove(CountryForm)

        #this gives the wizard the context expected by the admin app.
    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin
        opts = Cluster._meta
        self.extra_context.update({
                'title': 'Add %s' % force_unicode(opts.verbose_name),
                'current_app': admin.admin_site.name,
                'has_change_permission': admin.has_change_permission(request),
                'add': True, 'opts': opts,
                'root_path': admin.admin_site.root_path,
                'app_label': opts.app_label})

        #this renders the wizard.
        #the forms are rendered as Adminforms
    #formtype is a string that decribes the current form and is printed in the template
    def render_template(self, request, form, previous_fields, step, context=None):
        formtype = form.form_name
        form = AdminForm(form,
                         [(formtype, {'fields': form.base_fields.keys()})], {})
        context = context or {}
        context.update({'media': self._model_admin.media + form.media})
        return super(ClusterWizard, self).render_template(request, form,
                                                          previous_fields,
                                                          step, context)

#these are used to call the wizards.
create_station = StationWizard([StationForm, StationContactForm, ProfessionForm, ContactForm, ICTProfessionForm])
create_contact = ContactWizard([ContactForm, ProfessionForm])
create_cluster = ClusterWizard([ClusterForm, CountryForm])
create_subcluster = SubClusterWizard([SubClusterForm])

#this function takes a list of forms and creates a dictionary of all the fields and their value.
#this is used to create the summary
def GetModelData(forms):
    model_data = SortedDict()
    for form in forms:
        for field in form:
            model_data[field.label] = form.cleaned_data[field.name]
    return model_data
