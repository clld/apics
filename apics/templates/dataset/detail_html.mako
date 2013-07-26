<%inherit file="../home_comp.mako"/>

<h2>Welcome to ${request.dataset.formatted_name()}</h2>

<p>
This web site contains supporting electronic material for
the Atlas of Pidgin and Creole Language Structures (APiCS), a publication of
Oxford University Press. APiCS shows comparable synchronic data on the grammatical and
lexical structures of ${stats['language']} pidgin and creole languages. The language set contains not only
the most widely studied Atlantic and Indian Ocean creoles, but also less well known
pidgins and creoles from Africa, South Asia, Southeast Asia, Melanesia and Australia,
including some extinct varieties, and several mixed languages.
</p>

<p>
${request.dataset.formatted_name()} is a separate publication, edited by
Susanne Maria Michaelis, Philippe Maurer, Martin Haspelmath, and Magnus Huber.
It was made possible by support from the Deutsche Forschungsgemeinschaft and
the Max Planck Institute for Evolutionary Anthropology.
</p>

<p>
${request.dataset.formatted_name()} contains information on
<a href="${request.route_url('contributions')}">${stats['language']} languages</a> and
<a href="${request.route_url('parameters')}">${stats['parameter']} structural features</a>, which was
contributed by
<a href="${request.route_url('contributors')}">${stats['contributor']} contributors</a>. There are
<a href="${request.route_url('sentences')}">${stats['sentence']} examples</a> illustrating the features
and feature values. In addition, ${request.dataset.formatted_name()} is designed to allow comparison with data
from WALS (the World Atlas of Language Structures).
</p>

<p>
${request.dataset.formatted_name()} is an edited database consisting of ${stats['language']} datasets which should be regarded as
separate publications, like chapters of an edited volume. These datasets should be cited
as follows:
</p>
<blockquote>
    ${h.newline2br(citation.render(example_contribution, request))|n}
</blockquote>
<p>
The complete work should be cited as follows:
</p>
<blockquote>
    ${h.newline2br(citation.render(ctx, request))|n}
</blockquote>

<p>
${request.dataset.formatted_name()} overlaps with the book version of
the Atlas of Pidgin and Creole Language Structures (APiCS). Like the book atlas, it shows
all the maps, and in addition, it shows examples for each feature-language combination.
But it does not include the detailed discussion text on each of the 130 structural
features that the book atlas contains.
</p>
