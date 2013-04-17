<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>

##${util.data()}


<%def name="sidebar()">
    ${util.language_meta()}
</%def>


<% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, language=ctx.language) %>
<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Features</a></li>
        <li><a href="#tab2" data-toggle="tab">Sociolinguistic data</a></li>
        <li><a href="#tab3" data-toggle="tab">Segments</a></li>
    </ul>
    <div class="tab-content" style="overflow: visible;">
        <div id="tab1" class="tab-pane active">
            ${dt.render()}
        </div>
        <div id="tab2" class="tab-pane">
            <dl>
                % for v in [_v for _v in ctx.valuesets if _v.parameter.feature_type == 'sociolinguistic' and _v.values]:
                <dt>${h.link(request, v.parameter)}</dt>
                <dd>${v.values[0].domainelement.name}</dd>
                % endfor
            </dl>
        </div>
        <div id="tab3" class="tab-pane">
            <h4>Consonants</h4>
            ${u.ipa_consonants(ctx)}
            <h4>Vowels</h4>
            ${u.ipa_vowels(ctx)}


            <dl>
                % for v in [_v for _v in ctx.valuesets if _v.parameter.feature_type == 'segment' and _v.values and _v.parameter.jsondata['vowel']]:
                    % if v.values[0].domainelement.name.lower() != 'does not exist':
                <dt>${h.link(request, v.parameter)}</dt>
                <dd>${v.values[0].domainelement.name}</dd>
                    % endif
                % endfor
            </dl>
        </div>
    </div>
</div>


<%def name="sidebar()">
    <%util:well title="${_('Contributors')}">
    <dl>
        <dt>${_('Contributors')}:</dt>
        <dd>
            ${h.linked_contributors(request, ctx)}
            ${h.button('cite', onclick=h.JSModal.show(ctx.name, request.resource_url(ctx, ext='md.html')))}
        </dd>
    </dl>
    </%util:well>
    <%util:well>
        ${request.map.render()}
    </%util:well>
    <%util:well title="${_('References')}">
    <dl>
        % for ref in ctx.references:
        <dt>${h.link(request, ref.source)}</dt>
        <dd>${ref.source.description}</dd>
        % endfor
    </dl>
    </%util:well>
</%def>
