from .widgets import JupyterChart
from .util import (
    is_vbt_indicator, get_next_color
)
import pandas as pd

# Register the custom accessor
@pd.api.extensions.register_series_accessor("lw")
class PlotAccessor:
    """
    Custom plot accessor for pandas series.

    Usage: s
    series.lw.plot()
    series.lw.plot(size="m")
    """
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def plot(self, **kwargs):
        if "size" not in kwargs:
            kwargs["size"] = "xs"
        pane1 = Panel(
            right=[(self._obj, "line")],
        )
        ch = chart([pane1], **kwargs)

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


def chart(panes: list[Panel], sync=False, title='', size="m", xloc=None, session: str="9:30:00", precision=None):
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
                last_used_series = output_series if is_vbt_indicator(series) else series #pokud byl posledni series vbt, pak pouzijeme jeho outputy
                active_chart.vertical_span(start_time=xloc_me(last_used_series, xloc).vbt.xloc[session].obj.index.to_list(), color="rgba(252, 255, 187, 0.42)")

    if not main_title_set:
            chartX.topbar.textbox("title",title)
    chartX.legend(True)
    chartX.fit()
    chartX.load()
    return chartX
