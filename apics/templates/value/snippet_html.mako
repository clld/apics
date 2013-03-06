<%namespace name="util" file="../util.mako"/>

% if ctx.valueset.description:
<p>
    ${h.text2html(ctx.valueset.description)}
</p>
% endif

% if ctx.sentence_assocs:
<h4>${_('Sentences')}</h4>
${util.sentences(ctx)}
% endif

% if not ctx.valueset.description and not ctx.sentence_assocs:
-- no information --
% endif
