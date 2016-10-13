
function createMap(name) {
    var map = L.map(name, {
        center: L.latLng(52.3559, 4.951),
        zoom: 5,
        zoomSnap: 0.2,
        zoomDelta: 0.4
    });

    var tile_url = 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png';
    if (L.retina) {
        tile_url = 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png';
    }

    L.tileLayer(tile_url, {
        attribution: '<a href="http://data.hisparc.nl/" title="HiSPARC data">HiSPARC</a><br>' +
                     '<a href="http://openstreetmap.org/copyright" title="© OpenStreetMap contributors">OSM</a> | ' +
                     '<a href="https://carto.com/attributions" title="© CARTO Positron">CARTO</a>'
    }).addTo(map);
    L.control.scale({imperial: false}).addTo(map);

    map.on('zoomend', function(e) {
        var currentZoom = map.getZoom(),
            markerRadius = 0.8 * Math.pow(currentZoom, 0.88);
        map.eachLayer(function(layer) {
            if ('setStyle' in layer) {
                layer.setStyle({radius: markerRadius})
            }
        });
    });

    return map;
}

var statusColors = {
    down: 'red',
    problem: 'gold',
    up: 'green',
    unknown: 'grey',
    gpsold: '#EE9911',
    gpsnew: '#2A7AE2'
};

var pointStyle = {
    radius: 7,
    weight: 1.5,
    fillOpacity: 0.6
};

var boundsPadding = [15, 15];
