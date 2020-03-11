<%namespace name="util" file="../util.mako"/>

<h3>${h.link(request, ctx)}</h3>
<small>by ${h.linked_contributors(request, ctx.contribution)}</small>

% if valueset:
    ## called for the info windows on parameter maps
    <h4>${_('Value')}</h4>
    <ul class='unstyled'>
        % for value in valueset.values:
        <li>
            ${h.map_marker_img(request, value)}
            ${h.link(request, valueset, label=str(value))}
        </li>
        % endfor
    </ul>
    % if valueset.references:
    <h4>${_('Source')}</h4>
    <p>${h.linked_references(request, valueset)}</p>
    % endif
% endif
