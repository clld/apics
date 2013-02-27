<% comments = [c.comment for c in ctx.contribution.comments if c.parameter_pk == ctx.parameter_pk] %>

% if comments:
<p>
    ${h.text2html(comments[0])}
</p>
% endif

% if ctx.sentence_assocs:
<h4>${_('Sentences')}</h4>
<ol>
    % for a in ctx.sentence_assocs:
    <li>
        % if a.description:
        <p>${a.description}</p>
        % endif
        ${h.rendered_sentence(a.sentence)}
        % if a.sentence.references:
        <p>See ${h.linked_references(request, a.sentence)|n}</p>
        % endif
    </li>
    % endfor
</ol>
<script>
$(document).ready(function() {
    $('.ttip').tooltip({placement: 'bottom', delay: {hide: 300}});
});
</script>
% endif
