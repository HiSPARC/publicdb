
function createMap(name) {
    /* Create a Leaflet map in the div with the given name
    
    A reference to the created map is returned.
    Use this to add markers and other features to the map.

    Do not forget to set the map center and zoom level,
    either directly or by using the fitBounds method.
    
    */
    var map = L.map(name, {
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

// Use these colors to style markers depending on the station status
var statusColors = {
    down: 'red',
    problem: 'gold',
    up: 'green',
    unknown: 'grey',
    gpsold: '#EE9911',
    gpsnew: '#2A7AE2'
};

// Use as default circleMarker style
var pointStyle = {
    radius: 7,
    weight: 1.5,
    fillOpacity: 0.6
};

// Use as padding when using fitBounds
var boundsPadding = [15, 15];
