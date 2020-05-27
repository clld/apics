<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">Structure dataset ${ctx.id}: ${ctx.name}</%block>

<%block name="head">
    <style>
table caption {text-align: left;}
figure {display: table; margin-left: 0px;}
figcaption {display: table-caption; caption-side: top; font-size: 120%;}

${vowels_css}
${consonants_css}
${consonants_css.replace('pulmonic-consonants', 'special-segments')}
table caption {display: none !important;}
figure figcaption {display: none !important;}
    </style>
</%block>

<div style="float: right; margin-top: 10px;">
${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}
</div>

<h2>${title()}</h2>
${h.coins(request, ctx)}

% if ctx.language.survey:
<div class="alert alert-info">
    This language is described more fully in ${h.link(request, ctx.language.survey, label='survey chapter {0}'.format(ctx.language.survey.id))}.
</div>
% endif

${h.text2html(ctx.markup_description or ctx.description, mode='p', sep='\n')}

% if ctx.glossed_text.pdf:
<div class="alert alert-info">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    % if ctx.glossed_text.pdf:
        <div>${u.cdstar.link(ctx.glossed_text.pdf, label='Glossed text')}</div>
    % endif
    ##<strong>
    ##    <a href="${u.cdstar.bitstream_url(ctx.glossed_text.pdf)}" class="pdf">Glossed text</a>
    ##</strong>
    % if ctx.glossed_text.audio:
        <div>${u.cdstar.audio(ctx.glossed_text.audio, label='Glossed text')}</div>
    % endif
</div>
% endif

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#primary" data-toggle="tab">Primary features</a></li>
        <li><a href="#segments" data-toggle="tab">Segments</a></li>
        <li><a href="#ipa" data-toggle="tab">IPA chart</a></li>
        <li><a href="#sociolinguistic" data-toggle="tab">Sociolinguistic features</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="primary" class="tab-pane active">
            ${request.get_datatable('values', h.models.Value, language=ctx.language, ftype='primary').render()}
        </div>
        <div id="segments" class="tab-pane">
            ${request.get_datatable('values', h.models.Value, language=ctx.language, ftype='segment').render()}
        </div>
        <div id="ipa" class="tab-pane">

            <h4>Consonants</h4>
            ${consonants_html.replace('&lt;sup&gt;', '<sup>').replace('&lt;/sup&gt;', '</sup>')|n}

            <h4 style="margin-top: 2em;">Vowels</h4>
            ${vowels_html|n}

            <h4 style="margin-top: 2em;">Special segments</h4>
            <table class="table table-condensed table-nonfluid" id="special-segments">
                <caption>Other segments</caption>
                <tbody>
                    % for seg in uncovered:
                        <tr>
                            <td><a class="${seg.css_class}" href="${seg.href}">&nbsp;${seg.label|n}&nbsp;</a></td>
                            <td>${seg.title}</td>
                        </tr>
                    % endfor
                </tbody>
            </table>
            <h4 style="margin-top: 2em;">Legend</h4>
            ${u.legend(request)}
        </div>
        <div id="sociolinguistic" class="tab-pane">
            ${request.get_datatable('values', h.models.Value, language=ctx.language, ftype='sociolinguistic').render()}
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
        ${h.format_coordinates(ctx.language)}
        ${request.map.render()}
        <% data = [('Glottolog', h.external_link('http://glottolog.org/resource/languoid/id/'+ctx.language.glottocode, ctx.language.glottocode))] if ctx.language.glottocode else [] %>
        <% data.extend((d.key, d.value) for d in ctx.language.data) %>
        ${util.dl_table(*data)}
    </%util:well>
    <%util:well title="Survey chapter">
        ${h.link(request, ctx.survey_reference)}
        ##<p>${ctx.survey_reference.bibtex().text()}</p>
    </%util:well>
    <%util:well title="Sources">
        ${util.sources_list(sorted(list(ctx.language.sources), key=lambda s: s.name))}
    </%util:well>
</%def>
