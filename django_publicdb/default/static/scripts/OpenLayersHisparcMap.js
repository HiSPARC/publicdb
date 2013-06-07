function createMap(name) {
    var options = {
        fractionalZoom: true,
        controls: [
            new OpenLayers.Control.Navigation(
                {dragPanOptions: {enableKinetic: true}}),
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.ScaleLine()]};

    var map = new OpenLayers.Map(name, options);

    var mapLayer = new OpenLayers.Layer.OSM(null, null,
        {serverResolutions: [156543.03390625, 78271.516953125,
                             39135.7584765625, 19567.87923828125,
                             9783.939619140625, 4891.9698095703125,
                             2445.9849047851562, 1222.9924523925781,
                             611.4962261962891, 305.74811309814453,
                             152.87405654907226, 76.43702827453613,
                             38.218514137268066, 19.109257068634033,
                             9.554628534317017, 4.777314267158508,
                             2.388657133579254, 1.194328566789627,
                             0.5971642833948135],
         transitionEffect: 'resize'});

    map.addLayer(mapLayer);

    return map;
}

function createStyle(map) {
    var context = {
        getColor: function(feature) {
            var colors = {
                "down": 'red',
                "problem": 'gold',
                "up": 'green',
                "unknown": 'blue',
                "gpsold": '#B85C32',
                "gpsnew": '#2A7AE2'};
            return colors[feature.attributes["status"]];},
        getLabel: function(feature) {
            if (map.getZoom() >= 14) {
                return feature.attributes["id"];}
            else {
                return ''}},
        getSize: function(feature) {
            return .5 * map.getZoom();}};
    var pointStyle = {
        fillColor: "${getColor}", // using context.getColor(feature)
        fillOpacity: 0.8,
        strokeColor: 'black',
        strokeOpacity: 0.75,
        strokeWidth: 1,
        pointRadius: "${getSize}", // using context.getSize(feature)
        cursor: 'pointer',
        label: '${getLabel}', // using context.getLabel(feature)
        labelYOffset: 16,
        fontSize: 12,
        fontFamily: 'sans-serif',
        fontWeight: 'bold'};
    var style = new OpenLayers.Style(pointStyle, {context: context});

    return style;
}
