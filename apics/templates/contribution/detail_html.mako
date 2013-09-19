<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%block name="head">
    <script src="${request.static_url('clld:web/static/audiojs/audio.min.js')}"></script>
    <script>
        audiojs.events.ready(function() {
            var as = audiojs.createAll();
        });
    </script>
</%block>

<%def name="sidebar()">
    ${util.language_meta()}
</%def>

<%def name="sl_valuetable()">
    <%util:table items="${[_v for _v in ctx.valuesets if _v.parameter.feature_type == 'sociolinguistic' and _v.values]}" args="item" eid="dt-sl" class_="table-striped">
        <%def name="head()">
            <th>Feature id</th>
            <th>Feature</th>
            <th>Value</th>
            <th>Details</th>
            <th>Source</th>
        </%def>
        <td class="right">${h.link(request, item.parameter, label=item.parameter.id)}</td>
        <td>${h.link(request, item.parameter)}</td>
        <% label = '; '.join(v.domainelement.name for v in item.values) %>
        <td>${h.link(request, item, title=item.description or label, label=label)}</td>
        <td>
            <button href="${request.resource_url(item.values[0], ext='snippet.html')}" title="show details" class="btn btn-info sdetails">more</button>
        </td>
        <td>${h.linked_references(request, item)|n}</td>
    </%util:table>
</%def>

<%def name="sm_valuetable()">
    <%util:table items="${ctx.segment_valuesets}" args="item" eid="dt-sm" class_="table-striped">
        <%def name="head()">
            <th>Feature id</th>
            <th>Segment</th>
            <th>Value</th>
            ##<th>Example</th>
            <th>Category</th>
            <th>Details</th>
        </%def>
        <td class="right">${h.link(request, item.parameter, label=item.parameter.id)}</td>
        <td>${h.link(request, item.parameter)}</td>
        <% label = '; '.join(v.domainelement.name for v in item.values) %>
        <td>${h.link(request, item, title=item.description or label, label=label)}</td>
        ##<td>
        ##% if item.values and item.values[0].sentence_assocs:
        ##    <i>${item.values[0].sentence_assocs[0].sentence.name}</i>
        ##    (${item.values[0].sentence_assocs[0].sentence.description})
        ##% endif
        ##</td>
        <td>
        % if item.parameter.jsondata['vowel']:
            vowel
        % elif item.parameter.jsondata['obstruent']:
            obstruent consonant
        % else:
            sonorant consonant
        % endif
        </td>
        <td>
            <button href="${request.resource_url(item.values[0], ext='snippet.html')}" title="show details" class="btn btn-info sdetails">more</button>
        </td>
    </%util:table>
</%def>

<h2>${ctx.name}</h2>
${h.coins(request, ctx)}
${h.text2html(ctx.description, mode='p', sep='\n')}

% if ctx.glossed_text.pdf:
<div class="alert alert-info">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>
        <a href="${request.file_url(ctx.glossed_text.pdf)}" class="pdf">Glossed text</a>
    </strong>
    % if ctx.glossed_text.audio:
    <div>
        <audio controls="controls">
            <source src="${request.file_url(ctx.glossed_text.audio)}"/>
        </audio>
    </div>
    % endif
</div>
% endif

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Primary features</a></li>
        <li><a href="#tab2" data-toggle="tab">Sociolinguistic features</a></li>
        <li><a href="#segments" data-toggle="tab">Segments</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, language=ctx.language).render()}
        </div>
        <div id="tab2" class="tab-pane">
            ${sl_valuetable()}
        </div>
        <div id="segments" class="tab-pane">
            <% segments = u.segments(ctx) %>
            <h4>Consonants</h4>
            ${u.ipa_consonants(request, segments)}
            <h4>Vowels</h4>
            ${u.ipa_vowels(request, segments)}
            <% custom = u.ipa_custom(request, segments) %>
            % if custom:
            <h4>Special segments</h4>
            ${custom}
            % endif
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
        ${h.cite_button(request, ctx)}
    </%util:well>
    <%util:well>
        ${request.map.render()}
        <table class="table table-condensed">
            <tbody>
                % for d in ctx.language.data:
                <tr><td>${d.key}</td><td>${d.value}</td></tr>
                % endfor
            </tbody>
        </table>
    </%util:well>
    <%util:well title="Survey chapter">
        ${h.link(request, ctx.survey_reference)}
        ##<p>${ctx.survey_reference.bibtex().text()}</p>
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
