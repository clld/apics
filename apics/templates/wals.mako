<%inherit file="${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="util.mako"/>
<%! active_menu_item = "apics_wals" %>
<%block name="title">APiCS - WALS: ${ctx}</%block>

<h2>${title()}</h2>

<div class="row-fluid">
<div class="span6">
    <h4>WALS map: ${h.external_link('http://wals.info/feature/' + str(ctx.wals_id) + 'A', label=wals_data['name'])}</h4>
    <p>
        by ${wals_data['contributors']}
    </p>
</div>
<div class="span6">
    <h4>WALS-like APiCS map: ${h.link(request, ctx)}</h4>
</div>
</div>

<div class="row-fluid">
<div class="span6">
    ${wals_map.render()}
</div>
<div class="span6">
    ${apics_map.render()}
</div>
</div>
