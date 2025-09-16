#!/usr/bin/env python3

"""
Brother Project Collaborator

This script facilitates collaboration between our Smart Layer project
and the brother project at moesmovingpictures-tech/manus.
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional

class BrotherProjectCollaborator:
    """Handles collaboration with the brother project"""
    
    def __init__(self):
        self.token = self._load_token()
        self.repo_owner = "moesmovingpictures-tech"
        self.repo_name = "manus"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def _load_token(self) -> str:
        """Load GitHub token for brother project"""
        token_path = "/home/ubuntu/.brother_github_token"
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                return f.read().strip()
        raise ValueError("Brother project GitHub token not found")
    
    def get_repository_info(self) -> Dict:
        """Get basic repository information"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get repo info: {response.status_code}")
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """Get recent commits from the brother project"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits"
        params = {"per_page": limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get commits: {response.status_code}")
    
    def get_file_content(self, file_path: str, ref: str = "master") -> str:
        """Get content of a specific file"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        params = {"ref": ref}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            import base64
            content = response.json()["content"]
            return base64.b64decode(content).decode('utf-8')
        else:
            raise Exception(f"Failed to get file content: {response.status_code}")
    
    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict:
        """Create an issue in the brother project repository"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create issue: {response.status_code}")
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> Dict:
        """Add a comment to an existing issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments"
        
        data = {"body": comment}
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to add comment: {response.status_code}")
    
    def analyze_brother_project(self) -> Dict:
        """Analyze the brother project and generate insights"""
        
        print("🔍 Analyzing brother project...")
        
        # Get repository info
        repo_info = self.get_repository_info()
        
        # Get recent commits
        recent_commits = self.get_recent_commits(5)
        
        # Analyze key files
        key_files = [
            "main.py",
            "blueprint_v1.1.md",
            "memory/inner_voice.py",
            "memory/self_heal.py",
            "memory/learn.py"
        ]
        
        file_analysis = {}
        for file_path in key_files:
            try:
                content = self.get_file_content(file_path)
                file_analysis[file_path] = {
                    "size": len(content),
                    "lines": len(content.split('\n')),
                    "has_deepseek": "deepseek" in content.lower(),
                    "has_vector": "vector" in content.lower(),
                    "has_sqlite": "sqlite" in content.lower()
                }
            except Exception as e:
                file_analysis[file_path] = {"error": str(e)}
        
        analysis = {
            "repository": {
                "name": repo_info["name"],
                "description": repo_info.get("description", ""),
                "language": repo_info.get("language", ""),
                "size": repo_info.get("size", 0),
                "updated_at": repo_info.get("updated_at", "")
            },
            "recent_activity": [
                {
                    "sha": commit["sha"][:8],
                    "message": commit["commit"]["message"],
                    "date": commit["commit"]["author"]["date"],
                    "author": commit["commit"]["author"]["name"]
                }
                for commit in recent_commits
            ],
            "file_analysis": file_analysis,
            "insights": self._generate_insights(file_analysis, recent_commits)
        }
        
        return analysis
    
    def _generate_insights(self, file_analysis: Dict, commits: List[Dict]) -> List[str]:
        """Generate insights based on analysis"""
        insights = []
        
        # Check for DeepSeek integration
        deepseek_files = [f for f, data in file_analysis.items() 
                         if isinstance(data, dict) and data.get("has_deepseek", False)]
        if deepseek_files:
            insights.append(f"✅ DeepSeek integration found in: {', '.join(deepseek_files)}")
        
        # Check for vector capabilities
        vector_files = [f for f, data in file_analysis.items() 
                       if isinstance(data, dict) and data.get("has_vector", False)]
        if vector_files:
            insights.append(f"🔍 Vector capabilities in: {', '.join(vector_files)}")
        
        # Check for SQLite usage
        sqlite_files = [f for f, data in file_analysis.items() 
                       if isinstance(data, dict) and data.get("has_sqlite", False)]
        if sqlite_files:
            insights.append(f"🗄️ SQLite integration in: {', '.join(sqlite_files)}")
        
        # Analyze commit frequency
        if commits:
            latest_commit = commits[0]["commit"]["author"]["date"]
            insights.append(f"📅 Latest activity: {latest_commit}")
        
        return insights
    
    def suggest_collaboration_ideas(self) -> List[str]:
        """Generate collaboration ideas based on analysis"""
        return [
            "🤝 Mobile Interface Integration: Our React PWA could complement their FastAPI backend",
            "📊 Performance Analytics: Share our trajectory tracking and scoring system",
            "🔄 Memory Synchronization: Combine SQLite+vector with Supabase for cross-device sync",
            "🎯 Credit Optimization: Exchange DeepSeek integration best practices",
            "🧠 Knowledge Graph Visualization: Create mobile-friendly concept graph explorer",
            "🔧 Self-Healing Enhancement: Integrate our reflection system with their auto-patching",
            "📱 Real-time Dashboard: Provide mobile monitoring for their memory system",
            "🔐 RACI Integration: Enhance our credit management with their approval workflows"
        ]
    
    def create_collaboration_issue(self) -> Dict:
        """Create a collaboration issue in the brother project"""
        
        analysis = self.analyze_brother_project()
        suggestions = self.suggest_collaboration_ideas()
        
        title = "🤝 Collaboration Proposal from Sister Smart Layer Project"
        
        body = f"""# Collaboration Proposal

Hello from your sister project! 👋

We're building a complementary Manus AI Smart Layer system and would love to collaborate and learn from each other.

## Our Project
- **Repository**: https://github.com/starsh00ter/manus_ai_smart_layer
- **Focus**: Self-improving, credit-efficient personal management with phone-first accessibility
- **Key Features**: React PWA, trajectory tracking, performance analytics, recursive learning

## What We Admire About Your Project ✨

{chr(10).join(f"- {insight}" for insight in analysis['insights'])}

## Collaboration Ideas 💡

{chr(10).join(f"- {idea}" for idea in suggestions)}

## Proposed Collaboration Framework

1. **Shared Learning**: Exchange insights through dedicated collaboration files
2. **Code Sharing**: Share useful patterns and implementations
3. **Joint Development**: Potential integration opportunities
4. **Credit Optimization**: Share DeepSeek best practices and cost-saving strategies

## Next Steps

We've created a collaboration file in our repository to track insights and suggestions. We'd love to:

1. Set up regular knowledge exchange
2. Share our mobile-first interface approach
3. Learn from your sophisticated memory architecture
4. Explore integration possibilities

Looking forward to building amazing AI systems together! 🚀

---
*This issue was created automatically by our collaboration system.*
"""
        
        try:
            issue = self.create_issue(title, body, ["collaboration", "enhancement"])
            print(f"✅ Created collaboration issue: {issue['html_url']}")
            return issue
        except Exception as e:
            print(f"❌ Failed to create issue: {e}")
            return {}

def main():
    """Main collaboration function"""
    try:
        collaborator = BrotherProjectCollaborator()
        
        print("🤝 Starting brother project collaboration...")
        
        # Analyze the brother project
        analysis = collaborator.analyze_brother_project()
        
        print("\n📊 Analysis Results:")
        print(f"Repository: {analysis['repository']['name']}")
        print(f"Language: {analysis['repository']['language']}")
        print(f"Last updated: {analysis['repository']['updated_at']}")
        
        print("\n🔍 Key Insights:")
        for insight in analysis['insights']:
            print(f"  {insight}")
        
        print("\n💡 Collaboration Ideas:")
        suggestions = collaborator.suggest_collaboration_ideas()
        for suggestion in suggestions:
            print(f"  {suggestion}")
        
        # Save analysis to file
        analysis_file = "/home/ubuntu/my_manus_knowledge/collaboration/brother_project_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n📄 Analysis saved to: {analysis_file}")
        
        # Create collaboration issue
        print("\n🎯 Creating collaboration issue...")
        issue = collaborator.create_collaboration_issue()
        
        if issue:
            print("✅ Collaboration initiated successfully!")
        else:
            print("❌ Failed to initiate collaboration")
        
    except Exception as e:
        print(f"❌ Collaboration error: {e}")

if __name__ == "__main__":
    main()

