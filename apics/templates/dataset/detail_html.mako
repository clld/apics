<%inherit file="../home_comp.mako"/>
<% TxtCitation = h.get_adapter(h.interfaces.IRepresentation, ctx, request, ext='md.txt') %>
<% stats = u.get_stats(ctx) %>

<h2>Welcome to ${u.apics(request)}</h2>

<p>
This web site contains supporting electronic material for
the Atlas of Pidgin and Creole Language Structures (APiCS), a publication of
Oxford University Press. APiCS shows comparable synchronic data on the grammatical and
lexical structures of 76 pidgin and creole languages. The language set contains not only
the most widely studied Atlantic and Indian Ocean creoles, but also less well known
pidgins and creoles from Africa, South Asia, Southeast Asia, Melanesia and Australia,
including some extinct varieties, and several mixed languages.
</p>

<p>
${u.apics(request)} is a separate publication, edited by
Susanne Maria Michaelis, Philippe Maurer, Martin Haspelmath, and Magnus Huber.
It was made possible by support from the Deutsche Forschungsgemeinschaft and
the Max Planck Institute for Evolutionary Anthropology.
</p>

<p>
${u.apics(request)} contains information on
<a href="${request.route_url('contributions')}">76 languages</a> and
<a href="${request.route_url('parameters')}">130 structural features</a>, which was
contributed by
<a href="${request.route_url('contributors')}">88 contributors</a>. There are over
<a href="${request.route_url('sentences')}">18,000 examples</a> illustrating the features
and feature values. In addition, ${u.apics(request)} is designed to allow comparison with data
from WALS (the World Atlas of Language Structures).
</p>

<p>
${u.apics(request)} is an edited database consisting of 76 datasets which should be regarded as
separate publications, like chapters of an edited volume. These datasets should be cited
as follows:

<blockquote>
    ${h.newline2br(TxtCitation.render(request.db.query(h.models.Contribution).filter_by(id='58').one(), request))|n}
</blockquote>

The complete work should be cited as follows:

<blockquote>
    ${h.newline2br(TxtCitation.render(ctx, request))|n}
</blockquote>

</p>

<p>
${u.apics(request)} overlaps with the book version of
the Atlas of Pidgin and Creole Language Structures (APiCS). Like the book atlas, it shows
all the maps, and in addition, it shows examples for each feature-language combination.
But it does not include the detailed discussion text on each of the 130 structural
features that the book atlas contains.
</p>
