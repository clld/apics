<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<% values_dt = request.get_datatable('values', h.models.Value, parameter=ctx) %>

<%block name="title">${ctx.id} ${ctx.__unicode__()}</%block>

<ul style="margin-top: 10px;" class="nav nav-pills pull-right">
    <li style="margin-right: 10px;">${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}</li>
    <li class="active"><a href="#map-container">${h.icon('globe', style='vertical-align: bottom')}&nbsp;Map</a></li>
    <li class="active"><a href="#list-container">${h.icon('list', style='vertical-align: bottom')}&nbsp;List</a></li>
    <li class="active"><a href="${req.route_url('parameter_alt', id=ctx.id, ext='chapter.html')}">${h.icon('book', style='vertical-align: bottom')}&nbsp;Description</a></li>
    % if ctx.phoible:
    <li>
        ${h.external_link(ctx.phoible.url, ctx.phoible.segment + ' - PHOIBLE')}
    </li>
    % endif
</ul>

<h2>${title()}</h2>

<div class="row-fluid">
    % if ctx.description:
    <div class="span8">
        <h3>Summary</h3>
        ${h.text2html(u.feature_description(request, ctx), mode='p', sep='\n')}
    </div>
    % endif
    <div class="span4">
        % if ctx.authors:
        <%util:well title="Author">
            <span>${ctx.format_authors()}</span>
            ${h.cite_button(request, ctx)}
        </%util:well>
        % endif
        <%util:well title="Values">
            ${u.value_table(ctx, request)}
        </%util:well>
    </div>
</div>

${request.get_map('parameter', col='lexifier', dt=values_dt).render()}

${util.values_and_sentences(values_dt=values_dt)}
