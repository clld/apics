<%inherit file="home_comp.mako"/>

<h2>Introduction</h2>

${html|n}

<script>
    $(document).ready(function(){
        $('.ref-link').clickover({
            html: true,
            content: function() {
                var content = $(this).data('content');
                var $content = $('#ref-' + content);
                return $content.length > 0 ? $content.html() : '';
            }
        });
    });
</script>
