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
            size: 18},
        tickLength: 4,
        tickDecimals: 0,
        labelWidth: 55,
        axisLabelUseCanvas: true,
        axisLabelFontSizePixels: 22},
    xaxis: {
        show: true,
        position: "bottom",
        color: "#000",
        tickColor: "#000",
        font: {
            size: 18},
        tickLength: 4,
        tickDecimals: 0,
        labelHeight: 40,
        axisLabelUseCanvas: true,
        axisLabelFontSizePixels: 22},
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
        aboveData: false,
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

var _tracegraph_options = {
    series: {
        lines: {
            lineWidth: 3,
            steps: false}},
    xaxis: {
        axisLabel: 'Time (ns)'},
    yaxis: {
        axisLabel: 'Signal (ADC)',
        max: 20},
    grid: {
        markings: [{yaxis: {from: -53, to: -53},
                    color: "#ddd",
                    lineWidth: .5},
                   {yaxis: {from: -123, to: -123},
                    color: "#ddd",
                    lineWidth: .5},
                   {yaxis: {from: -210, to: -210},
                    color: "#ccc",
                    lineWidth: 1}]}
};

var tr_options = $.extend(true, {}, base_options, _tracegraph_options);
