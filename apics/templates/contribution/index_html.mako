<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<ul class="nav nav-pills pull-right">
    <li><a href="#map-container">Map</a></li>
    <li><a href="#list-container">List</a></li>
</ul>

<h2>${_('Contributions')}</h2>

${request.map.render()}

<div id="list-container">
    ${ctx.render()}
</div>
