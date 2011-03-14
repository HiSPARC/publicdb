import tables
import operator
import progressbar as pb


if __name__ == '__main__':
    try:
        data
    except NameError:
        data = tables.openFile('data.h5', 'a')

    group = data.root.s502
    events = group.events

    ts = [x for x in enumerate(events[:]['ext_timestamp'])]
    ts.sort(key=operator.itemgetter(1))

    prev = 0
    clist = []
    for i, t in ts:
        if t != prev:
            clist.append(i)
        prev = t

    clist.sort()
    print "Removing %d rows" % (len(events) - len(clist))

    if clist:
        tmptable = data.createTable(group, 't__events',
                                    description=events.description)
        rows = events.readCoordinates(clist)
        tmptable.append(rows)
        tmptable.flush()

        data.renameNode(tmptable, events._v_name, overwrite=True)
