APICS = {};

APICS.toggle_languages = function(eid) {
    var i, any, dt,
        ctrl = $('#dt-filter-lexifier'),
        checkboxes = {};
    $('input.lexifier').each(function(i) {checkboxes[$(this).attr('value')] = $(this).prop('checked')});

    any = checkboxes['--any--'];

    CLLD.mapFilterMarkers(eid, function(marker){
        return any || checkboxes[marker.feature.properties.language.lexifier];
    });

    for (i in checkboxes) {
        if (checkboxes[i]) {
            if (i == '--any--') {
                i = '';
            }
            ctrl.val(i);
            if (CLLD.DataTables.Values) {
                dt = CLLD.DataTables.Values;
            } else {
                dt = CLLD.DataTables.ApicsContributions;
            }
            dt.fnFilter(i, $("thead .control").index(ctrl));
        }
    }
};
