#!/usr/bin/env python

import logging
import traceback

from math import sqrt

import numpy

from scipy import optimize, stats

from . import esd
from .models import Configuration, PulseheightFit

logger = logging.getLogger('histograms.fit_pulseheight_peak')


def find_bin_next_minimum(y, start_bin):

    min_y = y[start_bin]

    for i in range(start_bin, len(y) + 1):
        current_y = y[i]
        # logger.debug("Bin %i: %s" % (i, current_y))
        if current_y < min_y:
            min_y = y[i]
        if current_y > min_y:
            return i - 1


def find_bin_next_maximum(y, start_bin):

    max_y = y[start_bin]

    for i in range(start_bin, len(y) + 1):
        current_y = y[i]
        # logger.debug("Bin %i: %s" % (i, current_y))
        if current_y > max_y:
            max_y = y[i]
        if current_y < max_y:
            return i - 1


def smooth_forward(y, n=5):

    y_smoothed = []

    for i in range(0, len(y) - n):
        sum = numpy.sum(y[i:i + n])
        avg = sum / n
        y_smoothed.append(avg)

    return y_smoothed


def get_fit_parameters(x, y):

    bias = (x[1] - x[0]) * 2

    # Rebin x

    x_rebinned = x.tolist()
    if len(x_rebinned) % 2 == 1:
        x_rebinned.append(x_rebinned[-1] + x_rebinned[1] - x_rebinned[0])
    x_rebinned = numpy.float_(x_rebinned)
    x_rebinned = x_rebinned.reshape(len(x_rebinned) / 2, 2).mean(axis=1)

    # Smooth y by averaging while keeping sharp cut at 120 ADC

    y_smoothed = smooth_forward(y, 5)

    for i in range(len(y_smoothed)):
        if x[i] > 120:
            break
        y_smoothed[i] = 0
    y_smoothed = numpy.float_(y_smoothed)

    # First derivative y while keeping sharp cut at 120 ADC

    if len(y_smoothed) % 2 == 1:
        y_smoothed = y_smoothed.tolist()
        y_smoothed.append(0.0)
        y_smoothed = numpy.float_(y_smoothed)

    y_smoothed_rebinned = (2 * y_smoothed.reshape(len(y_smoothed) / 2, 2)
                                         .mean(axis=1))

    y_diff = numpy.diff(y_smoothed_rebinned)

    for i in range(len(y_diff)):
        if x_rebinned[i] > 120:
            break

        y_diff[i] = 0

    # Smooth y by averaging while keeping sharp cut at 120 ADC

    y_diff_smoothed = numpy.convolve(y_diff, [0.2, 0.2, 0.2, 0.2, 0.2, 0], "same")

    for i in range(len(y_diff_smoothed)):
        if x_rebinned[i] > 120:
            break
        y_diff_smoothed[i] = 0

    # Find approx max using the derivative

    bin_minimum = find_bin_next_minimum(y_diff_smoothed, 0)
    bin_maximum = find_bin_next_maximum(y_diff_smoothed, bin_minimum)
    bin_minimum = find_bin_next_minimum(y_diff_smoothed, bin_maximum)

    max_x = x_rebinned[bin_maximum]
    min_x = x_rebinned[bin_minimum]

    # logger.debug("Approx maximum is at %s" % ((max_x + min_x) / 2))

    # Return fit peak, fit range minimum = max_x, fit range maximum = min_x

    return (max_x + min_x) / 2 + bias, max_x + bias, min_x + bias


def gauss(x, n, m, s):
    """Gaussian function for fitting"""
    return n * stats.norm.pdf(x, m, s)


def residual(params, x, y_data):
    """Residual which is to be minimized"""
    return y_data - gauss(x, *params)


def fit_pulseheight_peak(pulseheights):
    """
        pulseheights  : nparray
    """

    # Contents
    #
    # 1. Initialize work space
    # 2. Make histogram: occurence of dPulseheight vs pulseheight
    # 3. Get initial fit parameters for gauss: mean and width
    # 4. Fit with gauss
    # 5. Calculate the Chi2
    # 6. Return

    # 1. Initialize work space

    ph_min = 50  # ADC
    ph_max = 1550  # ADC

    pulseheight_fit = PulseheightFit(
        initial_mpv=0, initial_width=0, fitted_mpv=0,
        fitted_mpv_error=0, fitted_width=0, fitted_width_error=0,
        degrees_of_freedom=0, chi_square_reduced=0,
        error_type="", error_message="")

    # 2. Make histogram: occurence of dPulseheight vs pulseheight

    bins = numpy.arange(ph_min, ph_max, 10)

    occurence, bins = numpy.histogram(pulseheights, bins=bins)
    pulseheight = (bins[:-1] + bins[1:]) / 2

    # Do initial checks

    sum = occurence.sum()

    if sum < 100:
        pulseheight_fit.error_message = ("Sum is less than 100 ADC. Dataset "
                                         "is probably empty")
        return pulseheight_fit

    average_pulseheight = (pulseheight * occurence).sum() / occurence.sum()

    if average_pulseheight < 100:
        pulseheight_fit.error_message = ("Average pulseheight is less than "
                                         "100 ADC")
        return pulseheight_fit

    # 3. Get initial fit parameters for gauss: mean and width

    try:
        initial_mpv, minRange, maxRange = get_fit_parameters(pulseheight,
                                                             occurence)
        # logger.debug("Initial peak, minRange, maxRange: %s, %s, %s" %
        #              (initial_mpv, minRange, maxRange))
    except Exception, e:
        pulseheight_fit.error_type = "Exception"
        pulseheight_fit.error_message = ("Unable to find initial fit "
                                         "parameters: %s" % e)
        return pulseheight_fit

    pulseheight_fit.initial_mpv = initial_mpv
    pulseheight_fit.initial_width = initial_mpv - minRange

    # Check the width. More than 40 ADC is nice, just to be able to have a fit
    # at all.

    if pulseheight_fit.initial_width <= 40.0:
        pulseheight_fit.error_message = ("Initial width is less than or equal "
                                         "to 40 ADC. It should be more than "
                                         "that for a good fit")
        return pulseheight_fit

    # 4. Fit with gauss

    # Cut our data set

    fit_window_pulseheight = []
    fit_window_occurence = []
    for i in range(len(pulseheight)):
        if minRange < pulseheight[i] < maxRange:
            fit_window_pulseheight.append(pulseheight[i])
            fit_window_occurence.append(occurence[i])

    if 0 in fit_window_occurence:
        pulseheight_fit.error_message = (
            "There is an empty bin in the fit range. This is probably because "
            "the fit occurs somewhere in the tail of the histogram.")
        return pulseheight_fit

    # Initial parameter values

    initial_n = 16
    initial_mean = pulseheight_fit.initial_mpv
    initial_width = pulseheight_fit.initial_width

    try:
        fit_result = optimize.curve_fit(gauss,
                                        fit_window_pulseheight,
                                        fit_window_occurence,
                                        [initial_n, initial_mean,
                                         initial_width])
    except RuntimeError, exception:
        pulseheight_fit.error_type = "RuntimeError"
        pulseheight_fit.error_message = exception
        return pulseheight_fit

    fit_parameters = fit_result[0]
    fit_covariance = fit_result[1]

    if numpy.isinf(fit_covariance).any():
        pulseheight_fit.error_message = \
            "Unable to calculate the covariance matrix."
        fit_covariance = numpy.zeros((3, 3))

    # 5. Calculate the Chi2

    # Chi2 = Sum((y_data - y_fitted)^2 / sigma^2)
    # It is assumed that the events per bin are poisson distributed.
    # Sigma^2 for a poisson process is the same as the number of
    # events in the bin

    chi_square = (residual(fit_parameters, fit_window_pulseheight,
                           fit_window_occurence) ** 2 /
                  fit_window_occurence).sum()

    pulseheight_fit.degrees_of_freedom = (len(fit_window_occurence) -
                                          len(fit_parameters))
    pulseheight_fit.chi_square_reduced = (chi_square /
                                          pulseheight_fit.degrees_of_freedom)

    # 6. Return

    pulseheight_fit.fitted_mpv = fit_parameters[1]
    pulseheight_fit.fitted_mpv_error = sqrt(fit_covariance[1, 1])
    pulseheight_fit.fitted_width = fit_parameters[2]
    pulseheight_fit.fitted_width_error = sqrt(fit_covariance[2, 2])

    logger.debug("Fit result: peak %.1f +- %.1f, width %.1f +- %.1f" %
                 (fit_parameters[1], sqrt(fit_covariance[1, 1]),
                  fit_parameters[2], sqrt(fit_covariance[2, 2])))
    # logger.debug("Chi square: %.3f" % chi_square)
    # logger.debug("Degrees of freedom: %d" %
    #              pulseheight_fit.degrees_of_freedom)
    # logger.debug("Reduced chi square: %.1f" %
    #              pulseheight_fit.chi_square_reduced)

    return pulseheight_fit


def get_pulseheight_fits(summary):
    """Get pulseheight fits

    :param summary: Summary object

    """

    # Get pulseheight data from ESD

    pulseheights = esd.get_event_data(summary, 'pulseheights')

    if pulseheights is None:
        return []

    # Get number of detectors from the config data
    try:
        n_detectors = summary.station.number_of_detectors()
    except Configuration.DoesNotExist:
        raise

    # Get fits

    fits = []

    for detector_n in range(1, n_detectors + 1):
        try:
            fit = fit_pulseheight_peak(pulseheights[:, detector_n - 1])
        except Exception, exception:
            logger.error("[%s detector %s] %s" %
                         (summary, detector_n, exception))

            fit = PulseheightFit(initial_mpv=0,
                                 initial_width=0,
                                 fitted_mpv=0,
                                 fitted_mpv_error=0,
                                 fitted_width=0,
                                 fitted_width_error=0,
                                 degrees_of_freedom=0,
                                 chi_square_reduced=0,
                                 error_type="",
                                 error_message="")
            fit.error_type = "Exception"
            fit.error_message = traceback.format_exc()

        fit.source = summary
        fit.plate = detector_n

        fits.append(fit)

    return fits
