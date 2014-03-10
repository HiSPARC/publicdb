function HideTickLabels(v, axis) {
    return " ";}

var _base = {
    colors: ["#222", "#D22", "#1C2", "#1CC"],
    series: {
        lines: {
            lineWidth: 1.5,
            steps: true},
        shadowSize: 0},
    yaxis: {
        show: true,
        position: "left",
        color: "#000",
        tickColor: "#000",
        font: {
            size: 12},
        tickLength: 4,
        tickDecimals: 0,
        labelWidth: 33,
        axisLabelUseCanvas: true,
        axisLabelFontSizePixels: 16},
    xaxis: {
        show: true,
        position: "bottom",
        color: "#000",
        tickColor: "#000",
        font: {
            size: 12},
        tickLength: 4,
        tickDecimals: 0,
        labelHeight: 23,
        axisLabelUseCanvas: true,
        axisLabelFontSizePixels: 16},
    y2axis: {
        show: true,
        position: "right",
        tickLength: 2,
        alignTicksWithAxis: 1,
        axisLabel: '',
        labelWidth: 11,
        tickFormatter: HideTickLabels},
    x2axis: {
        show: true,
        position: "top",
        tickLength: 2,
        alignTicksWithAxis: 1,
        axisLabel: '',
        labelHeight: 0,
        tickFormatter: HideTickLabels},
    grid: {
        show: true,
        aboveData: 0,
        color: "#000",
        backgroundColor: "rgba(255, 255, 255, 0)",
        labelMargin: 7,
        axisMargin: 0,
        borderWidth: 0,
        minBorderMargin: 0,
        clickable: false,
        hoverable: false,
        autoHighlight: false},
    legend: {show: false}
};

var _coincidencetimehistogram = {
    yaxis: {
        axisLabel: 'Number of coincidences',
        min: 0},
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        min: 0,
        max: 24}
};

var _coincidencenumberhistogram = {
    yaxis: {
        axisLabel: 'Number of coincidences',
        min: 0.7,
        ticks: [0.1, 1, 10, 100, 1000, 10000, 100000],
        transform: function (N) {return Math.log(N);},
        inverseTransform: function (N) {return Math.exp(N);}},
    xaxis: {
        axisLabel: 'Number of stations in coincidence',
        ticks: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        min: 2,
        max: 20}
};

var _eventhistogram = {
    yaxis: {
        axisLabel: 'Number of events',
        min: 0},
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        min: 0,
        max: 24}
};

var _pulseheighthistogram = {
    yaxis: {
        axisLabel: 'Count',
        min: 0.7,
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
        transform: function (N) {return Math.log(N) / Math.LN10;},
        inverseTransform: function (N) {return Math.pow(10, N);}},
    xaxis: {
        axisLabel: 'Pulseheight (mV)'}
};

var _pulseintegralhistogram = {
    yaxis: {
        axisLabel: 'Count',
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
        min: 0.7,
        transform: function (N) {return Math.log(N) / Math.log(10);},
        inverseTransform: function (N) {return Math.pow(10, N);}},
    xaxis: {
        axisLabel: 'Pulseintegral (mVns)'}
};

var _temperaturedata = {
    series: {
        lines: {
            show: false},
        points: {
            show: true,
            radius: .75,
            lineWidth: 0.00001,
            fill: true,
            fillColor: "#222"}},
    yaxis: {
        axisLabel: 'Temperature (°C)'},
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        min: 0,
        max: 24}
};

var _barometerdata = {
    series: {
        lines: {
            show: false},
        points: {
            show: true,
            radius: .75,
            lineWidth: 0.00001,
            fill: true,
            fillColor: "#222"}},
    yaxis: {
        axisLabel: 'Air pressure (hPa)'},
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        min: 0,
        max: 24}
};

var _voltagegraph = {
    xaxis: {
        axisLabel: 'Date',
        mode: "time",
        timeformat: "%m/%Y"},
    yaxis: {
        axisLabel: 'PMT Voltage (V)',
        min: 300}
};

var _currentgraph = {
    xaxis: {
        axisLabel: 'Date',
        mode: "time",
        timeformat: "%m/%Y"},
    yaxis: {
        axisLabel: 'PMT Current (mV)',
        min: 0}
};

var _altitudegraph = {
    xaxis: {
        axisLabel: 'Date',
        mode: "time",
        timeformat: "%m/%Y"},
    yaxis: {
        axisLabel: 'Altitude (m)',
        min: 0}
};

var _tracegraph = {
    series: {
        lines: {
            steps: false}},
    xaxis: {
        axisLabel: 'Time (ns)',
        max: 200},
    yaxis: {
        axisLabel: 'Signal (mV)',
        min: -1500,
        max: 0}
};

var ct_options = $.extend(true, {}, _base, _coincidencetimehistogram);
var cn_options = $.extend(true, {}, _base, _coincidencenumberhistogram);
var eh_options = $.extend(true, {}, _base, _eventhistogram);
var ph_options = $.extend(true, {}, _base, _pulseheighthistogram);
var pi_options = $.extend(true, {}, _base, _pulseintegralhistogram);
var td_options = $.extend(true, {}, _base, _temperaturedata);
var bd_options = $.extend(true, {}, _base, _barometerdata);
var vg_options = $.extend(true, {}, _base, _voltagegraph);
var cg_options = $.extend(true, {}, _base, _currentgraph);
var ag_options = $.extend(true, {}, _base, _altitudegraph);
var tr_options = $.extend(true, {}, _base, _tracegraph);
