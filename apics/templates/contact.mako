<%inherit file="home_comp.mako"/>

<h3>Contact ${h.contactmail(req)}</h3>
<div class="well">
    You can contact us via email at <a href="mailto:${request.dataset.contact}">${request.dataset.contact}</a>.
</div>

<h3>Errata</h3>
<div class="well">
    <p>
        We keep a
        <a href="https://github.com/clld/apics-data/issues"><i class="icon-share"> </i>list of errata</a>
        as issues of the
        <a href="https://github.com/clld/apics-data"><i class="icon-share"> </i>apics-data project on github</a>.
    </p>
    <p>
        If you encounter an erratum you don't see listed yet, feel free to
        <a href="https://github.com/clld/apics-data/issues/new"><i class="icon-share"> </i>create a new issue</a>.
    </p>
</div>

<h3><i>APiCS</i> Logo</h3>
<div class="span1">
    <img src="${request.static_url('apics:static/apics-logo.png')}">
</div>
<div class="span5">
    The <i>APiCS</i> logo may be used to link to <i>APiCS Online</i>.
</div>
