import asyncio
import orjson
from datetime import datetime
from random import choices
from typing import Literal, Union
from numpy import isin
import pandas as pd
import re
from matplotlib.colors import to_rgba

# # Predefined colors that stand out well on dark backgrounds
# COLORS = [
#     'rgba(255, 0, 0, 0.6)',      # Red
#     'rgba(0, 255, 0, 0.6)',      # Green
#     'rgba(0, 0, 255, 0.6)',      # Blue
#     'rgba(255, 255, 0, 0.6)',    # Yellow
#     'rgba(255, 165, 0, 0.6)',    # Orange
#     'rgba(75, 0, 130, 0.6)',     # Indigo
#     'rgba(238, 130, 238, 0.6)',  # Violet
#     'rgba(0, 255, 255, 0.6)',    # Cyan
#     'rgba(255, 192, 203, 0.6)',  # Pink
#     'rgba(0, 128, 128, 0.6)',    # Teal
#     'rgba(128, 0, 128, 0.6)',    # Purple
#     'rgba(255, 215, 0, 0.6)',    # Gold
#     'rgba(173, 255, 47, 0.6)',   # Green Yellow
# ]

# def get_next_color():
#     return random.choice(COLORS)

# Predefined pool of colors
COLORS = [
    "#63AA57", "#8F8AB0", "#E24AEE", "#D06AA6", "#7891BA", "#A39A34", "#8A94A2", "#61BB2F",
    "#FD569D", "#1EB6E1", "#379AC9", "#FD6F2E", "#8C9858", "#39A4A3", "#6D97F4", "#1ECB01", "#FA5B16", "#A6891C",
    "#48CF10", "#D27B26", "#D56B55", "#FE3AB8", "#E35C51", "#EC4FE6", "#E250A3", "#BA618E", "#1BC074", "#C57784",
    "#888BC5", "#4FA452", "#80885C", "#B97272", "#33BF98", "#B7961D", "#A07284", "#02E54E", "#AF7F35", "#F852EF",
    "#6D955B", "#E0676E", "#F73DEC", "#CE53FD", "#9773D3", "#649E81", "#D062CE", "#AB73E7", "#A4729C", "#E76A07",
    "#E85CCB", "#A16FB1", "#4BB859", "#B25EE2", "#8580CE", "#A275EF", "#AC9245", "#4D988D", "#B672C9", "#4CA96E",
    "#C9873E", "#5BB147", "#10C783", "#D7647D", "#CB893A", "#A586BA", "#28C0A2", "#61A755", "#0EB7C5", "#2DADBC",
    "#17BB71", "#2BC733", "#2BB890", "#F04EF8", "#699580", "#A88809", "#EB3FF6", "#A75ED3", "#859171", "#BB6285",
    "#81A147", "#AD7CD2", "#65B630", "#C9616C", "#BD5EFA", "#7A9F30", "#2AB6AB", "#FC496A", "#687FC7", "#DB40E7",
    "#07BCE9", "#509F63", "#EC4FDD", "#A079BE", "#C17297", "#E447C2", "#E95AD9", "#9FA01E", "#7E86CF", "#21E316",
    "#1CABF9", "#17C24F", "#9C9254", "#C97994", "#4BA9DA", "#0DD595", "#13BEA8", "#C2855D", "#DF6C13", "#60B370",
    "#0FC3F6", "#C1830E", "#3AC917", "#0EBBB0", "#CC50B4", "#B768EC", "#D47F49", "#B47BC5", "#38ADBD", "#05DC53",
    "#44CD4E", "#838E65", "#49D70F", "#2DADBE", "#2CB0C9", "#DA703E", "#06B5CA", "#7BAF3E", "#918E79", "#2AA5E5",
    "#C37F5E", "#07B8C9", "#4CBA27", "#E752C6", "#7F93B2", "#4798CD", "#45AA4C", "#4DB666", "#7683A7", "#758685",
    "#4B9FAD", "#9280FD", "#6682DD", "#42ACBE", "#C1609F", "#D850DB", "#649A62", "#54CC22", "#AD81C1", "#BF7A43",
    "#0FCEA5", "#D06DAF", "#87799B", "#4DA94E", "#2FD654", "#07D587", "#21CF0C", "#03CF34", "#42C771", "#D563CD",
    "#6D9E9A", "#C76C59", "#68B368", "#11BCE5", "#0DCFB3", "#9266D8", "#BF67F6", "#88A04E", "#73BE17", "#67B437",
    "#8586E4", "#9F8749", "#479CA5", "#CC777E", "#4FAF46", "#9D9836", "#918DAF", "#D167B8", "#6F9DA5", "#2BB167",
    "#16B8BC", "#B4861F", "#A08487", "#67B357", "#5CAA5C", "#20CA49", "#D18813", "#15D63F", "#C8618F", "#887E92",
    "#21C457", "#4EA8CE", "#53BE49", "#5A86D5", "#BD7E4E", "#27B0A1", "#33CF42", "#709083", "#38A8DE", "#4CA762",
    "#1EA4FF", "#DE3EE4", "#70A860", "#39A3C8", "#6BBB39", "#F053F4", "#8C7FB5", "#969F21", "#B19841", "#E57148",
    "#C25DA7", "#6DA979", "#B27D73", "#7F9786", "#41AC99", "#C58848", "#948F9E", "#6BB620", "#81AB3B", "#09DE44",
    "#43A9D2", "#41B0D7", "#20ACAA", "#649FCB", "#CD8345", "#A88669", "#3EA5E7", "#F36A19", "#E06B48", "#8388BD",
    "#EC6153", "#639082", "#52CA32", "#878BAA", "#02BCDB", "#828FD9", "#3DC07F", "#29D46A", "#9C7CC1", "#EB7713",
    "#F95F6A", "#E25F4C", "#589994", "#D45AB7", "#DE66AB", "#B8715F", "#E850F4", "#FB6420", "#C2832C", "#6383C5",
    "#D57A58", "#EF652C", "#02D71A", "#ED664D", "#60A526"
]

# Iterator to keep track of the current color index
color_index = 0

def get_next_color():
    global color_index
    # Get the next color from the list
    color = COLORS[color_index]
    # Convert the color from HEX to RGBA format
    color_index = (color_index + 1) % len(COLORS)
    return hex_to_rgba(color)

def hex_to_rgba(hex_color, alpha=0.5):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'

def apply_opacity(color, opacity):
    """
    Converts any color format (named, hex, RGB, or RGBA) to RGBA format and applies a specified opacity.

    Parameters:
    - color (str): The color in named, hex, RGB, or RGBA format.
    - opacity (float): The opacity value to apply, ranging from 0.0 to 1.0.

    Returns:
    - str: The color in 'rgba(r, g, b, opacity)' format with the specified opacity applied.

    Raises:
    - ValueError: If the opacity is not within the range of 0 to 1.
    """
    # Validate the opacity
    if not (0 <= opacity <= 1):
        raise ValueError("Opacity must be between 0 and 1")

    # Check if color is already in rgba format
    rgba_regex = r'rgba?\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})(?:,\s*([0-9\.]+))?\)'
    match = re.match(rgba_regex, color)

    if match:
        # Color is in RGB or RGBA format
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        current_opacity = float(match.group(4)) if match.group(4) else 1
        # Apply the new opacity by multiplying with the current opacity if it exists
        final_opacity = current_opacity * opacity
    else:
        # Color is a named color or hex; convert it using matplotlib
        rgba = to_rgba(color)
        r, g, b, _ = [int(255 * x) for x in rgba]
        final_opacity = opacity  # Directly use the given opacity
    return f"rgba({r}, {g}, {b}, {final_opacity})"

def is_vbt_indicator(variable):
    # Get the module path of the variable's type
    module_path = variable.__class__.__module__
    # Check if it starts with 'vectorbtpro.indicators'
    return module_path.startswith('vectorbtpro.indicators')

class Pane:
    def __init__(self, window):
        from lightweight_charts import Window
        self.win: Window = window
        self.run_script = window.run_script
        self.bulk_run = window.bulk_run
        if hasattr(self, 'id'):
            return
        self.id = Window._id_gen.generate()


class IDGen(list):
    ascii = 'abcdefghijklmnopqrstuvwxyz'

    def generate(self) -> str:
        var = ''.join(choices(self.ascii, k=8))
        if var not in self:
            self.append(var)
            return f'window.{var}'
        self.generate()


def parse_event_message(window, string):
    name, args = string.split('_~_')
    args = args.split(';;;')
    func = window.handlers[name]
    return func, args


# def js_data(data: Union[pd.DataFrame, pd.Series]):
#     if isinstance(data, pd.DataFrame):
#         d = data.to_dict(orient='records')
#         filtered_records = [{k: v for k, v in record.items() if v is not None and not pd.isna(v)} for record in d]
#     else:
#         d = data.to_dict()
#         filtered_records = {k: v for k, v in d.items()}
#     return json.dumps(filtered_records)

def js_data(data: Union[pd.DataFrame, pd.Series]):
    if isinstance(data, pd.DataFrame):
        # Converting DataFrame to a list of dictionaries, filtering out NaN values
        filtered_records = data.dropna().to_dict(orient='records')
    else:
        # For pd.Series, convert to dict and drop NaN values
        filtered_records = data.dropna().to_dict()

    # Serialize using orjson, which returns bytes
    # Decode bytes to string if necessary (JavaScript consumption requires string)
    return orjson.dumps(filtered_records).decode('utf-8')

def snake_to_camel(s: str):
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

# def js_json(d: dict):
#     filtered_dict = {}
#     for key, val in d.items():
#         if key in ('self') or val in (None,):
#             continue
#         if '_' in key:
#             key = snake_to_camel(key)
#         filtered_dict[key] = val
#     return f"JSON.parse('{json.dumps(filtered_dict)}')"

def js_json(d: dict):
    filtered_dict = {}
    for key, val in d.items():
        if key == 'self' or val in (None,):
            continue
        if '_' in key:
            key = snake_to_camel(key)
        filtered_dict[key] = val

    # Serialize the dictionary using orjson, automatically handling types that orjson can serialize
    # Decode the bytes to string for use in JavaScript, escaping single quotes for JavaScript consumption
    json_str = orjson.dumps(filtered_dict).decode('utf-8').replace("'", "\\'")
    return f"JSON.parse('{json_str}')"

def jbool(b: bool): return 'true' if b is True else 'false' if b is False else None

MARKER_TYPE = Literal['entries', 'exits']

LINE_STYLE = Literal['solid', 'dotted', 'dashed', 'large_dashed', 'sparse_dotted']

MARKER_POSITION = Literal['above', 'below', 'inside']

MARKER_SHAPE = Literal['arrow_up', 'arrow_down', 'circle', 'square']

CROSSHAIR_MODE = Literal['normal', 'magnet', 'hidden']

PRICE_SCALE_MODE = Literal['normal', 'logarithmic', 'percentage', 'index100']

TIME = Union[datetime, pd.Timestamp, str, float]

NUM = Union[float, int]

FLOAT = Literal['left', 'right', 'top', 'bottom']


def as_enum(value, string_types):
    types = string_types.__args__
    return -1 if value not in types else types.index(value)


def marker_shape(shape: MARKER_SHAPE):
    return {
        'arrow_up': 'arrowUp',
        'arrow_down': 'arrowDown',
    }.get(shape) or shape


def marker_position(p: MARKER_POSITION):
    return {
        'above': 'aboveBar',
        'below': 'belowBar',
        'inside': 'inBar',
    }.get(p)


class Emitter:
    def __init__(self):
        self._callable = None

    def __iadd__(self, other):
        self._callable = other
        return self

    def _emit(self, *args):
        if self._callable:
            if asyncio.iscoroutinefunction(self._callable):
                asyncio.create_task(self._callable(*args))
            else:
                self._callable(*args)


class JSEmitter:
    def __init__(self, chart, name, on_iadd, wrapper=None):
        self._on_iadd = on_iadd
        self._chart = chart
        self._name = name
        self._wrapper = wrapper

    def __iadd__(self, other):
        def final_wrapper(*arg):
            other(self._chart, *arg) if not self._wrapper else self._wrapper(other, self._chart, *arg)
        async def final_async_wrapper(*arg):
            await other(self._chart, *arg) if not self._wrapper else await self._wrapper(other, self._chart, *arg)

        self._chart.win.handlers[self._name] = final_async_wrapper if asyncio.iscoroutinefunction(other) else final_wrapper
        self._on_iadd(other)
        return self


class Events:
    def __init__(self, chart):
        self.new_bar = Emitter()
        self.search = JSEmitter(chart, f'search{chart.id}',
            lambda o: chart.run_script(f'''
            Lib.Handler.makeSpinner({chart.id})
            {chart.id}.search = Lib.Handler.makeSearchBox({chart.id})
            ''')
        )
        salt = chart.id[chart.id.index('.')+1:]
        self.range_change = JSEmitter(chart, f'range_change{salt}',
            lambda o: chart.run_script(f'''
            let checkLogicalRange{salt} = (logical) => {{
                {chart.id}.chart.timeScale().unsubscribeVisibleLogicalRangeChange(checkLogicalRange{salt})
                
                let barsInfo = {chart.id}.series.barsInLogicalRange(logical)
                if (barsInfo) window.callbackFunction(`range_change{salt}_~_${{barsInfo.barsBefore}};;;${{barsInfo.barsAfter}}`)
                    
                setTimeout(() => {chart.id}.chart.timeScale().subscribeVisibleLogicalRangeChange(checkLogicalRange{salt}), 50)
            }}
            {chart.id}.chart.timeScale().subscribeVisibleLogicalRangeChange(checkLogicalRange{salt})
            '''),
            wrapper=lambda o, c, *arg: o(c, *[float(a) for a in arg])
        )

        self.click = JSEmitter(chart, f'subscribe_click{salt}',
            lambda o: chart.run_script(f'''
            let clickHandler{salt} = (param) => {{
                if (!param.point) return;
                const time = {chart.id}.chart.timeScale().coordinateToTime(param.point.x)
                const price = {chart.id}.series.coordinateToPrice(param.point.y);
                window.callbackFunction(`subscribe_click{salt}_~_${{time}};;;${{price}}`)
            }}
            {chart.id}.chart.subscribeClick(clickHandler{salt})
            '''),
            wrapper=lambda func, c, *args: func(c, *[float(a) for a in args])
        )

class BulkRunScript:
    def __init__(self, script_func):
        self.enabled = False
        self.scripts = []
        self.script_func = script_func

    def __enter__(self):
        self.enabled = True

    def __exit__(self, *args):
        self.enabled = False
        self.script_func('\n'.join(self.scripts))
        self.scripts = []

    def add_script(self, script):
        self.scripts.append(script)
