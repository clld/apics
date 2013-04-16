<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<h2>${_('Contribution')} ${ctx.name}</h2>

##${util.data()}


<%def name="sidebar()">
    ${util.language_meta()}
</%def>


<% dt = request.registry.getUtility(h.interfaces.IDataTable, 'values'); dt = dt(request, h.models.Value, language=ctx.language) %>

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Features</a></li>
        <li><a href="#tab2" data-toggle="tab">Sociolinguistic data</a></li>
        <li><a href="#tab3" data-toggle="tab">Segments</a></li>
    </ul>
    <div class="tab-content">
        <div id="tab1" class="tab-pane active">
            ${dt.render()}
        </div>
        <div id="tab2" class="tab-pane">
            <dl>
                % for v in [_v for _v in ctx.valuesets if _v.parameter.feature_type == 'sociolinguistic' and _v.values]:
                <dt>${h.link(request, v.parameter)}</dt>
                <dd>${v.values[0].domainelement.name}</dd>
                % endfor
            </dl>
        </div>
        <div id="tab3" class="tab-pane">




<table style="line-height:1.4em; background:transparent; margin:0em auto 0em auto;" cellspacing="0">
<tbody><tr style="text-align:center;">
<td></td>
<td style="width:64px;"><span style="position:relative; left:-0.4em;">Front</span></td>
<td style="width:62px;">Near-​front</td>
<td style="width:64px;">Central</td>
<td style="width:62px;">Near-​back</td>
<td style="width:64px;">Back</td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><b>Close</b></td>
<td style="height:210px;" colspan="5" rowspan="7">
<div style="position:relative;"><img alt="Blank vowel trapezoid.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Blank_vowel_trapezoid.svg/320px-Blank_vowel_trapezoid.svg.png" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Blank_vowel_trapezoid.svg/480px-Blank_vowel_trapezoid.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Blank_vowel_trapezoid.svg/640px-Blank_vowel_trapezoid.svg.png 2x" height="224" width="320">
<div style="background:transparent; position:absolute; top:0px; left:0px;">
<table style="position:relative; width:320px; height:224px; text-align:center; background:transparent; font-size:131%;">
<tbody><tr>
<td>
<div style="position:absolute; top:4px; left:-1px; width:60px; height:1px; background:transparent;">
    <span style="position:absolute; left:20px; width:20px;">
        <span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span>
        </span>
    </span>
    <span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;">
        <span style="background:#f9f9f9; padding:0px 1px 0px 2px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">
                <a href="/wiki/Close_front_unrounded_vowel" title="Close front unrounded vowel">i</a>
            </span>
        </span>
    </span>
    <span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;">
        <span style="background:#f9f9f9; padding:0px 2px 0px 0px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">
                <a href="/wiki/Close_front_rounded_vowel" title="Close front rounded vowel">y</a>
            </span>
        </span>
    </span>
</div>
<div style="position:absolute; top:4px; left:128px; width:60px; height:1px; background:transparent;">
    <span style="position:absolute; left:20px; width:20px;">
        <span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span>
        </span>
    </span>
    <span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;">
        <span style="background:#f9f9f9; padding:0px 1px 0px 2px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">
                <a href="/wiki/Close_central_unrounded_vowel" title="Close central unrounded vowel">ɨ</a>
            </span>
        </span>
    </span>
    <span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;">
        <span style="background:#f9f9f9; padding:0px 2px 0px 0px;">
            <span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">
                <a href="/wiki/Close_central_rounded_vowel" title="Close central rounded vowel">ʉ</a>
            </span>
        </span>
    </span>
</div>
<div style="position:absolute; top:4px; left:256px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close_back_unrounded_vowel" title="Close back unrounded vowel">ɯ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close_back_rounded_vowel" title="Close back rounded vowel">u</a></span></span></span></div>
<div style="position:absolute; top:35px; left:77px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-close_near-front_unrounded_vowel" title="Near-close near-front unrounded vowel">ɪ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-close_near-front_rounded_vowel" title="Near-close near-front rounded vowel">ʏ</a></span></span></span></div>
<div style="position:absolute; top:35px; left:138px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-close_central_unrounded_vowel" title="Near-close central unrounded vowel">ɪ̈</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-close_central_rounded_vowel" title="Near-close central rounded vowel">ʊ̈</a></span></span></span></div>
<div style="position:absolute; top:35px; left:201px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-close_near-back_vowel" title="Near-close near-back vowel">ʊ</a></span></span></span></div>
<div style="position:absolute; top:68px; left:43px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_front_unrounded_vowel" title="Close-mid front unrounded vowel">e</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_front_rounded_vowel" title="Close-mid front rounded vowel">ø</a></span></span></span></div>
<div style="position:absolute; top:68px; left:150px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_central_unrounded_vowel" title="Close-mid central unrounded vowel">ɘ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_central_rounded_vowel" title="Close-mid central rounded vowel">ɵ</a></span></span></span></div>
<div style="position:absolute; top:68px; left:256px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_back_unrounded_vowel" title="Close-mid back unrounded vowel">ɤ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Close-mid_back_rounded_vowel" title="Close-mid back rounded vowel">o</a></span></span></span></div>
<div style="position:absolute; top:98px; left:64px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Mid_front_unrounded_vowel" title="Mid front unrounded vowel">e̞</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Mid_front_rounded_vowel" title="Mid front rounded vowel">ø̞</a></span></span></span></div>
<div style="position:absolute; top:98px; left:160px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Mid-central_vowel" title="Mid-central vowel">ə</a></span></span></span></div>
<div style="position:absolute; top:98px; left:256px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Mid_back_unrounded_vowel" title="Mid back unrounded vowel">ɤ̞</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Mid_back_rounded_vowel" title="Mid back rounded vowel">o̞</a></span></span></span></div>
<div style="position:absolute; top:132px; left:85px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_front_unrounded_vowel" title="Open-mid front unrounded vowel">ɛ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_front_rounded_vowel" title="Open-mid front rounded vowel">œ</a></span></span></span></div>
<div style="position:absolute; top:132px; left:171px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_central_unrounded_vowel" title="Open-mid central unrounded vowel">ɜ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_central_rounded_vowel" title="Open-mid central rounded vowel">ɞ</a></span></span></span></div>
<div style="position:absolute; top:132px; left:256px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_back_unrounded_vowel" title="Open-mid back unrounded vowel">ʌ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open-mid_back_rounded_vowel" title="Open-mid back rounded vowel">ɔ</a></span></span></span></div>
<div style="position:absolute; top:166px; left:106px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-open_front_unrounded_vowel" title="Near-open front unrounded vowel">æ</a></span></span></span></div>
<div style="position:absolute; top:166px; left:185px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Near-open_central_vowel" title="Near-open central vowel">ɐ</a></span></span></span></div>
<div style="position:absolute; top:198px; left:128px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open_front_unrounded_vowel" title="Open front unrounded vowel">a</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open_front_rounded_vowel" title="Open front rounded vowel">ɶ</a></span></span></span></div>
<div style="position:absolute; top:198px; left:191px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open_central_unrounded_vowel" title="Open central unrounded vowel">ä</a></span></span></span></div>
<div style="position:absolute; top:198px; left:256px; width:60px; height:1px; background:transparent;"><span style="position:absolute; left:20px; width:20px;"><span style="text-align:center; background:#f9f9f9; padding:0px 2px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA">•</span></span></span><span style="position:absolute; left:0px; width:25px; text-align:right; background:transparent;"><span style="background:#f9f9f9; padding:0px 1px 0px 2px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open_back_unrounded_vowel" title="Open back unrounded vowel">ɑ</a></span></span></span><span style="position:absolute; left:35px; width:25px; text-align:left; background:transparent;"><span style="background:#f9f9f9; padding:0px 2px 0px 0px;"><span title="Representation in the International Phonetic Alphabet (IPA)" class="IPA"><a href="/wiki/Open_back_rounded_vowel" title="Open back rounded vowel">ɒ</a></span></span></span></div>
</td>
</tr>
</tbody></table>
</div>
</div>
</td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Near-close_vowel" title="Near-close vowel">Near-close</a></td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Close-mid_vowel" title="Close-mid vowel">Close-mid</a></td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Mid_vowel" title="Mid vowel"><b>Mid</b></a></td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Open-mid_vowel" title="Open-mid vowel">Open-mid</a></td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Near-open_vowel" title="Near-open vowel">Near-open</a></td>
</tr>
<tr>
<td style="height:32px; text-align:right;"><a href="/wiki/Open_vowel" title="Open vowel"><b>Open</b></a></td>
</tr>
</tbody></table>



            <dl>
                % for v in [_v for _v in ctx.valuesets if _v.parameter.feature_type == 'segment' and _v.values and _v.parameter.jsondata['vowel']]:
                    % if v.values[0].domainelement.name.lower() != 'does not exist':
                <dt>${h.link(request, v.parameter)}</dt>
                <dd>${v.values[0].domainelement.name}</dd>
                    % endif
                % endfor
            </dl>
        </div>
    </div>
</div>


<%def name="sidebar()">
    <%util:well title="${_('Contributors')}">
    <dl>
        <dt>${_('Contributors')}:</dt>
        <dd>
            ${h.linked_contributors(request, ctx)}
            ${h.button('cite', onclick=h.JSModal.show(ctx.name, request.resource_url(ctx, ext='md.html')))}
        </dd>
    </dl>
    </%util:well>
    <%util:well>
        ${request.map.render()}
    </%util:well>
    <%util:well title="${_('References')}">
    <dl>
        % for ref in ctx.references:
        <dt>${h.link(request, ref.source)}</dt>
        <dd>${ref.source.description}</dd>
        % endfor
    </dl>
    </%util:well>
</%def>
