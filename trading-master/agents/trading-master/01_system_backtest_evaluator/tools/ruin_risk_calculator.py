import argparse
import json

def calculate_expectancy_and_ruin(win_rate, reward_risk_ratio, risk_per_trade_pct):
    """
    计算交易系统的数学期望 (EV)、凯利占比 (Kelly F) 和简化版破产风险 (Risk of Ruin)
    """
    w = float(win_rate)
    l = 1.0 - w
    r = float(reward_risk_ratio)
    risk = float(risk_per_trade_pct) / 100.0
    
    # 1. 计算数学期望 (Expected Value in terms of R)
    ev = (w * r) - l
    
    # 2. 计算凯利公式 (Kelly Criterion)
    # f* = (p * b - q) / b (p:胜率, q:败率, b:赔率/盈亏比)
    if r > 0:
        kelly_pct = (w * r - l) / r
    else:
        kelly_pct = 0
        
    # 3. 计算连续亏损N次的概率 (Probability of losing N times in a row)
    # 假设账户回撤20%视为心理崩溃阈值 (Psychological Ruin)
    max_drawdown_allowed = 0.20
    trades_to_ruin = max_drawdown_allowed / risk if risk > 0 else float('inf')
    prob_of_ruin_streak = l ** trades_to_ruin if trades_to_ruin != float('inf') else 0
    
    result = {
        "Expected_Value_R": round(ev, 3),
        "Is_System_Profitable": ev > 0,
        "Kelly_Suggested_Risk_Pct": round(max(0, kelly_pct) * 100, 2),
        "Consecutive_Losses_To_20_Drawdown": int(trades_to_ruin),
        "Probability_Of_Such_Loss_Streak_Pct": round(prob_of_ruin_streak * 100, 4)
    }
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='System Viability Calculator')
    parser.add_argument('--win_rate', type=float, required=True, help='Estimated Win Rate (0.0 to 1.0)')
    parser.add_argument('--reward_risk', type=float, required=True, help='Reward to Risk Ratio (e.g., 2.0)')
    parser.add_argument('--risk_pct', type=float, required=True, help='Risk per trade percentage (e.g., 1.5)')
    
    args = parser.parse_args()
    
    res = calculate_expectancy_and_ruin(args.win_rate, args.reward_risk, args.risk_pct)
    print(json.dumps(res, indent=4))
