from ast import parse
from .widgets import JupyterChart
from .util import (
    is_vbt_indicator, get_next_color
)
import pandas as pd

#default settings for each pricescale
ohlcv_cols = ['close', 'volume', 'open', 'high', 'low']
right_cols = ['vwap']
left_cols = ['rsi', 'cci', 'macd', 'macdsignal', "chopiness", "chopiness_ma"]
middle1_cols = ["mom"]
middle2_cols = ["updated", "integer"]
histogram_cols = ['buyvolume', 'sellvolume', 'trades', 'macdhist']

def append_scales(df, right, histogram, left, middle1, middle2, name = ""):
    if isinstance(df, pd.DataFrame):
        for col in df.columns:
                match col:
                    case c if c.lower() in ohlcv_cols:
                            continue
                    case c if c.lower() in right_cols:
                        right.append((df[c],name+c,))
                    case c if c.lower() in histogram_cols:
                        histogram.append((df[c],name+c,))
                    case c if c.lower() in left_cols:
                        left.append((df[c],name+c,))
                    case c if c.lower() in middle1_cols:
                        middle1.append((df[c],name+c,))
                    case c if c.lower() in middle2_cols:
                        middle2.append((df[c],name+c,))
                    case _:
                        right.append((df[c],name+c,))
    else: #it is series (as df multiindex can be just envelope for series)
            right.append((df,str(df.name),))

def append_or_extend(target_list, value):
    if isinstance(value, list):
        target_list.extend(value)  # Extend if it's a list
    else:
        target_list.append(value)  # Append if it's a single value

def extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, auto_scale, kwargs):
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
        append_or_extend(middle2, kwargs['middle2'])
    if 'auto_scale' in kwargs:
        append_or_extend(auto_scale, kwargs['auto_scale'])    

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
        auto_scale = []

        #if there are additional series in kwargs add them too
        #ohlcv is returned as it is tuple thus immutable
        ohlcv = extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, auto_scale, kwargs)

        right.append((self._obj,name))

        pane1 = Panel(
            auto_scale=auto_scale,
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

        ohlcv = ()
        right = []
        left = []
        middle1 = []
        middle2 = []
        histogram = []
        auto_scale = []
                 
        if isinstance(self._obj.columns, pd.MultiIndex):
            for col_tuple in self._obj.columns:
                # Access the data for each column tuple dynamically
                df = self._obj.loc[:, col_tuple]
                name = str(col_tuple)+" "
                append_scales(df, right, histogram, left, middle1, middle2, name)
            first_column_df = self._obj.loc[:, self._obj.columns[0]]
            ohlcv = (first_column_df[ohlcv_cols],) if isinstance(first_column_df, pd.DataFrame) and first_column_df.columns in ohlcv else () #in case of multiindex only the first ohlcv is display only one ohlcv is allowed on the pane

        else:
            append_scales(self._obj, right, histogram, left, middle1, middle2)
            #add ohlcv if all columns ohlcv_cols
            #column mapping enables either both lowercase and first upper
            column_mapping = {key: next((col for col in self._obj.columns if col.lower() == key), None) for key in ohlcv_cols}
            mapped_columns = [column_mapping[key] for key in ohlcv_cols if column_mapping[key] is not None]
            ohlcv = (self._obj[mapped_columns],) if isinstance(self._obj, pd.DataFrame) and all(col in self._obj.columns.str.lower() for col in ohlcv_cols) else ()
            
        #if there are additional series in kwargs add them too
        ohlcv = extend_kwargs(ohlcv, right, left, middle1, middle2, histogram, auto_scale, kwargs)

        pane1 = Panel(
            auto_scale=auto_scale,
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
    * auto_scale: list of objects, optional - external objects (vbt indicators) that can be automatically parsed to given scaleID
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

    # or simply:
    
    Panel(
            auto_scale=[cdlbreakaway],
            ohlcv=(t1data.ohlcv.data["BAC"],entries),
            histogram=[],
            right=[],
            left=[],
            middle1=[],
            middle2=[]
            ).chart(size="s")

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
        auto_scale=[macd_vbt_ind],
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
    def __init__(self, auto_scale=[],ohlcv=None, right=None, left=None, middle1=None, middle2=None, histogram=None, title=None, xloc=None, precision=None):
        self.auto_scale = auto_scale
        self.ohlcv = ohlcv if ohlcv is not None else ()
        self.right = right if right is not None else []
        self.left = left if left is not None else []
        self.middle1 = middle1 if middle1 is not None else []
        self.middle2 = middle2 if middle2 is not None else []
        self.histogram = histogram if histogram is not None else []
        self.title = title
        self.xloc = xloc
        self.precision = precision

    def chart(self, **kwargs):
        chart([self], **kwargs)
    
def chart(panes: list[Panel], sync=False, title='', size="s", xloc=None, session = slice("09:30:00","9:30:05"), precision=None, params_detail=False, **kwargs):
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

        * params_detail (bool): If True displays in the legend full names of multiindex columns.

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


            def add_to_scale(series, right, histogram, left, middle1, middle2, column,name = None):
                """
                Assigns a series to a scaleId based on its name and pre-defined col names.
                
                Args:
                -----
                    series (pd.Series): The series to be added to a scaleId
                    right (list): The right scale to add to
                    histogram (list): The histogram scale to add to
                    left (list): The left scale to add to
                    middle1 (list): The middle1 scale to add to
                    middle2 (list): The middle2 scale to add to
                    name (str): The name of the series
                    
                Returns:
                -------
                    None
                
                Notes:
                -----
                The function checks if the series name is in the pre-defined column names 
                (e.g. ohlcv_cols, right_cols, histogram_cols, etc.) and assigns the series to 
                the corresponding scaleId. If the name is not found in any of the pre-defined 
                column names, the series is added to the right scale by default.
                """
                if name is None:
                     name = column
                if column.lower() in ohlcv_cols:
                    return
                elif column.lower() in right_cols:
                    right.append((series, name,))
                elif column.lower() in histogram_cols:
                    histogram.append((series, name))
                elif column.lower() in left_cols:
                    left.append((series, name))
                elif column.lower() in middle1_cols:
                    middle1.append((series, name))
                elif column.lower() in middle2_cols:
                    middle2.append((series, name))
                else:
                    right.append((series, name,))

            # automatic scale assignment
            if len(pane.auto_scale) > 0:
                 for obj in pane.auto_scale:
                    if is_vbt_indicator(obj): #for vbt indicators
                        for output in obj.output_names:
                            output_series = getattr(obj, output)
                            output_name = obj.short_name + ':' + output
                            output = obj.short_name if output == "real" else output
                            #if output_series is multiindex - add each combination to respective scaleId
                            if isinstance(output_series, pd.DataFrame) and isinstance(output_series.columns, pd.MultiIndex):
                                for col_tuple in output_series.columns:
                                    name=output_name + " " + str(col_tuple)
                                    series_copy = output_series.loc[:, col_tuple].copy(deep=True)
                                    add_to_scale(series_copy, pane.right, pane.histogram, pane.left, pane.middle1, pane.middle2, output, name)
                            elif isinstance(output_series, pd.DataFrame): #in case of multicolumns
                                for col in output_series.columns:
                                    name=output_name + " " + col
                                    series_copy = output_series.loc[:, col].copy(deep=True)
                                    add_to_scale(series_copy, pane.right, pane.histogram, pane.left, pane.middle1, pane.middle2, output, name)
                            # elif isinstance(output_series, pd.DataFrame): #it df with multiple columns (probably symbols)
                            #     for col in output_series.columns:
                            #         name=output_name + " " + col
                            #         series_copy = output_series[col].squeeze()
                            #         add_to_scale(series_copy, pane.right, pane.histogram, pane.left, pane.middle1, pane.middle2, output, name)
                            else: #add output to respective scale
                                series_copy = output_series.copy(deep=True)
                                add_to_scale(series_copy, pane.right, pane.histogram, pane.left, pane.middle1, pane.middle2, output, output_name)
                                
                    # zde jsem skoncil
                    #vbt ind

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
                    if isinstance(series, pd.DataFrame) and isinstance(series.columns, pd.MultiIndex): #multiindex handling
                        for col_tuple in series.columns:
                            kwargs = {'name': name + str(col_tuple)}
                            tmp = active_chart.create_histogram(**kwargs) #green transparent "rgba(53, 94, 59, 0.6)"
                            tmp.set(xloc_me(series.loc[:, col_tuple], xloc))
                    elif isinstance(series, pd.DataFrame): #it df with multiple columns (probably symbols)
                        for col in series.columns:
                            kwargs = {'name': name + str(col)}
                            tmp = active_chart.create_histogram(**kwargs) #green transparent "rgba(53, 94, 59, 0.6)"
                            tmp.set(xloc_me(series[col], xloc))                      
                    else:
                        tmp = active_chart.create_histogram(**kwargs) #green transparent "rgba(53, 94, 59, 0.6)"
                        tmp.set(xloc_me(series, xloc))

            if pane.title is not None:
                    active_chart.topbar.textbox("title",pane.title)
                    main_title_set = True if index==0 else False

            #iterate over keys - they are all priceScaleId except of these
            for att_name, att_value_tuple in vars(pane).items():
                    if att_name in ["ohlcv","histogram","title","xloc","precision", "auto_scale"]:
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
                                    output = name + ':' + output if name is not None else series.short_name + ":" + output  
                                    #if output_series is multiindex - create aline for each combination
                                    if isinstance(output_series, pd.DataFrame) and isinstance(output_series.columns, pd.MultiIndex):
                                        for col_tuple in output_series.columns:

                                            tmp = active_chart.create_line(name=output + " " + str(col_tuple), priceScaleId=att_name)#, color="blue")
                                            tmp.set(output_series.loc[:, col_tuple])
                                    elif isinstance(output_series, pd.DataFrame): #it df with multiple columns (probably symbols)
                                        for col in output_series.columns:
                                            tmp = active_chart.create_line(name=output + " " + str(col), priceScaleId=att_name)#, color="blue")
                                            tmp.set(output_series[col])                            
                                    else:  
                                        tmp = active_chart.create_line(name=output, priceScaleId=att_name)#, color="blue")
                                        tmp.set(output_series)
                            #if multiindex then unpack them all with tuple as names
                            elif isinstance(series, pd.DataFrame) and isinstance(series.columns, pd.MultiIndex):
                                for col_tuple in series.columns:
                                    #if required show all multiindex names
                                    if params_detail:   
                                        # Access MultiIndex level names
                                        index_names = series.columns.names
                                        # Build the name string by combining level names and their corresponding values
                                        col_name_str = " ".join([f"{index_names[i]}: {col_val}" for i, col_val in enumerate(col_tuple)])
                                        # Use this name in the chart, adding the provided name if it exists
                                        final_name = col_name_str if name is None else f"{name} {col_name_str}"
                                    else:
                                        final_name = str(col_tuple) if name is None else name+" "+str(col_tuple)
                                    tmp = active_chart.create_line(name=final_name, priceScaleId=att_name)#, color="blue")
                                    tmp.set(xloc_me(series.loc[:, col_tuple], xloc))
                            elif isinstance(series, pd.DataFrame): #it df with multiple columns (probably symbols)
                                
                        #recursive df handling - but make sure it
                                def traverse_dataframe(series, att_name, xloc, active_chart, name=""):
                                    nonlocal tmp
                                    # Check if the input is a DataFrame
                                    if isinstance(series, pd.DataFrame):
                                        for col in series.columns:
                                            col_name = name + " " + col if name else col
                                            # Recursively call the function for each column
                                            traverse_dataframe(series[col], att_name, xloc, active_chart, col_name)
                                    elif isinstance(series, pd.Series):
                                        # Once we hit the series level, create the result_name and call the active_chart method
                                        result_name = name.strip()  # Remove any leading/trailing spaces from column name
                                        result_series = series.squeeze()  # Extract the series data

                                        # Now call the `active_chart.create_line()` as per your requirement
                                        tmp = active_chart.create_line(name=result_name, priceScaleId=att_name)
                                        tmp.set(xloc_me(result_series, xloc))  # Call the xloc_me function for setting xloc

                                    else:
                                        raise ValueError(f"Unexpected type {type(series)} encountered")
                                    
                                if name is None:
                                      name = "no_name" if not hasattr(series, 'name') or series.name is None else str(series.name)

                                traverse_dataframe(series, att_name, xloc, active_chart, name)

                                # for col in series.columns:
                                #     name=name + " " + col 
                                #     series_copy = output_series[col].squeeze()
                                #     tmp = active_chart.create_line(name=name, priceScaleId=att_name)#, color="blue")
                                #     tmp.set(xloc_me(series_copy, xloc))
                            else:
                                if name is None:
                                      name = "no_name" if not hasattr(series, 'name') or series.name is None else str(series.name)

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
                    last_used_series = output_series.loc[:, col_tuple] if isinstance(output_series, pd.DataFrame) and isinstance(output_series.columns, pd.MultiIndex) else output_series if is_vbt_indicator(series) else series #pokud byl posledni series vbt, pak pouzijeme jeho outputy
                    last_used_series = last_used_series.iloc[:,0] if isinstance(last_used_series, pd.DataFrame) else last_used_series #if df then use just first column
                    t1 = xloc_me(last_used_series, xloc)
                    t1 = t1.vbt.xloc[session]
                    target_data = t1.obj
                    #we dont know the exact time of market start +- 3 seconds thus we find mark first row after 9:30
                    # Resample the data to daily frequency and get the first entry of each day
                    first_row_indexes = target_data.resample('D').apply(lambda x: x.index[0] if not x.empty else None).dropna()

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
