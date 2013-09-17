<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="header">
    <div id="header" class="container-fluid" style="background-repeat: no-repeat; background-image: url(${request.static_url('apics:static/banner.jpg')})">
        <h1>
            <a href="${request.route_url('dataset')}">${request.dataset.description}</a>
        </h1>
    </div>
</%block>

${next.body()}
