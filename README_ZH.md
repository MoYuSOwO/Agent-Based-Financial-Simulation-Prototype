# Agent-Based Financial Simulation Prototype

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

基于智能体的金融市场模拟原型系统，探索异质交易者互动对市场价格形成的影响。

🇬🇧 [English Documentation](README.md) | 🇨🇳 **中文**

## 目录
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [Agent模型](#agent模型)
- [发展方向](#发展方向)
- [贡献指南](#贡献指南)
- [许可协议](#许可协议)

## 核心特性

### 已实现功能
- 🎭 三类基础Agent模型
  - **噪声交易者 (Noise Traders)**：随机交易行为模拟市场流动性
  - **趋势跟踪者 (Momentum Traders)**：移动平均策略驱动价格动量
  - **价值投资者 (Value Investors)**：基于基本面分析的均值回归策略
- 📈 简化版市场引擎
  - 基于订单流的市价单撮合机制
  - 动态市场深度调整模型
  - 可配置的交易时段规则
  - Agent数量在一定比例范围内时保证市场的持续稳定运行，但超出范围会出现不稳定的市场波动反应，以学术理论依据反向印证模型有效性
- 📊 基础数据分析
  - Tick级交易数据记录
  - 自动生成OHLC K线数据

## Agent模型

### 噪声交易者 (NT)
- **决策逻辑**：随机生成买卖信号

### 趋势跟踪者 (MT)
- **决策逻辑**：
  ```math
  \text{Signal} = \frac{\text{P}_{t} - \text{SMA}_{t}}{\sigma_{t}}
  ```

### 价值投资者 (VI)
- **决策逻辑**：对比设定的基础价值，随机系数模拟个性化决策

## 发展方向

### 性能调优
- [x] 降低代码的时间复杂度

### 模型扩展
- [ ] 现有Agent更好的决策模型
- [ ] 简化的订单簿维护
- [ ] 新增Agent类型（高频交易者、做市商）
- [ ] 引入杠杆与卖空机制
- [ ] 企业基本面动态演化模型
- [ ] 由一支股票拓展为多支股票市场
- [ ] 添加其他金融衍生品

### 系统优化
- [ ] 分布式计算支持
- [ ] 实时可视化仪表盘
- [ ] 历史回测接口
- [ ] 多语言支持、配置文件分离

### 学术验证
- [ ] 收益率分布检验（厚尾特征）
- [ ] 波动率聚类模拟
- [ ] 微观结构效应分析

## 贡献指南

欢迎通过以下方式参与贡献：
1. 提交Issue报告问题或建议
2. Fork仓库并提交Pull Request
3. 完善文档与测试用例
4. 分享应用案例与研究结果

请遵循我们的[贡献规范](CONTRIBUTING.md)进行协作。

## 许可协议

本项目采用 [MIT License](LICENSE)，允许自由使用、修改和分发代码。学术研究引用请注明出处。

---
**研究合作**：欢迎高校与研究机构合作进行金融复杂性研究，联系邮箱：houjunhuang@link.cuhk.edu.cn