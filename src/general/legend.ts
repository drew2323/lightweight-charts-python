import { ISeriesApi, LineData, Logical, MouseEventParams, PriceFormatBuiltIn, SeriesType } from "lightweight-charts";
import { Handler } from "./handler";

interface LineElement {
    name: string;
    div: HTMLDivElement;
    row: HTMLDivElement;
    toggle: HTMLDivElement,
    series: ISeriesApi<SeriesType>,
    solid: string;
}

export class Legend {
    private handler: Handler;
    public div: HTMLDivElement;
    public contentWrapper: HTMLDivElement;
    private collapseButton: HTMLDivElement;
    private toggleAllButton: HTMLDivElement;
    private isCollapsed: boolean = false;
    private allVisible: boolean = true;

    private ohlcEnabled: boolean = false;
    private percentEnabled: boolean = false;
    private linesEnabled: boolean = false;
    private colorBasedOnCandle: boolean = false;

    private text: HTMLSpanElement;
    private candle: HTMLDivElement;
    public _lines: LineElement[] = [];

    constructor(handler: Handler) {
        this.legendHandler = this.legendHandler.bind(this)
    
        this.handler = handler;
        this.ohlcEnabled = false;
        this.percentEnabled = false
        this.linesEnabled = false
        this.colorBasedOnCandle = false
    
        this.div = document.createElement('div');
        this.div.classList.add('legend');
        this.div.style.maxWidth = '300px';
        this.div.style.minWidth = '200px';
        this.div.style.maxHeight = '300px';
        this.div.style.overflowY = 'auto';
        this.div.style.overflowX = 'hidden';
        this.div.style.position = 'absolute';
        this.div.style.backgroundColor = 'rgba(19, 23, 34, 0)';
        this.div.style.color = '#D1D4DC';
        this.div.style.padding = '1px';
        this.div.style.borderRadius = '4px';
        //this.div.style.border = '1px solid rgba(42, 46, 57, 0.85)';
        this.div.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
        this.div.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
        this.div.style.fontSize = '12px';
        this.div.style.zIndex = '5';
        this.div.style.display = 'none';
        this.div.style.pointerEvents = 'all';

        const buttonsContainer = document.createElement('div');
        buttonsContainer.style.position = 'absolute';
        buttonsContainer.style.right = '8px';
        buttonsContainer.style.top = '8px';
        buttonsContainer.style.display = 'flex';
        buttonsContainer.style.gap = '2px';
        buttonsContainer.style.zIndex = '6';
        buttonsContainer.style.pointerEvents = 'all';

        this.collapseButton = document.createElement('div');
        this.collapseButton.style.cursor = 'pointer';
        this.collapseButton.style.width = '20px';
        this.collapseButton.style.height = '20px';
        this.collapseButton.style.display = 'flex';
        this.collapseButton.style.alignItems = 'center';
        this.collapseButton.style.justifyContent = 'center';
        this.collapseButton.style.color = '#D1D4DC';
        this.collapseButton.style.fontSize = '16px';
        this.collapseButton.style.userSelect = 'none';
        this.collapseButton.style.pointerEvents = 'all';
        this.collapseButton.innerHTML = '−';
        this.collapseButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleCollapse();
        });

        this.toggleAllButton = document.createElement('div');
        this.toggleAllButton.style.cursor = 'pointer';
        this.toggleAllButton.style.width = '20px';
        this.toggleAllButton.style.height = '20px';
        this.toggleAllButton.style.display = 'flex';
        this.toggleAllButton.style.alignItems = 'center';
        this.toggleAllButton.style.justifyContent = 'center';
        this.toggleAllButton.style.color = '#D1D4DC';
        this.toggleAllButton.style.fontSize = '14px';
        this.toggleAllButton.style.userSelect = 'none';
        this.toggleAllButton.style.pointerEvents = 'all';
        this.toggleAllButton.innerHTML = '👁️';
        this.toggleAllButton.title = 'Toggle all';
        this.toggleAllButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleAll();
        });

        buttonsContainer.appendChild(this.toggleAllButton);
        buttonsContainer.appendChild(this.collapseButton);
        
        const style = document.createElement('style');
        style.textContent = `
            .legend::-webkit-scrollbar {
                width: 6px;
            }
            .legend::-webkit-scrollbar-track {
                background: #2A2E39;
            }
            .legend::-webkit-scrollbar-thumb {
                background: #434651;
                border-radius: 3px;
            }
            .legend::-webkit-scrollbar-thumb:hover {
                background: #545861;
            }
            .legend-toggle-switch {
                cursor: pointer;
                margin-left: 8px;
            }
        `;
        document.head.appendChild(style);
        
        this.contentWrapper = document.createElement('div');
        this.contentWrapper.style.minHeight = '100%';
        this.contentWrapper.style.width = '100%';
        this.contentWrapper.style.display = 'flex';
        this.contentWrapper.style.flexDirection = 'column';
        this.contentWrapper.style.gap = '1px';
        this.contentWrapper.style.marginTop = '20px';
        this.contentWrapper.style.pointerEvents = 'all';
    
        this.text = document.createElement('span');
        this.text.style.lineHeight = '1';
        this.text.style.display = 'block';
        this.text.style.color = '#D1D4DC';
        
        this.candle = document.createElement('div');
        this.candle.style.color = '#D1D4DC';
        this.candle.style.width = '100%';
    
        this.contentWrapper.appendChild(this.text);
        this.contentWrapper.appendChild(this.candle);
        this.div.appendChild(buttonsContainer);
        this.div.appendChild(this.contentWrapper);
        handler.div.appendChild(this.div);
    
        handler.chart.subscribeCrosshairMove(this.legendHandler)
    }

    private toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            this.contentWrapper.style.display = 'none';
            this.div.style.maxHeight = '40px'; // Changed from 'auto' to fixed height for buttons
            this.div.style.height = '40px';    // Added fixed height
            this.collapseButton.innerHTML = '+';
        } else {
            this.contentWrapper.style.display = 'flex';
            this.div.style.maxHeight = '300px';
            this.div.style.height = 'auto';    // Reset height to auto
            this.collapseButton.innerHTML = '−';
        }
    }

    private toggleAll() {
        this.allVisible = !this.allVisible;
        
        this._lines.forEach(line => {
            line.series.applyOptions({
                visible: this.allVisible
            });

            const group = line.toggle.querySelector('g');
            if (group) {
                if (this.allVisible) {
                    group.innerHTML = this.openEyeSvg(line.solid);
                } else {
                    group.innerHTML = this.closedEyeSvg(line.solid);
                }
            }
        });

        this.toggleAllButton.style.opacity = this.allVisible ? '1' : '0.5';
    }

    private openEyeSvg(strokeColor: string): string {
        return `
            <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${strokeColor};stroke-opacity:1;stroke-miterlimit:4;" d="M 21.998437 12 C 21.998437 12 18.998437 18 12 18 C 5.001562 18 2.001562 12 2.001562 12 C 2.001562 12 5.001562 6 12 6 C 18.998437 6 21.998437 12 21.998437 12 Z M 21.998437 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>
            <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${strokeColor};stroke-opacity:1;stroke-miterlimit:4;" d="M 15 12 C 15 13.654687 13.654687 15 12 15 C 10.345312 15 9 13.654687 9 12 C 9 10.345312 10.345312 9 12 9 C 13.654687 9 15 10.345312 15 12 Z M 15 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>
        `;
    }

    private closedEyeSvg(strokeColor: string): string {
        return `
            <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${strokeColor};stroke-opacity:1;stroke-miterlimit:4;" d="M 20.001562 9 C 20.001562 9 19.678125 9.665625 18.998437 10.514062 M 12 14.001562 C 10.392187 14.001562 9.046875 13.589062 7.95 12.998437 M 12 14.001562 C 13.607812 14.001562 14.953125 13.589062 16.05 12.998437 M 12 14.001562 L 12 17.498437 M 3.998437 9 C 3.998437 9 4.354687 9.735937 5.104687 10.645312 M 7.95 12.998437 L 5.001562 15.998437 M 7.95 12.998437 C 6.689062 12.328125 5.751562 11.423437 5.104687 10.645312 M 16.05 12.998437 L 18.501562 15.998437 M 16.05 12.998437 C 17.38125 12.290625 18.351562 11.320312 18.998437 10.514062 M 5.104687 10.645312 L 2.001562 12 M 18.998437 10.514062 L 21.998437 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>
        `;
    }

    toJSON() {
        const {_lines, handler, ...serialized} = this;
        return serialized;
    }

    makeSeriesRow(name: string, series: ISeriesApi<SeriesType>) {
        const strokeColor = series.options().color;
        let row = document.createElement('div')
        row.style.display = 'flex'
        row.style.alignItems = 'center'
        row.style.padding = '0px 0'
        row.style.color = '#D1D4DC'
        row.style.width = '100%'
        row.style.pointerEvents = 'all'
        row.style.cursor = 'default'

        let div = document.createElement('div')
        div.style.flex = '1'
        let toggle = document.createElement('div')
        toggle.classList.add('legend-toggle-switch');

        let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "22");
        svg.setAttribute("height", "16");

        let group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.innerHTML = this.openEyeSvg(strokeColor);

        let on = true
        toggle.addEventListener('click', () => {
            if (on) {
                on = false
                group.innerHTML = this.closedEyeSvg(strokeColor);
                series.applyOptions({
                    visible: false
                })
            } else {
                on = true
                series.applyOptions({
                    visible: true
                })
                group.innerHTML = this.openEyeSvg(strokeColor);
            }
        })

        svg.appendChild(group)
        toggle.appendChild(svg);
        row.appendChild(div)
        row.appendChild(toggle)
        this.contentWrapper.appendChild(row)

        const color = series.options().color;
        this._lines.push({
            name: name,
            div: div,
            row: row,
            toggle: toggle,
            series: series,
            solid: color.startsWith('rgba') ? color.replace(/[^,]+(?=\))/, '1') : color
        });
    }

    legendItemFormat(num: number, decimal: number) { 
        return num.toFixed(decimal).toString().padStart(8, ' ') 
    }

    shorthandFormat(num: number) {
        const absNum = Math.abs(num)
        if (absNum >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (absNum >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString().padStart(8, ' ');
    }
    legendHandler(param: MouseEventParams, usingPoint= false) {
        if (!this.ohlcEnabled && !this.linesEnabled && !this.percentEnabled) return;
        const options: any = this.handler.series.options()
    
        if (!param.time) {
            this.candle.style.color = 'transparent'
            this.candle.innerHTML = this.candle.innerHTML.replace(options['upColor'], '').replace(options['downColor'], '')                   
            return
        }
    
        let data: any;
        let logical: Logical | null = null;
    
        if (usingPoint) {
            const timeScale = this.handler.chart.timeScale();
            let coordinate = timeScale.timeToCoordinate(param.time)
            if (coordinate)
            logical = timeScale.coordinateToLogical(coordinate.valueOf())
            if (logical)
            data = this.handler.series.dataByIndex(logical.valueOf())
        }
        else {
            data = param.seriesData.get(this.handler.series);
        }
    
        this.candle.style.color = ''
        let str = '<span style="line-height: 1.0;">'
        if (data) {
            if (this.ohlcEnabled) {
                str += `O ${this.legendItemFormat(data.open, this.handler.precision)} `
                str += `| H ${this.legendItemFormat(data.high, this.handler.precision)} `
                str += `| L ${this.legendItemFormat(data.low, this.handler.precision)} `
                str += `| C ${this.legendItemFormat(data.close, this.handler.precision)} `
            }
    
            if (this.percentEnabled) {
                let percentMove = ((data.close - data.open) / data.open) * 100
                let color = percentMove > 0 ? options['upColor'] : options['downColor']
                let percentStr = `${percentMove >= 0 ? '+' : ''}${percentMove.toFixed(2)} %`
    
                if (this.colorBasedOnCandle) {
                    str += `| <span style="color: ${color};">${percentStr}</span>`
                } else {
                    str += '| ' + percentStr
                }
            }
    
            if (this.handler.volumeSeries) {
                let volumeData: any;
                if (logical) {
                    volumeData = this.handler.volumeSeries.dataByIndex(logical)
                }
                else {
                    volumeData = param.seriesData.get(this.handler.volumeSeries)
                }
                if (volumeData) {
                    str += this.ohlcEnabled ? `<br>V ${this.shorthandFormat(volumeData.value)}` : ''
                }
            }
        }
        this.candle.innerHTML = str + '</span>'
    
        this._lines.forEach((e) => {
            if (!this.linesEnabled) {
                e.row.style.display = 'none'
                return
            }
            e.row.style.display = 'flex'
    
            let data
            if (usingPoint && logical) {
                data = e.series.dataByIndex(logical) as LineData
            }
            else {
                data = param.seriesData.get(e.series) as LineData
            }
            if (data === undefined || data.value === undefined) return;
            let price;
            if (e.series.seriesType() == 'Histogram') {
                price = this.shorthandFormat(data.value)
            } else {
                const format = e.series.options().priceFormat as PriceFormatBuiltIn
                price = this.legendItemFormat(data.value, format.precision)
            }
            e.div.innerHTML = `<span style="color: ${e.solid};">▨ ${e.name} : ${price}</span>`
        })
    }
}