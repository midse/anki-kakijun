# Copyright 2020 Dimitri Ségard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw

config = mw.addonManager.getConfig(__name__)


def is_kanji(v):
    v = ord(v)
    return (
        (v >= 0x4E00 and v <= 0x9FC3)
        or (v >= 0x3400 and v <= 0x4DBF)
        or (v >= 0xF900 and v <= 0xFAD9)
        or (v >= 0x2E80 and v <= 0x2EFF)
        or (v >= 0x20000 and v <= 0x2A6DF)
    )


# Returns the unicode of a character in a unicode string, taking surrogate pairs into account
def realord(s, pos=0):
    if s is None:
        return None
    code = ord(s[pos])
    if code >= 0xD800 and code < 0xDC00:
        if len(s) <= pos + 1:
            print("realord warning: missing surrogate character")
            return 0
        code2 = ord(s[pos + 1])
        if code2 >= 0xDC00 and code < 0xE000:
            code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
    return hex(code).replace("x", "")


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


def svg_insert(field_text):
    template = """
    <div id="tooltip-{svg_id}" class="tooltip">
        <span onmouseover="animate_strokes('{svg_id}');">
        {kanji}
        </span>
        <div id="bottom-{svg_id}" class="bottom">
            <svg id="{svg_id}"></svg>
        </div>
    </div>"""

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

        svg_id = f"svg{i}"

        load_svg.append((svg_id, ret))
        output += template.format(svg_id=svg_id, kanji=item, kanji_id=ret)

    output += "<script>\n"
    output += "\n".join(
        [
            "loadSvg('{svg_id}', '{url}/{kanji_id}{svg_suffix}');".format(
                svg_id=c[0],
                kanji_id=c[1],
                url=config["url"],
                svg_suffix=config["svg_suffix"],
            )
            for c in load_svg
        ]
    )
    output += "</script>"

    return output


def on_card_render(output, context):
    output.question_text = headers + output.question_text
    output.answer_text = headers + output.answer_text


hooks.card_did_render.append(on_card_render)


def on_field_filter(text, field, filter, context: TemplateRenderContext):
    if filter != config["filter_name"]:
        return text

    try:
        return svg_insert(context.fields()[field])
    except KeyError:
        return text


hooks.field_filter.append(on_field_filter)
