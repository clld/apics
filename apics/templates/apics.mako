<%inherit file="app.mako"/>

##
## define app-level blocks:
##

<%block name="head">
    <link rel="shortcut icon" href="${request.static_url('apics:static/favicon.ico', _query=dict(v='1'))}" type="image/x-icon" />
    <link href="${request.static_url('apics:static/bootstrap.css')}" rel="stylesheet"/>
    <link href="${request.static_url('apics:static/apics.css')}" rel="stylesheet"/>
    <script src="${request.static_url('apics:static/apics.js')}"></script>
</%block>

<%block name="header">
    <h1>
        <a href="${request.route_url('home')}">The Atlas of Pidgin and Creole Language Structures</a>
    </h1>
</%block>

<%block name="footer">
    <div class="row-fluid" style="padding-top: 15px; border-top: 1px solid black;">
        <div class="span3">
        </div>
        <div class="span6" style="text-align: center;">
            <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">
                <img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/88x31.png" />
            </a>
            <br />
            ${u.apics(request)}
            edited by
            <span xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName" rel="cc:attributionURL">
                ${request.registry.settings['clld.publication.editors']}
           </span>
            is licensed under a
            <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">
                Creative Commons Attribution 3.0 Unported License
            </a>.
        </div>
        <div class="span3" style="text-align: right;">
            <a href="${request.route_url('legal')}">disclaimer</a>
        </div>
    </div>
</%block>

${next.body()}
