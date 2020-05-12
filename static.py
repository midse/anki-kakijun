css = """
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
"""


def js(drawing_speed, time_between_strokes):
    js_content = (
        """
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
        item.style.animationDuration = '"""
        + str(drawing_speed)
        + """s';
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
        }, """
        + str(time_between_strokes)
        + """);
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
        console.log(err);
    });
}
"""
    )
    return js_content
