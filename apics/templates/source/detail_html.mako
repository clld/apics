<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>

<h2>${ctx.name}</h2>
${ctx.coins(request)|n}

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Text</a></li>
        <li><a href="#tab2" data-toggle="tab">BibTeX</a></li>
    </ul>
    <div class="tab-content">
        <% bibrec = ctx.bibtex() %>
        <div id="tab1" class="tab-pane active">
            <p id="${h.format_gbs_identifier(ctx)}">${bibrec.text()|n}</p>
            % if ctx.datadict().get('Additional_information'):
            <p>
                ${ctx.datadict().get('Additional_information')}
            </p>
            % endif
            <ul class="inline">
                % if ctx.url:
                    <li>${u.format_external_link_in_label(ctx.url)}</li>
                % elif ctx.jsondata.get('doi'):
                    <li>${u.format_external_link_in_label('https://doi.org/%s' % ctx.jsondata['doi'], 'DOI')}</li>
                % endif
            </ul>
        </div>
        <div id="tab2" class="tab-pane"><pre>${bibrec}</pre></div>
    </div>
</div>

<%def name="sidebar()">
    <% referents = h.get_referents(ctx, exclude=['contribution']) %>
    <div class="accordion" id="sidebar-accordion">
    % if referents['language']:
        <%util:accordion_group eid="acc-l" parent="sidebar-accordion" title="${_('Languages')}" open="${True}">
            ${util.stacked_links(referents['language'])}
        </%util:accordion_group>
    % endif
    % if referents['valueset']:
        <%util:accordion_group eid="acc-v" parent="sidebar-accordion" title="${_('Datapoints')}">
            ${util.stacked_links(referents['valueset'])}
        </%util:accordion_group>
    % endif
    % if referents['sentence']:
        <%util:accordion_group eid="acc-s" parent="sidebar-accordion" title="${_('Examples')}">
            ${util.stacked_links(referents['sentence'])}
        </%util:accordion_group>
    % endif
    </div>
</%def>
