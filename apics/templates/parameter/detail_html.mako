<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${ctx.id} ${ctx.__unicode__()}</%block>

<ul class="nav nav-pills pull-right">
    <li><a href="#map-container">Map</a></li>
    <li><a href="#list-container">List</a></li>
</ul>

<h2>${title()}</h2>

<div class="row-fluid">
    % if ctx.description:
    <div class="span8">
        <h3>Description</h3>
        ${h.text2html(ctx.markup_description or ctx.description, mode='p', sep='\n')}
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

${request.map.render()}

##<div id="list-container">
    ##${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
    ##${request.get_datatable('sentences', h.models.Sentence, parameter=ctx).render()}
##</div>

<div class="tabbable" id="list-container">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Values</a></li>
        <li><a href="#tab2" data-toggle="tab">Examples</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
        </div>
        <div id="tab2" class="tab-pane">
            ${request.get_datatable('sentences', h.models.Sentence, parameter=ctx).render()}
        </div>
    </div>
</div>
