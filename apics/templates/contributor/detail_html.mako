<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributors" %>

<%def name="sidebar()">
    <%util:well>
        <dl>
            % if ctx.address:
                <dt>${_('Address')}:</dt>
                <dd>
                    <address>
                        ${h.text2html(ctx.address)|n}
                    </address>
                </dd>
            % endif
            % if ctx.url:
                <dt>${_('Web:')}</dt>
                <dd>${h.external_link(ctx.url)}</dd>
            % endif
            % if ctx.email:
                <dt>${_('Mail:')}</dt>
                <dd>${ctx.email.replace('@', '[at]')}</dd>
            % endif
            ${util.data(ctx, with_dl=False)}
        </dl>
    </%util:well>
</%def>


<h2>${ctx.name}</h2>

% if ctx.description:
<p>${ctx.description}</p>
% endif

% if ctx.survey_assocs:
    <h4>Language surveys</h4>
    <ul>
        % for c in ctx.survey_assocs:
            <li>${h.link(request, c.survey)}</li>
        % endfor
    </ul>
% endif
% if ctx.contribution_assocs:
    <h4>Structure datasets</h4>
    <ul>
        % for c in ctx.contribution_assocs:
            <li>${h.link(request, c.contribution)}</li>
        % endfor
    </ul>
% endif
% if ctx.feature_assocs:
    <h4>Feature chapters</h4>
    <ul>
        % for c in ctx.feature_assocs:
            <li>${h.link(request, c.feature, url_kw=dict(ext='chapter.html'))}</li>
        % endfor
    </ul>
% endif
