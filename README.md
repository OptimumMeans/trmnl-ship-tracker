# TRMNL Ship Tracker

A custom plugin for TRMNL e-ink displays that shows real-time ship tracking information using the position-api.

## Prerequisites

- Python 3.8+
- position-api running locally
- TRMNL device

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trmnl-ship-tracker.git
cd trmnl-ship-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your configurations
```

5. Run the position-api:
```bash
# Follow position-api setup instructions
```

6. Start the server:
```bash
python src/app.py
```

## Configuration

Edit the `.env` file to configure:
- MMSI number
- Refresh interval
- Font paths
- Server settings

## TRMNL Setup

1. Go to TRMNL dashboard
2. Add new Custom Plugin
3. Set webhook URL to `http://your-server:8080/webhook`
4. Set refresh interval to 15 minutes

## Development

Run tests:
```bash
pytest tests/
```

## License

Whatever whatever bish bash bosh

## Credits

Uses [position-api](https://github.com/transparency-everywhere/position-api) for ship tracking data.