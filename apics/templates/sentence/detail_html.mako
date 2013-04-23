<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sentences" %>

<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.language.contribution)}
        by
        ${h.linked_contributors(request, ctx.language.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.language.contribution.name, request.resource_url(ctx.language.contribution, ext='md.html')))}
    </dd>
</dl>
</div>
</%def>

<h2>${_('Sentence')} ${ctx.id}</h2>

${h.rendered_sentence(ctx)|n}

<dl>
% if ctx.comment:
<dt>Comment:</dt>
<dd>${ctx.comment}</dd>
% endif
% if ctx.source:
<dt>${_('Type')}:</dt>
<dd>${ctx.type}</dd>
% endif
% if ctx.references or ctx.source:
<dt>${_('Source')}:</dt>
% if ctx.source:
<dd>${ctx.source}</dd>
% endif
% if ctx.references:
<dd>${h.linked_references(request, ctx)|n}</dd>
% endif
% endif
</dl>
