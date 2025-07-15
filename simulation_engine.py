# simulation_engine.py (API服务版)

from flask import Flask, request, jsonify
import random
import json

# --- 1. 创建Flask应用 ---
app = Flask(__name__)

# --- 2. 核心函数 (这部分保持不变) ---
def _generate_fake_historical_data(days=365 * 3):
    """
    (内部函数) 生成一段模拟的股票历史价格数据，用于测试。
    未来这里应替换为调用真实的数据插件。
    """
    price_data = []
    price = 100.0
    for day in range(days):
        move = random.uniform(-2.5, 3.5) 
        price = round(price + move, 2)
        if price < 10:
            price = 10
        price_data.append({'date': f'day_{day+1}', 'price': price})
    return price_data

def run_simulation_and_review(strategy_object):
    """
    核心函数：接收策略，执行模拟，返回一份完整的复盘报告。
    """
    rules = strategy_object['rules']
    historical_data = _generate_fake_historical_data()

    cash = 100000.0
    shares = 0
    transactions = []
    win_trades = 0
    loss_trades = 0
    buy_price = 0.0

    for data_point in historical_data:
        current_price = data_point['price']

        if shares > 0:
            stop_loss_price = buy_price * (1 + rules['exitConditions']['conditions'][0]['value'] / 100)
            if current_price <= stop_loss_price:
                cash += shares * current_price
                profit = (current_price - buy_price) / buy_price
                if profit > 0: win_trades += 1 
                else: loss_trades += 1
                transactions.append(f"{data_point['date']}: SELL at {current_price:.2f} (Stop-Loss, Profit: {profit:.2%})")
                shares = 0
        
        elif shares == 0 and cash > current_price:
            pe_condition = rules['entryConditions']['conditions'][0]
            if current_price < pe_condition['value'] * 10:
                shares_to_buy = cash // current_price
                cash -= shares_to_buy * current_price
                shares = shares_to_buy
                buy_price = current_price
                transactions.append(f"{data_point['date']}: BUY at {current_price:.2f}")

    final_portfolio_value = cash + shares * historical_data[-1]['price']
    total_return_percent = (final_portfolio_value - 100000) / 100000 * 100
    total_trades = win_trades + loss_trades
    win_rate_percent = (win_trades / total_trades * 100) if total_trades > 0 else 0

    insights = []
    if total_return_percent > 15:
        insights.append("策略整体盈利能力不错，跑赢了市场基准。")
    elif total_return_percent < 0:
        insights.append("策略在本次历史回测中出现亏损，建议检查入场和止损条件。")
    if total_trades > 50:
        insights.append("交易较为频繁，请注意交易成本可能带来的影响。")
    elif total_trades < 5:
        insights.append("交易信号较少，策略大部分时间处于空仓状态，可能错过一些机会。")

    report = {
        "strategyName": strategy_object['strategyName'],
        "simulationPeriod": f"{historical_data[0]['date']} to {historical_data[-1]['date']}",
        "performanceMetrics": {
            "totalReturnPercent": round(total_return_percent, 2),
            "winRatePercent": round(win_rate_percent, 2),
            "totalTrades": total_trades
        },
        "aiCoachingInsights": insights,
        "transactionHistory": transactions[:5]
    }
    return report

# --- 3. 创建API接口 ---
@app.route('/run_simulation', methods=['POST'])
def api_run_simulation():
    try:
        strategy_object = request.get_json()
        if not strategy_object:
            return jsonify({"error": "Request body must contain a strategy object"}), 400
        
        review_report = run_simulation_and_review(strategy_object)
        return jsonify(review_report)
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "An internal error occurred"}), 500

# --- 4. 用于本地测试的启动代码 ---
if __name__ == '__main__':
    # 使用不同端口以避免冲突
    app.run(debug=True, host='0.0.0.0', port=5002)