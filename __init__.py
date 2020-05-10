from anki import hooks
from anki.template import TemplateRenderContext
from aqt import dialogs, gui_hooks, mw
from aqt.browser import PreviewDialog
from aqt.clayout import CardLayout
from aqt.qt import Qt
from aqt.reviewer import Reviewer

# Responding to clicks
############################
from aqt.utils import tooltip

def is_kanji(v):
    v = ord(v)
    return (v >= 0x4E00 and v <= 0x9FC3) or (v >= 0x3400 and v <= 0x4DBF) or (v >= 0xF900 and v <= 0xFAD9) or (v >= 0x2E80 and v <= 0x2EFF) or (v >= 0x20000 and v <= 0x2A6DF)

# Returns the unicode of a character in a unicode string, taking surrogate pairs into account
def realord(s, pos = 0):
    if s == None:
        return None
    code = ord(s[pos])
    if code >= 0xD800 and code < 0xDC00:
        if (len(s) <= pos + 1):
            print("realord warning: missing surrogate character")
            return 0
        code2 = ord(s[pos + 1])
        if code2 >= 0xDC00 and code < 0xE000:
            code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00) 
    return hex(code).replace('x', '')

headers = """
<style>
.tooltip {
    display:inline-block;
    position:relative;
    border-bottom:1px dotted #666;
    text-align:left;
    cursor: pointer;
}

.tooltip .bottom {
    min-width:100px;
    /*max-width:400px;*/

    left:50%;
    transform:translate(-50%, 0);
    padding:20px;
    color:#666666;
    background-color:#EEEEEE;
    font-weight:normal;
    font-size:13px;
    border-radius:8px;
    position:absolute;
    z-index:99999999;
    box-sizing:border-box;
    box-shadow:0 1px 8px rgba(0,0,0,0.5);
    display:none;
}

.tooltip:hover .bottom {
    display:block;
}

.tooltip .bottom svg {
    width:100px;
    height:100px;
}

</style>
<script type="text/javascript">
     function animate_stroke(selector, stroke) {
        var svg, cls, stroke, els, selector, factor, duration, new_duration;
        svg = document.getElementById(selector).children[0];
    
        /* cleanup all classes and durations, if necessary */
        var dataStrokeElements = svg.querySelectorAll('[data-stroke]');

        dataStrokeElements.forEach(function (item, index) {
            item.classList.remove('animate', 'current', 'brush', 'backward');
            item.style.animationDuration = '';
        });
  
        /* add classes to animating elaments */
        selector = '[data-stroke="' + stroke + '"]';
        var dataStrokeElements = svg.querySelectorAll(selector);

        dataStrokeElements.forEach(function (item, index) {
            item.classList.add('current', 'animate', 'brush');
            item.style.animationDuration = '1s';
        });

    }
    
    function kill_animation_timeout() {
        if(window.animator_timeout) {
            clearTimeout(window.animator_timeout);
            delete window.animator_timeout;
        }
    }

   
    function animate_strokes(selector) {
        var svg = document.getElementById(selector).children[0];
        var num_strokes = svg.getAttribute('data-num-strokes');

        kill_animation_timeout();
  
        /* setup the animating function */
        animator_loop = function(stroke) {
            var next_stroke, duration;
    
            next_stroke = stroke % num_strokes + 1;
            duration = animate_stroke(selector, stroke);
    
            window.animator_timeout = setTimeout(function(){
                animator_loop(next_stroke); 
            }, 1000);
        }
        
        /* start the animation */
        animator_loop(1);
    }

    function loadSvg(selector, url) {
        var target = document.getElementById(selector);

        fetch(url).then(function (response) {
            response.text().then(function (text) {
                target.innerHTML = text;
            });
        }).catch(function (err) {
            alert(err);
        });

     }
</script>
"""

template = """
<div id="tooltip-{svg_id}" class="tooltip">
    <span onmouseover="animate_strokes('{svg_id}');">
    {kanji}
    </span>
    <div id="bottom-{svg_id}" class="bottom">
        <svg id="{svg_id}"></svg>
    </div>
</div>"""

def svg_insert(field_text):
    output = ""
    load_svg = []
    for i, item in enumerate(field_text):
        if not is_kanji(item):
            output += item
            continue

        ret = realord(item)
        if ret == 0:
            output += item
            continue
        
        svg_id=f"svg{i}"

        load_svg.append((svg_id, ret))
        output += template.format(svg_id=svg_id, kanji=item, kanji_id=ret)

    output +="<script>\n"
    output += '\n'.join([
"loadSvg('{svg_id}', 'http://127.0.0.1:8001/kanimaji/converted/js_svg/{kanji_id}_js_anim.svg');".format(svg_id=c[0], kanji_id=c[1])
for c in load_svg])
    output += '</script>'
    
    return output

def on_card_render(output, context):
    output.question_text += headers
    output.answer_text += headers

    try:
        output.answer_text += svg_insert(context.fields()["Notes-Kanjified-vocab"])
    except KeyError:
        pass

hooks.card_did_render.append(on_card_render)

# def on_field_filter(field_text: str, field_name: str, filter_name: str, context: TemplateRenderContext
# ) -> str:

#     if field_name != "Notes-Kanjified-vocab":
#         return field_text


            

# hooks.field_filter.append(on_field_filter)
