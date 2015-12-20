from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.conf import settings

import datetime

from recaptcha.client import captcha

from .models import StationLayout, StationLayoutQuarantine
from .forms import StationLayoutQuarantineForm, ReviewStationLayoutForm
from ..histograms.models import Configuration


FIRSTDATE = datetime.date(2002, 1, 1)


def layout_submit(request):
    if request.method == 'POST':
        form = StationLayoutQuarantineForm(request.POST)
    else:
        form = StationLayoutQuarantineForm()

    html_captcha = "reCAPTCHA disabled"

    if settings.RECAPTCHA_ENABLED:
        html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)

    return render(request, 'layout_submit.html',
                  {'form': form, 'html_captcha': html_captcha})


def validate_layout_submit(request):
    if request.method != 'POST':
        return redirect(layout_submit)

    if settings.RECAPTCHA_ENABLED:
        check_captcha = captcha.submit(
            request.POST['recaptcha_challenge_field'],
            request.POST['recaptcha_response_field'],
            settings.RECAPTCHA_PRIVATE_KEY,
            request.META['REMOTE_ADDR'])
        if not check_captcha.is_valid:
            return layout_submit(request)

    form = StationLayoutQuarantineForm(request.POST)

    if not form.is_valid():
        return layout_submit(request)

    new_layout = StationLayoutQuarantine(
        name=form.cleaned_data['name'],
        email=form.cleaned_data['email'],
        station=form.cleaned_data['station'],
        active_date=form.cleaned_data['active_date'],
        detector_1_alpha=form.cleaned_data['detector_1_alpha'],
        detector_1_beta=form.cleaned_data['detector_1_beta'],
        detector_1_radius=form.cleaned_data['detector_1_radius'],
        detector_1_height=form.cleaned_data['detector_1_height'],
        detector_2_alpha=form.cleaned_data['detector_2_alpha'],
        detector_2_beta=form.cleaned_data['detector_2_beta'],
        detector_2_radius=form.cleaned_data['detector_2_radius'],
        detector_2_height=form.cleaned_data['detector_2_height'],
        detector_3_alpha=form.cleaned_data['detector_3_alpha'],
        detector_3_beta=form.cleaned_data['detector_3_beta'],
        detector_3_radius=form.cleaned_data['detector_3_radius'],
        detector_3_height=form.cleaned_data['detector_3_height'],
        detector_4_alpha=form.cleaned_data['detector_4_alpha'],
        detector_4_beta=form.cleaned_data['detector_4_beta'],
        detector_4_radius=form.cleaned_data['detector_4_radius'],
        detector_4_height=form.cleaned_data['detector_4_height'])

    new_layout.generate_hashes()
    new_layout.save()
    new_layout.sendmail_submit()

    return render(request, 'layout_submitted.html',
                  {'name': form.cleaned_data['name'],
                   'email': form.cleaned_data['email'],
                   'station': form.cleaned_data['station']})


def confirmed_layout(request, hash):
    submitted_layout = get_object_or_404(StationLayoutQuarantine,
                                         hash_submit=hash,
                                         email_verified=False)
    submitted_layout.email_verified = True
    submitted_layout.save()
    submitted_layout.sendmail_review()
    return render(request, 'layout_confirm.html')


def review_layout(request, hash):
    submitted_layout = get_object_or_404(StationLayoutQuarantine,
                                         hash_review=hash,
                                         email_verified=True,
                                         reviewed=False)
    if request.method == 'POST':
        form = ReviewStationLayoutForm(request.POST)
    else:
        form = ReviewStationLayoutForm()

    try:
        station = submitted_layout.station
        active_date = submitted_layout.active_date.replace(hour=23, minute=59,
                                                           second=59)
        config = (Configuration.objects.filter(source__station=station,
                                               timestamp__gte=FIRSTDATE,
                                               timestamp__lte=active_date)
                                       .exclude(gps_latitude=0.)).latest()
    except Configuration.DoesNotExist:
        config = None

    return render(request, 'layout_review.html',
                  {'layout': submitted_layout, 'form': form, 'hash': hash,
                   'config': config})


def validate_review_layout(request, hash):
    if request.method != 'POST':
        raise Http404

    form = ReviewStationLayoutForm(request.POST)

    if not form.is_valid():
        return review_layout(request)

    submitted_layout = get_object_or_404(StationLayoutQuarantine,
                                         hash_review=hash,
                                         email_verified=True,
                                         reviewed=False)
    submitted_layout.reviewed = True
    submitted_layout.approved = form.cleaned_data['approved']
    submitted_layout.save()

    if form.cleaned_data['approved']:
        accepted_layout = StationLayout(
            station=submitted_layout.station,
            active_date=submitted_layout.active_date,
            detector_1_alpha=submitted_layout.detector_1_alpha,
            detector_1_beta=submitted_layout.detector_1_beta,
            detector_1_radius=submitted_layout.detector_1_radius,
            detector_1_height=submitted_layout.detector_1_height,
            detector_2_alpha=submitted_layout.detector_2_alpha,
            detector_2_beta=submitted_layout.detector_2_beta,
            detector_2_radius=submitted_layout.detector_2_radius,
            detector_2_height=submitted_layout.detector_2_height,
            detector_3_alpha=submitted_layout.detector_3_alpha,
            detector_3_beta=submitted_layout.detector_3_beta,
            detector_3_radius=submitted_layout.detector_3_radius,
            detector_3_height=submitted_layout.detector_3_height,
            detector_4_alpha=submitted_layout.detector_4_alpha,
            detector_4_beta=submitted_layout.detector_4_beta,
            detector_4_radius=submitted_layout.detector_4_radius,
            detector_4_height=submitted_layout.detector_4_height)
        accepted_layout.save()
        submitted_layout.sendmail_accepted()
    else:
        submitted_layout.sendmail_declined()

    return render(request, 'layout_reviewed.html')
