#!/bin/bash

# 回测测试脚本
# 使用方法: ./test_backtest.sh

echo "======================================"
echo "回测功能测试"
echo "======================================"
echo ""

# 配置参数
STRATEGY_ID="ad7994b8-217a-4db1-98eb-1dc77090cc32"
STOCK_CODE="000001.SZ"
START_DATE="2024-01-01"
END_DATE="2024-12-31"
INITIAL_CAPITAL=100000
COMMISSION_RATE=0.0003
SLIPPAGE_RATE=0.0001

echo "测试参数:"
echo "  策略ID: $STRATEGY_ID"
echo "  股票代码: $STOCK_CODE"
echo "  开始日期: $START_DATE"
echo "  结束日期: $END_DATE"
echo "  初始资金: $INITIAL_CAPITAL"
echo "  手续费率: $COMMISSION_RATE"
echo "  滑点率: $SLIPPAGE_RATE"
echo ""

echo "发送回测请求..."
echo ""

# 发送请求
response=$(curl -s 'http://localhost:8000/api/backtests/run' \
  -H 'Content-Type: application/json' \
  --data-raw "{
    \"strategy_id\": \"$STRATEGY_ID\",
    \"stock_code\": \"$STOCK_CODE\",
    \"start_date\": \"$START_DATE\",
    \"end_date\": \"$END_DATE\",
    \"initial_capital\": $INITIAL_CAPITAL,
    \"commission_rate\": $COMMISSION_RATE,
    \"slippage_rate\": $SLIPPAGE_RATE
  }")

# 检查响应
if echo "$response" | grep -q "backtest_id"; then
    echo "✅ 回测成功!"
    echo ""
    echo "回测结果:"
    echo "$response" | python3 -m json.tool
    echo ""
    
    # 提取回测ID
    backtest_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['backtest_id'])")
    echo "回测ID: $backtest_id"
    echo ""
    echo "查看详细结果:"
    echo "  curl http://localhost:8000/api/backtests/$backtest_id | python3 -m json.tool"
    
elif echo "$response" | grep -q "detail"; then
    echo "❌ 回测失败!"
    echo ""
    echo "错误信息:"
    echo "$response" | python3 -m json.tool
    echo ""
    
    # 检查常见错误
    if echo "$response" | grep -q "策略不存在"; then
        echo "提示: 策略ID不存在，请先创建策略"
        echo "  查看所有策略: curl http://localhost:8000/api/strategies | python3 -m json.tool"
    elif echo "$response" | grep -q "没有找到K线数据"; then
        echo "提示: 没有找到K线数据，系统会自动从数据源获取"
        echo "  请检查:"
        echo "  1. 股票代码是否正确 (格式: 000001.SZ 或 600000.SH)"
        echo "  2. 日期范围是否合理 (不能是未来日期)"
        echo "  3. 数据源是否可用"
    fi
else
    echo "❌ 请求失败!"
    echo ""
    echo "响应内容:"
    echo "$response"
fi

echo ""
echo "======================================"
