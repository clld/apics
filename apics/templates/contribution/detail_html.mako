<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>

${util.data()}

<h3>${_('Value Sets')}</h3>

<%util:table items="${[v for v in ctx.valuesets if v.parameter.feature_type == 'default']}" args="item">\
    <%def name="head()">
        <th>Value Set</th><th>Parameter</th><th>Number of values</th>
    </%def>
    <td>${h.button(h.icon('icon-list'), href=request.resource_url(item), title="values")}</td>
    <td>${h.link(request, item.parameter)}</td>
    <td>${item.jsondata['_number_of_values']}</td>
</%util:table>

<%def name="sidebar()">
    <%util:well title="${_('Contributors')}">
    <dl>
        <dt>${_('Contributors')}:</dt>
        <dd>
            ${h.linked_contributors(request, ctx)}
            ${h.button('cite', onclick=h.JSModal.show(ctx.name, request.resource_url(ctx, ext='md.html')))}
        </dd>
    </dl>
    </%util:well>

    <%util:well title="${_('References')}">
    <dl>
        % for ref in ctx.references:
        <dt>${h.link(request, ref.source)}</dt>
        <dd>${ref.source.description}</dd>
        % endfor
    </dl>
    </%util:well>
</%def>
