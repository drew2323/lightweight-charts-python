import asyncio
import json
import os
from base64 import b64decode
from datetime import datetime
from typing import Callable, Union, Literal, List, Optional
import pandas as pd
import random
#from vectorbtpro.indicators import IndicatorFactory 
from .table import Table
from .toolbox import ToolBox
from .drawings import Box, HorizontalLine, RayLine, TrendLine, TwoPointDrawing, VerticalLine, VerticalSpan
from .topbar import TopBar
from .util import (
    BulkRunScript, Pane, Events, IDGen, as_enum, jbool, js_json, TIME, NUM, FLOAT,
    LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, CROSSHAIR_MODE, MARKER_TYPE,
    PRICE_SCALE_MODE, marker_position, marker_shape, js_data, is_vbt_indicator, apply_opacity
)

current_dir = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(current_dir, 'js', 'index.html')

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

class Window:
    _id_gen = IDGen()
    handlers = {}

    def __init__(
        self,
        script_func: Optional[Callable] = None,
        js_api_code: Optional[str] = None,
        run_script: Optional[Callable] = None
    ):
        self.loaded = False
        self.script_func = script_func
        self.scripts = []
        self.final_scripts = []
        self.bulk_run = BulkRunScript(script_func)

        if run_script:
            self.run_script = run_script

        if js_api_code:
            self.run_script(f'window.callbackFunction = {js_api_code}')

    def on_js_load(self):
        if self.loaded:
            return
        self.loaded = True

        if hasattr(self, '_return_q'):
            while not self.run_script_and_get('document.readyState == "complete"'):
                continue    # scary, but works

        initial_script = ''
        self.scripts.extend(self.final_scripts)
        for script in self.scripts:
            initial_script += f'\n{script}'
        self.script_func(initial_script)

    def run_script(self, script: str, run_last: bool = False):
        """
        For advanced users; evaluates JavaScript within the Webview.
        """
        if self.script_func is None:
            raise AttributeError("script_func has not been set")
        if self.loaded:
            if self.bulk_run.enabled:
                self.bulk_run.add_script(script)
            else:
                self.script_func(script)
        elif run_last:
            self.final_scripts.append(script)
        else:
            self.scripts.append(script)

    def run_script_and_get(self, script: str):
        self.run_script(f'_~_~RETURN~_~_{script}')
        return self._return_q.get()

    def create_table(
        self,
        width: NUM,
        height: NUM,
        headings: tuple,
        widths: Optional[tuple] = None,
        alignments: Optional[tuple] = None,
        position: FLOAT = 'left',
        draggable: bool = False,
        background_color: str = '#121417',
        border_color: str = 'rgb(70, 70, 70)',
        border_width: int = 1,
        heading_text_colors: Optional[tuple] = None,
        heading_background_colors: Optional[tuple] = None,
        return_clicked_cells: bool = False,
        func: Optional[Callable] = None
    ) -> 'Table':
        return Table(*locals().values())

    def create_subchart(
        self,
        position: FLOAT = 'left',
        width: float = 0.5,
        height: float = 0.5,
        sync_id: Optional[str] = None,
        scale_candles_only: bool = False,
        sync_crosshairs_only: bool = False,
        toolbox: bool = False,
        leftScale: bool = False
    ) -> 'AbstractChart':
        subchart = AbstractChart(
            self,
            width,
            height,
            scale_candles_only,
            toolbox,
            position=position,
            leftScale=leftScale
        )
        if not sync_id:
            return subchart
        self.run_script(f'''
            Lib.Handler.syncCharts(
                {subchart.id},
                {sync_id},
                {jbool(sync_crosshairs_only)}
            )
        ''', run_last=True)
        return subchart

    def style(
        self,
        background_color: str = '#0c0d0f',
        hover_background_color: str = '#3c434c',
        click_background_color: str = '#50565E',
        active_background_color: str = 'rgba(0, 122, 255, 0.7)',
        muted_background_color: str = 'rgba(0, 122, 255, 0.3)',
        border_color: str = '#3C434C',
        color: str = '#d8d9db',
        active_color: str = '#ececed'
    ):
        self.run_script(f'Lib.Handler.setRootStyles({js_json(locals())});')


class SeriesCommon(Pane):
    def __init__(self, chart: 'AbstractChart', name: str = ''):
        super().__init__(chart.win)
        self._chart = chart
        if hasattr(chart, '_interval'):
            self._interval = chart._interval
        else:
            self._interval = 1
        self._last_bar = None
        self.name = name
        self.num_decimals = 2
        self.offset = 0
        self.data = pd.DataFrame()
        self.markers = {}

    def _set_interval(self, df: pd.DataFrame):
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        common_interval = df['time'].diff().value_counts()
        if common_interval.empty:
            return
        self._interval = common_interval.index[0].total_seconds()

        units = [
            pd.Timedelta(microseconds=df['time'].dt.microsecond.value_counts().index[0]),
            pd.Timedelta(seconds=df['time'].dt.second.value_counts().index[0]),
            pd.Timedelta(minutes=df['time'].dt.minute.value_counts().index[0]),
            pd.Timedelta(hours=df['time'].dt.hour.value_counts().index[0]),
            pd.Timedelta(days=df['time'].dt.day.value_counts().index[0]),
        ]
        self.offset = 0
        for value in units:
            value = value.total_seconds()
            if value == 0:
                continue
            elif value >= self._interval:
                break
            self.offset = value
            break

    @staticmethod
    def _format_labels(data, labels, index, exclude_lowercase):
        def rename(la, mapper):
            return [mapper[key] if key in mapper else key for key in la]
        if 'date' not in labels and 'time' not in labels:
            labels = labels.str.lower()
            if exclude_lowercase:
                labels = rename(labels, {exclude_lowercase.lower(): exclude_lowercase})
        if 'date' in labels:
            labels = rename(labels, {'date': 'time'})
        elif 'time' not in labels:
            data['time'] = index
            labels = [*labels, 'time']
        return labels

    def _df_datetime_format(self, df: pd.DataFrame, exclude_lowercase=None):
        df = df.copy()
        df.columns = self._format_labels(df, df.columns, df.index, exclude_lowercase)
        self._set_interval(df)
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        df['time'] = df['time'].astype('int64') / 10 ** 9 #removed integer divison // 10 ** 9 to keep subseconds precision

        # if 'updated' in df.columns:
        #     df['updated'] = pd.to_datetime(df['updated']).astype('int64') / 10**9

        # Iterate over all columns and convert any additional datetime columns to timestamps (for example updated)
        for col in df.columns:
            # Skip columns that are explicitly managed elsewhere or meant to be excluded
            if col == 'time' or not pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
            # Convert datetime to timestamp with nanosecond precision after the decimal
            df[col] = pd.to_datetime(df[col]).astype('int64') / 10**9

        return df

    def _series_datetime_format(self, series: pd.Series, exclude_lowercase=None):
        series = series.copy()
        series.index = self._format_labels(series, series.name, series.index, exclude_lowercase)
        series['time'] = self._single_datetime_format(series['time'])
        return series

    def _single_datetime_format(self, arg) -> float:
        if isinstance(arg, (str, int, float)) or not pd.api.types.is_datetime64_any_dtype(arg):
            try:
                arg = pd.to_datetime(arg, unit='ms')
            except ValueError:
                arg = pd.to_datetime(arg)
        arg = self._interval * (arg.timestamp() // self._interval)+self.offset
        return arg

    def set(self, df: Optional[Union[pd.DataFrame, pd.Series]] = None, format_cols: bool = True):
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            self.run_script(f'{self.id}.series.setData([])')
            self.data = pd.DataFrame()
            return
        if is_vbt_indicator(df):
            df = df.real
        #if df is pd.Series then convert to df
        if isinstance(df, pd.Series):
            df = df.to_frame(name=self.name)
        if format_cols:
            df = self._df_datetime_format(df, exclude_lowercase=self.name)
        if self.name:
            if self.name not in df:
                raise NameError(f'No column named "{self.name}".')
            df = df.rename(columns={self.name: 'value'})
        self.data = df.copy()
        self._last_bar = df.iloc[-1]
        self.run_script(f'{self.id}.series.setData({js_data(df)}); ')

    def update(self, series: pd.Series):
        series = self._series_datetime_format(series, exclude_lowercase=self.name)
        if self.name in series.index:
            series.rename({self.name: 'value'}, inplace=True)
        if self._last_bar is not None and series['time'] != self._last_bar['time']:
            self.data.loc[self.data.index[-1]] = self._last_bar
            self.data = pd.concat([self.data, series.to_frame().T], ignore_index=True)
        self._last_bar = series
        self.run_script(f'{self.id}.series.update({js_data(series)})')

    def _update_markers(self):
        self.run_script(f'{self.id}.series.setMarkers({json.dumps(list(self.markers.values()))})')

    def markers_set(self, markers: Union[pd.Series, pd.DataFrame],
                    type: MARKER_TYPE = None,
                    col_name: Optional[str] = None,
                    position: MARKER_POSITION = 'below',
                    shape: MARKER_SHAPE = 'arrow_up',
                    color: str = '#2196F3', text: str = ''):
        """
        Adds multiple markers from pd series or Dataframe
        :param markers: A pandas Series or Dataframe with DateTimeIndex and boolean values.
                        The index should be DateTimeIndex and values should be True/False.
        :param type: The type of the marker to quickly style entries or exits
        :param col_name: The name of the column to use in case of DataFrame
        :param position: The position of the marker.
        :param shape: The shape of the marker.
        :param color: The color of the marker.
        :return: a list of marker ids.

        It adds new markers to the chart. Existing markers will remain.
        To delete markers use remove_marker() or clear_markers()
        """
        if type is not None:
            match type:
                case "entries":
                    position = "below"
                    shape = "arrow_up"
                    color = "blue"
                case "exits":
                    position = "above"
                    shape = "arrow_down"
                    color = "red"
        
        if isinstance(markers, pd.Series):
            markers = markers.to_frame(name="markers")
        markers = self._df_datetime_format(markers)
    
        # Get the list of columns in the DataFrame - must be datetimeindex
        #either with one column, or col_name is set
        columns = markers.columns.tolist()

        if "time" not in columns:
            raise ValueError("Time column required in the dataframe.")
        
        # If there are exactly two columns
        if len(columns) == 2:
            # Rename the non-"time" column to "value"
            other_col = [col for col in columns if col != "time"][0]
            markers.rename(columns={other_col: "value"}, inplace=True)
        
        # If there are more than two columns
        elif len(columns) > 2:
            if col_name in columns:
                # Keep "time" and col_name column and rename it to "value"
                markers = markers[["time", col_name]]
                markers.rename(columns={col_name: "value"}, inplace=True)
            else:
                raise ValueError("Specify a column name in the dataframe.")
        else:
            raise ValueError("No matching columns in the dataframe.")
        
        marker_ids = []
        #self.markers = {}

        valid_rows = markers[markers['value']]  # Filter rows where value is True

        for timestamp in valid_rows['time']:
            marker_id = self.win._id_gen.generate()
            self.markers[marker_id] = {
                "time": timestamp,
                "position": marker_position(position),  # Default position
                "color": color,   # Default color
                "shape": marker_shape(shape),    # Default shape
                "text": text,           # Default text
            }
            marker_ids.append(marker_id)

        # Sort markers by time
        self.markers = dict(sorted(self.markers.items(), key=lambda item: item[1]["time"]))
        self._update_markers()
        return marker_ids


    def marker_list(self, markers: list):
        """
        Creates multiple markers.\n
        :param markers: The list of markers to set. These should be in the format:\n
        [
            {"time": "2021-01-21", "position": "below", "shape": "circle", "color": "#2196F3", "text": ""},
            {"time": "2021-01-22", "position": "below", "shape": "circle", "color": "#2196F3", "text": ""},
            ...
        ]
        :return: a list of marker ids.
        """
        markers = markers.copy()
        marker_ids = []
        for marker in markers:
            marker_id = self.win._id_gen.generate()
            self.markers[marker_id] = {
                "time": self._single_datetime_format(marker['time']),
                "position": marker_position(marker['position']),
                "color": marker['color'],
                "shape": marker_shape(marker['shape']),
                "text": marker['text'],
            }
            marker_ids.append(marker_id)
        self._update_markers()
        return marker_ids

    def marker(self, time: Optional[datetime] = None, position: MARKER_POSITION = 'below',
               shape: MARKER_SHAPE = 'arrow_up', color: str = '#2196F3', text: str = ''
               ) -> str:
        """
        Creates a new marker.\n
        :param time: Time location of the marker. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The id of the marker placed.
        """
        try:
            formatted_time = self._last_bar['time'] if not time else self._single_datetime_format(time)
        except TypeError:
            raise TypeError('Chart marker created before data was set.')
        marker_id = self.win._id_gen.generate()

        self.markers[marker_id] = {
            "time": formatted_time,
            "position": marker_position(position),
            "color": color,
            "shape": marker_shape(shape),
            "text": text,
        }
        self._update_markers()
        return marker_id

    def remove_marker(self, marker_id: str):
        """
        Removes the marker with the given id.\n
        """
        self.markers.pop(marker_id)
        self._update_markers()

    def horizontal_line(self, price: NUM, color: str = 'rgb(122, 146, 202)', width: int = 2,
                        style: LINE_STYLE = 'solid', text: str = '', axis_label_visible: bool = True,
                        func: Optional[Callable] = None
                        ) -> 'HorizontalLine':
        """
        Creates a horizontal line at the given price.
        """
        return HorizontalLine(self, price, color, width, style, text, axis_label_visible, func)

    def trend_line(
        self,
        start_time: TIME,
        start_value: NUM,
        end_time: TIME,
        end_value: NUM,
        round: bool = False,
        line_color: str = '#1E80F0',
        width: int = 2,
        style: LINE_STYLE = 'solid',
    ) -> TwoPointDrawing:
        return TrendLine(*locals().values())

    def box(
        self,
        start_time: TIME,
        start_value: NUM,
        end_time: TIME,
        end_value: NUM,
        round: bool = False,
        color: str = '#1E80F0',
        fill_color: str = 'rgba(255, 255, 255, 0.2)',
        width: int = 2,
        style: LINE_STYLE = 'solid',
    ) -> TwoPointDrawing:
        return Box(*locals().values())

    def ray_line(
        self,
        start_time: TIME,
        value: NUM,
        round: bool = False,
        color: str = '#1E80F0',
        width: int = 2,
        style: LINE_STYLE = 'solid',
        text: str = ''
    ) -> RayLine:
    # TODO
        return RayLine(*locals().values())

    def vertical_line(
        self,
        time: TIME,
        color: str = '#1E80F0',
        width: int = 2,
        style: LINE_STYLE ='solid',
        text: str = ''
    ) -> VerticalLine:
        return VerticalLine(*locals().values())

    def clear_markers(self):
        """
        Clears the markers displayed on the data.\n
        """
        self.markers.clear()
        self._update_markers()

    def price_line(self, label_visible: bool = True, line_visible: bool = True, title: str = ''):
        self.run_script(f'''
        {self.id}.series.applyOptions({{
            lastValueVisible: {jbool(label_visible)},
            priceLineVisible: {jbool(line_visible)},
            title: '{title}',
        }})''')

    def precision(self, precision: int):
        """
        Sets the precision and minMove.\n
        :param precision: The number of decimal places.
        """
        min_move = 1 / (10**precision)
        self.run_script(f'''
        {self.id}.series.applyOptions({{
            priceFormat: {{precision: {precision}, minMove: {min_move}}}
        }})''')
        self.num_decimals = precision

    def hide_data(self):
        self._toggle_data(False)

    def show_data(self):
        self._toggle_data(True)

    def _toggle_data(self, arg):
        self.run_script(f'''
        {self.id}.series.applyOptions({{visible: {jbool(arg)}}})
        if ('volumeSeries' in {self.id}) {self.id}.volumeSeries.applyOptions({{visible: {jbool(arg)}}})
        ''')

    def vertical_span(
        self,
        start_time: Union[TIME, tuple, list],
        end_time: Optional[TIME] = None,
        color: str = 'rgba(252, 219, 3, 0.2)',
        round: bool = False
    ):
        """
        Creates a vertical line or span across the chart.\n
        Start time and end time can be used together, or end_time can be
        omitted and a single time or a list of times can be passed to start_time.
        """
        if round:
            start_time = self._single_datetime_format(start_time)
            end_time = self._single_datetime_format(end_time) if end_time else None
        return VerticalSpan(self, start_time, end_time, color)


class Line(SeriesCommon):
    def __init__(self, chart, name, color, style, width, price_line, price_label, crosshair_marker=True, priceScaleId="right"):

        super().__init__(chart, name)
        self.color = color

        #priceScaleId_line = f"priceScaleId: '{priceScaleId}'," if priceScaleId is not None else ''

        script = f'''
            {self.id} = {self._chart.id}.createLineSeries(
                "{name}",
                {{
                    color: '{color}',
                    lineStyle: {as_enum(style, LINE_STYLE)},
                    lineWidth: {width},
                    lastValueVisible: {jbool(price_label)},
                    priceScaleId: '{priceScaleId}',
                    priceLineVisible: {jbool(price_line)},
                    crosshairMarkerVisible: {jbool(crosshair_marker)},
                    {"""autoscaleInfoProvider: () => ({
                            priceRange: {
                                minValue: 1_000_000_000,
                                maxValue: 0,
                            },
                        }),
                    """ if chart._scale_candles_only else ''}
                }}
            )
        null'''

        #print(script)

        self.run_script(script)

    # def _set_trend(self, start_time, start_value, end_time, end_value, ray=False, round=False):
    #     if round:
    #         start_time = self._single_datetime_format(start_time)
    #         end_time = self._single_datetime_format(end_time)
    #     else:
    #         start_time, end_time = pd.to_datetime((start_time, end_time)).astype('int64') // 10 ** 9

    #     self.run_script(f'''
    #     {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: false}})
    #     {self.id}.series.setData(
    #         calculateTrendLine({start_time}, {start_value}, {end_time}, {end_value},
    #                             {self._chart.id}, {jbool(ray)}))
    #     {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: true}})
    #     ''')

    def scale(self, scale_margin_top: float = 0.0, scale_margin_bottom: float = 0.0):
        self.run_script(f'''
        {self.id}.series.priceScale().applyOptions({{
            scaleMargins: {{top: {scale_margin_top}, bottom: {scale_margin_bottom}}}
        }})''')

    def delete(self):
        """
        Irreversibly deletes the line, as well as the object that contains the line.
        """
        self._chart._lines.remove(self) if self in self._chart._lines else None
        self.run_script(f'''
            {self.id}legendItem = {self._chart.id}.legend._lines.find((line) => line.series == {self.id}.series)
            {self._chart.id}.legend._lines = {self._chart.id}.legend._lines.filter((item) => item != {self.id}legendItem)

            if ({self.id}legendItem) {{
                {self._chart.id}.legend.div.removeChild({self.id}legendItem.row)
            }}

            {self._chart.id}.chart.removeSeries({self.id}.series)
            delete {self.id}legendItem
            delete {self.id}
        ''')


class Histogram(SeriesCommon):
    def __init__(self, chart, name, color, price_line, price_label, scale_margin_top, scale_margin_bottom):
        super().__init__(chart, name)
        self.color = color
        self.run_script(f'''
        {self.id} = {chart.id}.createHistogramSeries(
            "{name}",
            {{
                color: '{color}',
                lastValueVisible: {jbool(price_label)},
                priceLineVisible: {jbool(price_line)},
                priceScaleId: '{self.id}',
                priceFormat: {{type: "volume"}},
            }},
            // precision: 2,
        )
        {self.id}.series.priceScale().applyOptions({{
            scaleMargins: {{top:{scale_margin_top}, bottom: {scale_margin_bottom}}}
        }})''')

    def delete(self):
        """
        Irreversibly deletes the histogram.
        """
        self.run_script(f'''
            {self.id}legendItem = {self._chart.id}.legend._lines.find((line) => line.series == {self.id}.series)
            {self._chart.id}.legend._lines = {self._chart.id}.legend._lines.filter((item) => item != {self.id}legendItem)

            if ({self.id}legendItem) {{
                {self._chart.id}.legend.div.removeChild({self.id}legendItem.row)
            }}
            
            {self._chart.id}.chart.removeSeries({self.id}.series)
            delete {self.id}legendItem
            delete {self.id}
        ''')

    def scale(self, scale_margin_top: float = 0.0, scale_margin_bottom: float = 0.0):
        self.run_script(f'''
        {self.id}.series.priceScale().applyOptions({{
            scaleMargins: {{top: {scale_margin_top}, bottom: {scale_margin_bottom}}}
        }})''')


class Candlestick(SeriesCommon):
    def __init__(self, chart: 'AbstractChart'):
        super().__init__(chart)
        self._volume_up_color = 'rgba(83,141,131,0.8)'
        self._volume_down_color = 'rgba(200,127,130,0.8)'

        self.candle_data = pd.DataFrame()

        # self.run_script(f'{self.id}.makeCandlestickSeries()')

    def set(self, df: Optional[pd.DataFrame] = None, keep_drawings=False):
        """
        Sets the initial data for the chart.\n
        :param df: columns: date/time, open, high, low, close, volume (if volume enabled).
        :param keep_drawings: keeps any drawings made through the toolbox. Otherwise, they will be deleted.
        """
        if df is None or df.empty:
            self.run_script(f'{self.id}.series.setData([])')
            self.run_script(f'{self.id}.volumeSeries.setData([])')
            self.candle_data = pd.DataFrame()
            return
        df = self._df_datetime_format(df)
        self.candle_data = df.copy()
        self._last_bar = df.iloc[-1]
        self.run_script(f'{self.id}.series.setData({js_data(df)})')

        if 'volume' not in df:
            return
        volume = df.drop(columns=['open', 'high', 'low', 'close']).rename(columns={'volume': 'value'})
        volume['color'] = self._volume_down_color
        volume.loc[df['close'] > df['open'], 'color'] = self._volume_up_color
        self.run_script(f'{self.id}.volumeSeries.setData({js_data(volume)})')

        for line in self._lines:
            if line.name not in df.columns:
                continue
            line.set(df[['time', line.name]], format_cols=False)
        # set autoScale to true in case the user has dragged the price scale
        self.run_script(f'''
            if (!{self.id}.chart.priceScale("right").options.autoScale)
                {self.id}.chart.priceScale("right").applyOptions({{autoScale: true}})
        ''')
        # TODO keep drawings doesn't work consistenly w
        if keep_drawings:
            self.run_script(f'{self._chart.id}.toolBox?._drawingTool.repositionOnTime()')
        else:
            self.run_script(f"{self._chart.id}.toolBox?.clearDrawings()")

    def update(self, series: pd.Series, _from_tick=False):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: labels: date/time, open, high, low, close, volume (if using volume).
        """
        series = self._series_datetime_format(series) if not _from_tick else series
        if series['time'] != self._last_bar['time']:
            self.candle_data.loc[self.candle_data.index[-1]] = self._last_bar
            self.candle_data = pd.concat([self.candle_data, series.to_frame().T], ignore_index=True)
            self._chart.events.new_bar._emit(self)

        self._last_bar = series
        self.run_script(f'{self.id}.series.update({js_data(series)})')
        if 'volume' not in series:
            return
        volume = series.drop(['open', 'high', 'low', 'close']).rename({'volume': 'value'})
        volume['color'] = self._volume_up_color if series['close'] > series['open'] else self._volume_down_color
        self.run_script(f'{self.id}.volumeSeries.update({js_data(volume)})')

    def update_from_tick(self, series: pd.Series, cumulative_volume: bool = False):
        """
        Updates the data from a tick.\n
        :param series: labels: date/time, price, volume (if using volume).
        :param cumulative_volume: Adds the given volume onto the latest bar.
        """
        series = self._series_datetime_format(series)
        if series['time'] < self._last_bar['time']:
            raise ValueError(f'Trying to update tick of time "{pd.to_datetime(series["time"])}", which occurs before the last bar time of "{pd.to_datetime(self._last_bar["time"])}".')
        bar = pd.Series(dtype='float64')
        if series['time'] == self._last_bar['time']:
            bar = self._last_bar
            bar['high'] = max(self._last_bar['high'], series['price'])
            bar['low'] = min(self._last_bar['low'], series['price'])
            bar['close'] = series['price']
            if 'volume' in series:
                if cumulative_volume:
                    bar['volume'] += series['volume']
                else:
                    bar['volume'] = series['volume']
        else:
            for key in ('open', 'high', 'low', 'close'):
                bar[key] = series['price']
            bar['time'] = series['time']
            if 'volume' in series:
                bar['volume'] = series['volume']
        self.update(bar, _from_tick=True)

    def price_scale(
        self,
        auto_scale: bool = True,
        mode: PRICE_SCALE_MODE = 'normal',
        invert_scale: bool = False,
        align_labels: bool = True,
        scale_margin_top: float = 0.2,
        scale_margin_bottom: float = 0.2,
        border_visible: bool = False,
        border_color: Optional[str] = None,
        text_color: Optional[str] = None,
        entire_text_only: bool = False,
        visible: bool = True,
        ticks_visible: bool = False,
        minimum_width: int = 0
    ):
        self.run_script(f'''
            {self.id}.series.priceScale().applyOptions({{
                autoScale: {jbool(auto_scale)},
                mode: {as_enum(mode, PRICE_SCALE_MODE)},
                invertScale: {jbool(invert_scale)},
                alignLabels: {jbool(align_labels)},
                scaleMargins: {{top: {scale_margin_top}, bottom: {scale_margin_bottom}}},
                borderVisible: {jbool(border_visible)},
                {f'borderColor: "{border_color}",' if border_color else ''}
                {f'textColor: "{text_color}",' if text_color else ''}
                entireTextOnly: {jbool(entire_text_only)},
                visible: {jbool(visible)},
                ticksVisible: {jbool(ticks_visible)},
                minimumWidth: {minimum_width}
            }})''')

    def candle_style(
            self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
            wick_visible: bool = True, border_visible: bool = True, border_up_color: str = '',
            border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.\n
        If only `up_color` and `down_color` are passed, they will color all parts of the candle.
        """
        border_up_color = border_up_color if border_up_color else up_color
        border_down_color = border_down_color if border_down_color else down_color
        wick_up_color = wick_up_color if wick_up_color else up_color
        wick_down_color = wick_down_color if wick_down_color else down_color
        self.run_script(f"{self.id}.series.applyOptions({js_json(locals())})")

    def volume_config(self, scale_margin_top: float = 0.8, scale_margin_bottom: float = 0.0,
                      up_color='rgba(83,141,131,0.8)', down_color='rgba(200,127,130,0.8)'):
        """
        Configure volume settings.\n
        Numbers for scaling must be greater than 0 and less than 1.\n
        Volume colors must be applied prior to setting/updating the bars.\n
        """
        self._volume_up_color = up_color if up_color else self._volume_up_color
        self._volume_down_color = down_color if down_color else self._volume_down_color
        self.run_script(f'''
        {self.id}.volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
            top: {scale_margin_top},
            bottom: {scale_margin_bottom},
            }}
        }})''')


class AbstractChart(Candlestick, Pane):
    def __init__(self, window: Window, width: float = 1.0, height: float = 1.0,
                 scale_candles_only: bool = False, toolbox: bool = False,
                 autosize: bool = True, position: FLOAT = 'left', leftScale: bool = False):
        Pane.__init__(self, window)

        self._lines = []
        self._scale_candles_only = scale_candles_only
        self._width = width
        self._height = height
        self.events: Events = Events(self)

        from lightweight_charts.polygon import PolygonAPI
        self.polygon: PolygonAPI = PolygonAPI(self)

        self.run_script(
            f'{self.id} = new Lib.Handler("{self.id}", {width}, {height}, "{position}", {jbool(autosize)}, {jbool(leftScale)})')

        Candlestick.__init__(self, self)

        self.topbar: TopBar = TopBar(self)
        if toolbox:
            self.toolbox: ToolBox = ToolBox(self)

    def fit(self):
        """
        Fits the maximum amount of the chart data within the viewport.
        """
        self.run_script(f'{self.id}.chart.timeScale().fitContent()')

    def create_line(
            self, name: str = '', color: str = None,
            style: LINE_STYLE = 'solid', width: int = 2,
            price_line: bool = False, price_label: bool = False, priceScaleId: str = "right"
    ) -> Line:
        """
        Creates and returns a Line object.
        """
        if color is None:
            color = get_next_color()
        self._lines.append(Line(self, name, color, style, width, price_line, price_label, True, priceScaleId))
        return self._lines[-1]

    def create_histogram(
            self, name: str = '', color: str = None,
            price_line: bool = False, price_label: bool = True,
            scale_margin_top: float = 0.0, scale_margin_bottom: float = 0.0, opacity: float = None,
    ) -> Histogram:
        """
        Creates and returns a Histogram object.
        """
        if color is None:
            color = get_next_color()
        if opacity is not None:
            color = apply_opacity(color, opacity)
        return Histogram(
            self, name, color, price_line, price_label,
            scale_margin_top, scale_margin_bottom)

    def lines(self) -> List[Line]:
        """
        Returns all lines for the chart.
        """
        return self._lines.copy()

    def set_visible_range(self, start_time: TIME, end_time: TIME):
        self.run_script(f'''
        {self.id}.chart.timeScale().setVisibleRange({{
            from: {pd.to_datetime(start_time).timestamp()},
            to: {pd.to_datetime(end_time).timestamp()}
        }})
        ''')

    def resize(self, width: Optional[float] = None, height: Optional[float] = None):
        """
        Resizes the chart within the window.
        Dimensions should be given as a float between 0 and 1.
        """
        self._width = width if width is not None else self._width
        self._height = height if height is not None else self._height
        self.run_script(f'''
        {self.id}.scale.width = {self._width}
        {self.id}.scale.height = {self._height}
        {self.id}.reSize()
        ''')

    def time_scale(self, right_offset: int = 0, min_bar_spacing: float = 0.5,
                   visible: bool = True, time_visible: bool = True, seconds_visible: bool = False,
                   border_visible: bool = True, border_color: Optional[str] = None):
        """
        Options for the timescale of the chart.
        """
        self.run_script(f'''{self.id}.chart.applyOptions({{timeScale: {js_json(locals())}}})''')

    def layout(self, background_color: str = '#000000', text_color: Optional[str] = None,
               font_size: Optional[int] = None, font_family: Optional[str] = None):
        """
        Global layout options for the chart.
        """
        self.run_script(f"""
            document.getElementById('container').style.backgroundColor = '{background_color}'
            {self.id}.chart.applyOptions({{
            layout: {{
                background: {{color: "{background_color}"}},
                {f'textColor: "{text_color}",' if text_color else ''}
                {f'fontSize: {font_size},' if font_size else ''}
                {f'fontFamily: "{font_family}",' if font_family else ''}
            }}}})""")

    def grid(self, vert_enabled: bool = True, horz_enabled: bool = True,
             color: str = 'rgba(29, 30, 38, 5)', style: LINE_STYLE = 'solid'):
        """
        Grid styling for the chart.
        """
        self.run_script(f"""
           {self.id}.chart.applyOptions({{
           grid: {{
               vertLines: {{
                   visible: {jbool(vert_enabled)},
                   color: "{color}",
                   style: {as_enum(style, LINE_STYLE)},
               }},
               horzLines: {{
                   visible: {jbool(horz_enabled)},
                   color: "{color}",
                   style: {as_enum(style, LINE_STYLE)},
               }},
           }}
           }})""")

    def crosshair(
        self,
        mode: CROSSHAIR_MODE = 'normal',
        vert_visible: bool = True,
        vert_width: int = 1,
        vert_color: Optional[str] = None,
        vert_style: LINE_STYLE = 'large_dashed',
        vert_label_background_color: str = 'rgb(46, 46, 46)',
        horz_visible: bool = True,
        horz_width: int = 1,
        horz_color: Optional[str] = None,
        horz_style: LINE_STYLE = 'large_dashed',
        horz_label_background_color: str = 'rgb(55, 55, 55)'
    ):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        self.run_script(f'''
        {self.id}.chart.applyOptions({{
            crosshair: {{
                mode: {as_enum(mode, CROSSHAIR_MODE)},
                vertLine: {{
                    visible: {jbool(vert_visible)},
                    width: {vert_width},
                    {f'color: "{vert_color}",' if vert_color else ''}
                    style: {as_enum(vert_style, LINE_STYLE)},
                    labelBackgroundColor: "{vert_label_background_color}"
                }},
                horzLine: {{
                    visible: {jbool(horz_visible)},
                    width: {horz_width},
                    {f'color: "{horz_color}",' if horz_color else ''}
                    style: {as_enum(horz_style, LINE_STYLE)},
                    labelBackgroundColor: "{horz_label_background_color}"
                }}
            }}
        }})''')

    def watermark(self, text: str, font_size: int = 44, color: str = 'rgba(180, 180, 200, 0.5)'):
        """
        Adds a watermark to the chart.
        """
        self.run_script(f'''
          {self.id}.chart.applyOptions({{
              watermark: {{
                  visible: true,
                  horzAlign: 'center',
                  vertAlign: 'center',
                  ...{js_json(locals())}
              }}
          }})''')

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, lines: bool = True,
               color: str = 'rgb(191, 195, 203)', font_size: int = 11, font_family: str = 'Monaco',
               text: str = '', color_based_on_candle: bool = False):
        """
        Configures the legend of the chart.
        """
        l_id = f'{self.id}.legend'
        if not visible:
            self.run_script(f'''
            {l_id}.div.style.display = "none"
            {l_id}.ohlcEnabled = false
            {l_id}.percentEnabled = false
            {l_id}.linesEnabled = false
            ''')
            return
        self.run_script(f'''
        {l_id}.div.style.display = 'flex'
        {l_id}.ohlcEnabled = {jbool(ohlc)}
        {l_id}.percentEnabled = {jbool(percent)}
        {l_id}.linesEnabled = {jbool(lines)}
        {l_id}.colorBasedOnCandle = {jbool(color_based_on_candle)}
        {l_id}.div.style.color = '{color}'
        {l_id}.color = '{color}'
        {l_id}.div.style.fontSize = '{font_size}px'
        {l_id}.div.style.fontFamily = '{font_family}'
        {l_id}.text.innerText = '{text}'
        ''')

    def spinner(self, visible):
        self.run_script(f"{self.id}.spinner.style.display = '{'block' if visible else 'none'}'")

    def hotkey(self, modifier_key: Literal['ctrl', 'alt', 'shift', 'meta', None],
               keys: Union[str, tuple, int], func: Callable):
        if not isinstance(keys, tuple):
            keys = (keys,)
        for key in keys:
            key = str(key)
            if key.isalnum() and len(key) == 1:
                key_code = f'Digit{key}' if key.isdigit() else f'Key{key.upper()}'
                key_condition = f'event.code === "{key_code}"'
            else:
                key_condition = f'event.key === "{key}"'
            if modifier_key is not None:
                key_condition += f'&& event.{modifier_key}Key'

            self.run_script(f'''
                    {self.id}.commandFunctions.unshift((event) => {{
                        if ({key_condition}) {{
                            event.preventDefault()
                            window.callbackFunction(`{modifier_key, keys}_~_{key}`)
                            return true
                        }}
                        else return false
                    }})''')
        self.win.handlers[f'{modifier_key, keys}'] = func

    def create_table(
        self,
        width: NUM,
        height: NUM,
        headings: tuple,
        widths: Optional[tuple] = None,
        alignments: Optional[tuple] = None,
        position: FLOAT = 'left',
        draggable: bool = False,
        background_color: str = '#121417',
        border_color: str = 'rgb(70, 70, 70)',
        border_width: int = 1,
        heading_text_colors: Optional[tuple] = None,
        heading_background_colors: Optional[tuple] = None,
        return_clicked_cells: bool = False,
        func: Optional[Callable] = None
    ) -> Table:
        args = locals()
        del args['self']
        return self.win.create_table(*args.values())

    def screenshot(self) -> bytes:
        """
        Takes a screenshot. This method can only be used after the chart window is visible.
        :return: a bytes object containing a screenshot of the chart.
        """
        serial_data = self.win.run_script_and_get(f'{self.id}.chart.takeScreenshot().toDataURL()')
        return b64decode(serial_data.split(',')[1])

    def create_subchart(self, position: FLOAT = 'left', width: float = 0.5, height: float = 0.5,
                        sync: Optional[Union[str, bool]] = None, scale_candles_only: bool = False,
                        sync_crosshairs_only: bool = False,
                        toolbox: bool = False, leftScale: bool = False) -> 'AbstractChart':
        if sync is True:
            sync = self.id
        args = locals()
        del args['self']
        return self.win.create_subchart(*args.values())
