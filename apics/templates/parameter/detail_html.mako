<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>

<ul class="nav nav-pills pull-right">
    <li><a href="#map-container">Map</a></li>
    <li><a href="#list-container">List</a></li>
</ul>

<h2>${ctx.name}</h2>

<div class="row-fluid">
    <div class="span4">
        <%util:well title="Values">
            ${u.value_table(ctx, request)}
        </%util:well>
    </div>
    <div class="span8">
        <%util:well title="Description">
            TODO
        </%util:well>
    </div>
</div>

${request.map.render()}

<div id="list-container">
    <% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, parameter=ctx) %>
    ${dt.render()}
</div>
