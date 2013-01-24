function HideTickLabels(v, axis) {
    return " ";}

var base_options = {
    colors: ["#222", "#D22", "#1C2", "#1CC"],
    series: {
        lines: {
            lineWidth: 1,
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

var _eh_options = {
    series: {
        lines: {
            lineWidth: 1.5}},
    yaxis: {
        axisLabel: 'Number of events',
        min: 0},
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        min: 0,
        max: 24}
};

var _ph_options = {
    yaxis: {
        axisLabel: 'Count',
        min: 0.7,
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
        transform: function (N) {return Math.log(N);},
        inverseTransform: function (N) {return Math.exp(N);}},
    xaxis: {
        axisLabel: 'Pulseheight (mV)'}
};

var _pi_options = {
    yaxis: {
        axisLabel: 'Count',
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000],
        min: 0.7,
        transform: function (N) {return Math.log(N);},
        inverseTransform: function (N) {return Math.exp(N);}},
    xaxis: {
        axisLabel: 'Pulseintegral (mVns)'}
};

var _td_options = {
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

var _bd_options = {
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

var _vg_options = {
    xaxis: {
        axisLabel: 'Date',
        mode: "time",
        timeformat: "%m/%Y"},
    yaxis: {
        axisLabel: 'PMT Voltage (V)',
        min: 300}
    }

var _cg_options = {
    xaxis: {
        axisLabel: 'Date',
        mode: "time",
        timeformat: "%m/%Y"},
    yaxis: {
        axisLabel: 'PMT Current (mV)',
        min: 0}
    }

var eh_options = $.extend(true, {}, base_options, _eh_options);
var ph_options = $.extend(true, {}, base_options, _ph_options);
var pi_options = $.extend(true, {}, base_options, _pi_options);
var td_options = $.extend(true, {}, base_options, _td_options);
var bd_options = $.extend(true, {}, base_options, _bd_options);
var vg_options = $.extend(true, {}, base_options, _vg_options);
var cg_options = $.extend(true, {}, base_options, _cg_options);
