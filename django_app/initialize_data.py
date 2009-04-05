from symposium2009.models import *
for c in Coincidence.objects.filter(nevents__gte=3):
    ac = AnalyzedCoincidence(coincidence=c)
    ac.save()

s = Student(name='TestStudent')
s.save()

ac = AnalyzedCoincidence.objects.all()[0]
ac.student = s
ac.save()
