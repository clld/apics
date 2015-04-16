<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<ul class="unstyled">
    % for id_, contrib in surveys:
    <li>
        <a href="${request.route_url('survey', id=id_)}">${contrib.name}</a>
    </li>
    % endfor
</ul>