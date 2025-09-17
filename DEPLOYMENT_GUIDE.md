# Manus AI Smart Layer - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Supabase account (optional)
- DeepSeek API key (recommended)

### 1. Clone and Setup
```bash
git clone https://github.com/starsh00ter/manus_ai_smart_layer.git
cd manus_ai_smart_layer
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### 3. Database Setup (Optional)
If using Supabase:
```bash
# Execute the database schema
# Copy contents of database_schema.sql to Supabase SQL Editor
```

### 4. Test System
```bash
python3 test_complete_system.py
```

### 5. Start Smart Layer
```bash
python3 smart_layer.py
```

## 📱 Mobile Interface Deployment

### Local Development
```bash
cd smart-layer-ui
npm install
npm run dev --host
```

### Production Deployment
```bash
cd smart-layer-ui
npm run build
# Deploy dist/ folder to your hosting service
```

## 🔧 Configuration Options

### Credit Management
- Daily limit: 300,000 tokens (configurable in `memory/router.py`)
- Warning threshold: 80% usage
- Automatic reset at midnight UTC

### Reflection Schedule
- Time-based: Every 4 hours
- Action-based: Every 50 actions
- Manual trigger available

### Supabase Integration
- Vector search with pgvector
- Automatic embedding storage
- Cross-device synchronization

## 🤝 Brother Project Collaboration

### Setup Collaboration
```bash
# Set brother project token
echo "your_github_token" > ~/.brother_github_token

# Run collaboration analysis
python3 collaboration/brother_project_collaborator.py
```

### Collaboration Features
- Automated analysis and insights
- GitHub issue creation
- Knowledge sharing protocol
- Cross-project learning

## 📊 Monitoring and Analytics

### System Status
```python
from smart_layer import get_smart_layer

smart_layer = get_smart_layer()
status = smart_layer.get_system_status()
print(json.dumps(status, indent=2))
```

### Performance Analytics
- Trajectory tracking with scoring
- Credit efficiency metrics
- Self-reflection insights
- Optimization recommendations

## 🔄 Maintenance

### Daily Tasks
- Review credit usage
- Check system performance
- Update collaboration insights
- Commit changes to Git

### Weekly Tasks
- Analyze performance trends
- Update brother project collaboration
- Review and optimize prompts
- Update documentation

### Monthly Tasks
- Full system backup
- Performance optimization review
- Feature roadmap update
- Security audit

## 🛠️ Troubleshooting

### Common Issues

#### Supabase Connection Failed
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python3 -c "from memory.supabase_client import get_client; print('OK')"
```

#### Credit Limit Exceeded
```bash
# Check current usage
python3 -c "from smart_layer import get_smart_layer; print(get_smart_layer().get_system_status()['credit_management'])"

# Switch to DeepSeek mode
export USE_DEEPSEEK_ONLY=true
```

#### Mobile Interface Issues
```bash
cd smart-layer-ui
npm run build
# Check for build errors
```

## 📈 Optimization Tips

### Credit Efficiency
1. Use DeepSeek for heavy processing
2. Batch similar operations
3. Leverage caching system
4. Monitor daily usage patterns

### Performance
1. Regular self-reflection sessions
2. Optimize high-cost operations
3. Use trajectory scoring for improvement
4. Implement suggested optimizations

### Collaboration
1. Weekly brother project sync
2. Share successful patterns
3. Exchange optimization strategies
4. Contribute to shared knowledge base

## 🔐 Security

### API Keys
- Store in environment variables
- Never commit to Git
- Rotate regularly
- Use minimal required permissions

### Data Protection
- Local CSV fallback for critical data
- Git-based persistence
- Supabase encryption at rest
- Regular backups

## 📚 Additional Resources

- [Credit Optimization Guide](docs/credit_optimization_guide.md)
- [Brother Project Insights](collaboration/brother_project_insights.md)
- [System Architecture](README.md)
- [Database Schema](database_schema.sql)

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review system logs
3. Run diagnostic tests
4. Contact development team

---

*Last Updated: 2025-09-16*
*Version: 1.0.0*

