# 🤖 Data Assistant AI - LangChain SQL

An AI-powered data analysis assistant that enables natural language querying of MySQL databases. This project combines LangChain and OpenAI to translate natural language questions into SQL queries and present results interactively. Built with modularity and universal dataset compatibility in mind.

## 🌟 Key Features

- **Natural Language Processing**: Converts plain language questions into SQL queries using LangChain and GPT-4
- **Universal Dataset Compatibility**: Works with any structured dataset in MySQL
- **Interactive UI**: Clean and intuitive Streamlit interface
- **Intelligent Data Visualization**: Automatic chart generation based on query results
- **Comprehensive Data Analysis**: Provides insights, patterns, and follow-up suggestions
- **Multi-language Support**: Responds in the same language as the question
- **Robust CSV Loading**: Advanced CSV import with multiple encoding and delimiter strategies
- **Debug & Development Tools**: Built-in debugging panel and logging system

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.8+
- **UI Framework**: Streamlit
- **AI/ML**:
  - LangChain
  - OpenAI GPT-4
  - LangChain Community
- **Database**: MySQL
- **Data Processing**:
  - Pandas
  - NumPy
- **Visualization**:
  - Matplotlib
  - Seaborn
- **Development Tools**:
  - Python-dotenv
  - Logging system
  - Type hints

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server
- OpenAI API key
- Git (for repository management)

## 🚀 Installation

1. **Clone the Repository**:
```bash
git clone https://github.com/ronaldmego/data_assistant_ai.git
cd data_assistant_ai
```

2. **Run Setup Script**:
```bash
python scripts/setup.py
```
This script will:
- Create a virtual environment
- Install all dependencies
- Generate requirements.txt
- Guide you through initial configuration

3. **Configure Environment Variables**:
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=your_mysql_host
MYSQL_DATABASE=your_database_name
IGNORED_TABLES=table1,table2,table3
```

## 💡 Usage

1. **Start the Application**:
```bash
streamlit run src/pages/Home.py
```

2. **Load Your Data**:
- Place CSV files in the `data/` directory
- Use the data loader:
```bash
python scripts/load.py
```

3. **Access the Interface**:
- Local: `http://localhost:8501`
- Network: `http://[your-ip]:8501`

4. **Query Your Data**:
The assistant supports various types of queries:
- Overview questions: "What data is available?"
- Statistical queries: "Show me the distribution of incidents by type"
- Time-based analysis: "What's the trend over the last 6 months?"
- Cross-tabulations: "Compare categories by volume"

## 🔍 Advanced Features

### Data Loading
- Multiple encoding support (UTF-8, ISO-8859-1, CP1252)
- Automatic delimiter detection (comma, semicolon)
- Robust error handling with multiple fallback strategies
- Automatic data type inference
- Batch processing for large datasets

### Visualization
- Automatic chart type selection based on data structure
- Interactive visualizations with Streamlit
- Support for bar charts, line plots, and custom visualizations
- Dynamic color schemes

### Debug Panel
- Real-time query logging
- Performance metrics tracking
- Error monitoring
- State management visualization

## 🛠️ Development

### Adding New Features
1. Follow the modular structure
2. Update type hints
3. Add appropriate logging
4. Include error handling
5. Update tests if applicable

### Code Style
- Use type hints for better code documentation
- Follow PEP 8 standards
- Document functions and classes
- Use meaningful variable names
- Include comprehensive error handling

## 🔄 Continuous Improvement

### Current Development Focus
- [ ] Enhanced visualization options
- [ ] Query caching system
- [ ] Additional data source support
- [ ] Improved error handling
- [ ] Extended testing coverage

### Future Plans
- [ ] Real-time data processing
- [ ] Custom visualization templates
- [ ] Advanced query optimization
- [ ] Multiple database support
- [ ] Export functionality

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add your changes
4. Submit a pull request

### Contribution Guidelines
- Follow existing code structure
- Add documentation
- Include error handling
- Maintain code style consistency
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 👥 Author

**Ronald Mego**
- Portfolio: [ronaldmego.github.io](https://ronaldmego.github.io/)
- GitHub: [@ronaldmego](https://github.com/ronaldmego)

## 🙏 Acknowledgments

- Family and supporters
- Open source community
- Documentation and feedback providers

---

For more information and updates, visit the [project repository](https://github.com/ronaldmego/data_assistant_ai).