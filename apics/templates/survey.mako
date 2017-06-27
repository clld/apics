<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%block name="head">
    <style>
        body p {line-height: 150%}
        ${css}
    </style>
</%block>

<%! from itertools import groupby %>
<%! from clldutils.misc import slug %>
<%def name="sidebar()">
    % if authors:
        <%util:well title="Authors">
            <ul class="unstyled">
                % for a in authors:
                    <li>${h.link(request, a)}</li>
                % endfor
            </ul>
        </%util:well>
    % endif
    % if ctx:
        <%util:well>
            <div style="text-align: center">
            % for data in maps:
                <img style="margin-bottom: 10px; border: 1px solid black" src="${data}">
            % endfor
                    ${h.format_coordinates(ctx.language)}
            </div>
        </%util:well>
        <%util:well>
                ##${request.map.render()}
        <% data = [('Glottolog', h.external_link('http://glottolog.org/resource/languoid/id/'+ctx.language.glottocode, ctx.language.glottocode))] if ctx.language.glottocode else [] %>
                <% data.extend((d.key, d.value) for d in ctx.language.data) %>
                ${util.dl_table(*data)}
        </%util:well>
    % endif
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

% if ctx:
    <h2>Survey chapter: ${md['title']}</h2>
    <blockquote>
        <ul class="unstyled">
            % for label, fragment in md['outline']:
                <li><a href="#${fragment}">${label|n}</a></li>
            % endfor
        </ul>
    </blockquote>
% else:
    <h2>${md['title']}</h2>
% endif

${html|n}
<p>&nbsp;</p>
<script>
    $(document).ready(function(){
        $('.popover-note').clickover({'html': true, 'content': $(this).data('content')});
        $('.ref-link').clickover({
            html: true,
            content: function() {
                var content = $(this).data('content');
                var $content = $('#ref-' + content);
                return $content.length > 0 ? $content.html() : '';
            }
        });
    });
</script>
