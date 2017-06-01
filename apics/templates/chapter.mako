<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<%! from itertools import groupby %>
<%! from clldutils.misc import slug %>

<%block name="head">
    <style>
      ${css}
    </style>
</%block>

<%def name="sidebar()">
    % if ctx.authors:
        <%util:well title="Author">
            <span>${ctx.format_authors()}</span>
            ${h.cite_button(request, ctx)}
        </%util:well>
    % endif
    ##<%util:well title="Values">
    ##    ${u.value_table(ctx, request)}
    ##</%util:well>
        % if md['refs']:
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

<h2>${ctx.id} ${ctx.name}</h2>
<ul class="unstyled">
    % for label, fragment in md['outline']:
        <li><a href="#${fragment}">${label}</a></li>
    % endfor
</ul>

${html(u.value_table(ctx, request))|n}

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
