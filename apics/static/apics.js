CLLD.Map.style_maps["apics_feature"] = new OpenLayers.StyleMap({
    "default": {
        externalGraphic: "${icon}",
        graphicWidth: 30,  // use this to scale the icons! ${size} or somesuch
        graphicHeight: 30
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
