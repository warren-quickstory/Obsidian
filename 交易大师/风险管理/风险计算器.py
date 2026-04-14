#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货交易风险计算器
版本: 1.0
最后更新: 2026年4月10日
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TradeDirection(Enum):
    """交易方向枚举"""
    LONG = "做多"
    SHORT = "做空"


class RiskLevel(Enum):
    """风险级别枚举"""
    NORMAL = "正常"
    WARNING = "警告"
    DANGER = "危险"
    CRITICAL = "临界"


@dataclass
class ContractInfo:
    """合约信息"""
    symbol: str  # 品种代码
    name: str    # 品种名称
    multiplier: float  # 每点价值
    margin_rate: float  # 保证金比例
    min_price_move: float  # 最小变动价位
    exchange: str  # 交易所


@dataclass
class AccountInfo:
    """账户信息"""
    balance: float  # 账户余额
    used_margin: float  # 已用保证金
    floating_pnl: float  # 浮动盈亏
    risk_tolerance: float = 0.02  # 单笔风险容忍度，默认2%


@dataclass
class PositionInfo:
    """持仓信息"""
    symbol: str
    direction: TradeDirection
    entry_price: float
    quantity: int
    stop_loss: float
    take_profit: float


class RiskCalculator:
    """风险计算器主类"""
    
    # 常见期货合约信息
    CONTRACT_DB = {
        "RB": ContractInfo("RB", "螺纹钢", 10, 0.10, 1, "上期所"),
        "HC": ContractInfo("HC", "热轧卷板", 10, 0.10, 1, "上期所"),
        "I": ContractInfo("I", "铁矿石", 100, 0.12, 0.5, "大商所"),
        "J": ContractInfo("J", "焦炭", 100, 0.12, 0.5, "大商所"),
        "JM": ContractInfo("JM", "焦煤", 60, 0.12, 0.5, "大商所"),
        "MA": ContractInfo("MA", "甲醇", 10, 0.08, 1, "郑商所"),
        "TA": ContractInfo("TA", "PTA", 5, 0.07, 2, "郑商所"),
        "CF": ContractInfo("CF", "棉花", 5, 0.07, 5, "郑商所"),
        "SR": ContractInfo("SR", "白糖", 10, 0.07, 1, "郑商所"),
        "CU": ContractInfo("CU", "铜", 5, 0.08, 10, "上期所"),
        "AL": ContractInfo("AL", "铝", 5, 0.08, 5, "上期所"),
        "ZN": ContractInfo("ZN", "锌", 5, 0.08, 5, "上期所"),
        "AU": ContractInfo("AU", "黄金", 1000, 0.08, 0.02, "上期所"),
        "AG": ContractInfo("AG", "白银", 15, 0.10, 1, "上期所"),
        "SC": ContractInfo("SC", "原油", 1000, 0.10, 0.1, "能源中心"),
        "FU": ContractInfo("FU", "燃料油", 10, 0.10, 1, "上期所"),
        "BU": ContractInfo("BU", "沥青", 10, 0.10, 2, "上期所"),
        "IF": ContractInfo("IF", "沪深300股指", 300, 0.12, 0.2, "中金所"),
        "IC": ContractInfo("IC", "中证500股指", 200, 0.14, 0.2, "中金所"),
        "IH": ContractInfo("IH", "上证50股指", 300, 0.12, 0.2, "中金所"),
    }
    
    def __init__(self, account: AccountInfo):
        self.account = account
        self.positions: List[PositionInfo] = []
        
    def add_position(self, position: PositionInfo):
        """添加持仓"""
        self.positions.append(position)
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               stop_loss: float, direction: TradeDirection,
                               risk_percentage: float = None) -> Tuple[int, Dict]:
        """
        计算建议仓位大小
        
        参数:
            symbol: 品种代码
            entry_price: 入场价格
            stop_loss: 止损价格
            direction: 交易方向
            risk_percentage: 风险比例，默认使用账户设置
            
        返回:
            (建议手数, 详细计算信息)
        """
        if symbol not in self.CONTRACT_DB:
            raise ValueError(f"未知品种: {symbol}")
        
        contract = self.CONTRACT_DB[symbol]
        risk_pct = risk_percentage or self.account.risk_tolerance
        
        # 计算止损点数
        if direction == TradeDirection.LONG:
            stop_loss_pips = entry_price - stop_loss
        else:  # SHORT
            stop_loss_pips = stop_loss - entry_price
        
        if stop_loss_pips <= 0:
            raise ValueError("止损价格设置错误")
        
        # 计算最大风险金额
        max_risk_amount = self.account.balance * risk_pct
        
        # 计算每手风险金额
        risk_per_contract = stop_loss_pips * contract.multiplier
        
        # 计算建议手数
        suggested_qty = math.floor(max_risk_amount / risk_per_contract)
        
        # 计算实际风险金额
        actual_risk = suggested_qty * risk_per_contract
        actual_risk_pct = actual_risk / self.account.balance
        
        # 计算所需保证金
        required_margin = suggested_qty * entry_price * contract.multiplier * contract.margin_rate
        
        result = {
            "symbol": symbol,
            "contract_name": contract.name,
            "direction": direction.value,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "stop_loss_pips": stop_loss_pips,
            "risk_per_contract": risk_per_contract,
            "max_risk_amount": max_risk_amount,
            "suggested_quantity": suggested_qty,
            "actual_risk_amount": actual_risk,
            "actual_risk_percentage": actual_risk_pct,
            "required_margin": required_margin,
            "margin_ratio": required_margin / self.account.balance,
            "risk_reward_info": "需手动计算止盈目标"
        }
        
        return suggested_qty, result
    
    def calculate_risk_reward(self, entry_price: float, stop_loss: float,
                            take_profit: float, direction: TradeDirection) -> Dict:
        """
        计算风险收益比
        
        参数:
            entry_price: 入场价格
            stop_loss: 止损价格
            take_profit: 止盈价格
            direction: 交易方向
            
        返回:
            风险收益信息
        """
        if direction == TradeDirection.LONG:
            risk_amount = entry_price - stop_loss
            reward_amount = take_profit - entry_price
        else:  # SHORT
            risk_amount = stop_loss - entry_price
            reward_amount = entry_price - take_profit
        
        if risk_amount <= 0:
            raise ValueError("风险金额计算错误")
        
        risk_reward_ratio = reward_amount / risk_amount
        
        return {
            "risk_amount": risk_amount,
            "reward_amount": reward_amount,
            "risk_reward_ratio": risk_reward_ratio,
            "evaluation": self._evaluate_rr_ratio(risk_reward_ratio)
        }
    
    def _evaluate_rr_ratio(self, ratio: float) -> str:
        """评估风险收益比"""
        if ratio >= 3:
            return "优秀 (≥3:1)"
        elif ratio >= 2:
            return "良好 (2:1-3:1)"
        elif ratio >= 1.5:
            return "一般 (1.5:1-2:1)"
        else:
            return "较差 (<1.5:1)"
    
    def calculate_portfolio_risk(self) -> Dict:
        """
        计算投资组合整体风险
        
        返回:
            组合风险信息
        """
        if not self.positions:
            return {"total_risk": 0, "risk_level": RiskLevel.NORMAL.value}
        
        total_risk = 0
        symbol_risks = {}
        
        for pos in self.positions:
            contract = self.CONTRACT_DB.get(pos.symbol)
            if not contract:
                continue
            
            # 计算当前价格（简化处理，使用入场价）
            current_price = pos.entry_price
            
            # 计算单笔持仓风险
            if pos.direction == TradeDirection.LONG:
                risk_per_contract = (pos.entry_price - pos.stop_loss) * contract.multiplier
            else:  # SHORT
                risk_per_contract = (pos.stop_loss - pos.entry_price) * contract.multiplier
            
            position_risk = risk_per_contract * pos.quantity
            total_risk += position_risk
            
            # 记录品种风险
            if pos.symbol not in symbol_risks:
                symbol_risks[pos.symbol] = 0
            symbol_risks[pos.symbol] += position_risk
        
        # 计算风险比例
        total_risk_pct = total_risk / self.account.balance
        
        # 评估风险级别
        risk_level = self._assess_risk_level(total_risk_pct)
        
        # 计算保证金使用率
        total_margin = sum(
            pos.quantity * pos.entry_price * self.CONTRACT_DB[pos.symbol].multiplier * 
            self.CONTRACT_DB[pos.symbol].margin_rate 
            for pos in self.positions if pos.symbol in self.CONTRACT_DB
        )
        margin_ratio = total_margin / self.account.balance
        
        return {
            "total_risk_amount": total_risk,
            "total_risk_percentage": total_risk_pct,
            "risk_level": risk_level.value,
            "symbol_risks": symbol_risks,
            "total_margin": total_margin,
            "margin_ratio": margin_ratio,
            "available_balance": self.account.balance - total_margin + self.account.floating_pnl
        }
    
    def _assess_risk_level(self, risk_pct: float) -> RiskLevel:
        """评估风险级别"""
        if risk_pct <= 0.3:
            return RiskLevel.NORMAL
        elif risk_pct <= 0.5:
            return RiskLevel.WARNING
        elif risk_pct <= 0.7:
            return RiskLevel.DANGER
        else:
            return RiskLevel.CRITICAL
    
    def calculate_daily_loss_limit(self) -> Dict:
        """
        计算单日亏损限额
        
        返回:
            单日风险限制信息
        """
        daily_limit_pct = 0.05  # 单日最大亏损5%
        daily_limit_amount = self.account.balance * daily_limit_pct
        
        # 计算当前已实现亏损（简化处理）
        realized_loss = 0  # 实际应用中应从交易记录获取
        
        remaining_daily_limit = daily_limit_amount - realized_loss
        
        return {
            "daily_limit_percentage": daily_limit_pct,
            "daily_limit_amount": daily_limit_amount,
            "realized_loss": realized_loss,
            "remaining_daily_limit": remaining_daily_limit,
            "can_trade": remaining_daily_limit > 0
        }
    
    def generate_risk_report(self) -> str:
        """生成风险报告"""
        portfolio_risk = self.calculate_portfolio_risk()
        daily_limit = self.calculate_daily_loss_limit()
        
        report = []
        report.append("=" * 60)
        report.append("期货交易风险报告")
        report.append("=" * 60)
        report.append(f"报告时间: 2026-04-10")
        report.append(f"账户余额: ¥{self.account.balance:,.2f}")
        report.append(f"已用保证金: ¥{self.account.used_margin:,.2f}")
        report.append(f"浮动盈亏: ¥{self.account.floating_pnl:,.2f}")
        report.append("")
        
        report.append("持仓风险分析:")
        report.append("-" * 40)
        report.append(f"总风险金额: ¥{portfolio_risk['total_risk_amount']:,.2f}")
        report.append(f"总风险比例: {portfolio_risk['total_risk_percentage']:.2%}")
        report.append(f"风险级别: {portfolio_risk['risk_level']}")
        report.append(f"保证金使用率: {portfolio_risk['margin_ratio']:.2%}")
        report.append(f"可用资金: ¥{portfolio_risk['available_balance']:,.2f}")
        report.append("")
        
        report.append("单日风险限制:")
        report.append("-" * 40)
        report.append(f"单日亏损限额: ¥{daily_limit['daily_limit_amount']:,.2f}")
        report.append(f"已实现亏损: ¥{daily_limit['realized_loss']:,.2f}")
        report.append(f"剩余限额: ¥{daily_limit['remaining_daily_limit']:,.2f}")
        report.append(f"是否可交易: {'是' if daily_limit['can_trade'] else '否'}")
        report.append("")
        
        if self.positions:
            report.append("持仓明细:")
            report.append("-" * 40)
            for pos in self.positions:
                contract = self.CONTRACT_DB.get(pos.symbol, ContractInfo(pos.symbol, "未知", 1, 0.1, 1, "未知"))
                risk_per_contract = abs(pos.entry_price - pos.stop_loss) * contract.multiplier
                position_risk = risk_per_contract * pos.quantity
                
                report.append(f"{pos.symbol} ({contract.name}):")
                report.append(f"  方向: {pos.direction.value}")
                report.append(f"  手数: {pos.quantity}")
                report.append(f"  入场价: {pos.entry_price}")
                report.append(f"  止损价: {pos.stop_loss}")
                report.append(f"  止盈价: {pos.take_profit}")
                report.append(f"  单笔风险: ¥{position_risk:,.2f}")
                report.append("")
        
        report.append("风险建议:")
        report.append("-" * 40)
        if portfolio_risk['risk_level'] == RiskLevel.CRITICAL.value:
            report.append("⚠️ 风险级别: 临界 - 建议立即减仓或平仓")
        elif portfolio_risk['risk_level'] == RiskLevel.DANGER.value:
            report.append("⚠️ 风险级别: 危险 - 建议停止新开仓，考虑减仓")
        elif portfolio_risk['risk_level'] == RiskLevel.WARNING.value:
            report.append("⚠️ 风险级别: 警告 - 建议谨慎开仓，控制风险")
        else:
            report.append("✅ 风险级别: 正常 - 可正常交易")
        
        if not daily_limit['can_trade']:
            report.append("❌ 单日亏损已达限额 - 建议停止当日交易")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# 使用示例
if __name__ == "__main__":
    # 创建账户信息
    account = AccountInfo(
        balance=1000000,  # 100万账户
        used_margin=200000,
        floating_pnl=15000,
        risk_tolerance=0.02  # 2%单笔风险
    )
    
    # 创建风险计算器
    calculator = RiskCalculator(account)
    
    # 示例1: 计算螺纹钢交易仓位
    print("示例1: 螺纹钢交易仓位计算")
    print("-" * 40)
    
    try:
        qty, details = calculator.calculate_position_size(
            symbol="RB",
            entry_price=3800,
            stop_loss=3750,
            direction=TradeDirection.LONG
        )
        
        print(f"品种: {details['contract_name']} ({details['symbol']})")
        print(f"方向: {details['direction']}")
        print(f"入场价: {details['entry_price']}")
        print(f"止损价: {details['stop_loss']}")
        print(f"止损点数: {details['stop_loss_pips']}")
        print(f"每手风险: ¥{details['risk_per_contract']:,.2f}")
        print(f"最大风险金额: ¥{details['max_risk_amount']:,.2f}")
        print(f"建议手数: {details['suggested_quantity']}")
        print(f"实际风险金额: ¥{details['actual_risk_amount']:,.2f}")
        print(f"实际风险比例: {details['actual_risk_percentage']:.2%}")
        print(f"所需保证金: ¥{details['required_margin']:,.2f}")
        print(f"保证金比例: {details['margin_ratio']:.2%}")
    except ValueError as e:
        print(f"计算错误: {e}")
    
    print("\n" + "=" * 60 + "\n")
    
    # 示例2: 计算风险收益比
    print("示例2: 风险收益比计算")
    print("-" * 40)
    
    rr_info = calculator.calculate_risk_reward(
        entry_price=3800,
        stop_loss=3750,
        take_profit=3900,
        direction=TradeDirection.LONG
    )
    
    print(f"风险金额: {rr_info['risk_amount']}点")
    print(f"收益金额: {rr_info['reward_amount']}点")
    print(f"风险收益比: {rr_info['risk_reward_ratio']:.2f}:1")
    print(f"评估: {rr_info['evaluation']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # 示例3: 添加持仓并生成风险报告
    print("示例3: 投资组合风险报告")
    print("-" * 40)
    
    # 添加一些示例持仓
    calculator.add_position(PositionInfo(
        symbol="RB",
        direction=TradeDirection.LONG,
        entry_price=3800,
        quantity=10,
        stop_loss=3750,
        take_profit=3900
    ))
    
    calculator.add_position(PositionInfo(
        symbol="I",
        direction=TradeDirection.SHORT,
        entry_price=850,
        quantity=5,
        stop_loss=870,
        take_profit=800
    ))
    
    # 生成风险报告
    report = calculator.generate_risk_report()
    print(report)