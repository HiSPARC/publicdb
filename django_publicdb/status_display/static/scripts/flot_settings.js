var base_options = {
    colors: ["#222", "#D22", "#1C2", "#1CC",],
    series: {
        lines: {
            lineWidth: 1,
            steps: true,
        },
        shadowSize: 0,
    },
    yaxis: {
        tickLength: 4,
        tickColor: "#000",
        labelWidth: 45,
        font: {
            size: 12,
        },
    },
    xaxis: {
        tickLength: 4,
        tickColor: "#000",
        labelHeight: 20,
        font: {
            size: 12,
        },
    },
    
    grid: {
        show: true,
        aboveData: 0,
        color: "#000",
        backgroundColor: "#FFF",
        labelMargin: 4,
        axisMargin: 0,
        borderWidth: 1,
        borderColor: "#000",
        minBorderMargin: 1,
        clickable: false,
        hoverable: false,
        autoHighlight: false,
    },
    legend: {show: false,},
};

var _eh_options = {
    yaxis: {
        axisLabel: 'Number of events',
        min: 0,
    },
    y2axis: {
        alignTicksWithAxis: 1,
        axisLabel: '',
        position: "right",
        labelWidth: 0,
    },
    xaxis: {
        axisLabel : 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        max: 24,
    },
    x2axis: {
        alignTicksWithAxis: 1,
        axisLabel: '',
        position: "top",
        labelHeight: 0,
    },
};

var _ph_options = {
    yaxis: {
        axisLabel: 'Count',
        min: 1,
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000],
        tickLength: 4,
        tickColor: "#000",
        transform: function (N) { return Math.log(N); },
        inverseTransform: function (N) { return Math.exp(N); },
    },
    xaxis: {
        axisLabel: 'Pulseheight (mV)',
    },
};

var _pi_options = {
    yaxis: {
        axisLabel: 'Count',
        min: 1,
        ticks: [1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000],
        tickLength: 4,
        tickColor: "#000",
        transform: function (N) { return Math.log(N); },
        inverseTransform: function (N) { return Math.exp(N); },
    },
    xaxis: {
        axisLabel: 'Pulseintegral (mVns)',
    },
};

var _td_options = {
    yaxis: {
        axisLabel: 'Temperature (°C)',
    },
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        max: 24,
    },
};

var _bd_options = {
    series: {
        lines: {
            show: false,
        },
        points: {
            show: true,
            radius: 0,
        },
    },
    yaxis: {
        axisLabel: 'Air pressure (hPa)',
    },
    xaxis: {
        axisLabel: 'Hour of day (UTC)',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        max: 24,
    },
};

var eh_options = {};
var ph_options = {};
var pi_options = {};
var td_options = {};
var bd_options = {};
$.extend(true, eh_options, base_options, _eh_options);
$.extend(true, ph_options, base_options, _ph_options);
$.extend(true, pi_options, base_options, _pi_options);
$.extend(true, td_options, base_options, _td_options);
$.extend(true, bd_options, base_options, _bd_options);
