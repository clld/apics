<%inherit file="../apics.mako"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>

<%! from itertools import groupby %>
<%! from clldutils.misc import slug %>

<%block name="head">
    <style>
      ${css}
    </style>
</%block>

<%def name="sidebar()">
    <%util:well title="Authors">
        ${ctx.formatted_contributors()}
        ##${h.cite_button(request, ctx)}
    </%util:well>
    <%util:well title="Maps">
        <ul>
            <li>
                <a href="${request.route_url('parameter', id=ctx.id, _anchor='map-container')}">
                    Online Feature map in Web Mercator projection
                </a>
            </li>
            <li>
                ${u.cdstar.link(ctx._files[0], label='Feature map in Gall-Peters projection')}
            </li>
        </ul>
    </%util:well>
    % if md.get('refs'):
        <%util:well title="References">
            <dl>
                % for cat, items in groupby(md['refs'], key=lambda t: t['category']):
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

<h2>Chapter ${ctx.id}: ${ctx.name}</h2>

<div class="alert alert-info">
    Feature information for this chapter can be found in
    ${h.link(request, ctx, label='feature {0}'.format(ctx.id))}.
</div>

<blockquote>
    <ul class="unstyled">
        % for label, fragment in md['outline']:
            <li><a href="#${fragment}">${label|n}</a></li>
        % endfor
    </ul>
</blockquote>

${html(u.value_table(ctx, request))|n}

<br>

<script>
    $(document).ready(function () {
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
