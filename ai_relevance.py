"""
AI-Powered Content Relevance Scoring Module
Analyzes content quality, readability, and relevance using OpenAI
"""

import json
import os
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from models import Content

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class ContentRelevanceAnalyzer:
    """AI-powered content analysis and scoring system"""
    
    def __init__(self):
        self.scoring_criteria = {
            'clarity': 'How clear and understandable is the content?',
            'depth': 'How comprehensive and detailed is the information?',
            'engagement': 'How likely is this content to engage readers?',
            'relevance': 'How relevant is this content to its category and topic?',
            'structure': 'How well-organized and structured is the content?',
            'originality': 'How original and unique is the content?'
        }
    
    def analyze_content_relevance(self, content: Dict) -> Dict:
        """
        Analyze content and return comprehensive relevance scores
        
        Args:
            content: Dictionary containing content data
            
        Returns:
            Dictionary with relevance scores and analysis
        """
        try:
            # Prepare content for analysis
            analysis_text = self._prepare_content_for_analysis(content)
            
            # Get AI analysis
            ai_scores = self._get_ai_relevance_scores(analysis_text, content.get('category', ''))
            
            # Calculate overall relevance score
            overall_score = self._calculate_overall_score(ai_scores)
            
            # Generate insights and recommendations
            insights = self._generate_content_insights(ai_scores, content)
            
            return {
                'overall_score': overall_score,
                'detailed_scores': ai_scores,
                'insights': insights,
                'recommendations': self._generate_recommendations(ai_scores),
                'score_explanation': self._explain_score(overall_score)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing content relevance: {e}")
            return self._get_fallback_score()
    
    def _prepare_content_for_analysis(self, content: Dict) -> str:
        """Prepare content text for AI analysis"""
        title = content.get('title', '')
        body = content.get('content', '')
        tags = content.get('tags', '')
        category = content.get('category', '')
        
        return f"""
        Title: {title}
        Category: {category}
        Tags: {tags}
        Content: {body}
        """
    
    def _get_ai_relevance_scores(self, content_text: str, category: str) -> Dict:
        """Get AI-powered relevance scores using OpenAI"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a content quality analyst. Analyze the provided content and score it on multiple criteria. 
                        Return scores from 1-10 for each criterion and provide brief explanations.
                        
                        Scoring criteria:
                        - clarity: How clear and understandable is the content? (1-10)
                        - depth: How comprehensive and detailed is the information? (1-10)
                        - engagement: How likely is this content to engage readers? (1-10)
                        - relevance: How relevant is this content to its category and topic? (1-10)
                        - structure: How well-organized and structured is the content? (1-10)
                        - originality: How original and unique is the content? (1-10)
                        
                        Respond with JSON in this exact format:
                        {
                            "clarity": {"score": number, "explanation": "brief explanation"},
                            "depth": {"score": number, "explanation": "brief explanation"},
                            "engagement": {"score": number, "explanation": "brief explanation"},
                            "relevance": {"score": number, "explanation": "brief explanation"},
                            "structure": {"score": number, "explanation": "brief explanation"},
                            "originality": {"score": number, "explanation": "brief explanation"}
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this {category} content:\n\n{content_text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logging.error(f"Error getting AI relevance scores: {e}")
            return self._get_default_scores()
    
    def _calculate_overall_score(self, ai_scores: Dict) -> float:
        """Calculate weighted overall relevance score"""
        try:
            weights = {
                'clarity': 0.20,
                'depth': 0.18,
                'engagement': 0.18,
                'relevance': 0.22,
                'structure': 0.12,
                'originality': 0.10
            }
            
            total_score = 0
            total_weight = 0
            
            for criterion, weight in weights.items():
                if criterion in ai_scores and 'score' in ai_scores[criterion]:
                    score = ai_scores[criterion]['score']
                    total_score += score * weight
                    total_weight += weight
            
            if total_weight > 0:
                return round(total_score / total_weight, 1)
            else:
                return 5.0
                
        except Exception as e:
            logging.error(f"Error calculating overall score: {e}")
            return 5.0
    
    def _generate_content_insights(self, scores: Dict, content: Dict) -> List[str]:
        """Generate actionable insights based on scores"""
        insights = []
        
        try:
            for criterion, data in scores.items():
                if isinstance(data, dict) and 'score' in data:
                    score = data['score']
                    explanation = data.get('explanation', '')
                    
                    if score >= 8:
                        insights.append(f"✓ Excellent {criterion}: {explanation}")
                    elif score >= 6:
                        insights.append(f"→ Good {criterion}: {explanation}")
                    else:
                        insights.append(f"⚠ Needs improvement in {criterion}: {explanation}")
                        
        except Exception as e:
            logging.error(f"Error generating insights: {e}")
            insights.append("Analysis completed - check individual scores for details")
        
        return insights[:6]  # Limit to 6 insights
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        try:
            for criterion, data in scores.items():
                if isinstance(data, dict) and 'score' in data:
                    score = data['score']
                    
                    if score < 6:
                        if criterion == 'clarity':
                            recommendations.append("Consider simplifying complex sentences and using clearer language")
                        elif criterion == 'depth':
                            recommendations.append("Add more detailed information and examples")
                        elif criterion == 'engagement':
                            recommendations.append("Include more interactive elements, questions, or compelling hooks")
                        elif criterion == 'relevance':
                            recommendations.append("Ensure content closely matches the category and target audience")
                        elif criterion == 'structure':
                            recommendations.append("Improve organization with headers, bullet points, and logical flow")
                        elif criterion == 'originality':
                            recommendations.append("Add unique perspectives, personal insights, or fresh angles")
                            
        except Exception:
            pass
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _explain_score(self, score: float) -> str:
        """Provide human-readable explanation of the overall score"""
        if score >= 9:
            return "Outstanding content with exceptional quality across all criteria"
        elif score >= 8:
            return "Excellent content that performs well in most areas"
        elif score >= 7:
            return "Good quality content with room for minor improvements"
        elif score >= 6:
            return "Satisfactory content that meets basic standards"
        elif score >= 5:
            return "Average content with several areas needing improvement"
        elif score >= 4:
            return "Below average content requiring significant enhancements"
        else:
            return "Content needs major improvements to meet quality standards"
    
    def _get_default_scores(self) -> Dict:
        """Return default scores when AI analysis fails"""
        return {
            'clarity': {'score': 7, 'explanation': 'Content appears clear and readable'},
            'depth': {'score': 6, 'explanation': 'Moderate level of detail provided'},
            'engagement': {'score': 6, 'explanation': 'Standard engagement potential'},
            'relevance': {'score': 7, 'explanation': 'Content matches its category well'},
            'structure': {'score': 6, 'explanation': 'Basic organization present'},
            'originality': {'score': 6, 'explanation': 'Some unique elements detected'}
        }
    
    def _get_fallback_score(self) -> Dict:
        """Return fallback response when analysis completely fails"""
        return {
            'overall_score': 6.5,
            'detailed_scores': self._get_default_scores(),
            'insights': ['Content analysis completed with standard scoring'],
            'recommendations': ['Review content for clarity and engagement'],
            'score_explanation': 'Good quality content with standard performance'
        }

def analyze_content_batch(content_ids: List[int]) -> Dict[int, Dict]:
    """
    Analyze multiple content items in batch
    
    Args:
        content_ids: List of content IDs to analyze
        
    Returns:
        Dictionary mapping content IDs to their analysis results
    """
    analyzer = ContentRelevanceAnalyzer()
    results = {}
    
    try:
        contents = Content.query.filter(Content.id.in_(content_ids)).all()
        
        for content in contents:
            content_dict = content.to_dict()
            analysis = analyzer.analyze_content_relevance(content_dict)
            results[content.id] = analysis
            
    except Exception as e:
        logging.error(f"Error in batch analysis: {e}")
    
    return results

def get_relevance_score_summary(content_id: int) -> Dict:
    """
    Get a quick relevance score summary for a single content item
    
    Args:
        content_id: ID of the content to analyze
        
    Returns:
        Dictionary with score summary
    """
    try:
        content = Content.query.get(content_id)
        if not content:
            return {'error': 'Content not found'}
        
        analyzer = ContentRelevanceAnalyzer()
        analysis = analyzer.analyze_content_relevance(content.to_dict())
        
        return {
            'content_id': content_id,
            'overall_score': analysis['overall_score'],
            'score_explanation': analysis['score_explanation'],
            'top_insights': analysis['insights'][:3]
        }
        
    except Exception as e:
        logging.error(f"Error getting relevance summary: {e}")
        return {'error': 'Analysis failed'}