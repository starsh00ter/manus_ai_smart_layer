# Credit Optimization Guide for Manus AI

## Overview
This guide helps you minimize Manus credit usage while maximizing the effectiveness of our Smart Layer system. Based on insights from our brother project and our own optimizations.

## Core Principles 🎯

### 1. Use DeepSeek for Heavy Lifting
- **DeepSeek is FREE** - use it for complex reasoning, analysis, and generation
- **Manus credits** - reserve for specialized Manus features and tools
- **Rule**: If it's pure text processing, use DeepSeek

### 2. Batch Operations
- Combine multiple requests into single calls
- Process multiple items in one prompt
- Use structured outputs to handle multiple tasks

### 3. Smart Caching
- Our system automatically caches responses
- Reuse previous computations when possible
- Check trajectory history before making new calls

## Prompting Strategies to Save Credits 💡

### ✅ DO: Efficient Prompting
```
"Analyze these 5 code files and provide optimization suggestions for each:
1. [file1 content]
2. [file2 content]
..."
```

### ❌ DON'T: Multiple Separate Calls
```
"Analyze this code file: [file1]"
"Now analyze this code file: [file2]"
"Now analyze this code file: [file3]"
```

### ✅ DO: Structured Requests
```
"Create a comprehensive project plan including:
- Timeline with milestones
- Resource requirements
- Risk assessment
- Implementation steps
Format as JSON for easy parsing."
```

### ❌ DON'T: Incremental Building
```
"Create a timeline"
"Now add milestones to that timeline"
"Now add resource requirements"
"Now add risk assessment"
```

## DeepSeek Integration Tips 🚀

### When to Use DeepSeek
- Code analysis and optimization
- Document generation and editing
- Complex reasoning and problem-solving
- Data analysis and interpretation
- Creative writing and content generation

### When to Use Manus
- File operations and system interactions
- Browser automation and web scraping
- Image/video generation and editing
- Service deployment and management
- Specialized tool integrations

### Hybrid Approach Example
```python
# Use DeepSeek for analysis
analysis = call_deepseek("Analyze this codebase and suggest improvements")

# Use Manus for implementation
manus_smart_call(f"Implement these improvements: {analysis}")
```

## Budget Management 💰

### Daily Limits
- **Manus**: 300kT per day (strictly enforced)
- **DeepSeek**: Unlimited (free tier)
- **Strategy**: Use 80% DeepSeek, 20% Manus

### Cost Estimation
- **Simple text**: ~100-500 tokens
- **Code analysis**: ~1000-3000 tokens
- **Complex reasoning**: ~2000-5000 tokens
- **Document generation**: ~1000-4000 tokens

### Warning Thresholds
- 🟢 **0-60%**: Normal usage
- 🟡 **60-80%**: Caution advised
- 🔴 **80-100%**: Critical - switch to DeepSeek only

## Optimization Techniques 🔧

### 1. Prompt Compression
```
# Instead of:
"Please analyze this code and tell me what it does, identify any bugs, suggest improvements, check for security issues, and provide optimization recommendations."

# Use:
"Code analysis: functionality, bugs, improvements, security, optimization"
```

### 2. Context Reuse
- Reference previous conversations: "Based on our earlier discussion about X..."
- Use session memory: "Continue from where we left off"
- Build on existing context rather than restating

### 3. Efficient Tool Selection
- Use the right tool for the job
- Prefer file operations over repeated API calls
- Batch file reads/writes when possible

### 4. Smart Caching
- Our system caches responses automatically
- Similar prompts will reuse cached results
- Check logs before making duplicate requests

## Advanced Strategies 🎓

### 1. Template-Based Prompting
Create reusable templates for common tasks:
```
TEMPLATE: Code Review
"Review this {language} code for:
- Functionality: {specific_function}
- Performance: {performance_criteria}
- Security: {security_focus}
- Best practices: {standards}

Code: {code_content}"
```

### 2. Progressive Refinement
Start with broad requests, then refine:
```
1. "High-level architecture for X"
2. "Detailed implementation for component Y from above"
3. "Specific code for function Z"
```

### 3. Conditional Logic
Use smart conditionals to avoid unnecessary processing:
```
"If this code has performance issues, suggest optimizations.
If not, focus on readability improvements."
```

## Monitoring and Alerts 📊

### Real-Time Monitoring
- Dashboard shows current credit usage
- Automatic warnings at 60% and 80%
- Daily usage trends and projections

### Smart Alerts
- "High credit usage detected - switch to DeepSeek?"
- "Daily limit approaching - defer non-critical tasks?"
- "Optimization opportunity - batch these requests?"

### Performance Tracking
- Track credit efficiency per task type
- Identify high-cost operations
- Optimize based on usage patterns

## Emergency Protocols 🚨

### When Credits Run Low
1. **Switch to DeepSeek immediately**
2. **Defer non-critical operations**
3. **Use cached responses when available**
4. **Batch remaining operations**

### Credit Recovery
- Wait for daily reset (midnight UTC)
- Use DeepSeek for continued work
- Plan next day's operations efficiently

## Best Practices Summary ✨

1. **Plan Before Prompting**: Think about what you really need
2. **Batch Operations**: Combine related requests
3. **Use DeepSeek First**: Default to free options
4. **Monitor Usage**: Keep an eye on the dashboard
5. **Cache Smartly**: Reuse previous work
6. **Optimize Continuously**: Learn from usage patterns

## Quick Reference 📋

### High-Efficiency Prompts
- "Analyze and provide comprehensive report on..."
- "Create complete implementation including..."
- "Review, optimize, and document this..."

### Credit-Saving Phrases
- "Based on previous analysis..."
- "Using cached results..."
- "Building on earlier work..."

### Emergency Switches
- "Switch to DeepSeek mode"
- "Defer until tomorrow"
- "Use minimal processing"

---

*Remember: The goal is to maximize value while minimizing cost. Smart prompting and tool selection are your best friends!*

