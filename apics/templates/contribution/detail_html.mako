<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${ctx.name}</h2>
${h.coins(request, ctx)}

<%def name="sidebar()">
    ${util.language_meta()}
</%def>

<%def name="sl_valuetable()">
    <%util:table items="${[_v for _v in ctx.valuesets if _v.parameter.feature_type == 'sociolinguistic' and _v.values]}" args="item" eid="dt-sl" class_="table-striped">
        <%def name="head()">
            <th>Parameter</th>
            <th>Value</th>
        </%def>
        <td>${h.link(request, item.parameter)}</td>
        <td>${'; '.join(v.domainelement.name for v in item.values)}</td>
    </%util:table>
</%def>

<%def name="sm_valuetable()">
    <%util:table items="${[_v for _v in ctx.valuesets if _v.parameter.feature_type == 'segment' and _v.values]}" args="item" eid="dt-sm" class_="table-striped">
        <%def name="head()">
            <th>Parameter</th>
            <th>Value</th>
            <th>Example</th>
            <th>Category</th>
        </%def>
        <td>${h.link(request, item.parameter)}</td>
        <td>${'; '.join(v.domainelement.name for v in item.values)}</td>
        <td>
        % if item.values and item.values[0].sentence_assocs:
            ${item.values[0].sentence_assocs[0].sentence.name}
            (${item.values[0].sentence_assocs[0].sentence.description})
        % endif
        </td>
        <td>
        % if item.parameter.jsondata['vowel']:
            vowel
        % elif item.parameter.jsondata['obstruent']:
            obstruent consonant
        % else:
            sonorant consonant
        % endif
        </td>
    </%util:table>
</%def>

<% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, language=ctx.language) %>
<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Primary features</a></li>
        <li><a href="#tab2" data-toggle="tab">Sociolinguistic features</a></li>
        <li><a href="#segments" data-toggle="tab">Segments</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${dt.render()}
        </div>
        <div id="tab2" class="tab-pane">
            ${sl_valuetable()}
        </div>
        <div id="segments" class="tab-pane">
            <% segments = u.segments(ctx) %>
            <h4>Consonants</h4>
            ${u.ipa_consonants(segments)}
            <h4>Vowels</h4>
            ${u.ipa_vowels(segments)}
            <h4>Special segments</h4>
            ${u.ipa_custom(segments)}
            ${sm_valuetable()}
        </div>
    </div>
    <script>
$(document).ready(function() {
    if (location.hash !== '') {
        $('a[href="#' + location.hash.substr(2) + '"]').tab('show');
    }
    return $('a[data-toggle="tab"]').on('shown', function(e) {
        return location.hash = 't' + $(e.target).attr('href').substr(1);
    });
});
    </script>
</div>


<%def name="sidebar()">
    <%util:well title="Author">
        ${h.linked_contributors(request, ctx)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.name, request.resource_url(ctx, ext='md.html')))}
    </%util:well>
    <%util:well>
        ${request.map.render()}
    </%util:well>
    <%util:well title="Sources">
    <dl>
        % for source in sorted(list(ctx.language.sources), key=lambda s: s.name):
        <dt style="clear: right;">${h.link(request, source)}</dt>
        <dd id="${h.format_gbs_identifier(source)}">${source.description}</dd>
        % endfor
    </dl>
    ${util.gbs_links(filter(None, [s.gbs_identifier for s in ctx.language.sources]))}
    </%util:well>
</%def>
