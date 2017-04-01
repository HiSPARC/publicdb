function HideTickLabels(v, axis) {
    return " ";}

var en_options = {
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
        axisLabel: 'Count',
        min: 0,
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
        axisLabel: 'Energy (in log(eV))',
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

