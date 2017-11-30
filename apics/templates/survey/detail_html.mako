<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "surveys" %>
<%! from itertools import groupby %>
<%! from clldutils.misc import slug %>

<%block name="title">Survey chapter: ${ctx.name}</%block>
<%block name="head">
    <style>
        body p {
            line-height: 150%
        }
            ${css}
    </style>
</%block>


<%def name="sidebar()">
    <%util:well title="Author">
        ${h.linked_contributors(request, ctx)}
        ${h.cite_button(request, ctx)}
    </%util:well>
    % for lang in ctx.languages:
        <%util:well title="${lang.name}">
            ${h.format_coordinates(lang)}
            <% data = [('Glottolog', h.external_link('http://glottolog.org/resource/languoid/id/'+lang.glottocode, lang.glottocode))] if lang.glottocode else [] %>
            <% data.extend((d.key, d.value) for d in lang.data) %>
            ${util.dl_table(*data)}
            % if lang.contribution.glossed_text.pdf:
                <button type="button" class="close" data-dismiss="alert">&times;</button>
                % if lang.contribution.glossed_text.pdf:
                    <div>${u.cdstar.link(lang.contribution.glossed_text.pdf, label='Glossed text')}</div>
                % endif
                % if lang.contribution.glossed_text.audio:
                    <div>${u.cdstar.audio(lang.contribution.glossed_text.audio, label='Glossed text')}</div>
                % endif
            % endif
        </%util:well>
    % endfor
    <%util:well>
        <div style="text-align: center">
            % for data in maps:
                <img style="margin-bottom: 10px; border: 1px solid black" src="${data}">
            % endfor
        </div>
    </%util:well>
    % if md.get('refs'):
        <%util:well title="References">
            <dl>
                % for cat, items in groupby(md.get('refs', []), key=lambda t: t['category']):
                    <dt><strong>${cat or ''}</strong></dt>
                    <dd>
                        <ul class="unstyled">
                            % for item in items:
                                <li id="ref-${item['id']}">${item['html']|n}</li>
                            % endfor
                        </ul>
                    </dd>
                % endfor
            </dl>
        </%util:well>
    % endif
</%def>

<h2>${title()}</h2>

<div class="alert alert-info">
    Structure data for these languages can be found in
    % for lang in ctx.languages:
        % if not loop.first:
            and
        % endif
        ${h.link(request, lang.contribution, label='structure dataset {0}'.format(lang.contribution.id))}.
    % endfor
</div>

<blockquote>
    <ul class="unstyled">
        % for label, fragment in md['outline']:
            <li><a href="#${fragment}">${label|n}</a></li>
        % endfor
    </ul>
</blockquote>


${html|n}
<p>&nbsp;</p>
<script>
    $(document).ready(function () {
        $('.popover-note').clickover({'html': true, 'content': $(this).data('content')});
        $('.ref-link').clickover({
            html: true,
            content: function () {
                var content = $(this).data('content');
                var $content = $('#ref-' + content);
                return $content.length > 0 ? $content.html() : '';
            }
        });
    });
</script>
