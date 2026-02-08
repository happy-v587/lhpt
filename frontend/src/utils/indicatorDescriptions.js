/**
 * 技术指标说明和描述
 */

export const indicatorDescriptions = {
  // 趋势类指标
  MA: {
    name: '移动平均线',
    fullName: 'Moving Average',
    description: '计算一定周期内的平均价格，用于判断价格趋势方向',
    usage: '当短期MA上穿长期MA时为金叉（买入信号），下穿为死叉（卖出信号）',
    params: {
      periods: '计算周期数组，如[5,10,20]表示5日、10日、20日均线'
    },
    example: 'MA5 > MA10 表示短期趋势向上'
  },
  
  EMA: {
    name: '指数移动平均线',
    fullName: 'Exponential Moving Average',
    description: '对近期价格赋予更高权重的移动平均线，反应更灵敏',
    usage: '比MA更快地反应价格变化，适合短线交易',
    params: {
      periods: '计算周期数组，常用[12,26,50]'
    },
    example: 'EMA12 > EMA26 表示短期上涨趋势'
  },
  
  MACD: {
    name: '指数平滑异同移动平均线',
    fullName: 'Moving Average Convergence Divergence',
    description: '通过快慢两条EMA的差值来判断趋势强度和转折点',
    usage: 'DIF上穿DEA为金叉（买入），下穿为死叉（卖出）；MACD柱状图由负转正为买入信号',
    params: {
      fast_period: '快线周期，默认12',
      slow_period: '慢线周期，默认26',
      signal_period: '信号线周期，默认9'
    },
    example: 'DIF > DEA 且 MACD > 0 表示强势上涨'
  },
  
  BOLL: {
    name: '布林带',
    fullName: 'Bollinger Bands',
    description: '由中轨（MA）和上下轨（标准差）组成，用于判断价格波动范围',
    usage: '价格触及下轨可能反弹（买入），触及上轨可能回调（卖出）',
    params: {
      period: '移动平均周期，默认20',
      std_dev: '标准差倍数，默认2.0'
    },
    example: 'close < BOLL_lower 表示超卖，可能反弹'
  },
  
  DMI: {
    name: '趋向指标',
    fullName: 'Directional Movement Index',
    description: '通过+DI和-DI判断趋势方向，ADX判断趋势强度',
    usage: '+DI上穿-DI为买入信号，ADX>25表示趋势明显',
    params: {
      period: '计算周期，默认14'
    },
    example: 'ADX > 25 且 +DI > -DI 表示强势上涨'
  },
  
  // 动量类指标
  RSI: {
    name: '相对强弱指标',
    fullName: 'Relative Strength Index',
    description: '衡量价格涨跌速度的动量指标，范围0-100',
    usage: 'RSI<30为超卖（买入信号），RSI>70为超买（卖出信号）',
    params: {
      period: '计算周期，默认14'
    },
    example: 'RSI < 30 表示超卖，可能反弹'
  },
  
  KDJ: {
    name: '随机指标',
    fullName: 'Stochastic Oscillator',
    description: '通过K、D、J三条线判断超买超卖状态，范围0-100',
    usage: 'K线上穿D线为金叉（买入），J<20为超卖，J>80为超买',
    params: {
      n: 'RSV周期，默认9',
      m1: 'K值平滑周期，默认3',
      m2: 'D值平滑周期，默认3'
    },
    example: 'K > D 且 J < 20 表示超卖后开始反弹'
  },
  
  CCI: {
    name: '顺势指标',
    fullName: 'Commodity Channel Index',
    description: '衡量价格偏离统计平均值的程度，无固定范围',
    usage: 'CCI>100为超买，CCI<-100为超卖',
    params: {
      period: '计算周期，默认14'
    },
    example: 'CCI < -100 表示超卖，可能反弹'
  },
  
  WR: {
    name: '威廉指标',
    fullName: 'Williams %R',
    description: '衡量超买超卖的动量指标，范围0到-100',
    usage: 'WR<-80为超卖（买入），WR>-20为超买（卖出）',
    params: {
      period: '计算周期，默认14'
    },
    example: 'WR < -80 表示超卖区域'
  },
  
  // 波动类指标
  ATR: {
    name: '平均真实波幅',
    fullName: 'Average True Range',
    description: '衡量价格波动幅度的指标，用于设置止损位',
    usage: 'ATR值越大表示波动越剧烈，可用于调整仓位大小',
    params: {
      period: '计算周期，默认14'
    },
    example: 'ATR > 历史平均值 表示波动加大，需谨慎'
  },
  
  // 成交量类指标
  OBV: {
    name: '能量潮指标',
    fullName: 'On Balance Volume',
    description: '通过累计成交量变化判断资金流向',
    usage: 'OBV上升表示资金流入（看涨），下降表示资金流出（看跌）',
    params: {},
    example: 'OBV持续上升 且 价格上涨 表示上涨动能强'
  },
  
  VWAP: {
    name: '成交量加权平均价',
    fullName: 'Volume Weighted Average Price',
    description: '考虑成交量的平均价格，反映真实的市场成本',
    usage: '价格高于VWAP表示强势，低于VWAP表示弱势',
    params: {},
    example: 'close > VWAP 表示价格在平均成本之上'
  }
}

/**
 * 回测指标说明
 */
export const backtestMetrics = {
  initial_capital: {
    name: '初始资金',
    description: '回测开始时的资金总额'
  },
  final_capital: {
    name: '最终资金',
    description: '回测结束时的资金总额'
  },
  total_return: {
    name: '总收益率',
    description: '(最终资金 - 初始资金) / 初始资金，表示整个回测期间的收益率',
    format: '百分比',
    example: '0.15 表示 15% 收益'
  },
  annual_return: {
    name: '年化收益率',
    description: '将总收益率按年计算，便于与其他投资比较',
    format: '百分比',
    example: '0.20 表示年化 20% 收益'
  },
  sharpe_ratio: {
    name: '夏普比率',
    description: '风险调整后的收益率，衡量每承担一单位风险获得的超额回报',
    interpretation: '> 1 良好，> 2 优秀，> 3 卓越',
    formula: '(投资回报率 - 无风险利率) / 收益标准差',
    example: '1.5 表示每承担1单位风险获得1.5单位超额收益'
  },
  max_drawdown: {
    name: '最大回撤',
    description: '从峰值到谷底的最大跌幅，衡量最坏情况下的损失',
    format: '负百分比',
    example: '-0.15 表示最大回撤 15%'
  },
  win_rate: {
    name: '胜率',
    description: '盈利交易次数 / 总交易次数',
    format: '百分比',
    example: '0.60 表示 60% 的交易是盈利的'
  },
  total_trades: {
    name: '总交易次数',
    description: '回测期间执行的买卖次数总和'
  },
  winning_trades: {
    name: '盈利交易次数',
    description: '卖出价格高于买入价格的交易次数'
  },
  losing_trades: {
    name: '亏损交易次数',
    description: '卖出价格低于买入价格的交易次数'
  }
}

/**
 * 操作符说明
 */
export const operatorDescriptions = {
  '>': '大于',
  '<': '小于',
  '>=': '大于等于',
  '<=': '小于等于',
  '==': '等于',
  'cross_up': '上穿（从下方穿过）',
  'cross_down': '下穿（从上方穿过）'
}

/**
 * 获取指标的简短描述
 */
export function getIndicatorShortDesc(type) {
  const indicator = indicatorDescriptions[type]
  return indicator ? `${indicator.name} - ${indicator.description}` : type
}

/**
 * 获取指标的完整说明
 */
export function getIndicatorFullDesc(type) {
  return indicatorDescriptions[type] || null
}

/**
 * 获取回测指标说明
 */
export function getMetricDesc(metric) {
  return backtestMetrics[metric] || null
}
