var en_options = {
    colors: ["#222", "#D22", "#1C2", "#1CC"],
    series: {
        lines: {
            lineWidth: 1,
            steps: true
        },
        shadowSize: 0
    },
    yaxis: {
        tickLength: 4,
        tickColor: "#000",
        labelWidth: 45,
        font: {
            size: 12
        },
        axisLabel: 'Number of events',
        min: 0
    },
    xaxis: {
        tickLength: 4,
        tickColor: "#000",
        labelHeight: 20,
        font: {
            size: 12
        },
        axisLabel: 'Energy',
        ticks: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
        max: 24

    },
    y2axis: {
        alignTicksWithAxis: 1,
        axisLabel: '',
        position: "right",
        labelWidth: 0
    },
    x2axis: {
        alignTicksWithAxis: 1,
        axisLabel: '',
        position: "top",
        labelHeight: 0
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
        autoHighlight: false
    },
    legend: {show: false}
};
