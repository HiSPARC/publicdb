#!/usr/bin/env python

import sys
import os
import re
import code
import string
import logging
from math import sqrt

import types

import tables
import numpy
import scipy
import scipy.optimize
import scipy.stats

from models import *
import datastore

from django_publicdb.inforecords.models import Station


logger = logging.getLogger('histograms.fit_pulseheight_peak')

uid = 0
hists = []

import datastore
from django_publicdb.histograms.models import *

def findBinNextMinimum(y, startBin):

    minY = y[startBin]

    for i in range(startBin, len(y)+1):

        currentY = y[i]

        #print "Bin %i: %s" % (i, currentY)

        if currentY < minY:
            minY = y[i]

        if currentY > minY:
            return i-1


def findBinNextMaximum(y, startBin):

    maxY = y[startBin]

    for i in range(startBin, len(y) + 1):

        currentY = y[i]

        #print "Bin %i: %s" % (i, currentY)

        if currentY > maxY:
            maxY = y[i]

        if currentY < maxY:
            return i-1


def smooth_forward(y, n=5):
    y_smoothed = []
    for i in range(0, len(y)-n):
        sum = numpy.sum(y[i:i+n])
        avg = sum / n
        y_smoothed.append(avg)

    return y_smoothed


def getFitParameters(x, y, stationNumber, plateNumber):

    bias = (x[1]-x[0])*2

    # Rebin x

    x_rebinned = x.tolist()
    if len(x_rebinned) % 2 == 1:
        x_rebinned.append(x_rebinned[-1] + x_rebinned[1] - x_rebinned[0])
    x_rebinned = numpy.float_(x_rebinned)
    x_rebinned = x_rebinned.reshape(len(x_rebinned)/2, 2).mean(axis=1)

    # Smooth y by averaging while keeping sharp cut at 120 ADC

    y_smoothed = smooth_forward(y, 5)

    for i in range(len(y_smoothed)):
        if x[i] > 120:
            break
        y_smoothed[i] = 0

    #plot(x[0:200], y_smoothed[0:200], "-o")

    y_smoothed = numpy.float_(y_smoothed)

    # First derivative y while keeping sharp cut at 120 ADC

    if len(y_smoothed) % 2 == 1:
        y_smoothed = y_smoothed.tolist()
        y_smoothed.append(0.0)
        y_smoothed = numpy.float_(y_smoothed)

    y_smoothed_rebinned = 2*y_smoothed.reshape(len(y_smoothed)/2, 2).mean(axis=1)

    y_diff = numpy.diff(y_smoothed_rebinned)

    for i in range(len(y_diff)):
        if x_rebinned[i] > 120:
            break

        y_diff[i] = 0

    #plot(x_rebinned[0:200], y_diff[0:200], 'o')

    # Smooth y by averaging while keeping sharp cut at 120 ADC

    y_diff_smoothed = numpy.convolve(y_diff, [0.2, 0.2, 0.2, 0.2, 0.2, 0], "same")

    for i in range(len(y_diff_smoothed)):
        if x_rebinned[i] > 120:
            break
        y_diff_smoothed[i] = 0

    # Plot

    plot(x_rebinned[0:200], y_diff_smoothed[0:200])

    # Find approx max using the derivative

    binMinimum = findBinNextMinimum(y_diff_smoothed, 0)

    #print "Found minimum at x = %s" % hist.GetBinCenter( binMinimum)

    binMaximum = findBinNextMaximum(y_diff_smoothed, binMinimum)

    print "Found maximum at x = %s" % x_rebinned[binMaximum]

    binMinimum = findBinNextMinimum(y_diff_smoothed, binMaximum)

    print "Found minimum at x = %s" % x_rebinned[binMinimum]

    maxX = x_rebinned[binMaximum]
    minX = x_rebinned[binMinimum]

    print "approx maximum is at %s" % ((maxX + minX)/2)

    # Return fit peak, fit range minimum = maxX, fit range maximum = minX

    return (maxX + minX)/2 + bias, maxX+bias, minX+bias


def fitPulseheightPeak(events, stationNumber, plateNumber):
    """
        events        : table
        plateNumber   : int 0..3
        stationNumber : int
    """

    if len(events) == 0:
        return

    if plateNumber > 3 or plateNumber < 0:
        return

    if len(events) == 0:
        return

    phMin = 50  # ADC
    phMax = 1550.0 # ADC

    #---------------------------------------------------------------------------
    # Data
    #---------------------------------------------------------------------------

    data = []

    for event in events:

        ph = event['pulseheights'][plateNumber]

        if ph < phMin or ph > phMax:
            continue

        data.append(ph)

    #---------------------------------------------------------------------------
    # Determine fit range
    #---------------------------------------------------------------------------

    # Make histogram: occurence of dPulseheight vs pulseheight

    bins = numpy.arange(0, 5000, 10)

    occurence, bins = numpy.histogram(numpy.float_(data), bins=bins)
    pulseheight     = (bins[:-1] + bins[1:]) / 2

    plot(pulseheight, occurence, 'o')
    xlabel('Pulseheight (ADC)')
    ylabel('Number of events')

    # Get fit parameters

    average_pulseheight = (pulseheight * occurence).sum() / occurence.sum()

    if average_pulseheight < 100:
        raise ValueError( "Average pulseheight is less than 100" )

    peak, minRange, maxRange = getFitParameters(pulseheight, occurence,
                                                stationNumber, plateNumber)
    width = peak - minRange

    peakOrig = peak

    print "Initial peak, minRange, maxRange: %s, %s, %s" %(peak, minRange, maxRange)

    # Check the width. More than 40 ADC is nice, just to be able to have a fit
    # at all.

    if width <= 40:
        fitParameters = numpy.zeros(3)
        fitCovariance = numpy.zeros((3,3))

        fitResult     = [fitParameters, fitCovariance]
        chiSquare     = -1

        return len(data), peak, width, fitResult, chiSquare

    #---------------------------------------------------------------------------
    # Fit within found fit range
    #---------------------------------------------------------------------------

    # Fit function

    gauss = lambda x, N, m, s: N * scipy.stats.norm.pdf(x, m, s)

    # Residual which is to be minimized

    def residual(params, x, y_data):
        constant = params[0]
        mean     = params[1]
        width    = params[2]

        y_model = gauss(x, constant, mean, width)

        return (y_data-y_model)

    # Cut our data set such that it only include minRange < pulseheight < maxRange

    fit_window_pulseheight = []
    fit_window_occurence   = []
    for i in range(len(pulseheight)):
        if pulseheight[i] < minRange:
            continue

        if pulseheight[i] > maxRange:
            continue

        fit_window_pulseheight.append(pulseheight[i])
        fit_window_occurence.append(occurence[i])

    # Initial parameter values

    initial_N = 16
    initial_mean = peak
    initial_width = width

    # Fit

    print "Count pulseheight: %d" % len(fit_window_pulseheight)
    print "Count occurence:   %d" % len(fit_window_occurence)

    fitResult = scipy.optimize.curve_fit(gauss,
                                         fit_window_pulseheight,
                                         fit_window_occurence,
                                         [initial_N, initial_mean, initial_width])

    fitParameters = fitResult[0]
    fitCovariance = fitResult[1]

    # Calculate the Chi2
    # Chi2 = Sum( (y_data - y_fitted)^2 / sigma^2 )
    # It is assumed that the events per bin are poisson distributed.
    # Sigma^2 for a poisson process is the same as the number of events in the bin
    # Sigma is then sqrt(number of events in bin)

    chiSquare = (residual(fitParameters,
                          fit_window_pulseheight,
                          fit_window_occurence)**2 / fit_window_occurence).sum()
    reducedChiSquare = chiSquare / (len(fit_window_occurence) - len(fitParameters))

    logger.debug("Fit result: peak %.1f +- %.1f, width %.1f +- %.1f" %
                 (fitParameters[1], sqrt(fitCovariance[1,1]),
                  fitParameters[2], sqrt(fitCovariance[2,2])))
    logger.debug("Chi square: %.3f" % chiSquare)
    logger.debug("Degrees of freedom: %d" %
                 (len(fit_window_occurence) - len(fitParameters)))
    logger.debug("Reduced chi square: %.1f" % reducedChiSquare)

    return len(data), peak, width, fitResult, reducedChiSquare

#-------------------------------------------------------------------------------
# Prepare data
#-------------------------------------------------------------------------------

def getEventsFromStation( h5File, station ):
    """
        h5File:  tables.File
        station: int

        return: tables.Table
    """

    # Files created by the download_data function have a different structure
    # /station/events

    try:
        events = h5File.getNode('/s%s' % station, 'events')
        return events
    except:
        pass

    # Files in the datastore have another structure
    # /hisparc/cluster/station/events

    try:
        for clusterNode in h5File.root.hisparc:
            for stationNode in clusterNode:
                if string.count(stationNode.__str__(), "station_%s" % station):
                    return h5File.getNode(stationNode, "events")
    except:
        pass

def getPulseheightFits( summary ):
    """
        file: string
        station : int
    """

    #---------------------------------------------------------------------------
    # Checks
    #---------------------------------------------------------------------------

    if not isinstance(summary, Summary):
        raise Exception

    #---------------------------------------------------------------------------
    # Input data
    #---------------------------------------------------------------------------

    file = datastore.get_data_path(summary.date)
    data = tables.openFile(file, 'r')

    station = summary.station.number
    events = getEventsFromStation( data, station )

    if isinstance(events, types.NoneType) or len(events) == 0:
        logger.error("Error: no events found for station %s" % station)
        return

    #---------------------------------------------------------------------------
    # Fit
    #---------------------------------------------------------------------------

    fits = []

    for numberOfPlate in range(4):

        # Initial values

        fit = PulseheightFit(
            source = summary,
            plate = int(numberOfPlate),

            initial_mpv = 0,
            initial_width = 0,

            fitted_mpv = 0,
            fitted_mpv_error = 0,
            fitted_width = 0,
            fitted_width_error = 0,

            chi_square_reduced = -1
        )

        # Fit

        try:
            entries, initial_peak, initial_width, fit_result, chi_square_reduced = fitPulseheightPeak(events,
                                                                                                      station,
                                                                                                      numberOfPlate)

            fit.initial_mpv = initial_peak
            fit.initial_width = initial_width

            fit.fitted_mpv = fit_result[0][1]
            fit.fitted_mpv_error = sqrt(fit_result[1][1,1])
            fit.fitted_width = fit_result[0][2]
            fit.fitted_width_error = sqrt(fit_result[1][2,2])

            fit.chi_square_reduced = chi_square_reduced

        except ValueError:
            pass

        fits.append(fit)

    return fits
