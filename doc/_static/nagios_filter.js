/**
 * Hide every div with class 'section', except the one containing the given
 * Nagios tag and its ancestors. Currently a 4-level deep div is supported.
 * Add link to show all
 */
$(document).ready(function() {
    var tag = getNagiosQuery()
    if (tag.length) {
        var topics = $('strong:contains("' + tag + '")');
        var topic_divs = topics.closest('div')
        if (topics.length) {
            $('div.section').hide();
            topic_divs.parent().parent().parent().closest('div').show();
            topic_divs.parent().parent().closest('div').show();
            topic_divs.parent().closest('div').show();
            topic_divs.show();
            $('<p class="filter-nagios"><a href="#" onclick="showAllIssues();' +
              'return false;">Show All Issues</a></p>').appendTo($('#searchbox'));}}
});

function showAllIssues() {
    $('#searchbox .filter-nagios').fadeOut();
    $('div.section').fadeIn();
}

function getNagiosQuery() {
    var params = $.getQueryParameters();
    var terms = (params.nagios) ? params.nagios[0] : [];
    return terms;
}

/**
 * This function returns the parsed url parameters of the
 * current request. Multiple values per key are supported,
 * it will always return arrays of strings for the value parts.
 */
$.getQueryParameters = function(s) {
    if (typeof s == 'undefined')
        s = document.location.search;
    var parts = s.substr(s.indexOf('?') + 1).split('&');
    var result = {};
    for (var i = 0; i < parts.length; i++) {
        var tmp = parts[i].split('=', 2);
        var key = jQuery.urldecode(tmp[0]);
        var value = jQuery.urldecode(tmp[1]);
        if (key in result)
          result[key].push(value);
        else
          result[key] = [value];
    }
    return result;
};

/**
 * Make the jQuery selector ':contains' case-insensitive (jQuery 1.8+)
 */
// $.expr[":"].contains = $.expr.createPseudo(function(arg) {
//     return function(elem) {
//         return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
//     };
// });

/**
 * Make the jQuery selector ':contains' case-insensitive (jQuery <1.8)
 */
jQuery.expr[':'].contains = function(a, i, m) {
    return jQuery(a).text().toLowerCase().replace(/\s[a-z]:/g,'').replace(/\s/g,'').replace(/[^a-z0-9\-]/g,'')
        .indexOf(m[3].toLowerCase().replace(/\s[a-z]:/g,'').replace(/\s/g,'').replace(/[^a-z0-9\-]/g,'')) >= 0;
};
