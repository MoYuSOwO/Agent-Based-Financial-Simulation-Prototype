# Agent-Based Financial Simulation Prototype

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

An agent-based financial market simulation prototype exploring how heterogeneous trader interactions influence price formation.

🇨🇳 [中文文档](README_ZH.md) | 🇬🇧 **English** 

## Table of Contents
- [Key Features](#key-features)
- [Getting Started](#getting-started)
- [Agent Models](#agent-models)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

## Key Features

### Implemented Features
- 🎭 Three Core Agent Types
  - **Noise Traders (NT)**: Generate random orders to simulate market liquidity
  - **Momentum Traders (MT)**: Drive price trends using moving-average strategies
  - **Value Investors (VI)**: Mean-reversion strategies based on fundamental analysis
- 📈 Simplified Market Engine
  - Order flow-driven price determination
  - Dynamic market depth adjustment
  - Configurable trading sessions
- 📊 Basic Analytics
  - Tick-level transaction recording
  - Auto-generated OHLC candlestick data

## Agent Models

### Noise Traders (NT)
- **Logic**: Random order generation
- **Key Parameters**:
  ```python
  {
      "trade_prob": 0.3,    # Order probability per tick
      "max_volume": 5       # Maximum shares per order
  }
  ```

### Momentum Traders (MT)
- **Decision Logic**:
  ```math
  \text{Signal} = \frac{\text{Price}_t - \text{SMA}_t}{\sigma_t}
  ```
- **Risk Controls**:
  - Dynamic cooling periods
  - Position limits

### Value Investors (VI)
- **Valuation Model**:
  ```math
  IV_t = \frac{D}{r - g} \times (1 + \epsilon)
  ```
  - D: Dividend, r: Discount rate, g: Growth rate, ε: Valuation error

## Future Roadmap

### Model Extensions
- [ ] New agent types (HFT, Market Makers)
- [ ] Margin trading & short selling
- [ ] Dynamic fundamental analysis models

### System Improvements
- [ ] Distributed computing support
- [ ] Real-time visualization dashboard
- [ ] Historical backtesting interface

### Academic Validation
- [ ] Return distribution analysis (fat-tail verification)
- [ ] Volatility clustering simulation
- [ ] Market microstructure analysis

## Bilingual Support

We provide dual-language support through:
1. Main documentation in English with key Chinese terminology
2. Separate [Chinese documentation](README_ZH.md)
3. Bilingual code comments
4. Multi-language config labels:
   ```json
   {
       "parameter_description": {
           "name": "n_nt",
           "description": "Number of Noise Traders/噪声交易者数量"
       }
   }
   ```

## Contributing

We welcome contributions through:
1. Submitting issues for bug reports/suggestions
2. Forking repository and creating PRs
3. Improving documentation and test cases
4. Sharing use cases and research findings

Please follow our [Contribution Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE). Academic references should cite this project.

---
**Research Collaboration**: Universities and institutions are welcome to collaborate on financial complexity research. Contact: research@simfinance.org
```

### 文件管理建议：
1. **主README**：`README.md` (英文版)
2. **中文README**：`README_ZH.md`
3. **在英文README顶部添加语言切换链接**：
   ```markdown
   🇨🇳 [中文文档](README_ZH.md) | 🇬🇧 **English**
   ```
4. **在中文README中反向链接**：
   ```markdown
   🇬🇧 [English Documentation](README.md) | 🇨🇳 **中文**
   ```

这种结构符合GitHub的默认文档规范，同时保持双语用户的易访问性。