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
    <table style="width: 100%; border-top: 1px solid black;">
        <tr>
            <td style="width: 33%;">published</td>
            <td style="width: 33%; text-align: center;">license</td>
            <td style="width: 33%; text-align: right;">disclaimer</td>
        </tr>
    </table>
</%block>

${next.body()}
