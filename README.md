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
  - When the number of Agents remains within a specific proportional range, it ensures sustained stable market operations. However, exceeding this range triggers unstable market fluctuations. This phenomenon inversely validates the model’s effectiveness in alignment with established academic theoretical frameworks.
- 📊 Basic Analytics
  - Tick-level transaction recording
  - Auto-generated OHLC candlestick data

## Agent Models

### Noise Traders (NT)
- **Decision Logic**: Random order generation

### Momentum Traders (MT)
- **Decision Logic**:
  ```math
  \text{Signal} = \frac{\text{P}_{t} - \text{SMA}_{t}}{\sigma_{t}}
  ```

### Value Investors (VI)
- **Decision Logic**: Make decisions by comparing current prices with predefined fundamental values, using randomized coefficients to simulate individualized agent behaviors.

## Future Roadmap

### Model Extensions
- [ ] Add new agent types (HFT, Market Makers)
- [ ] Implement leverage & short selling mechanisms
- [ ] Dynamic corporate fundamentals evolution models
- [ ] Extend to multi-asset market from single-stock
- [ ] Introduce financial derivatives

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
**Research Collaboration**: Universities and institutions are welcome to collaborate on financial complexity research. Contact: 124090210@link.cuhk.edu.cn