<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>

<h2>${ctx.name}</h2>

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
            ${util.gbs_links(filter(None, [ctx.gbs_identifier]))}
        </div>
        <div id="tab2" class="tab-pane"><pre>${bibrec}</pre></div>
    </div>
</div>

<%def name="sidebar()">
    <div class="accordion" id="sidebar-accordion">
    % if ctx.languagesource:
        <%util:accordion_group eid="acc-l" parent="sidebar-accordion" title="${_('Languages')}" open="${True}">
            <ul class="nav nav-pills nav-stacked">
            ##% for source_assoc in ctx.languagesource:
            % for vsr in u.get_referents(ctx, 'language'):
                <li>${h.link(request, vsr.language)}</li>
            % endfor
            </ul>
        </%util:accordion_group>
    % endif
    % if ctx.valuesetreferences:
        <%util:accordion_group eid="acc-v" parent="sidebar-accordion" title="${_('Datapoints')}">
            <ul class="nav nav-pills nav-stacked">
            ##% for vsr in ctx.valuesetreferences[:100]:
            % for vsr in u.get_referents(ctx, 'valueset'):
                <li>${h.link(request, vsr.valueset)}</li>
            % endfor
            </ul>
        </%util:accordion_group>
    % endif
    % if ctx.sentencereferences:
        <%util:accordion_group eid="acc-s" parent="sidebar-accordion" title="${_('Examples')}">
            <ul class="nav nav-pills nav-stacked">
            ##% for vsr in ctx.sentencereferences[:100]:
            % for vsr in u.get_referents(ctx, 'sentence'):
                <li>${h.link(request, vsr.sentence)}</li>
            % endfor
            </ul>
        </%util:accordion_group>
    % endif
    </div>
</%def>
