# Discord-Telegram Notification Trading Bot

A sophisticated trading notification system that evaluates trading opportunities using a custom points-based strategy and sends real-time alerts to Discord or Telegram.

## 📋 Description

This bot implements a custom trading strategy by analyzing market conditions and assigning points to potential trading opportunities. When a signal meets your configured threshold, the bot automatically sends notifications to your preferred messaging platform (Discord or Telegram), allowing you to act quickly on trading opportunities.

## ✨ Features

- **Custom Points System**: Implements a proprietary points-based trading strategy
- **Multi-Platform Notifications**: Send alerts to Discord and/or Telegram
- **Real-Time Monitoring**: Continuous market analysis and instant notifications
- **Configurable Thresholds**: Customize point thresholds for different signal strengths
- **Trading Signals**: Get actionable buy/sell notifications based on your strategy
- **Easy Setup**: Simple configuration process for both messaging platforms

## 🚀 Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or higher
- A Discord account and bot token (if using Discord notifications)
- A Telegram account and bot token (if using Telegram notifications)
- API access to your trading platform/data provider
- Basic knowledge of trading concepts

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/LexyBandzzV2/Discord-Telegram-notification-trading-bot.git
cd Discord-Telegram-notification-trading-bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Discord Setup

1. Create a Discord bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Navigate to the "Bot" section and create a bot
   - Copy the bot token

2. Add bot to your server:
   - In the OAuth2 section, select "bot" scope
   - Grant necessary permissions (Send Messages, Embed Links)
   - Use the generated URL to add the bot to your server

3. Configure the bot:
   - Create a `config.json` file in the project root
   - Add your Discord bot token and channel ID

### Telegram Setup

1. Create a Telegram bot:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command and follow the instructions
   - Copy the bot token provided

2. Get your chat ID:
   - Start a conversation with your bot
   - Use a service like [@userinfobot](https://t.me/userinfobot) to get your chat ID

3. Configure the bot:
   - Add your Telegram bot token and chat ID to `config.json`

### Configuration File Example

```json
{
  "discord": {
    "enabled": true,
    "token": "YOUR_DISCORD_BOT_TOKEN",
    "channel_id": "YOUR_CHANNEL_ID"
  },
  "telegram": {
    "enabled": true,
    "token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "trading": {
    "point_threshold": 75,
    "update_interval": 60,
    "symbols": ["BTC/USDT", "ETH/USDT"]
  }
}
```

## 🎯 Usage

1. Start the bot:
```bash
python main.py
```

2. The bot will:
   - Connect to your configured messaging platforms
   - Start monitoring market conditions
   - Calculate points for trading opportunities
   - Send notifications when signals meet your threshold

3. Notification format:
   - Signal type (Buy/Sell)
   - Trading pair
   - Point score
   - Confidence level
   - Current price
   - Suggested entry/exit points

## 📊 Points System

The bot uses a multi-factor points system that evaluates:

- Technical indicators
- Price action patterns
- Volume analysis
- Market momentum
- Risk/reward ratios

Each factor contributes points, and when the total reaches your threshold, a notification is triggered.

## 🛠️ Customization

You can customize the points system by:

1. Adjusting factor weights in the strategy configuration
2. Adding new technical indicators
3. Modifying point thresholds for different signal types
4. Creating custom notification templates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This bot is for educational and informational purposes only. It does not constitute financial advice. Trading cryptocurrencies and other financial instruments involves risk. Always do your own research and never invest more than you can afford to lose.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Telegram Bot Documentation](https://core.telegram.org/bots)
- [Report Issues](https://github.com/LexyBandzzV2/Discord-Telegram-notification-trading-bot/issues)

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub or reach out to the project maintainer.

---

**Note**: Remember to keep your bot tokens and API keys secure. Never commit them to version control or share them publicly.
