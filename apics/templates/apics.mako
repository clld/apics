<%inherit file="app.mako"/>

##
## define app-level blocks:
##

<%block name="head">
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
            published
        </div>
        <div class="span6" style="text-align: center;">
            <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">
                <img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/88x31.png" />
            </a>
            <br />
            <span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Dataset" property="dct:title" rel="dct:type">The Atlas of Pidgin and Creole language Structures online</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="http://apics-online.info" property="cc:attributionName" rel="cc:attributionURL">Susanne Maria Michaelis, Philippe Maurer,Martin Haspelmath, and Magnus Huber </a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">Creative Commons Attribution 3.0 Unported License</a>.
        </div>
        <div class="span3" style="text-align: right;">
            disclaimer
        </div>
    </div>
</%block>

${next.body()}
