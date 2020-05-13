<%inherit file="home_comp.mako"/>

<h3>Contact ${h.contactmail(req)}</h3>
<div class="well">
    You can contact us via email at <a href="mailto:${request.dataset.contact}">${request.dataset.contact}</a>.
</div>

<h3>Errata</h3>
<div class="well">
<% drepo = request.registry.settings['clld.github_repos_data'] %>
    <p>
        We keep a
        <a href="https://github.com/${drepo}/issues"><i class="icon-share"> </i>list of errata</a>
        as issues of the
        <a href="https://github.com/${drepo}"><i class="icon-share"> </i>APiCS data repository on github</a>.
    </p>
    <p>
        If you encounter an erratum you don't see listed yet, feel free to
        <a href="https://github.com/${drepo}/issues/new"><i class="icon-share"> </i>create a new issue</a>.
    </p>
</div>

<h3>Bugs or Technical Comments</h3>
<div class="well">
<% srepo = request.registry.settings['clld.github_repos'] %>
    <p>
        <a href="https://github.com/${srepo}/issues"><i class="icon-share"> </i>Issues with the APiCS software</a>
        are kept in the issue tracker of the
        <a href="https://github.com/${srepo}"><i class="icon-share"> </i>apics project on github</a>.
    </p>
    <p>
        If you encounter any problems or glitches using this website, feel free to
        <a href="https://github.com/${srepo}/issues/new"><i class="icon-share"> </i>create a new issue</a>.
    </p>
</div>

<h3><i>APiCS</i> Logo</h3>
<div class="span1">
    <img src="${request.static_url('apics:static/apics-logo.png')}">
</div>
<div class="span5">
    The <i>APiCS</i> logo may be used to link to <i>APiCS Online</i>.
</div>
