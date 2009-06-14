from symposium2009.models import *
import operator

def ver_weg_punt():
    for ac in AnalyzedCoincidence.objects.all():
        student = ac.student
        lat = ac.core_position_y
        long = ac.core_position_x
        if not 52 < lat < 53 or not 4 < long < 5:
            if lat and long:
                    print student, lat, long

def top_lijst():
    scores = []
    for s in Student.objects.all():
        error = []
        num_events = 0
        for ac in AnalyzedCoincidence.objects.filter(student=s):
            if ac.error_estimate:
                error.append(ac.error_estimate)
                num_events += 1
        if error:
            avg_error = average(error)
            wgh_error = avg_error / num_events
            min_error = min(error)
            scores.append({'name': s.name, 'avg_error': avg_error,
                           'wgh_error': wgh_error, 'min_error': min_error,
                           'num_events': num_events})
    lijst = sorted(scores, key=operator.itemgetter('avg_error'))
    print_results(lijst, 'avg_error')

    lijst = sorted(scores, key=operator.itemgetter('min_error'))
    print_results(lijst, 'min_error')

    lijst = sorted(scores, key=operator.itemgetter('wgh_error'))
    print_results(lijst, 'wgh_error')

    lijst = sorted(scores, key=operator.itemgetter('num_events'))
    lijst.reverse()
    print_results(lijst, 'num_events')

    return scores

def print_results(lijst, key):
    print
    print 'Results sorted on', key
    print 70*'-'
    for i in range(10):
        print i+1, lijst[i]['name'], lijst[i][key]
    print '...'
    print len(lijst), lijst[-1]['name'], lijst[-1][key]
    print

def show_energies():
    energies = []
    for ac in AnalyzedCoincidence.objects.filter(
                error_estimate__isnull=False):
        energies.append(ac.log_energy)
    print 'Totaal aantal showers:', len(energies)
    hist(energies, bins=arange(14, 22, .5))
    
    energies = []
    for ac in AnalyzedCoincidence.objects.filter(
                error_estimate__isnull=False, error_estimate__lte=100.):
        energies.append(ac.log_energy)
    print 'Totaal aantal showers:', len(energies)
    hist(energies, bins=arange(14, 22, .5))

    xlabel('log(energie)')
    ylabel('aantal coincidenties')

#ver_weg_punt()
scores = top_lijst()
#show_energies()
