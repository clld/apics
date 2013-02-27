<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%! from clld.interfaces import IDataTable %>
<%! from clld.db.models.common import Value %>

<h2>${_('Contribution')} ${ctx.name}</h2>

${util.data()}

<h3>References</h3>
<dl>
    % for ref in ctx.references:
    <dt>${h.link(request, ref.source)}</dt>
    <dd>${ref.source.description}</dd>
    % endfor
</dl>
