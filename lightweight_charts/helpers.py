from .widgets import JupyterChart
from .util import (
    is_vbt_indicator, get_next_color
)
import pandas as pd

def append_or_extend(target_list, value):
    if isinstance(value, list):
        target_list.extend(value)  # Extend if it's a list
    else:
        target_list.append(value)  # Append if it's a single value

def extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, kwargs):
    """
    Mutate lists based on kwargs for accessor.
    Used when user added additional series to kwargs when using accessor.
    """
    if 'ohlcv' in kwargs:
        ohlcv = kwargs['ohlcv'] #ohlcv is only a tuple
    if 'left' in kwargs:
        append_or_extend(left, kwargs['left'])
    if 'right' in kwargs:
        append_or_extend(right, kwargs['right'])
    if 'histogram' in kwargs:
        append_or_extend(histogram, kwargs['histogram'])
    if 'middle1' in kwargs:
        append_or_extend(middle1, kwargs['middle1'])         
    if 'middle2' in kwargs:
        append_or_extend(middle1, kwargs['middle2'])   

    return ohlcv #as tuple is immutable

# Register the custom accessor
@pd.api.extensions.register_series_accessor("lw")
class PlotSRAccessor:
    """
    Custom plot accessor for pandas series. Quickly displays series values as line on the single pane.

    Also additional priceseries can be added on top of them. They can be added
    for each scale in the correct format - either as tuple(OHLCV) or as list of tuple (others)

        # input parameter / expected format:
        #     ohlcv=(), #(series, entries, exits, other_markers)
        #     histogram=[], # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
        #     right=[],
        #     left=[], #[(series, name, entries, exits, other_markers)]
        #     middle1=[],
        #     middle2=[],


    Usage: s
    series.lw.plot() #plot series as line
    series.lw.plot(size="m") #on medium panesize
    series.lw.plot(histogram=(trade_series, "trades")) #plot histogram with trades on top of that
    """
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def plot(self, **kwargs):
        if "size" not in kwargs:
            kwargs["size"] = "xs"
        name = kwargs["name"] if "name" in kwargs else "line"
             
        ohlcv = ()
        right = []
        left = []
        middle1 = []
        middle2 = []
        histogram = []

        #if there are additional series in kwargs add them too
        #ohlcv is returned as it is tuple thus immutable
        ohlcv = extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, kwargs)

        right.append((self._obj,name))

        pane1 = Panel(
            ohlcv=ohlcv,
            histogram=histogram,
            right=right,
            left=left,
            middle1=middle1,
            middle2=middle2
            )

        ch = chart([pane1], **kwargs)

@pd.api.extensions.register_dataframe_accessor("lw")
class PlotDFAccessor:
    """
    Custom plot accessor for dataframe. Quickly displays all columns on the single pane.

    Series type is automatically extracted for each column based on following setting:
        scale / columns
        ohlcv = ['close', 'volume', 'open', 'high', 'low']
        right = ['vwap']
        left = ['rsi']
        middle1 = []
        middle2 = []
        histogram = ['buyvolume', 'sellvolume', 'trades']

    Also additional priceseries can be added on top of them as parameters. They can be added
    for each scale in the correct format - either as tuple(OHLCV) or as list of tuple (others)

        # input parameter / expected format:
        #     ohlcv=(), #(series, entries, exits, other_markers)
        #     histogram=[], # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
        #     right=[],
        #     left=[], #[(series, name, entries, exits, other_markers)]
        #     middle1=[],
        #     middle2=[],


    Usage:
    ohlcv_df.lw.plot()
    ohlcv_df.lw.plot(size="m")
    ohlcv_df.lw.plot(right=(rsi_series, "rsi"))
    ohlcv_df.lw.plot(right=[(rsi_series, "rsi"), (angle_series, "angle")])
    basic_data.data[SYMBOL].lw.plot(histogram=(basic_data.data[SYMBOL].close, "close"), size="m")
    """
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def plot(self, **kwargs):
        if "size" not in kwargs:
            kwargs["size"] = "xs"

        #default settings for each pricescale
        ohlcv_cols = ['close', 'volume', 'open', 'high', 'low']
        right_cols = ['vwap']
        left_cols = ['rsi']
        middle1_cols = []
        middle2_cols = []
        histogram_cols = ['buyvolume', 'sellvolume', 'trades']
        
        ohlcv = ()
        right = []
        left = []
        middle1 = []
        middle2 = []
        histogram = []

        for col in self._obj.columns:
             if col in right_cols:
                  right.append((self._obj[col],col,))
             if col in histogram_cols:
                  histogram.append((self._obj[col],col,))
             if col in left_cols:
                  left.append((self._obj[col],col,))
             if col in middle1_cols:
                  middle1_cols.append((self._obj[col],col,))
             if col in middle2_cols:
                  middle2_cols.append((self._obj[col],col,))

        ohlcv = (self._obj[ohlcv_cols],)

        #if there are additional series in kwargs add them too
        ohlcv = extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, kwargs)

        pane1 = Panel(
            ohlcv=ohlcv,
            histogram=histogram,
            right=right,
            left=left,
            middle1=middle1,
            middle2=middle2
            )

        ch = chart([pane1], **kwargs)

        # pane1 = Panel(
        #     ohlcv=(), #(series, entries, exits, other_markers)
        #     histogram=[], # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
        #     right=[],
        #     left=[], #[(series, name, entries, exits, other_markers)]
        #     middle1=[],
        #     middle2=[],
        # )

class Panel:
    """
    A class to represent a panel in a chart.

    Attributes
    ----------
    * ohlcv : tuple optional\n
        (series, entries, exits, other_markers).\n
        entries, exits and other_markers can be sr/df or lists of sr/df or list of tuples (if you want to specify color)
    * histogram : list of tuples, optional.\n
        [(series, name, color, opacity)]
    * title : str, optional
        The title of the panel. Default is None.
    * right : list of tuples, optional
        A list of line tuples in given scale.\n
        [(series, name, entries, exits, other_markers)]
    * left : list of tuples, optional
    * middle1 : list of tuples, optional
    * middle2 : list of tuples, optional
    * xloc : str or slice, optional. Vectorbt indexing. Default is None.
    * precision: int, optional. The number of digits after the decimal point. Apply to all lines on this pane. Default is None.

    Examples
    -------
    # Simple example
    ```
    pane1 = Panel(
        ohlcv=(), #(series, entries, exits, other_markers)
        histogram=[], # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
        right=[],
        left=[], #[(series, name, entries, exits, other_markers)]
        middle1=[],
        middle2=[],
    )

    ch = chart([pane1])

    # Synced example
    pane1 = Panel(
        ohlcv=(t1data.data["BAC"],),  #(series, entries, exits, other_markers)
        histogram=[(order_imbalance_allvolume, "oivol")], # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
        right=[], # [(series, name, entries, exits, other_markers)]
        left=[(sma, "sma", short_signals, short_exits)],
        middle1=[],
        middle2=[],
        xloc="2024-02-12 09:30",
        precision=3
    )

    pane2 = Panel(
        ohlcv=(t1data.data["BAC"],),
        right=[],
        left=[(sma, "sma_below", short_signals, short_exits)],
        middle1=[],
        middle2=[],
        histogram=[(order_imbalance_sma, "oisma")],
    )

    ch = chart([pane1, pane2], sync=True, title="neco", size="m", xloc=slice("2024-02-12 09:30","2024-02-12 16:00"))

    #Markers examples

    #assume i want to display simple entries or exits on series or ohlcv 
    #based on tuple positions it determines entries or exits (and set colors and shape accordingly)
    pane1 = Panel(
        ohlcv=(ohlcv_df, clean_long_entries, clean_short_entries)
    )
    ch = chart([pane1], title="Chart with Entry/Exit Markers", session=None, size="s")

    #if you want to display more entries or exits, use tuples with their colors
    # Create Panel with OHLC data and entry signals
    pane1 = Panel(
        ohlcv=(data.ohlcv.get(),
            [(clean_long_entries, "yellow"), (clean_short_entries, "pink")], #list of entries tuples with color
            [(clean_long_exits, "yellow"), (clean_short_exits, "pink")]), #list of exits tuples with color
    )

    # # Create the chart with the panel
    ch = chart([pane1], title="Chart with EntryShort/ExitShort (yellow) and EntryLong/ExitLong markers (pink)", sync=True, session=None, size="s")
    ```
    """
    def __init__(self, ohlcv=None, right=None, left=None, middle1=None, middle2=None, histogram=None, title=None, xloc=None, precision=None):
        self.ohlcv = ohlcv if ohlcv is not None else ()
        self.right = right if right is not None else []
        self.left = left if left is not None else []
        self.middle1 = middle1 if middle1 is not None else []
        self.middle2 = middle2 if middle2 is not None else []
        self.histogram = histogram if histogram is not None else []
        self.title = title
        self.xloc = xloc
        self.precision = precision


def chart(panes: list[Panel], sync=False, title='', size="m", xloc=None, session = slice("09:30:00","9:30:05"), precision=None, **kwargs):
    """
    Function to fast render a chart with multiple panes. This function manipulates graphical
    output or interfaces with an external framework to display charts with synchronized
    scales if required.

    Args:
    -----
        * panes (List[Pane]): A list of Pane instances to be rendered in the chart. Each Pane
                            can include various data series and configurations such as OHLCV,
                            histograms, and indicators positioned on left, right, or middle scales.
        * sync (bool): If True, synchronize scales of all panes to have the same scale limits.
                     Default is False.
        * title (str): Title of the chart. If not specified, defaults to an empty string.

        * size (str): The size designation, which can be 's', 'm', or 'xl'. Defaults to'm'.
                    Expected values:
                    - 'xs' for extra-small
                    - 's' for small
                    - 'm' for medium
                    - 'xl' for extra large

        * session (str): Draw session vertical divider at that time. Defaults to '9:30'. Can be any time in 24-hour format or xloc slice

        * precision (int): The number of digits after the decimal point. Defaults to None. Applies to lines on all panes, if not overriden by pane-specific precision.

        * xloc (str): xloc advanced filtering of vbt.xloc accessor. Defaults to None. Applies to all panes.
        Might be overriden by pane-specific xloc.
            
        XLOC Examples:
            xloc["2020-01-01 17:30"]  
            xloc["2020-01-01"]  
            xloc["2020-01"]  
            xloc["2020"]  
            xloc["2020-01-01":"2021-01-01"]  
            xloc["january":"april"]  
            xloc["monday":"saturday"]  
            xloc["09:00":"16:00"]  
            xloc["16:00":"09:00"]  
            xloc["monday 09:00":"friday 16:00"] 

    Returns:
        None: This function does not return a value. It performs operations to render graphical content.

    Examples:
    ---------
    ```
    pane1 = Pane(
        ohlcv=(t1data.data["BAC"],),
        histogram=[(order_imbalance_allvolume, "oivol")]
        right=[],
        left=[(sma, "sma", short_signals, short_exits)],
        middle1=[],
        middle2=[],
        xloc=slice("2024-02-12 09:30","2024-02-12 16:00"),
        precision=4
    )
    pane2 = Pane(
        ohlcv=(t1data.data["BAC"],),
        right=[],
        left=[(sma, "sma_below", short_signals, short_exits)],
        middle1=[],
        middle2=[],
        histogram=[(order_imbalance_sma, "oisma")]
    )
    ch = chart([pane1, pane2], sync=True, title="Chart", size="l", xloc=slice("2024-02-12 09:30","2024-02-12 16:00"), session="9:30")
    ```

    Notes:
    ------

    """

    def xloc_me(dfsr, xloc):
          if xloc is None:
                return dfsr
          else:
                return dfsr.vbt.xloc[xloc].obj

    size_to_dimensions = {
            'xs': (600, 200),
            's': (800, 400),
            'm': (1000, 600),
            'l': (1300, 800)}
    width, height = size_to_dimensions.get(size, (1000, 600))
    height_ratio = 1 / len(panes)
    main_title_set = False
    output_series = None
    for index, pane in enumerate(panes):
            subchartX = None
            if index == 0:
                    chartX = JupyterChart(width=width, height=height, inner_width=1, inner_height=height_ratio, leftScale=bool(pane.left))
                    active_chart = chartX
            else:
                    subchartX = chartX.create_subchart(position='right', width=1, height=height_ratio, sync=sync, leftScale=bool(pane.left))
                    active_chart = subchartX

            xloc = pane.xloc if pane.xloc is not None else xloc

            def display_markers(active_chart: JupyterChart, markers, type= None, xloc=None):
                color = None
                if isinstance(markers, list):
                        for markerset in markers:
                            if isinstance(markerset, tuple):
                                  markerset,color = markerset
                            active_chart.markers_set(markers=xloc_me(markerset, xloc), type=type, color=color if color is not None else None)
                else:
                    if isinstance(markers, tuple):
                        markers,color = markers
                    active_chart.markers_set(markers=xloc_me(markers, xloc), type=type, color=color if color is not None else None)                  


            if pane.ohlcv != ():
                    series, entries, exits, markers = (pane.ohlcv + (None,) * 4)[:4]
                    if series is None:
                          raise ValueError("OHLCV series cannot be None. Omit the OHLCV tuple.")
                    active_chart.set(xloc_me(series, xloc))
                    if entries is not None:
                        display_markers(active_chart=active_chart, markers=entries, type="entries", xloc=xloc)
                    if exits is not None:
                        display_markers(active_chart=active_chart, markers=exits, type="exits", xloc=xloc)
                    if markers is not None:
                        display_markers(chart=active_chart, markers=markers, xloc=xloc)

            for tup in pane.histogram:
                    series, name, color, opacity, _ = (tup + (None, None, None, None, None))[:5]
                    if series is None:
                            continue
                    #conditionally include color
                    kwargs = {'name': name}
                    if color is not None:
                            kwargs['color'] = color 
                    if opacity is not None:
                            kwargs['opacity'] = opacity
                    tmp = active_chart.create_histogram(**kwargs) #green transparent "rgba(53, 94, 59, 0.6)"
                    tmp.set(xloc_me(series, xloc))

            if pane.title is not None:
                    active_chart.topbar.textbox("title",pane.title)
                    main_title_set = True if index==0 else False

            #iterate over keys - they are all priceScaleId except of these
            for att_name, att_value_tuple in vars(pane).items():
                    if att_name in ["ohlcv","histogram","title","xloc","precision"]:
                            continue
                    for tup in att_value_tuple:
                            series, name, entries, exits, markers = (tup + (None, None, None, None, None))[:5]
                            if series is None:
                                continue

                            #pokud jde o vbt indikator vytahneme vsechny output a predpokladame, ze jde o lines a vykreslime je
                            if is_vbt_indicator(series):
                                series = series.xloc[xloc] if xloc is not None else series
                                for output in series.output_names:
                                    output_series = getattr(series, output)
                                    output = name + ':' + output if name is not None else output       
                                    tmp = active_chart.create_line(name=output, priceScaleId=att_name)#, color="blue")
                                    tmp.set(output_series)
                            else:
                                if name is None:
                                      name = "no_name"

                                tmp = active_chart.create_line(name=name, priceScaleId=att_name)#, color="blue")
                                tmp.set(xloc_me(series, xloc))

                            if pane.precision is not None or precision is not None:
                                  tmp.precision(pane.precision if pane.precision is not None else precision)

                            if entries is not None:
                                display_markers(active_chart=tmp, markers=entries, type="entries", xloc=xloc)
                            if exits is not None:
                                display_markers(active_chart=tmp, markers=exits, type="exits", xloc=xloc)
                            if markers is not None:
                                display_markers(active_chart=tmp, markers=markers, xloc=xloc)
            
            active_chart.legend(True)
            active_chart.fit()
            if session is not None and session:
                try:
                    last_used_series = output_series if is_vbt_indicator(series) else series #pokud byl posledni series vbt, pak pouzijeme jeho outputy
                    t1 = xloc_me(last_used_series, xloc)
                    t1 = t1.vbt.xloc[session]
                    target_data = t1.obj
                    #we dont know the exact time of market start +- 3 seconds thus we find mark first row after 9:30
                    # Resample the data to daily frequency and get the first entry of each day
                    first_row_indexes = target_data.resample('D').apply(lambda x: x.index[0])

                    # Convert the indexes to a list
                    session_starts = first_row_indexes.to_list()

                    active_chart.vertical_span(start_time=session_starts, color="rgba(252, 255, 187, 0.42)")
                except Exception as e:
                    print("Error fetching main session")

    if not main_title_set:
            chartX.topbar.textbox("title",title)
    chartX.legend(True)
    chartX.fit()
    chartX.load()
    return chartX
