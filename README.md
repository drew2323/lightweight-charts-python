Fork of the original [lightweight-charts](louisnw01/lightweight-charts-python) with enhancements and supporting vectorbtpro workflow
* legends cookie matching line colors
* automatic colors picks if not provided
* support for left and mid price scales
* accepts df,pd.series or vectorbtpro indicator object (including unpacking multi outputs)
* new markers_set method allowing to set pd.series or dataframe as markers input
* supports simple df/sr accessors `close.lw.plot()` for quick visualization of single panel chart
* supports `ch = chart([pane1, pane2], sync=True, title="Title", size="m")` to quickly display chart with N panes (`Panels`). Also supports syncing the Panels `sync=True` or using xloc.
  

<img width="1005" alt="image" src="https://github.com/drew2323/lightweight-charts-python/assets/28433232/856c32aa-e0ff-4de0-b4a2-befc34adb571">

It should be installed directly from this repository.

## Examples

```python
from lightweight_charts import chart, Panel

#one liner, displays close series as line on single Panel
close.lw.plot()

#quick few liner, displays close series with label "close" on right pricescale and rsi on left price scale, all on single Panel
pane1 = Panel(
    right=[(close, "close")],
    left=[(rsi,"rsi")]
)
ch = chart([pane1])

# display two Panels
# on first displays ohlcv data, orderimbalance volume as histogram with opacity, bbands on the right pricescale and
# sma with short_signals and short_exits on the left pricescale
pane1 = Panel(
    ohlcv=(t1data.data["BAC"],),     #(series, entries, exits, other_markers)
    histogram=[(order_imbalance_allvolume, "oivol",None, 0.3)],  # [(series, name, "rgba(53, 94, 59, 0.6)", opacity)]
    
    #following attributes assign lineseries series to different priceScaleIds, format: # [(series, name, entries, exits, other_markers)]
    right=[(bbands)],   #multioutput indicator, outputs are autom.extracted
    left=[(sma, "sma", short_signals, short_exits) #simple vbt indicator with markers in and outs
          (supertrend.trend, "ST_trend") #explicitly just one output of multioutput indicator
         ], 
    middle1=[],
    middle2=[],
)
#on second panel displays also ohlcv data, and sma on the left pricescale and histogram
pane2 = Panel(
    ohlcv=(t1data.data["BAC"],),
    right=[],
    left=[(sma, "sma_below", short_signals, short_exits)],
    middle1=[],
    middle2=[],
    histogram=[(order_imbalance_sma, "oisma")],
)

#display both Panels, sync them and pick size, use xloc
ch = chart([pane1, pane2], sync=True, title="Title", size="l", xloc=slice("1-1-2024","1-2-2024")

```

## Example with markers

```python

#assume i want to display simple entries or exits on series or ohlcv 
#based on tuple positions it determines entries or exits (and set colors and shape accordingly)
pane1 = Panel(
    ohlcv=(ohlcv_df, clean_long_entries, clean_short_entries)
)
ch = chart([pane1], title="Chart with Entry/Exit Markers", session=None, size="s")
```
<img width="798" alt="image" src="https://github.com/drew2323/lightweight-charts-python/assets/28433232/0cdc3930-b8b1-40f8-af95-55467879148b">

```python
#if you want to display more entries or exits, use tuples with their colors

# Create Panel with OHLC data and entry signals
pane1 = Panel(
    ohlcv=(data.ohlcv.get(),
           [(clean_long_entries, "yellow"), (clean_short_entries, "pink")], #list of entries tuples with color
           [(clean_long_exits, "yellow"), (clean_short_exits, "pink")]), #list of exits tuples with color
)

# # Create the chart with the panel
ch = chart([pane1], title="Chart with EntryShort/ExitShort (yellow) and EntryLong/ExitLong markers (pink)", session=None, size="s")
```
<img width="800" alt="image" src="https://github.com/drew2323/lightweight-charts-python/assets/28433232/0acde2bf-600e-4f45-8db0-5077822d6993">


<div align="center">
    
# lightweight-charts-python

[![PyPi Release](https://img.shields.io/pypi/v/lightweight-charts?color=32a852&label=PyPi)](https://pypi.org/project/lightweight-charts/)
[![Made with Python](https://img.shields.io/badge/Python-3.8+-c7a002?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
[![License](https://img.shields.io/github/license/louisnw01/lightweight-charts-python?color=9c2400)](https://github.com/louisnw01/lightweight-charts-python/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/index.html)

![cover](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/cover.png)

lightweight-charts-python aims to provide a simple and pythonic way to access and implement [TradingView's Lightweight Charts](https://www.tradingview.com/lightweight-charts/).
</div>


## Installation
```
pip install lightweight-charts
```
___

## Features
1. Streamlined for live data, with methods for updating directly from tick data.
2. Multi-pane charts using [Subcharts](https://lightweight-charts-python.readthedocs.io/en/latest/reference/abstract_chart.html#AbstractChart.create_subchart).
3. The [Toolbox](https://lightweight-charts-python.readthedocs.io/en/latest/reference/toolbox.html), allowing for trendlines, rectangles, rays and horizontal lines to be drawn directly onto charts.
4. [Events](https://lightweight-charts-python.readthedocs.io/en/latest/tutorials/events.html) allowing for timeframe selectors (1min, 5min, 30min etc.), searching, hotkeys, and more.
5. [Tables](https://lightweight-charts-python.readthedocs.io/en/latest/reference/tables.html) for watchlists, order entry, and trade management.
6. Direct integration of market data through [Polygon.io's](https://polygon.io/?utm_source=affiliate&utm_campaign=pythonlwcharts) market data API.

__Supports:__ Jupyter Notebooks, PyQt6, PyQt5, PySide6, wxPython, Streamlit, and asyncio.

PartTimeLarry: [Interactive Brokers API and TradingView Charts in Python](https://www.youtube.com/watch?v=TlhDI3PforA)
___

### 1. Display data from a csv:

```python
import pandas as pd
from lightweight_charts import Chart


if __name__ == '__main__':
    
    chart = Chart()
    
    # Columns: time | open | high | low | close | volume 
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    
    chart.show(block=True)

```
![setting_data image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/1_setting_data/setting_data.png)
___

### 2. Updating bars in real-time:

```python
import pandas as pd
from time import sleep
from lightweight_charts import Chart

if __name__ == '__main__':

    chart = Chart()

    df1 = pd.read_csv('ohlcv.csv')
    df2 = pd.read_csv('next_ohlcv.csv')

    chart.set(df1)

    chart.show()

    last_close = df1.iloc[-1]['close']
    
    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')
            
        last_close = series['close']
        sleep(0.1)

```

![live data gif](https://github.com/louisnw01/lightweight-charts-python/blob/main/examples/2_live_data/live_data.gif?raw=true)
___

### 3. Updating bars from tick data in real-time:

```python
import pandas as pd
from time import sleep
from lightweight_charts import Chart


if __name__ == '__main__':
    
    df1 = pd.read_csv('ohlc.csv')
    
    # Columns: time | price 
    df2 = pd.read_csv('ticks.csv')
    
    chart = Chart()
    
    chart.set(df1)
    
    chart.show()
    
    for i, tick in df2.iterrows():
        chart.update_from_tick(tick)
            
        sleep(0.03)

```
![tick data gif](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/3_tick_data/tick_data.gif)
___

### 4. Line Indicators:

```python
import pandas as pd
from lightweight_charts import Chart


def calculate_sma(df, period: int = 50):
    return pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()


if __name__ == '__main__':
    chart = Chart()
    chart.legend(visible=True)

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)

    line = chart.create_line('SMA 50')
    sma_data = calculate_sma(df, period=50)
    line.set(sma_data)

    chart.show(block=True)

```
![line indicators image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/4_line_indicators/line_indicators.png)
___

### 5. Styling:

```python
import pandas as pd
from lightweight_charts import Chart


if __name__ == '__main__':
    
    chart = Chart()

    df = pd.read_csv('ohlcv.csv')

    chart.layout(background_color='#090008', text_color='#FFFFFF', font_size=16,
                 font_family='Helvetica')

    chart.candle_style(up_color='#00ff55', down_color='#ed4807',
                       border_up_color='#FFFFFF', border_down_color='#FFFFFF',
                       wick_up_color='#FFFFFF', wick_down_color='#FFFFFF')

    chart.volume_config(up_color='#00ff55', down_color='#ed4807')

    chart.watermark('1D', color='rgba(180, 180, 240, 0.7)')

    chart.crosshair(mode='normal', vert_color='#FFFFFF', vert_style='dotted',
                    horz_color='#FFFFFF', horz_style='dotted')

    chart.legend(visible=True, font_size=14)

    chart.set(df)

    chart.show(block=True)

```
![styling image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/5_styling/styling.png)
___

### 6. Callbacks:

```python
import pandas as pd
from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


def on_search(chart, searched_string):  # Called when the user searches.
    new_data = get_bar_data(searched_string, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.topbar['symbol'].set(searched_string)
    chart.set(new_data)


def on_timeframe_selection(chart):  # Called when the user changes the timeframe.
    new_data = get_bar_data(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.set(new_data, True)


def on_horizontal_line_move(chart, line):
    print(f'Horizontal line moved to: {line.price}')


if __name__ == '__main__':
    chart = Chart(toolbox=True)
    chart.legend(True)

    chart.events.search += on_search

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', ('1min', '5min', '30min'), default='5min',
                          func=on_timeframe_selection)

    df = get_bar_data('TSLA', '5min')
    chart.set(df)

    chart.horizontal_line(200, func=on_horizontal_line_move)

    chart.show(block=True)

```
![callbacks gif](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/6_callbacks/callbacks.gif)
___

<div align="center">

[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/index.html)

Inquiries: [shaders_worker_0e@icloud.com](mailto:shaders_worker_0e@icloud.com)
___

_This package is an independent creation and has not been endorsed, sponsored, or approved by TradingView. The author of this package does not have any official relationship with TradingView, and the package does not represent the views or opinions of TradingView._
</div>
