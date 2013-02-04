% for c in [c for c in ctx.contribution.comments if c.parameter_pk == ctx.parameter_pk]:
<p>
    ${c.comment}
</p>
% endfor
