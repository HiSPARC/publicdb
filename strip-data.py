import calendar
import time
import gzip

if __name__ == '__main__':
    t0 = calendar.timegm(time.strptime('Jul 1, 2008', '%b %d, %Y'))
    t1 = calendar.timegm(time.strptime('Nov 1, 2008', '%b %d, %Y'))

    g = gzip.open('HiSparc.dat.gz')
    f = gzip.open('kascade.dat.gz', 'w')

    while True:
        # read a line from the subprocess stdout buffer
        line = g.readline()
        if not line:
            # no more lines left, EOF
            break

        # break up the line into an array of floats
        data = line.split(' ')
        data = [float(x) for x in data]

        # read all columns into KASCADE-named variables
        Irun, Ieve, Gt, Mmn, EnergyArray, Xc, Yc, Ze, Az, Size, Nmu, He0, \
        Hmu0, He1, Hmu1, He2, Hmu2, He3, Hmu3, P200, T200 = data

        if Gt < t0:
            # Ignore event
            continue
        elif Gt > t1:
            # We've got everything
            break
        else:
            f.write(line)
