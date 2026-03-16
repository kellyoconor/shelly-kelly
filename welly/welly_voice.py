#!/usr/bin/env python3
"""
welly-voice: Kelly's specific personality and communication style

Converts interpreted state into check-ins, questions, and gentle nudges
using Kelly's exact voice preferences and communication patterns.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class WellyVoice:
    def __init__(self):
        # Kelly's voice preferences from specifications
        self.voice_style = {
            "warm": True,
            "calm": True, 
            "observant": True,
            "lightly_playful": True,
            "never_clinical": True,
            "never_alarmist": True,
            "never_cheesy": True
        }
        
        # Kelly's approved voice examples
        self.approved_phrases = {
            "body_signals": [
                "Your body's been whispering for a few days",
                "Something's been trying to get your attention",
                "Your system's sending some quiet signals"
            ],
            "push_patterns": [
                "This looks like one of your 'I can push through it' stretches",
                "Recognizing that familiar push-through mode",
                "Feels like you're in override mode again"
            ],
            "mind_body_misalignment": [
                "Numbers say okay-ish. Mood says not quite",
                "Metrics look fine but something feels off",
                "Your data and your feel aren't quite matching up"
            ],
            "gentle_inquiry": [
                "How are you feeling about that?",
                "What's your sense of things?",
                "Does that land for you?",
                "What's coming up for you?"
            ],
            "pattern_flags": [
                "This feels familiar",
                "I'm seeing a pattern here",
                "We've been here before",
                "This reminds me of last month"
            ]
        }
        
        # Phrases to NEVER use (Kelly's dislikes)
        self.avoid_phrases = [
            "based on your biometrics",
            "remember to prioritize recovery",
            "you should", 
            "your data shows",
            "it's important to",
            "make sure you",
            "don't forget to",
            "optimize your",
            "maximize your",
            "according to science"
        ]
        
    def generate_daily_check_in(self, interpreted_state: Dict, memory_patterns: Dict) -> Optional[str]:
        """Generate a daily check-in following Kelly's 3-part format"""
        
        # Check if we should speak up at all
        if not self._should_speak_up(interpreted_state):
            return None
        
        # Generate Kelly's 3-part structure
        parts = []
        
        # 1. What I'm noticing
        noticing = self._generate_noticing(interpreted_state, memory_patterns)
        if noticing:
            parts.append(f"**What I'm noticing:** {noticing}")
        
        # 2. What I'm wondering  
        wondering = self._generate_wondering(interpreted_state, memory_patterns)
        if wondering:
            parts.append(f"**What I'm wondering:** {wondering}")
        
        # 3. Gentle nudge
        nudge = self._generate_gentle_nudge(interpreted_state, memory_patterns)
        if nudge:
            parts.append(f"**Gentle nudge:** {nudge}")
        
        # Optional pattern flag
        pattern_flag = self._generate_pattern_flag(memory_patterns)
        if pattern_flag:
            parts.append(f"**Pattern:** {pattern_flag}")
        
        if len(parts) >= 2:  # Minimum viable check-in
            return "\n\n".join(parts)
        
        return None
    
    def _should_speak_up(self, interpreted_state: Dict) -> bool:
        """Determine if Welly should speak up based on Kelly's trigger logic"""
        
        # Stay quiet conditions
        recovery_status = interpreted_state.get("recovery_status", "unknown")
        if recovery_status == "good":
            return False
        
        mind_body_alignment = interpreted_state.get("mind_body_alignment", "aligned")
        if mind_body_alignment == "aligned" and recovery_status == "okay-ish":
            return False
        
        push_risk = interpreted_state.get("push_risk", "low")
        emotional_load = interpreted_state.get("emotional_load", "light")
        
        # Speak up conditions from Kelly's specs
        speak_up_reasons = []
        
        # Readiness low 2+ days + high effort
        if recovery_status in ["concerning", "needs-attention"]:
            speak_up_reasons.append("recovery_concern")
        
        # Mind/body mismatch
        if mind_body_alignment in ["slight_mismatch", "misaligned"]:
            speak_up_reasons.append("alignment_issue")
        
        # High push risk
        if push_risk in ["high", "very_high"]:
            speak_up_reasons.append("push_pattern")
        
        # High emotional load
        if emotional_load in ["heavy", "overwhelming"]:
            speak_up_reasons.append("emotional_load")
        
        return len(speak_up_reasons) > 0
    
    def _generate_noticing(self, interpreted_state: Dict, memory_patterns: Dict) -> Optional[str]:
        """Generate 'What I'm noticing' observation"""
        
        insights = interpreted_state.get("insights", [])
        recovery_status = interpreted_state.get("recovery_status", "unknown")
        mind_body_alignment = interpreted_state.get("mind_body_alignment", "aligned")
        push_risk = interpreted_state.get("push_risk", "low")
        
        # Priority: mind-body misalignment (Kelly's key focus)
        if mind_body_alignment in ["slight_mismatch", "misaligned"]:
            mismatch_insights = [i for i in insights if any(word in i.lower() 
                               for word in ["energy feels", "numbers", "metrics"])]
            if mismatch_insights:
                return self._translate_to_kelly_voice(mismatch_insights[0])
        
        # Push patterns
        if push_risk in ["high", "very_high"]:
            push_insights = [i for i in insights if any(word in i.lower() 
                           for word in ["stress", "motivation", "push", "override"])]
            if push_insights:
                return random.choice(self.approved_phrases["push_patterns"])
        
        # Body signals 
        if recovery_status in ["concerning", "needs-attention"]:
            body_insights = [i for i in insights if any(word in i.lower()
                           for word in ["sleep", "hrv", "readiness", "trending"])]
            if body_insights:
                return random.choice(self.approved_phrases["body_signals"])
        
        # General observation
        if insights:
            return self._translate_to_kelly_voice(insights[0])
        
        return None
    
    def _generate_wondering(self, interpreted_state: Dict, memory_patterns: Dict) -> Optional[str]:
        """Generate 'What I'm wondering' curiosity"""
        
        mind_body_alignment = interpreted_state.get("mind_body_alignment", "aligned")
        push_risk = interpreted_state.get("push_risk", "low")
        emotional_load = interpreted_state.get("emotional_load", "light")
        
        wonderings = []
        
        # Mind-body curiosity
        if mind_body_alignment in ["slight_mismatch", "misaligned"]:
            wonderings.extend([
                "if there's something your body knows that your mind hasn't caught up to yet",
                "what's behind the disconnect between how you feel and what the numbers say",
                "if you're sensing something the metrics aren't picking up"
            ])
        
        # Push pattern curiosity  
        if push_risk in ["moderate", "high", "very_high"]:
            wonderings.extend([
                "if this feels like familiar territory",
                "what's driving the 'keep going' impulse right now",
                "if you're running on willpower vs. genuine energy"
            ])
        
        # Emotional load curiosity
        if emotional_load in ["heavy", "overwhelming"]:
            wonderings.extend([
                "how the emotional stuff is landing in your body",
                "if the stress is asking for something specific",
                "what would feel supportive right now"
            ])
        
        # Pattern-based curiosity from memory
        relevant_patterns = memory_patterns.get("push_tendencies", [])
        if relevant_patterns:
            top_pattern = relevant_patterns[0]
            if top_pattern["confidence"] > 0.7:
                wonderings.extend([
                    "if this pattern is trying to tell you something",
                    "what this familiar feeling is about"
                ])
        
        return random.choice(wonderings) if wonderings else None
    
    def _generate_gentle_nudge(self, interpreted_state: Dict, memory_patterns: Dict) -> Optional[str]:
        """Generate gentle nudge (never prescriptive)"""
        
        push_risk = interpreted_state.get("push_risk", "low")
        mind_body_alignment = interpreted_state.get("mind_body_alignment", "aligned")
        emotional_load = interpreted_state.get("emotional_load", "light")
        
        nudges = []
        
        # Push risk nudges
        if push_risk in ["high", "very_high"]:
            nudges.extend([
                "Maybe worth checking in with yourself about what's really needed",
                "Might be a good moment to pause and listen to what's underneath",
                "Could be worth asking what your body actually wants right now"
            ])
        
        # Mind-body misalignment nudges
        if mind_body_alignment in ["slight_mismatch", "misaligned"]:
            nudges.extend([
                "Trust the feeling - it's usually onto something",
                "Your intuition about your body is pretty reliable",
                "Worth honoring what you're sensing, even if the numbers disagree"
            ])
        
        # Emotional load nudges
        if emotional_load in ["heavy", "overwhelming"]:
            nudges.extend([
                "Emotional load counts as training load too",
                "Your nervous system doesn't distinguish between types of stress",
                "Sometimes the kindest thing is to adjust expectations"
            ])
        
        # Recovery nudges
        recovery_status = interpreted_state.get("recovery_status", "unknown")
        if recovery_status in ["concerning", "needs-attention"]:
            nudges.extend([
                "Your future self might thank you for listening to this",
                "Small adjustments now can prevent bigger adjustments later",
                "Recovery is where the adaptation actually happens"
            ])
        
        return random.choice(nudges) if nudges else None
    
    def _generate_pattern_flag(self, memory_patterns: Dict) -> Optional[str]:
        """Generate optional pattern flag when meaningful"""
        
        # Only flag high-confidence patterns
        all_patterns = []
        for pattern_type, patterns in memory_patterns.items():
            for pattern in patterns:
                if pattern.get("confidence", 0) > 0.8 and pattern.get("count", 0) >= 3:
                    all_patterns.append(pattern)
        
        if not all_patterns:
            return None
        
        # Choose highest confidence pattern
        top_pattern = max(all_patterns, key=lambda p: p.get("confidence", 0))
        
        pattern_descriptions = {
            "stress_motivation_push": "You tend to maintain high intensity when stressed",
            "energy_training_disconnect": "Low energy + high training is a recurring theme",
            "identity_erosion_signal": "Feeling 'somewhat' like yourself often precedes needed rest",
            "optimistic_energy_bias": "You often feel more energetic than your body metrics suggest",
            "metrics_energy_disconnect": "Sometimes your intuition picks up what metrics miss"
        }
        
        pattern_name = top_pattern.get("name", "")
        if pattern_name in pattern_descriptions:
            base_phrase = random.choice(self.approved_phrases["pattern_flags"])
            description = pattern_descriptions[pattern_name]
            return f"{base_phrase} - {description}"
        
        return None
    
    def _translate_to_kelly_voice(self, clinical_insight: str) -> str:
        """Convert clinical language to Kelly's preferred voice"""
        
        # Common translations
        translations = {
            "hrv down": "heart rate variability dipped",
            "readiness low": "readiness scores are lower",
            "sleep debt": "sleep has been short",
            "consecutive": "several days of",
            "elevated": "higher than usual",
            "concerning": "getting my attention",
            "metrics show": "I'm seeing",
            "data indicates": "it looks like",
            "analysis reveals": "what stands out is"
        }
        
        result = clinical_insight.lower()
        for clinical, kelly in translations.items():
            result = result.replace(clinical, kelly)
        
        # Remove clinical language
        for avoid in self.avoid_phrases:
            if avoid in result:
                result = result.replace(avoid, "")
        
        # Ensure it starts with Kelly's observational style
        if not any(result.startswith(prefix) for prefix in ["your", "it looks", "i'm seeing", "what stands"]):
            result = f"your {result}" if not result.startswith("your") else result
        
        return result.capitalize()
    
    def generate_manual_checkin_prompt(self) -> str:
        """Generate prompt for manual check-in in Kelly's voice"""
        
        prompts = [
            "Quick body check - how are things feeling today?",
            "Time for a check-in with yourself. What's your sense of things?", 
            "Let's see how you're doing. What's happening in your world?",
            "Body and mind check - what's the real story today?",
            "How are you actually feeling? The honest version."
        ]
        
        return random.choice(prompts)
    
    def format_for_whatsapp(self, message: str) -> str:
        """Format message for WhatsApp (Kelly's preferred channel)"""
        # Replace ** bold ** with WhatsApp formatting
        formatted = message.replace("**", "*")
        
        # Keep it conversational for mobile
        # No markdown tables, use bullet points
        
        return formatted
    
    def should_stay_quiet(self, interpreted_state: Dict) -> bool:
        """Kelly's specific 'stay quiet' conditions"""
        
        recovery_status = interpreted_state.get("recovery_status", "unknown") 
        mind_body_alignment = interpreted_state.get("mind_body_alignment", "aligned")
        push_risk = interpreted_state.get("push_risk", "low")
        
        # Stay quiet when: nothing meaningful changed
        if (recovery_status == "good" and 
            mind_body_alignment == "aligned" and 
            push_risk == "low"):
            return True
        
        # Stay quiet when: would just restate data
        insights = interpreted_state.get("insights", [])
        if len(insights) == 0:
            return True
        
        # Stay quiet when: everything is "okay-ish" with no patterns
        if (recovery_status == "okay-ish" and 
            mind_body_alignment == "aligned" and
            not any("pattern" in insight.lower() for insight in insights)):
            return True
        
        return False

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly_voice.py test           # Test voice generation")
        print("  python3 welly_voice.py checkin       # Generate check-in prompt")
        print("  python3 welly_voice.py format <msg>  # Format for WhatsApp")
        return
    
    voice = WellyVoice()
    command = sys.argv[1]
    
    if command == "test":
        # Test with sample interpreted state
        test_state = {
            "recovery_status": "concerning",
            "mind_body_alignment": "misaligned", 
            "push_risk": "high",
            "emotional_load": "heavy",
            "insights": [
                "Energy feels good but body metrics suggest rest",
                "High stress but high motivation - classic push zone",
                "HRV down 20% from baseline"
            ]
        }
        
        test_patterns = {
            "push_tendencies": [{
                "name": "stress_motivation_push",
                "confidence": 0.9,
                "count": 5
            }],
            "mind_body_patterns": []
        }
        
        check_in = voice.generate_daily_check_in(test_state, test_patterns)
        if check_in:
            print("Generated check-in:")
            print(check_in)
        else:
            print("Would stay quiet")
            
    elif command == "checkin":
        prompt = voice.generate_manual_checkin_prompt()
        print(f"Check-in prompt: {prompt}")
        
    elif command == "format":
        if len(sys.argv) > 2:
            message = " ".join(sys.argv[2:])
            formatted = voice.format_for_whatsapp(message)
            print("Formatted for WhatsApp:")
            print(formatted)
        else:
            print("Please provide a message to format")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()