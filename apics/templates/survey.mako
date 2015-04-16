<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%! from itertools import groupby %>
<%! from clld.util import slug %>
<%def name="sidebar()">
    <%util:well title="Authors">
        <p>${md['authors']}</p>
    </%util:well>
    <%util:well>
        ${h.format_coordinates(ctx.language)}
        ##${request.map.render()}
        <% data = [('Glottolog', h.external_link('http://glottolog.org/resource/languoid/id/'+ctx.language.glottocode, ctx.language.glottocode))] if ctx.language.glottocode else [] %>
        <% data.extend((d.key, d.value) for d in ctx.language.data) %>
        ${util.dl_table(*data)}
    </%util:well>
    <%util:well title="References">
        <dl>
            % for cat, items in groupby(md['refs'], key=lambda t: t[0]):
                <dt><strong>${cat}</strong></dt>
                <dd>
                    <ul class="unstyled">
                    % for c, t, p, k in items:
                    <li id="ref-${slug(k)}">${p|n}</li>
                    % endfor
                    </ul>
                </dd>
            % endfor
        </dl>
    </%util:well>
</%def>

<h2>${md['title']}</h2>
<ul class="unstyled">
    % for label, fragment in md['outline']:
    <li><a href="#${fragment}">${label}</a></li>
    % endfor
</ul>

${html|n}

<script>
    $(document).ready(function(){
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