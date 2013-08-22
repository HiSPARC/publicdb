#!/usr/bin/env python

import sys
import os
import string
import logging
from math import sqrt
import datetime
import types

import tables
import numpy
import scipy
import scipy.optimize
import scipy.stats

from models import *
import esd


logger = logging.getLogger('histograms.fit_pulseheight_peak')


def findBinNextMinimum(y, startBin):

    minY = y[startBin]

    for i in range(startBin, len(y) + 1):
        currentY = y[i]
        #logger.debug("Bin %i: %s" % (i, currentY))
        if currentY < minY:
            minY = y[i]
        if currentY > minY:
            return i - 1


def findBinNextMaximum(y, startBin):

    maxY = y[startBin]

    for i in range(startBin, len(y) + 1):
        currentY = y[i]
        #logger.debug("Bin %i: %s" % (i, currentY))
        if currentY > maxY:
            maxY = y[i]
        if currentY < maxY:
            return i - 1


def smooth_forward(y, n=5):

    y_smoothed = []

    for i in range(0, len(y) - n):
        sum = numpy.sum(y[i:i + n])
        avg = sum / n
        y_smoothed.append(avg)

    return y_smoothed


def getFitParameters(x, y):

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

    y_smoothed_rebinned = 2 * y_smoothed.reshape(len(y_smoothed) / 2, 2).mean(axis=1)

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

    binMinimum = findBinNextMinimum(y_diff_smoothed, 0)
    binMaximum = findBinNextMaximum(y_diff_smoothed, binMinimum)
    binMinimum = findBinNextMinimum(y_diff_smoothed, binMaximum)

    maxX = x_rebinned[binMaximum]
    minX = x_rebinned[binMinimum]

    logger.debug("Approx maximum is at %s" % ((maxX + minX) / 2))

    # Return fit peak, fit range minimum = maxX, fit range maximum = minX

    return (maxX + minX) / 2 + bias, maxX + bias, minX + bias


def fitPulseheightPeak(pulseheights):
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

    #---------------------------------------------------------------------------
    # 1. Initialize work space

    phMin = 50  # ADC
    phMax = 1550  # ADC

    pulseheightFit = PulseheightFit(initial_mpv = 0,
                                    initial_width = 0,
                                    fitted_mpv = 0,
                                    fitted_mpv_error = 0,
                                    fitted_width = 0,
                                    fitted_width_error = 0,
                                    degrees_of_freedom = 0,
                                    chi_square_reduced = 0,
                                    error_type = "",
                                    error_message = "")

    #---------------------------------------------------------------------------
    # 2. Make histogram: occurence of dPulseheight vs pulseheight

    bins = numpy.arange(phMin, phMax, 10)

    occurence, bins = numpy.histogram(pulseheights, bins=bins)
    pulseheight = (bins[:-1] + bins[1:]) / 2

    # Do initial checks

    sum = occurence.sum()

    if sum < 100:
        pulseheightFit.error_message = "Sum is less than 100 ADC. Dataset is probably empty"
        return pulseheightFit

    average_pulseheight = (pulseheight * occurence).sum() / occurence.sum()

    if average_pulseheight < 100:
        pulseheightFit.error_message = "Average pulseheight is less than 100 ADC"
        return pulseheightFit

    #---------------------------------------------------------------------------
    # 3. Get initial fit parameters for gauss: mean and width

    try:
        initial_mpv, minRange, maxRange = getFitParameters(pulseheight, occurence)
        logger.debug("Initial peak, minRange, maxRange: %s, %s, %s" %
	             (initial_mpv, minRange, maxRange))
    except Exception, e:
        pulseheightFit.error_type = "Exception"
        pulseheightFit.error_message = "Unable to find initial fit parameters: %s" % e
        return pulseheightFit

    pulseheightFit.initial_mpv = initial_mpv
    pulseheightFit.initial_width = initial_mpv - minRange

    # Check the width. More than 40 ADC is nice, just to be able to have a fit
    # at all.

    if pulseheightFit.initial_width <= 40.0:
        pulseheightFit.error_message = "Initial width is less than or equal to 40 ADC. It should be more than that for a good fit"
        return pulseheightFit

    #---------------------------------------------------------------------------
    # 4. Fit with gauss

    # Fit function

    gauss = lambda x, N, m, s: N * scipy.stats.norm.pdf(x, m, s)

    # Residual which is to be minimized

    def residual(params, x, y_data):
        constant = params[0]
        mean = params[1]
        width = params[2]

        y_model = gauss(x, constant, mean, width)

        return (y_data - y_model)

    # Cut our data set

    fit_window_pulseheight = []
    fit_window_occurence = []
    for i in range(len(pulseheight)):
        if minRange < pulseheight[i] < maxRange:
            fit_window_pulseheight.append(pulseheight[i])
            fit_window_occurence.append(occurence[i])

    if 0 in fit_window_occurence:
        pulseheightFit.error_message = "There is an empty bin in the fit range. This is probably because the fit occurs somewhere in the tail of the histogram."
        return pulseheightFit

    # Initial parameter values

    initial_N = 16
    initial_mean = pulseheightFit.initial_mpv
    initial_width = pulseheightFit.initial_width

    try:
        fitResult = scipy.optimize.curve_fit(gauss,
                                             fit_window_pulseheight,
                                             fit_window_occurence,
                                             [initial_N, initial_mean, initial_width])
    except RuntimeError, exception:
        pulseheightFit.error_type = "RuntimeError"
        pulseheightFit.error_message = exception
        return pulseheightFit

    fitParameters = fitResult[0]
    fitCovariance = fitResult[1]

    #---------------------------------------------------------------------------
    # 5. Calculate the Chi2

    # Chi2 = Sum((y_data - y_fitted)^2 / sigma^2)
    # It is assumed that the events per bin are poisson distributed.
    # Sigma^2 for a poisson process is the same as the number of events in the bin

    chiSquare = (residual(fitParameters,
                          fit_window_pulseheight,
                          fit_window_occurence)**2 / fit_window_occurence).sum()

    pulseheightFit.degrees_of_freedom = (len(fit_window_occurence) - len(fitParameters))
    pulseheightFit.chi_square_reduced = chiSquare / pulseheightFit.degrees_of_freedom

    #---------------------------------------------------------------------------
    # 6. Return

    pulseheightFit.fitted_mpv = fitParameters[1]
    pulseheightFit.fitted_mpv_error = sqrt(fitCovariance[1,1])
    pulseheightFit.fitted_width = fitParameters[2]
    pulseheightFit.fitted_width_error = sqrt(fitCovariance[2,2])

    logger.debug("Fit result: peak %.1f +- %.1f, width %.1f +- %.1f" %
                 (fitParameters[1], sqrt(fitCovariance[1,1]),
                  fitParameters[2], sqrt(fitCovariance[2,2])))
    logger.debug("Chi square: %.3f" % chiSquare)
    logger.debug("Degrees of freedom: %d" % pulseheightFit.degrees_of_freedom )
    logger.debug("Reduced chi square: %.1f" % pulseheightFit.chi_square_reduced)

    return pulseheightFit


def getPulseheightFits(summary):
    """
        summary: Summary
    """

    # Get pulseheight data from ESD

    pulseheights = esd.get_event_data(summary, 'pulseheights')

    if pulseheights == None:
        return []

    # Get number of plates from the config data

    today = datetime.datetime.utcnow()

    try:
        n_plates = summary.station.number_of_plates()
    except Configuration.DoesNotExist:
        raise

    # Get fits

    fits = []

    for numberOfPlate in range(1, n_plates + 1):
        try:
            fit = fitPulseheightPeak(pulseheights[:, numberOfPlate - 1])
        except Exception, exception:
            logger.error("[%s plate %s] %s" %
                         (summary, numberOfPlate, exception))
            fit = PulseheightFit()
            fit.error_type = "Exception"
            fit.error_message = exception

        fit.source = summary
        fit.plate = numberOfPlate

        fits.append(fit)

    return fits
