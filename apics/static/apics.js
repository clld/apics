APICS = {};

CLLD.Map.style_maps["apics_feature"] = new OpenLayers.StyleMap({
    "default": {
        externalGraphic: "${icon}",
        graphicWidth: 30,  // use this to scale the icons! ${size} or somesuch
        graphicHeight: 30,
        graphicZIndex: 200
    },
    "temporary": {
        label : "${name}",
        fontColor: "black",
        fontSize: "12px",
        fontFamily: "Courier New, monospace",
        fontWeight: "bold",
        labelAlign: "cm",
        labelOutlineColor: "white",
        labelOutlineWidth: 3
    }
});


APICS.make_style_map = function (name) {
    var styles = new OpenLayers.StyleMap({
        "default": {
            pointRadius: 5,
            strokeColor: "black",
            strokeWidth: 1,
            strokeOpacity: 0.6,
            fillColor: "${icon_color}",
            fillOpacity: 0.4,
            graphicXOffset: 50,
            graphicYOffset: 50,
            graphicZIndex: 20
        },
        "temporary": {
            pointRadius: 8,
            label : "${name}",
            fontColor: "black",
            fontSize: "12px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelAlign: "cm",
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        }
    }),
        wals_icons = {
      "s": {graphicName: "square"}, // square
      "d": {graphicName: "square", rotation: 45}, // diamond
      "t": {graphicName: "triangle"},
      "f": {graphicName: "triangle", rotation: 180},
      "c": {graphicName: "circle"}
    };
    styles.addUniqueValueRules("default", "icon_type", wals_icons);
    styles.addUniqueValueRules("select", "icon_type", wals_icons);
    return styles;
}

CLLD.Map.style_maps["wals_feature"] = APICS.make_style_map("wals_feature");
