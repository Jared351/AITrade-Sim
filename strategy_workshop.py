# strategy_workshop.py (v3 - API服务版)

from flask import Flask, request, jsonify
import uuid
import copy
import json

# --- 1. 创建Flask应用 ---
app = Flask(__name__)

# --- 2. 固定的策略模板 (这部分保持不变) ---
template_value = {
  "templateId": "template_value_01",
  "strategyName": "价值投资精选",
  "strategyType": "价值投资",
  "description": "寻找财务健康、但当前股价被市场低估的公司，适合长期持有。",
  "rules": {
    "universe": ["沪深300"], "entryConditions": {"logic": "AND", "conditions": [{"factor": "PE_TTM", "operator": "<", "value": 15}, {"factor": "PB", "operator": "<", "value": 2}, {"factor": "ROE", "operator": ">", "value": 12}]}, "exitConditions": {"logic": "OR", "conditions": [{"factor": "STOP_LOSS_PERCENT", "operator": "<=", "value": -10}, {"factor": "TAKE_PROFIT_PERCENT", "operator": ">=", "value": 25}]}, "positionSizing": {"maxPositions": 5, "sizingMethod": "EQUAL_WEIGHT"}, "rebalancing": {"frequency": "QUARTERLY"}
  }
}

template_trend = {
  "templateId": "template_trend_01",
  "strategyName": "趋势跟踪入门",
  "strategyType": "趋势跟踪",
  "description": "追随市场强势股，当股价突破关键阻力位时买入，适合能承受较大波动的投资者。",
  "rules": {
    "universe": ["全市场"], "entryConditions": {"logic": "AND", "conditions": [{"factor": "PRICE_VS_MA60", "operator": ">", "value": 1.1}, {"factor": "TURNOVER_RATE_5D", "operator": ">", "value": 3}]}, "exitConditions": {"logic": "OR", "conditions": [{"factor": "STOP_LOSS_PERCENT", "operator": "<=", "value": -8}, {"factor": "PRICE_VS_MA20", "operator": "<", "value": 1}]}, "positionSizing": {"maxPositions": 8, "sizingMethod": "EQUAL_WEIGHT"}, "rebalancing": {"frequency": "MONTHLY"}
  }
}

# --- 3. 核心函数 (这部分保持不变) ---
def create_custom_strategy(answers, user_id):
    """
    功能2 (已升级)：根据用户的一系列回答，动态构建一个全新的、个性化的策略。
    """
    rules = {}
    style = answers.get('style', 'value')
    if style == 'value':
        rules['entryConditions'] = {"logic": "AND", "conditions": [{"factor": "PE_TTM", "operator": "<", "value": 20}, {"factor": "ROE", "operator": ">", "value": 10}]}
        strategy_type_cn = "价值型"
    elif style == 'growth':
        rules['entryConditions'] = {"logic": "AND", "conditions": [{"factor": "G_REVENUE_YOY", "operator": ">", "value": 20}, {"factor": "G_PROFIT_YOY", "operator": ">", "value": 20}]}
        strategy_type_cn = "成长型"
    else: # trend
        rules['entryConditions'] = {"logic": "AND", "conditions": [{"factor": "PRICE_VS_MA60", "operator": ">", "value": 1.05}]}
        strategy_type_cn = "趋势型"

    risk = answers.get('risk_tolerance', 'medium')
    stop_loss_map = {'low': -8, 'medium': -15, 'high': -22}
    risk_cn = {'low': "稳健", 'medium': "平衡", 'high': "进取"}[risk]
    rules['exitConditions'] = {"logic": "OR", "conditions": [{"factor": "STOP_LOSS_PERCENT", "operator": "<=", "value": stop_loss_map[risk]}]}

    horizon = answers.get('horizon', 'medium')
    rebalancing_map = {'short': "MONTHLY", 'medium': "QUARTERLY", 'long': "HALF_YEARLY"}
    horizon_cn = {'short': "短期", 'medium': "中期", 'long': "长期"}[horizon]
    rules['rebalancing'] = {"frequency": rebalancing_map[horizon]}

    rules['universe'] = ["沪深300"]
    rules['positionSizing'] = {"maxPositions": 10, "sizingMethod": "EQUAL_WEIGHT"}

    strategy_name = f"{user_id}的{horizon_cn}{risk_cn}{strategy_type_cn}策略"
    description = f"一个根据您的{horizon_cn}投资期限、{risk_cn}风险偏好和{strategy_type_cn}投资风格定制的策略。"

    final_strategy = {
        "strategyId": "strategy_" + str(uuid.uuid4()),
        "strategyName": strategy_name,
        "strategyType": strategy_type_cn,
        "creationMethod": "ai_guided",
        "authorId": user_id,
        "description": description,
        "rules": rules
    }
    return final_strategy

# --- 4. 创建API接口 ---
@app.route('/create_strategy', methods=['POST'])
def api_create_strategy():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        answers = data.get('answers')
        user_id = data.get('user_id')

        if not answers or not user_id:
            return jsonify({"error": "Missing 'answers' or 'user_id' in request body"}), 400

        strategy = create_custom_strategy(answers, user_id)
        return jsonify(strategy)
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "An internal error occurred"}), 500

# --- 5. 用于本地测试的启动代码 ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)