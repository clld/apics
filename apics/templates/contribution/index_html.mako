<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<ul class="nav nav-pills pull-right">
    <li><a href="#map-container">Map</a></li>
    <li><a href="#list-container">List</a></li>
</ul>

<h2>${_('Contributions')}</h2>

${request.get_map('contributions', col='lexifier', dt=ctx).render()}

<div id="list-container">
    ${ctx.render()}
</div>
