from django import forms
from django.forms import fields, models, widgets
from django.contrib.formtools.wizard import FormWizard
from inforecords.models import *
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.shortcuts import render_to_response
from django.utils.datastructures import SortedDict

class ClusterForm(forms.Form):
	cluster_name = forms.CharField(max_length=70,label='Cluster Name')
	cluster_country = forms.ModelChoiceField(queryset=Country.objects.all(),required=False,empty_label='new country',label='country')
	cluster_url = forms.URLField(required=False, label='url')
   
class SubClusterForm(forms.Form):
	subcluster_name = forms.CharField(max_length= 70, label='Cluster Name')
	parent = forms.ModelChoiceField(queryset=Cluster.objects.filter(parent=None),empty_label=None, label='parent cluster')
	subcluster_url = forms.URLField(required=False, label='url')

class CountryForm(forms.Form):
	country_name = forms.CharField(max_length=70,label='Country Name')
	country_number = forms.IntegerField()

class ContactForm(forms.Form):
	contact_first_name = forms.CharField(max_length=40,label='First Name')
	contact_prefix_surname = forms.CharField(max_length=10,label='Prefix surname',required=False)
	contact_surname = forms.CharField(max_length=40, label='Surname')
	contact_profession = forms.ModelChoiceField(queryset=Profession.objects.all(),empty_label='new profession', label='profession',required=False)
	contact_title = forms.CharField(max_length=20, label='Title',required=False)
	contact_street_1 = forms.CharField(max_length=40, label='street')
	contact_street_2 = forms.CharField(max_length=40, label='street', required=False)
	contact_postalcode = forms.CharField(max_length=6, label='postalcode') 
	contact_city = forms.CharField(max_length=40,label='city')
	contact_pobox = forms.CharField(max_length=9,label='pobox', required=False)
	contact_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
	contact_pobox_city = forms.CharField(max_length=40,label='pobox City', required=False)
	contact_phone_work = forms.CharField(max_length=20,label='Phone Work')
	contact_phone_home = forms.CharField(max_length=20,label='Phone Home', required=False)
	contact_fax = forms.CharField(max_length=20,label='Fax', required=False)
	contact_email_work = forms.EmailField(label = 'Email Work')
	contact_email_private = forms.EmailField(label = 'Email Private', required=False)
	contact_url = forms.URLField(label = 'url', required=False)

class StationContactForm(forms.Form):
        stationcontact_first_name = forms.CharField(max_length=40,label='First Name')
        stationcontact_prefix_surname = forms.CharField(max_length=10, label='Prefix surname',required=False)
        stationcontact_surname = forms.CharField(max_length=40, label='Surname')
        stationcontact_profession = forms.ModelChoiceField(queryset=Profession.objects.all(),empty_label='new profession', label='profession',required=False)
        stationcontact_title = forms.CharField(max_length=20, label='title')
        stationcontact_street_1 = forms.CharField(max_length=40, label='street')
        stationcontact_street_2 = forms.CharField(max_length=40, label='street', required=False)
        stationcontact_postalcode = forms.CharField(max_length=6, label='postalcode')
        stationcontact_city = forms.CharField(max_length=40,label='city')
        stationcontact_pobox = forms.CharField(max_length=9,label='pobox', required=False)
        stationcontact_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
        stationcontact_pobox_city = forms.CharField(max_length=40,label='pobox City', required=False)
        stationcontact_phone_work = forms.CharField(max_length=20,label='Phone Work')
        stationcontact_phone_home = forms.CharField(max_length=20,label='Phone Home', required=False)
        stationcontact_fax = forms.CharField(max_length=20,label='Fax', required=False)
        stationcontact_email_work = forms.EmailField(label = 'Email Work')
        stationcontact_email_private = forms.EmailField(label = 'Email Private', required=False)
        stationcontact_url = forms.URLField(label = 'url', required=False)

class StationForm(forms.Form):
	station_cluster = forms.ModelChoiceField(queryset=Cluster.objects.all(),empty_label=None,label='cluster')
        station_street_1 = forms.CharField(max_length=40, label='street')
        station_street_2 = forms.CharField(max_length=40, label='street', required=False)
        station_postalcode = forms.CharField(max_length=6, label='postalcode')
        station_city = forms.CharField(max_length=40,label='city')
        station_pobox = forms.CharField(max_length=9,label='pobox', required=False)
        station_pobox_postalcode = forms.CharField(max_length=6, label='Pobox Postalcode', required=False)
        station_pobox_city = forms.CharField(max_length=40,label='pobox City', required=False)
        station_phone_work = forms.CharField(max_length=20,label='Phone Work')
        station_phone_home = forms.CharField(max_length=20,label='Phone Home', required=False)
        station_fax = forms.CharField(max_length=20,label='Fax', required=False)
        station_email_work = forms.EmailField(label = 'Email Work')
        station_email_private = forms.EmailField(label = 'Email Private', required=False)
        station_url = forms.URLField(label = 'url', required=False)
        station_password = forms.CharField(max_length=40, label='password')
        station_infopage = forms.URLField(label = 'infopage', required=False)
	station_contact = forms.ModelChoiceField(queryset=Contact.objects.all(),empty_label='Nieuwe contactpersoon',label='contactpersoon',required=False) 
        station_contact_is_ict = forms.BooleanField(label = 'Contact is also ICT contact',required=False)
        station_ict_contact = forms.ModelChoiceField(queryset=Contact.objects.all(),empty_label='gelijk aan contact of nieuw contactpersoon',label = 'ICT contactpersoon',required=False)

class ProfessionForm(forms.Form):
	profession_description = forms.CharField(max_length=40, label='profession')
class ICTProfessionForm(forms.Form):
        ICTprofession_description = forms.CharField(max_length=40, label='profession')

class StationWizard(FormWizard):
        @property
        def __name__(self):
                return self.__class__.__name__
	
	def done(self, request, form_list):
		data= {}
		for form in form_list:
			data.update(form.cleaned_data)
                station_contact_information = ContactInformation(
                        street_1 = data['station_street_1'],
                        street_2 = data['station_street_2'],
                        postalcode = data['station_postalcode'],
                        city = data['station_city'],
                        pobox = data['station_pobox'],
                        pobox_postalcode = data['station_pobox_postalcode'],
                        pobox_city = data['station_pobox_city'],
                        phone_work = data['station_phone_work'],
                        phone_home = data['station_phone_home'],
                        fax = data['station_fax'],
                        email_work = data['station_email_work'],
                        email_private = data['station_email_private'],
                        url = data['station_url']
                )
		station_contact_information.save()
		if data['station_contact'] == None:
			contact_contact_information = ContactInformation(
                        	street_1 = data['stationcontact_street_1'],
                        	street_2 = data['stationcontact_street_2'],
                        	postalcode = data['stationcontact_postalcode'],
                        	city = data['stationcontact_city'],
                        	pobox = data['stationcontact_pobox'],
                        	pobox_postalcode = data['stationcontact_pobox_postalcode'],
                        	pobox_city = data['stationcontact_pobox_city'],
                        	phone_work = data['stationcontact_phone_work'],
                        	phone_home = data['stationcontact_phone_home'],
                        	fax = data['stationcontact_fax'],
                        	email_work = data['stationcontact_email_work'],
                        	email_private = data['stationcontact_email_private'],
                        	url = data['stationcontact_url']
				)
			contact_contact_information.save()
			if data['stationcontact_profession']==None:
                        	profession = Profession(
                                	description = data['profession_description']
                        	)
                        	profession.save()
                	else:
                        	profession = data['stationcontact_profession']
                	stationcontact = Contact(
                        	profession = profession,
                        	title = data['stationcontact_title'],
                        	first_name = data['stationcontact_first_name'],
                        	prefix_surname = data['stationcontact_prefix_surname'],
                        	surname = data['stationcontact_surname'],
                        	contactinformation = contact_contact_information
                        	)
			stationcontact.save()
		else:
			stationcontact = data['station_contact']
		
                if data['station_ict_contact'] == None and data['station_contact_is_ict'] != True:
                        ICT_contact_information = ContactInformation(
                                street_1 = data['contact_street_1'],
                                street_2 = data['contact_street_2'],
                                postalcode = data['contact_postalcode'],
                                city = data['contact_city'],
                                pobox = data['contact_pobox'],
                                pobox_postalcode = data['contact_pobox_postalcode'],
                                pobox_city = data['contact_pobox_city'],
                                phone_work = data['contact_phone_work'],
                                phone_home = data['contact_phone_home'],
                                fax = data['contact_fax'],
                                email_work = data['contact_email_work'],
                                email_private = data['contact_email_private'],
                                url = data['contact_url']
                                )
                        ICT_contact_information.save()
                        if data['contact_profession']==None:
                                ictprofession = Profession(
                                        description = data['ICTprofession_description']
                                )
                                ictprofession.save()
                        else:
                        	ictprofession = data['contact_profession']
                        station_ict_contact = Contact(
                       	profession = ictprofession,
                        title = data['contact_title'],
                        first_name = data['contact_first_name'],
                        prefix_surname = data['contact_prefix_surname'],
                        surname = data['contact_surname'],
                        contactinformation = ICT_contact_information
                        )
			station_ict_contact.save()	
		elif data['station_contact_is_ict']:
			station_ict_contact = stationcontact
		else:
                	station_ict_contact = data['station_ict_contact']

		station = Station(
			contactinformation = station_contact_information,
			cluster = data['station_cluster'],
			contact = stationcontact,
			ict_contact = station_ict_contact,
			password = data['station_password'],
			info_page = data['station_infopage']
			)
		station.save()
                modeldata= GetModelData(form_list)
                response={"modeldata":modeldata}
                return render_to_response('summary.html',response)

	def process_step(self, request,form, step):
        	if form.is_valid():
			formtype=form.__class__.__name__
			if formtype=='StationForm': 
				if form.cleaned_data['station_contact']!=None and StationContactForm in self.form_list:
					self.form_list.remove(StationContactForm)
					self.form_list.remove(ProfessionForm)
				if form.cleaned_data['station_ict_contact']!=None and ContactForm in self.form_list:
					self.form_list.remove(ContactForm)
			 		self.form_list.remove(ICTProfessionForm)
                                if form.cleaned_data['station_contact_is_ict']==True and ContactForm in self.form_list:
                                        self.form_list.remove(ContactForm)
                                        self.form_list.remove(ICTProfessionForm)
			if formtype=='StationContactForm':
				if form.cleaned_data['stationcontact_profession']!=None and ProfessionForm in self.form_list:
					self.form_list.remove(ProfessionForm)
			if formtype=='ContactForm':
				if form.cleaned_data['contact_profession']!=None and ICTProfessionForm in self.form_list:
					self.form_list.remove(ICTProfessionForm)
	
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

        def render_template(self, request, form, previous_fields, step, context=None):
                from django.contrib.admin.helpers import AdminForm
                form = AdminForm(form, [(
                        'Step %d of %d' % (step + 1, self.num_steps()),
                        {'fields': form.base_fields.keys()}
                        )], {})
                context = context or {}
                context.update({
                        'media': self._model_admin.media + form.media
                })
                return super(StationWizard, self).render_template(request, form, previous_fields, step, context)

			
				 

			

		

class ContactWizard(FormWizard):
	@property
        def __name__(self):
                return self.__class__.__name__
        def done(self, request, form_list):
                data = {}
                for form in form_list:
                        data.update(form.cleaned_data)
                contact_information = ContactInformation(
			street_1 = data['contact_street_1'],
			street_2 = data['contact_street_2'],
			postalcode = data['contact_postalcode'],
			city = data['contact_city'],
			pobox = data['contact_pobox'],
			pobox_postalcode = data['contact_pobox_postalcode'],
			pobox_city = data['contact_pobox_city'],
			phone_work = data['contact_phone_work'],
			phone_home = data['contact_phone_home'],
			fax = data['contact_fax'],
			email_work = data['contact_email_work'],
			email_private = data['contact_email_private'],
                        url = data['contact_url']
                )
                contact_information.save()
		if data['contact_profession']==None:
			profession = Profession(
				description = data['profession_description']
			)
			profession.save()
		else:			
			profession = data['contact_profession']
		
		contact = Contact(
			profession = profession,
			title = data['contact_title'],
			first_name = data['contact_first_name'],
			prefix_surname = data['contact_prefix_surname'],
			surname = data['contact_surname'],
			contactinformation = contact_information
			)
		contact.save()
		modeldata= GetModelData(form_list)
		response={"modeldata":modeldata} 
		return render_to_response('summary.html',response)
        def process_step(self, request, form, step):
                if form.is_valid():
                        formtype=form.__class__.__name__
                        if formtype=='ContactForm':
                                if form.cleaned_data['contact_profession']!=None and ProfessionForm in self.form_list:
                                        self.form_list.remove(ProfessionForm)
        def parse_params(self, request, admin=None, *args, **kwargs):
                self._model_admin = admin
                opts = Contact._meta
                self.extra_context.update({
                        'title': 'Add %s' % force_unicode(opts.verbose_name),
                        'current_app': admin.admin_site.name,
                        'has_change_permission': admin.has_change_permission(request),
                        'add': True,
                        'opts': opts,
                        'root_path': admin.admin_site.root_path,
                        'app_label': opts.app_label})

        def render_template(self, request, form, previous_fields, step, context=None):
                from django.contrib.admin.helpers import AdminForm
                form = AdminForm(form, [(
                        'Step %d of %d' % (step + 1, self.num_steps()),
                        {'fields': form.base_fields.keys()}
                        )], {})
                context = context or {}
                context.update({
                        'media': self._model_admin.media + form.media
                })
                return super(ContactWizard, self).render_template(request, form, previous_fields, step, context)

class SubClusterWizard(FormWizard):
	@property
	def __name__(self):
                return self.__class__.__name__

        def done(self, request, form_list):
                data = {}
                for form in form_list:
                        data.update(form.cleaned_data)
                subcluster = Cluster(
                        name = data['subcluster_name'],
                        number = None,
                        parent = data['parent'],
                        country = data['parent'].country,
                        url = data['subcluster_url']
                )
                subcluster.save()
                modeldata= GetModelData(form_list)
                response={"modeldata":modeldata}
                return render_to_response('summary.html',response)

        def parse_params(self, request, admin=None, *args, **kwargs):
                self._model_admin = admin
                opts = Cluster._meta
                self.extra_context.update({
                        'title': 'Add %s' % force_unicode(opts.verbose_name),
                        'current_app': admin.admin_site.name,
                        'has_change_permission': admin.has_change_permission(request),
                        'add': True,
                        'opts': opts,
                        'root_path': admin.admin_site.root_path,
                        'app_label': opts.app_label})
        
	def render_template(self, request, form, previous_fields, step, context=None):
                from django.contrib.admin.helpers import AdminForm
                form = AdminForm(form, [(
                        'Step %d of %d' % (step + 1, self.num_steps()),
                        {'fields': form.base_fields.keys()}
                        )], {})
                context = context or {}
                context.update({
                       'media': self._model_admin.media + form.media
                })
                return super(SubClusterWizard, self).render_template(request, form, previous_fields, step, context)

class ClusterWizard(FormWizard):
	@property
	def __name__(self):
		return self.__class__.__name__

	def done(self, request, form_list):
		data = {}
		for form in form_list:
			data.update(form.cleaned_data)
		if data['cluster_country']==None:
			country = Country(
				name = data['country_name'],
				number = data['country_number']
			)
       		else:
    			country = data['cluster_country']
		country.save()
		cluster = Cluster(
			name = data['cluster_name'],
			number = None, 
    			parent = None,
    			country = country,
    			url = data['cluster_url']
		)
		cluster.save()
                modeldata= GetModelData(form_list)
                response={"modeldata":modeldata}
                return render_to_response('summary.html',response)

	def process_step(self, request, form, step):
		data = {}
		data.update(form.cleaned_data)
		if self.step==0 and data['cluster_country']!=None:
			self.form_list.remove(CountryForm)
			
	def parse_params(self, request, admin=None, *args, **kwargs):
    		self._model_admin = admin 
    		opts = Cluster._meta 
                self.extra_context.update({
                        'title': 'Add %s' % force_unicode(opts.verbose_name),
                        'current_app': admin.admin_site.name,
                        'has_change_permission': admin.has_change_permission(request),
                        'add': True,
                        'opts': opts,
                        'root_path': admin.admin_site.root_path,
                        'app_label': opts.app_label})	
	def render_template(self, request, form, previous_fields, step, context=None):
    		from django.contrib.admin.helpers import AdminForm
    		form = AdminForm(form, [(
        		'Step %d of %d' % (step + 1, self.num_steps()),
        		{'fields': form.base_fields.keys()}
        		)], {})
    		context = context or {}
    		context.update({
        		'media': self._model_admin.media + form.media
    		})
    		return super(ClusterWizard, self).render_template(request, form, previous_fields, step, context)

create_station = StationWizard([StationForm, StationContactForm, ProfessionForm, ContactForm, ICTProfessionForm])
create_contact = ContactWizard([ContactForm, ProfessionForm])			
create_cluster = ClusterWizard([ClusterForm, CountryForm])
create_subcluster = SubClusterWizard([SubClusterForm])

def GetModelData(forms):
    model_data = SortedDict() 
    for form in forms:
    	for field in form:
        	model_data[field.label] = form.cleaned_data[field.name]
    return model_data 
