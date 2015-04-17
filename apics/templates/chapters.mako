<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<ul class="unstyled">
    % for c in chapters:
        <li>
            <a href="${request.route_url('chapter', id=c.id)}">${c.id} ${c.name}</a>
        </li>
    % endfor
</ul>
