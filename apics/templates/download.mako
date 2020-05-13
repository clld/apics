<%inherit file="home_comp.mako"/>

<h3>Downloads</h3>

<p>
    <a href="${req.resource_url(req.dataset)}">APiCS Online</a>
    serves the latest
    ${h.external_link('https://github.com/cldf-datasets/apics/releases', label='released version')}
    of data curated at
    ${h.external_link('https://github.com/cldf-datasets/apics', label='cldf-datasets/apics')}.
    All released versions are accessible via <br/>
    <a href="https://doi.org/10.5281/zenodo.3823887">
        <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3823887.svg" alt="DOI">
    </a>
    <br/>
    on
    ${h.external_link('https://zenodo.org', label='Zenodo')}
    as well.
</p>
