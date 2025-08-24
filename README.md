# 📊 Personal Dashboard

A modern, data-driven personal dashboard built with Streamlit for the frontend and a robust Python core for data processing and analytics.

## 🏗️ Architecture

This project follows a clean architecture pattern with clear separation of concerns:

- **Frontend (Mind)**: Streamlit-based user interface for data visualization and interaction
- **Core (Body)**: Pure Python functions for data extraction, processing, and analytics
- **Shared**: Common models and utilities shared between frontend and core

## 📁 Project Structure

```
personal-dashboard/
├── src/
│   ├── frontend/          # Streamlit application
│   │   ├── app.py        # Main application
│   │   ├── pages/        # Dashboard pages
│   │   └── components/   # Reusable UI components
│   ├── core/             # Data processing engine
│   │   ├── data_extractors/    # Data source connectors
│   │   ├── data_processors/    # Data transformation functions
│   │   ├── analytics/          # Analysis and insights
│   │   └── utils/             # Core utilities
│   └── shared/           # Shared models and utilities
│       └── models/       # Data models
├── data/                 # Data files
├── config/              # Configuration files
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd personal-dashboard
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   streamlit run src/frontend/app.py
   ```

The dashboard will be available at `http://localhost:8501`

## 🛠️ Development

### Installing Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks

### Running Tests

```bash
pytest
```

## 📊 Features

### Data Extraction
- CSV/Excel file support
- API data fetching
- Database connectivity (configurable)
- Real-time data streams

### Data Processing
- Data cleaning and validation
- Aggregation and transformation
- Time series analysis
- Statistical calculations

### Analytics
- Trend detection
- Outlier identification
- Correlation analysis
- Performance metrics

### Visualization
- Interactive charts with Plotly
- Real-time updates
- Responsive design
- Customizable dashboards

## 🔧 Configuration

The application is configured through `config/config.yaml`. Key configuration areas:

- **Data Sources**: Configure CSV directories, API endpoints, database connections
- **Processing**: Batch sizes, worker counts, caching settings
- **Analytics**: Default parameters for analysis functions
- **UI**: Theme, layout, and visualization settings

## 📝 Usage

### Adding New Data Sources

1. Create a new extractor in `src/core/data_extractors/`
2. Implement the extraction logic
3. Add configuration in `config/config.yaml`
4. Update the frontend to use the new data source

### Creating New Analytics

1. Add analysis functions in `src/core/analytics/`
2. Implement pure functions for calculations
3. Create visualization components in `src/frontend/components/`
4. Integrate into dashboard pages

### Customizing the Dashboard

1. Modify `src/frontend/app.py` for main layout changes
2. Add new pages in `src/frontend/pages/`
3. Create reusable components in `src/frontend/components/`
4. Update configuration as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🔮 Roadmap

- [ ] Machine learning integration
- [ ] Real-time data streaming
- [ ] Advanced visualizations
- [ ] Mobile responsiveness
- [ ] Authentication system
- [ ] Multi-user support
- [ ] API endpoints for external access
- [ ] Docker containerization

---

**Built with ❤️ using Streamlit and Python**
