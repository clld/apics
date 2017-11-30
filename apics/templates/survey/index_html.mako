<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "surveys" %>
<%block name="title">Surveys</%block>

<h2>Surveys</h2>

${ctx.render()}
