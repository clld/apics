<%inherit file="../home_comp.mako"/>

<h2>Welcome to ${request.dataset.formatted_name()}</h2>

<div class="span4 alert">
    <img src="${request.static_url('apics:static/fishing_boats_small.jpg')}"
         class="img-polaroid"/>
    <div>
        <small>
            Fishing boats: Fishermen selling their catch at Abandze, Ghana, the site of
            the
            first British trading station on the Gold Coast, Fort Kormantin, established
            in
            1632. Photograph by Thorsten Brato, 2008.
        </small>
    </div>
</div>
<div class="span7">
    <p>
        The <i>Atlas of Pidgin and Creole Language Structures (APiCS)</i> provides
        expert-based
        information on 130 grammatical and lexical features of 76 pidgin and creole
        languages from around the world.
    </p>
    <p>
        It was edited by Susanne Maria Michaelis, Philippe Maurer, Martin Haspelmath, and
        Magnus Huber, with crucial support from the Max Planck Institute for Evolutionary
        Anthropology (Leipzig) and the Deutsche Forschungsgemeinschaft (DFG).
    </p>
    <p>
        The original 2013 version was
        ${h.external_link('https://global.oup.com/academic/product/the-atlas-and-survey-of-pidgin-and-creole-languages-9780199677702?cc=de&lang=en&#.UlUFPXiJSLM', label="published as a set of four books by Oxford University Press")}
        ,
        containing the Atlas volume proper as well as three Survey
        volumes, with the following bibliographical information:
    </p>
    <blockquote>
        Michaelis, Susanne Maria & Maurer, Philippe & Haspelmath, Martin & Huber, Magnus
        (eds.) 2013. <i>The Atlas of Pidgin and Creole Language Structures</i>. Oxford:
        Oxford
        University Press. 400 pages.
    </blockquote>
    <blockquote>
        Michaelis, Susanne Maria & Maurer, Philippe & Haspelmath, Martin & Huber, Magnus
        (eds.) 2013. <i>The Survey of Pidgin and Creole Languages</i>. 3 volumes. Volume
        I:
        English-based and Dutch-based Languages; Volume II: Portuguese-based,
        Spanish-based, and French-based Languages. Volume III: Contact Languages Based on
        Languages From Africa, Australia, and the Americas. Oxford: Oxford University
        Press.
    </blockquote>

    <p>
        The online version contains all the materials from the printed version, plus a
        large number of examples and feature value comments. In addition, it was
        specifically designed to allow comparison with data from <i>WALS (the World Atlas
        of
        Language Structures)</i>.
    </p>

    <!--p>
        This web site contains supporting electronic material for
        the <i>Atlas of Pidgin and Creole Language Structures (APiCS)</i>,
        ${h.external_link('http://ukcatalogue.oup.com/product/9780199677702.do#.UlUFPXiJSLM', label="a publication of Oxford University Press")}.
        <i>APiCS</i> shows comparable synchronic data on the grammatical and
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
        from <i>WALS (the World Atlas of Language Structures)</i>.
    </p-->
</div>
<div class="clearfix" width="100%"></div>

<p>
    The online <i>APiCS</i> contains three kinds of contributions:
</p>
<ul>
    <li>
        <a href="${request.route_url('parameters')}">${stats['parameter']} features and
            chapters</a> dealing with grammatical and lexical features, containing
        information on feature values from up to 76 creole, pidgin and mixed languages;
        each of the chapters was written by one (or sometimes two) of the four editors of
        APiCS. The chapters in the online version are identical to the chapters in the
        book version, but the online version allows direct access to information on each
        feature value for each language.
    </li>
    <li>
        <a href="${request.route_url('contributions')}">${stats['language']} language
            structure datasets</a> providing information on the 130 features for each
        language, including examples and comments for many of the language-feature
        combinations. The structure datasets are unique to the online version.
    </li>
    <li>
        ## FIXME: link to survey index
        74 language surveys
        giving prose overview of each language, both its
        sociohistorical context and its grammatical properties. The surveys in the online
        version are identical to the survey chapters in the book version.
    </li>
</ul>

<div class="span4 pull-right alert">
    <img src="${request.static_url('apics:static/fish_and_sari_small.jpg')}"
         class="img-polaroid"/>
    <div>
        <small>
            Fish & Sari: Hanging bummalo ("Bombay duck") to dry on the beach of Simbor,
            the site of a
            ruined Portuguese fort not far from Diu, India. Photograph by Hugo Cardoso,
            2005.
        </small>
    </div>
</div>

<p>
    Since the Atlas chapters and the Survey chapters are identical to the book version,
    they should be cited like the book chapters. However, the language structure datasets
    are unique to the online version, and they should be cited as follows:
</p>

<blockquote>
    ${h.newline2br(citation.render(example_contribution, request))|n}
</blockquote>
<p>

    The complete online version, including both the atlas chapters and the surveys, can be
    cited as follows:
    ${h.cite_button(request, ctx)}
</p>
<blockquote>
    ${h.newline2br(citation.render(ctx, request))|n}
</blockquote>

<p>
    More background information is found in the <a href="${request.route_url('about')}">Introduction</a>.
</p>
