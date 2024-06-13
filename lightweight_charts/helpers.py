from .widgets import JupyterChart
from .util import (
    is_vbt_indicator
)

class Panel:
    """
    A class to represent a panel in a chart.

    Attributes
    ----------
    * ohlcv : tuple optional\n
        (series, entries, exits, other_markers)
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
        xloc="2024-02-12 09:30"
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
    ```
    """
    def __init__(self, ohlcv=None, right=None, left=None, middle1=None, middle2=None, histogram=None, title=None, xloc=None):
        self.ohlcv = ohlcv if ohlcv is not None else []
        self.right = right if right is not None else []
        self.left = left if left is not None else []
        self.middle1 = middle1 if middle1 is not None else []
        self.middle2 = middle2 if middle2 is not None else []
        self.histogram = histogram if histogram is not None else []
        self.title = title
        self.xloc = xloc


def chart(panes: list[Panel], sync=False, title='', size="m", xloc=None, session: str="9:30"):
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
                    - 's' for small
                    - 'm' for medium
                    - 'xl' for extra large

        * session (str): Draw session vertical divider at that time. Defaults to '9:30'. Can be any time in 24-hour format or xloc slice

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
        xloc=slice("2024-02-12 09:30","2024-02-12 16:00")
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
            's': (800, 400),
            'm': (1000, 600),
            'l': (1300, 800)}
    width, height = size_to_dimensions.get(size, (1000, 600))
    height_ratio = 1 / len(panes)
    main_title_set = False
    for index, pane in enumerate(panes):
            subchartX = None
            if index == 0:
                    chartX = JupyterChart(width=width, height=height, inner_width=1, inner_height=height_ratio, leftScale=bool(pane.left))
                    active_chart = chartX
            else:
                    subchartX = chartX.create_subchart(position='right', width=1, height=height_ratio, sync=sync, leftScale=bool(pane.left))
                    active_chart = subchartX
            xloc = pane.xloc if pane.xloc is not None else xloc

            if pane.ohlcv is not None:
                    series, entries, exits, markers = (pane.ohlcv + (None,) * 4)[:4]
                    active_chart.set(xloc_me(series, xloc))
                    if entries is not None:
                            active_chart.markers_set(xloc_me(entries, xloc), "entries")
                    if exits is not None:
                            active_chart.markers_set(xloc_me(exits, xloc), "exits")
                    if markers is not None:
                            active_chart.markers_set(xloc_me(markers, xloc))

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
                    if att_name in ["ohlcv","histogram","title","xloc"]:
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
                                    tmp = active_chart.create_line(name=output, priceScaleId=att_name)#, color="blue")
                                    tmp.set(output_series)
                            else:
                                if name is None:
                                      name = "no_name"

                                tmp = active_chart.create_line(name=name, priceScaleId=att_name)#, color="blue")
                                tmp.set(xloc_me(series, xloc))

                            if entries is not None:
                                tmp.markers_set(xloc_me(entries, xloc), "entries")
                            if exits is not None:
                                tmp.markers_set(xloc_me(exits, xloc), "exits")
                            if markers is not None:
                                tmp.markers_set(xloc_me(markers, xloc))
            
            active_chart.legend(True)
            active_chart.fit()
            if session is not None and session:
                active_chart.vertical_span(start_time=xloc_me(series, xloc).vbt.xloc[session].obj.index.to_list(), color="rgba(252, 219, 3, 0.4)")

    if not main_title_set:
            chartX.topbar.textbox("title",title)
    chartX.legend(True)
    chartX.fit()
    chartX.load()
    return chartX
