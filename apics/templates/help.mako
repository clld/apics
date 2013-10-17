<%inherit file="home_comp.mako"/>

<h3>Help</h3>
<h4 id="dataset">1. <i>APiCS Online</i></h4>
<p>
    <i>APiCS Online</i> contains information on
    <a href="${request.route_url('languages')}">76 languages</a> and
    <a href="${request.route_url('parameters')}">130 structural features</a>, which was contributed by
    <a href="${request.route_url('contributors')}">88 contributors</a>.
    There are
    <a href="${request.route_url('sentences')}">18525 examples</a> illustrating the features and feature values.
    In addition, <i>APiCS Online</i> is designed to allow
    comparison with data from
    ${h.external_link('http://wals.info', label="WALS")}
    (the <i>World Atlas of Language Structures</i>).
</p>
<h4 id="languages">2. Languages</h4>
<p>
    The 76 contact languages were chosen as representative of the kinds of languages that are generally discussed under the
    headings “pidgin” and “creole”, and we also added a few bilingual mixed languages (Media Lengua, Gurindji Kriol, Michif,
    and Mixed Ma’a/Mbugu). Some of the “languages” are closely related varieties that would normally be regarded as dialects.
</p>
<p>
    The data for each language were contributed by an author (or author team), and it is these language structure datasets
    that make up the individual contributions of <i>APiCS Online</i>. The list of languages is therefore also the list of
    individually citable contributions.
</p>

<h5 id="languages-no">No.</h5>
<p>
    The languages are ordered and numbered as in the Survey of Pidgin and Creole Languages. The English- and Dutch-based
    languages are followed by Romance-based languages and then by languages with non-European lexifiers. Within each lexifier
    group, the order is usually west to east. This ordering has the consequence rthat often languages which are similar occur
    next to each other.
</p>

<h5 id="languages-lexifier">Lexifier</h5>
<p>
    Most languages have a single (major) lexifier, i.e. a single language that contributed the bulk of its words (lexical items).
    However, among the ten languages which are classified under “Other” here, there are a few (Michif, Gurindji Kriol, Mixed Ma’a/Mbugu)
    where a single lexifier is difficult to identify.
</p>

<h5 id="languages-region">Region</h5>
<p>
    This column provides a rough classification of languages into geographical world regions.
</p>

<h5 id="languages-cite">Cite</h5>
<p>
    The cite button tells the user how the dataset contribution should be cited. Note that each dataset is a regular scientific
    publication and should be treated as such.
</p>

<h4 id="language">Individual language pages</h4>
<p>
    Each language page gives a short prose description (including a description of the default lect, i.e. the variety of the
    language that the data are based on), as well as the link to a glossed text (with sound file for many of the languages).
    On the right-hand side, an infobox gives a basic overview of the most important facts about the language. Below this is a
    link to the corresponding chapter in the <i>Survey of Pidgin and Creole Languages</i> (a three-volume book publication), followed
    by a list of references that were used in <i>APiCS</i> for the language.
</p>
<p>
    The individual-language pages give the values in three tables (in four tabs): the 130 primary features, the segment features
    (in a sortable table as well as in the form of an IPA chart), and the sociolinguistic features. In each of these tables, the
    datapoints (language/feature combinations) are listed by feature.
</p>

<h5 id="language-value">Value</h5>
<p>
    The Value column gives the feature value for every feature. When a language has multiple feature values, the feature is listed
    twice (or more times), once for every value. By clicking on the value name, the user gets to the datapoint page, which includes
    all information on a language/feature combination.
</p>

<h5 id="language-precentage">Percentage (%)</h5>
<p>
    This column shows the relative importance of a value choice where a language allows multiple options (only in multiple-choice
    features). This is a rough estimate of the relative importance in terms of token frequency or type frequency. (For details, see
    the description in the introduction of the printed <i>APiCS</i>.)
</p>

<h5 id="language-lect">Lect</h5>
<p>
    For some languages and some features, information on multiple lects is given, e.g. for Ghanaian Pidgin English, in addition
    to the default lect, 11 features have information on the Student Pidgin lect and 1 feature has information on the Acrolectal
    lect. Note that the maps and the value box only show the default lect.
</p>

<h5 id="language-more">Details</h5>
<p>
    By clicking on “more”, users get access to examples, prose comments and confidence values.
</p>

<h5 id="language-source">Source</h5>
<p>
    Each value is associated with a source, which can be “own knowledge” in case no specific place in the literature is referred to.
</p>


<h4 id="parameters">3. Features</h4>
<p>
    The primary 130 features were chosen as representative of the kinds of features by which pidgin and creole languages (and other
    contact languages) have been said to differ among each other. In order to facilitate comparison between APiCS languages and the
    world’s languages, 48 of them are very similar to features of the World Atlas of Language Structures (wals.info).
</p>
<p>
    Of the 130 primary features, 62 are multiple-choice features, i.e. features for which several different values can be true.
    For these features, the language dots are pie charts showing multiple colours. The remaining features are single-choice features.
</p>
<p>
    Below the feature map, the “Values” tab shows the languages and their values, while the “Examples” tab shows the examples that
    are related to the feature.
</p>

<h5>Feature type</h5>
<p>
    In addition to the 130 primary features, we also have 177 segment features which give much more limited information about
    phonological segments (consonants and vowels), as well as 28 sociolinguistic features, which give information about the speakers
    and the use of the languages in society.
</p>

<h5>Area</h5>
<p>
    The feature area provides a rough classification of features into thematic areas of grammar.
</p>

<h5>WALS-APiCS</h5>
<p>
    This column gives the link to the corresponding WALS-APiCS page for those features which were based on WALS features.
</p>

<h5>Cite</h5>
<p>
    The cite button tells the user how the feature contribution can be cited. Note that it is better to cite the chapter of the
    printed <i>Atlas of Pidgin and Creole Language Structures</i> (published by Oxford University Press), because this also contains a
    text chapter discussing the feature.
</p>

<h4>Individual feature pages</h4>
<p>
    The individual-feature pages give a short feature description, the Values box and the map. Below the map is the datapoint table
    and a list of examples relevant to the feature in a second tab.
</p>

<h5>Values</h5>
<p>
    The “Values” box above the feature map lists the values, and gives the number of languages showing each value. For multiple-choice
    features, there are three columns: The first column (“excl”) shows the number of languages that have this value exclusively (i.e.
    that have a single-colour pie chart). The second column (“shrd”) shows the number of languages that have this value as one among
    several shared values (one piece in the pie chart), and the third column (“all”) shows the number of languages that show the value,
    regardless of whether they show it exclusively or not.
</p>
<p>
    By “representation” we mean the number of languages for which information is available (when no information is available, the
    language is simply not shown).
</p>

<h5>Map</h5>
<p>
    The map shows the 76 <i>APiCS</i> languages, with different colours for different feature values. When multiple values are true (only in
    multiple-choice features), a pie chart is given for the language, showing the relative importance of the values.
</p>
<p>
    The menu bar at the top of the map allows the user to see a legend, to modify the icon size, to limit the languages to those with
    a certain lexifier, and to show or hide language name labels.
</p>
<p>
    The button in the upper right hand allows a choice between several different base maps.
</p>

<h5>Value</h5>
<p>
    The Value column gives the feature value for every language. When a language has multiple feature values, it is listed twice
    (or more times), once for every value. By clicking on the value name, the user gets to the datapoint page, which includes all
    information on a language/feature combination.
</p>

<h5>Percentage (%)</h5>
<p>
    This column shows the relative importance of a value choice where a language allows multiple options (only in multiple-choice
    features). This is a rough estimate of the relative importance in terms of token frequency or type frequency. (For details,
    see the description in the introduction of the printed <i>APiCS</i>.)
</p>

<h5>Details</h5>
<p>
    By clicking on the “more” button, the user can get access to the prose comments (if any) and examples.
</p>

<h4>4. WALS-APiCS</h4>
<p>
    Here we list the 48 primary features that were modeled on WALS features.
</p>
<p>
    The WALS-APiCS pages show the WALS map on the left, and the corresponding <i>APiCS</i> map on the left, using the same colours
    for matching values.
</p>
<p>
    The APiCS map shown here is called “WALS-like APiCS map”, because in many cases it has been adapted to WALS. Since only APiCS,
    but not WALS, allows multiple-choice features, the multiple-choice features had to be transformed into single-choice features.
    (For the precise way in which this was done, see the printed <i>APiCS</i>.)
</p>

<h5>APiCS total</h5>
<p>
    This shows the number of languages represented on the <i>APiCS</i> map.
</p>

<h5>WALS total</h5>
<p>
    This shows the number of languages represented on the WALS (2011) map.
</p>

<h4>5. Examples</h4>
<p>
    Here all 18525 examples are listed.
</p>

<h5>Id</h5>
<p>
    The example ID consists of the language number and the number of the example within the language.
</p>

<h5>Primary text</h5>
<p>
    The primary text is the example text as it would be found in a running text (using Latin script, but no further annotation).
    By clicking on the primary text of an example, the user gets to the example page, which includes all information on an example,
    including the gloss in interlinear format, the source and an optional prose comment on the example. For some languages, the
    original script is given for many of the examples (Chinese Pidgin English, Chinese Pidgin Russian).
</p>

<h5>Analyzed text</h5>
<p>
    The analyzed text is often identical to the primary text, but sometimes differs from it by including morpheme boundaries within
    a word (marked by a hyphen) or other analytical notation.
</p>

<h5>Gloss</h5>
<p>
    The gloss contains a morpheme-by-morpheme translation of the analyzed text. Each string of the analyzed text corresponds to
    exactly one string in the gloss. The abbreviations of grammatical category labels are shown in caps. On the example page,
    they are resolved by mouseover.
</p>

<h5>Translation</h5>
<p>
    This gives the idiomatic translation into English. For some languages and some examples, the example page in addition contains
    the translation into some other language that is important in the context (e.g. into French for Haitian Creole).
</p>

<h5>Details</h5>
<p>
    The “more” button gives the example in a more readable interlinear format.
</p>
