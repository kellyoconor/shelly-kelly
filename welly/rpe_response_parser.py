#!/usr/bin/env python3
"""
RPE Response Parser: Extract perceived effort data from Kelly's natural responses

Parses natural language responses about runs and automatically logs RPE data to Welly
"""

import re
import json
import sys
from datetime import datetime
from rpe_tracker import RPETracker

class RPEResponseParser:
    def __init__(self):
        self.effort_keywords = {
            # High effort indicators
            'hard': 8, 'tough': 8, 'struggled': 8, 'fight': 8, 'push': 7, 'work': 7,
            'grind': 8, 'battle': 8, 'challenging': 7, 'difficult': 7,
            
            # Medium effort indicators  
            'okay': 5, 'alright': 5, 'fine': 5, 'decent': 6, 'moderate': 5,
            'normal': 5, 'average': 5,
            
            # Low effort indicators
            'easy': 3, 'smooth': 3, 'comfortable': 4, 'relaxed': 3, 'effortless': 2,
            'cruise': 4, 'flow': 4
        }
        
        self.leg_keywords = {
            # Poor leg feeling
            'dead': 2, 'heavy': 3, 'tired': 3, 'sluggish': 3, 'laggy': 3,
            'weren\'t there': 2, 'no legs': 1, 'concrete': 2, 'cement': 2,
            'fatigued': 3, 'sore': 4,
            
            # Good leg feeling
            'bouncy': 8, 'spring': 8, 'light': 7, 'fresh': 7, 'strong': 7,
            'good': 6, 'responsive': 7, 'sharp': 7,
            
            # Neutral leg feeling
            'okay': 5, 'fine': 5, 'normal': 5, 'alright': 5
        }
        
        self.satisfaction_keywords = {
            # High satisfaction
            'great': 8, 'awesome': 9, 'fantastic': 9, 'perfect': 10, 'loved': 8,
            'solid': 7, 'good': 7, 'nice': 6, 'pleased': 7,
            
            # Low satisfaction  
            'terrible': 2, 'awful': 2, 'bad': 3, 'rough': 3, 'disappointing': 3,
            'frustrated': 3, 'annoyed': 3, 'meh': 4,
            
            # Medium satisfaction
            'okay': 5, 'fine': 5, 'alright': 5, 'decent': 6
        }
        
    def parse_response(self, response_text, run_data=None):
        """Parse natural language response and extract RPE data"""
        text = response_text.lower().strip()
        
        # Extract perceived effort
        perceived_effort = self._extract_effort(text)
        
        # Extract leg feeling  
        leg_feeling = self._extract_leg_feeling(text)
        
        # Extract satisfaction
        satisfaction = self._extract_satisfaction(text)
        
        # Extract contextual notes
        notes = self._extract_context(text, response_text)  # Use original case for notes
        
        return {
            'perceived_effort': perceived_effort,
            'leg_feeling': leg_feeling, 
            'satisfaction': satisfaction,
            'notes': notes,
            'confidence': self._calculate_confidence(text),
            'parsed_from': response_text
        }
        
    def _extract_effort(self, text):
        """Extract perceived effort from text"""
        # Look for explicit ratings first
        explicit_match = re.search(r'effort.*?(\d+)(?:/10)?', text)
        if explicit_match:
            return min(10, max(1, int(explicit_match.group(1))))
            
        # Look for effort keywords
        effort_scores = []
        for keyword, score in self.effort_keywords.items():
            if keyword in text:
                effort_scores.append(score)
                
        # Modifiers
        if any(word in text for word in ['really', 'very', 'super', 'extremely']):
            if effort_scores:
                effort_scores = [min(10, s + 1) for s in effort_scores]
                
        if any(word in text for word in ['little', 'bit', 'slightly', 'somewhat']):
            if effort_scores:
                effort_scores = [max(1, s - 1) for s in effort_scores]
        
        # Contextual adjustments
        if 'had to push' in text or 'push more' in text or 'def had to push' in text:
            effort_scores.append(8)  # Definitely felt hard
        if 'harder than' in text or 'felt harder' in text:
            effort_scores.append(7)
        if 'slow and' in text and any(word in text for word in ['laggy', 'heavy', 'sluggish']):
            effort_scores.append(6)  # Felt slower than usual
            
        return int(sum(effort_scores) / len(effort_scores)) if effort_scores else 6
        
    def _extract_leg_feeling(self, text):
        """Extract leg feeling from text"""
        # Look for explicit leg ratings
        leg_match = re.search(r'legs?.*?(\d+)(?:/10)?', text)
        if leg_match:
            return min(10, max(1, int(leg_match.group(1))))
            
        # Look for leg-specific keywords
        leg_scores = []
        for keyword, score in self.leg_keywords.items():
            if keyword in text:
                # Weight leg-specific mentions more heavily
                if 'legs' in text or 'leg' in text:
                    leg_scores.append(score)
                elif keyword in ['dead', 'heavy', 'tired', 'weren\'t there', 'no legs']:
                    leg_scores.append(score)
                    
        # Contextual leg indicators
        if 'legs' in text and any(phrase in text for phrase in ['weren\'t there', 'not there', 'just weren\'t', 'didn\'t have', 'just didn\'t have']):
            leg_scores.append(2)
        if 'legs' in text and any(word in text for word in ['fine', 'good', 'okay']):
            leg_scores.append(6)
        if 'no legs' in text or 'didn\'t have the legs' in text:
            leg_scores.append(1)  # Really bad leg day
            
        return int(sum(leg_scores) / len(leg_scores)) if leg_scores else 5
        
    def _extract_satisfaction(self, text):
        """Extract overall satisfaction from text"""
        # Look for explicit satisfaction ratings
        sat_match = re.search(r'(?:satisfaction|satisfied).*?(\d+)(?:/10)?', text)
        if sat_match:
            return min(10, max(1, int(sat_match.group(1))))
            
        # Look for satisfaction keywords
        sat_scores = []
        for keyword, score in self.satisfaction_keywords.items():
            if keyword in text:
                sat_scores.append(score)
                
        # Contextual satisfaction indicators
        if 'got through it' in text or 'finished' in text:
            sat_scores.append(6)  # Accomplished but not thrilled
        if 'at least' in text:
            sat_scores.append(5)  # Grudging acceptance
            
        return int(sum(sat_scores) / len(sat_scores)) if sat_scores else 5
        
    def _extract_context(self, text_lower, original_text):
        """Extract contextual information as notes"""
        context_indicators = [
            'sleep', 'tired', 'monday', 'morning', 'weekend', 'stress', 'work',
            'weather', 'hot', 'cold', 'rain', 'wind', 'hills', 'flat',
            'pace', 'hr', 'heart rate', 'watch', 'garmin'
        ]
        
        notes = []
        
        # Check for context mentions
        for indicator in context_indicators:
            if indicator in text_lower:
                # Try to extract the relevant sentence
                sentences = original_text.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        notes.append(sentence.strip())
                        break
                        
        # Add the full response as context (truncated)
        if len(original_text) <= 100:
            notes.insert(0, f"Response: {original_text}")
        else:
            notes.insert(0, f"Response: {original_text[:100]}...")
            
        return " | ".join(notes[:3])  # Keep notes manageable
        
    def _calculate_confidence(self, text):
        """Calculate confidence in the parsing"""
        # More specific language = higher confidence
        specific_words = ['effort', 'legs', 'feeling', 'felt', 'was', 'had to']
        confidence = sum(1 for word in specific_words if word in text)
        
        # Explicit numbers = high confidence
        if re.search(r'\d+(?:/10)?', text):
            confidence += 3
            
        return min(1.0, confidence / 5)

def auto_log_rpe_from_response(response_text, run_data):
    """Automatically log RPE data from a natural language response"""
    parser = RPEResponseParser()
    rpe_data = parser.parse_response(response_text, run_data)
    
    # Only log if we have reasonable confidence
    if rpe_data['confidence'] > 0.3:
        tracker = RPETracker()
        tracker.capture_post_run_rpe(
            run_data,
            rpe_data['perceived_effort'],
            rpe_data['leg_feeling'],
            rpe_data['satisfaction'], 
            rpe_data['notes']
        )
        
        return {
            'logged': True,
            'data': rpe_data,
            'summary': f"Auto-logged: Effort {rpe_data['perceived_effort']}/10, Legs {rpe_data['leg_feeling']}/10, Satisfaction {rpe_data['satisfaction']}/10"
        }
    else:
        return {
            'logged': False,
            'reason': 'Low confidence in parsing',
            'data': rpe_data
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rpe-response-parser.py 'response text'")
        sys.exit(1)
        
    response = " ".join(sys.argv[1:])
    parser = RPEResponseParser()
    result = parser.parse_response(response)
    
    print("Parsed RPE data:")
    print(json.dumps(result, indent=2))