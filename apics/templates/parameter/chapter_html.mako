<%inherit file="../apics.mako"/>
<%namespace name="util" file="../util.mako"/>

<%! from itertools import groupby %>
<%! from clldutils.misc import slug %>

<%block name="head">
    <style>
      ${css}
    </style>
</%block>

<ul style="margin-top: 10px;" class="nav nav-pills pull-right">
    <li style="margin-right: 10px;">${h.alt_representations(request, ctx, doc_position='left', exclude=['md.html'])}</li>
    <li class="active"><a href="${req.resource_url(ctx, _anchor='map-container')}">${h.icon('globe', style='vertical-align: bottom')}&nbsp;Map</a></li>
    <li class="active"><a href="${req.resource_url(ctx, _anchor='list-container')}">${h.icon('list', style='vertical-align: bottom')}&nbsp;List</a></li>
    ##<li class="active"><a href="#desc-container">${h.icon('book', style='vertical-align: bottom')}&nbsp;Description</a></li>
    % if ctx.phoible:
    <li>
        ${h.external_link(ctx.phoible.url, ctx.phoible.segment + ' - PHOIBLE')}
    </li>
% endif
</ul>

% if ctx:
    <h2>Chapter ${ctx.id}: ${ctx.name}</h2>
    <div class="row-fluid">
        <div class="span8">
            ${html(u.value_table(ctx, request))|n}
        </div>
        <div class="span4">
            % if md.get('outline'):
                <%util:well title="Contents">
                    <ul class="unstyled">
                        % for label, fragment in md['outline']:
                            <li><a href="#${fragment}">${label}</a></li>
                        % endfor
                    </ul>
                </%util:well>
            % endif
            % if ctx.authors:
                <%util:well title="Author">
                    <span>${ctx.format_authors()}</span>
                ${h.cite_button(request, ctx)}
                </%util:well>
            % endif
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
        </div>
    </div>
% else:
    <h2>Introduction</h2>
    ${html('')|n}
% endif
<div style="margin-bottom: 20px"> </div>


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
