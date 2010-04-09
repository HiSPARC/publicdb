import enthought.traits.api as traits
import enthought.traits.ui.api as tui
import enthought.enable.api as enable
import enthought.chaco.api as chaco
import numpy as np

import datetime
import time

from enthought.chaco.scales.api import CalendarScaleSystem
from enthought.chaco.scales_tick_generator import ScalesTickGenerator
from enthought.chaco.scales_axis import PlotAxis as ScalesPlotAxis


class MyModel(traits.HasTraits):
    data = traits.Any()
    myplot = traits.Any()

    def _data_default(self):
        t0 = time.mktime(datetime.datetime(2010, 3, 11, 0).timetuple())
        t1 = time.mktime(datetime.datetime(2010, 3, 12, 0).timetuple())
        x = np.linspace(t0, t1, 50)
        y = np.random.normal(100, 5, size=len(x))
        return chaco.ArrayPlotData(x=x, y=y)

    def _myplot_default(self):
        plot = chaco.Plot(data=self.data)
        plot.plot(('x', 'y'))


        tick_generator = ScalesTickGenerator(scale=CalendarScaleSystem())
        bottom_axis = ScalesPlotAxis(plot, orientation="bottom",
                                     tick_generator=tick_generator)
        plot.index_axis = bottom_axis

        return plot


if __name__ == '__main__':
    view = tui.View(tui.Item('myplot', editor=enable.ComponentEditor(),
                             show_label=False),
                    resizable=True)
    MyModel().configure_traits(view=view)
