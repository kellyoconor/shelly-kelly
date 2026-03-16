#!/usr/bin/env python3
"""
welly-memory: Long-term pattern storage for Kelly's body-awareness companion

Stores recurring fatigue patterns, injury signals, emotional/training links,
and builds Kelly's personalized recovery insights over time.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics

class WellyMemory:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        
        self.setup_memory_tables()
        
    def setup_memory_tables(self):
        """Initialize memory pattern tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pattern storage for Kelly's tendencies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kelly_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_name TEXT NOT NULL,
                description TEXT,
                triggers TEXT,
                confidence REAL DEFAULT 0.0,
                last_seen TEXT,
                occurrence_count INTEGER DEFAULT 1,
                created_at TEXT,
                UNIQUE(pattern_type, pattern_name)
            )
        ''')
        
        # Injury/pain signal tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS injury_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                body_part TEXT,
                signal_type TEXT,
                severity INTEGER,
                description TEXT,
                preceded_by TEXT,
                resolved_date TEXT,
                created_at TEXT
            )
        ''')
        
        # Emotional-training correlations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotional_training_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                emotional_state TEXT,
                stress_level INTEGER,
                training_response TEXT,
                outcome TEXT,
                notes TEXT,
                created_at TEXT
            )
        ''')
        
        # Recovery pattern insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                insight_text TEXT NOT NULL,
                supporting_data TEXT,
                confidence REAL DEFAULT 0.0,
                first_observed TEXT,
                last_validated TEXT,
                validation_count INTEGER DEFAULT 1,
                created_at TEXT,
                UNIQUE(insight_type, insight_text)
            )
        ''')
        
        # Monthly pattern summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_summaries (
                month TEXT PRIMARY KEY,
                avg_readiness REAL,
                avg_energy REAL,
                avg_stress REAL,
                push_through_episodes INTEGER,
                recovery_wins INTEGER,
                key_patterns TEXT,
                lessons_learned TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def learn_from_daily_state(self, interpreted_state: Dict):
        """Learn patterns from a daily interpretation"""
        date_str = interpreted_state["date"]
        
        # Extract learning signals
        self._extract_push_patterns(date_str, interpreted_state)
        self._extract_alignment_patterns(date_str, interpreted_state) 
        self._extract_recovery_patterns(date_str, interpreted_state)
        self._extract_emotional_patterns(date_str, interpreted_state)
        
    def _extract_push_patterns(self, date_str: str, state: Dict):
        """Identify and store Kelly's push-through patterns"""
        push_risk = state.get("push_risk", "low")
        insights = state.get("insights", [])
        
        # Look for classic push-through signals
        push_indicators = []
        for insight in insights:
            if "high stress but high motivation" in insight.lower():
                push_indicators.append("stress_motivation_push")
            elif "low energy but maintained high training" in insight.lower():
                push_indicators.append("energy_training_disconnect") 
            elif "feeling 'somewhat' like yourself" in insight.lower():
                push_indicators.append("identity_erosion_signal")
            elif "readiness trending down but training intensity up" in insight.lower():
                push_indicators.append("overriding_body_signals")
        
        for indicator in push_indicators:
            self._store_pattern("push_tendency", indicator, {
                "date": date_str,
                "risk_level": push_risk,
                "context": insights
            })
    
    def _extract_alignment_patterns(self, date_str: str, state: Dict):
        """Learn Kelly's mind-body alignment patterns"""
        alignment = state.get("mind_body_alignment", "aligned")
        insights = state.get("insights", [])
        
        if alignment == "misaligned":
            # Store specific mismatch patterns
            for insight in insights:
                if "energy feels good but body metrics suggest rest" in insight.lower():
                    self._store_pattern("mind_body_mismatch", "optimistic_energy_bias", {
                        "date": date_str,
                        "context": insight
                    })
                elif "numbers look good but energy feels low" in insight.lower():
                    self._store_pattern("mind_body_mismatch", "metrics_energy_disconnect", {
                        "date": date_str, 
                        "context": insight
                    })
                elif "feel good but body metrics concerning" in insight.lower():
                    self._store_pattern("mind_body_mismatch", "subjective_override", {
                        "date": date_str,
                        "context": insight
                    })
    
    def _extract_recovery_patterns(self, date_str: str, state: Dict):
        """Learn Kelly's recovery patterns and what works"""
        recovery_status = state.get("recovery_status", "unknown")
        
        # Track what leads to good recovery
        if recovery_status == "good":
            self._store_pattern("recovery_success", "good_recovery_day", {
                "date": date_str,
                "insights": state.get("insights", [])
            })
        
        # Track concerning recovery patterns
        elif recovery_status in ["concerning", "needs-attention"]:
            self._store_pattern("recovery_concern", f"{recovery_status}_recovery", {
                "date": date_str,
                "insights": state.get("insights", [])
            })
    
    def _extract_emotional_patterns(self, date_str: str, state: Dict):
        """Learn emotional load patterns and impacts"""
        emotional_load = state.get("emotional_load", "light")
        
        if emotional_load in ["heavy", "overwhelming"]:
            # Store in emotional-training correlation table
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO emotional_training_links
                    (date, emotional_state, stress_level, training_response, outcome, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date_str,
                    emotional_load,
                    0,  # Would get from daily data
                    "unknown",  # Would analyze training response
                    "pending",  # Would track outcome
                    json.dumps(state.get("insights", [])),
                    datetime.now().isoformat()
                ))
                conn.commit()
            except Exception as e:
                print(f"Error storing emotional pattern: {e}")
            finally:
                conn.close()
    
    def _store_pattern(self, pattern_type: str, pattern_name: str, context: Dict):
        """Store or update a pattern in Kelly's memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if pattern already exists
            cursor.execute('''
                SELECT occurrence_count, confidence FROM kelly_patterns 
                WHERE pattern_type = ? AND pattern_name = ?
            ''', (pattern_type, pattern_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                new_count = existing[0] + 1
                new_confidence = min(1.0, existing[1] + 0.1)  # Gradual confidence increase
                
                cursor.execute('''
                    UPDATE kelly_patterns 
                    SET occurrence_count = ?, confidence = ?, last_seen = ?
                    WHERE pattern_type = ? AND pattern_name = ?
                ''', (new_count, new_confidence, context.get("date"), pattern_type, pattern_name))
            else:
                # Create new pattern
                cursor.execute('''
                    INSERT INTO kelly_patterns
                    (pattern_type, pattern_name, description, triggers, confidence, last_seen, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_type,
                    pattern_name, 
                    json.dumps(context),
                    "",  # Could add trigger analysis
                    0.3,  # Starting confidence
                    context.get("date"),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
        except Exception as e:
            print(f"Error storing pattern: {e}")
        finally:
            conn.close()
    
    def get_relevant_patterns(self, current_state: Dict) -> Dict:
        """Get patterns relevant to Kelly's current state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            relevant_patterns = {
                "push_tendencies": [],
                "mind_body_patterns": [],
                "recovery_patterns": [],
                "emotional_patterns": []
            }
            
            # Get push tendency patterns if current risk is moderate+
            if current_state.get("push_risk", "low") in ["moderate", "high", "very_high"]:
                cursor.execute('''
                    SELECT pattern_name, description, confidence, occurrence_count, last_seen
                    FROM kelly_patterns 
                    WHERE pattern_type = 'push_tendency' AND confidence > 0.5
                    ORDER BY confidence DESC, occurrence_count DESC
                ''')
                
                for row in cursor.fetchall():
                    relevant_patterns["push_tendencies"].append({
                        "name": row[0],
                        "description": json.loads(row[1]) if row[1] else {},
                        "confidence": row[2],
                        "count": row[3],
                        "last_seen": row[4]
                    })
            
            # Get mind-body patterns if alignment is off
            if current_state.get("mind_body_alignment") != "aligned":
                cursor.execute('''
                    SELECT pattern_name, description, confidence, occurrence_count
                    FROM kelly_patterns 
                    WHERE pattern_type = 'mind_body_mismatch' AND confidence > 0.4
                    ORDER BY confidence DESC
                ''')
                
                for row in cursor.fetchall():
                    relevant_patterns["mind_body_patterns"].append({
                        "name": row[0],
                        "description": json.loads(row[1]) if row[1] else {},
                        "confidence": row[2],
                        "count": row[3]
                    })
            
            # Get recovery patterns
            cursor.execute('''
                SELECT pattern_name, description, confidence, occurrence_count
                FROM kelly_patterns 
                WHERE pattern_type LIKE '%recovery%' AND confidence > 0.4
                ORDER BY confidence DESC
                LIMIT 5
            ''')
            
            for row in cursor.fetchall():
                relevant_patterns["recovery_patterns"].append({
                    "name": row[0],
                    "description": json.loads(row[1]) if row[1] else {},
                    "confidence": row[2],
                    "count": row[3]
                })
            
            return relevant_patterns
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def generate_personalized_insight(self, current_state: Dict) -> Optional[str]:
        """Generate a personalized insight based on Kelly's learned patterns"""
        patterns = self.get_relevant_patterns(current_state)
        
        # Check for high-confidence push patterns
        push_patterns = patterns.get("push_tendencies", [])
        if push_patterns:
            top_pattern = push_patterns[0]
            if top_pattern["confidence"] > 0.7:
                if top_pattern["name"] == "stress_motivation_push":
                    return "This looks like one of your 'I can push through it' stretches"
                elif top_pattern["name"] == "energy_training_disconnect":
                    return "Your body's been whispering for a few days"
                elif top_pattern["name"] == "identity_erosion_signal":
                    return "You've been feeling 'somewhat' like yourself - worth checking in"
        
        # Check for mind-body misalignment patterns
        mind_body_patterns = patterns.get("mind_body_patterns", [])
        if mind_body_patterns:
            top_pattern = mind_body_patterns[0]
            if top_pattern["confidence"] > 0.6:
                if top_pattern["name"] == "optimistic_energy_bias":
                    return "Numbers say okay-ish. Mood says not quite"
                elif top_pattern["name"] == "metrics_energy_disconnect":
                    return "Metrics look good but something feels off - trust the feeling"
        
        return None
    
    def create_monthly_summary(self, month_str: str):
        """Create monthly pattern summary for Kelly's review"""
        start_date = datetime.strptime(f"{month_str}-01", "%Y-%m-%d")
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get monthly averages
            cursor.execute('''
                SELECT AVG(readiness), AVG(energy), AVG(stress)
                FROM daily_state
                WHERE date >= ? AND date <= ?
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            averages = cursor.fetchone()
            avg_readiness, avg_energy, avg_stress = averages if averages else (0, 0, 0)
            
            # Count push episodes and recovery wins
            cursor.execute('''
                SELECT COUNT(*)
                FROM kelly_patterns
                WHERE pattern_type = 'push_tendency' 
                AND last_seen >= ? AND last_seen <= ?
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            push_episodes = cursor.fetchone()[0] if cursor.fetchone() else 0
            
            cursor.execute('''
                SELECT COUNT(*)
                FROM kelly_patterns
                WHERE pattern_type = 'recovery_success'
                AND last_seen >= ? AND last_seen <= ?
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            recovery_wins = cursor.fetchone()[0] if cursor.fetchone() else 0
            
            # Get key patterns for the month
            cursor.execute('''
                SELECT pattern_type, pattern_name, occurrence_count
                FROM kelly_patterns
                WHERE last_seen >= ? AND last_seen <= ?
                ORDER BY occurrence_count DESC
                LIMIT 5
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            key_patterns = []
            for row in cursor.fetchall():
                key_patterns.append(f"{row[1]} ({row[2]}x)")
            
            # Generate lessons learned
            lessons = []
            if avg_energy < 3:
                lessons.append("Energy consistently low - consider recovery focus")
            if avg_stress > 3.5:
                lessons.append("Stress elevated frequently - impacts training")
            if push_episodes > recovery_wins:
                lessons.append("More pushing than recovering - balance needed")
            
            # Store monthly summary
            cursor.execute('''
                INSERT OR REPLACE INTO monthly_summaries
                (month, avg_readiness, avg_energy, avg_stress, push_through_episodes,
                 recovery_wins, key_patterns, lessons_learned, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                month_str,
                avg_readiness or 0,
                avg_energy or 0, 
                avg_stress or 0,
                push_episodes,
                recovery_wins,
                json.dumps(key_patterns),
                json.dumps(lessons),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            return {
                "month": month_str,
                "averages": {
                    "readiness": avg_readiness,
                    "energy": avg_energy,
                    "stress": avg_stress
                },
                "episodes": {
                    "push_through": push_episodes,
                    "recovery_wins": recovery_wins
                },
                "key_patterns": key_patterns,
                "lessons_learned": lessons
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_pattern_insights(self, lookback_days: int = 30) -> List[str]:
        """Get actionable insights from learned patterns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insights = []
        
        try:
            # Most frequent push patterns
            cursor.execute('''
                SELECT pattern_name, occurrence_count, confidence
                FROM kelly_patterns
                WHERE pattern_type = 'push_tendency'
                AND last_seen >= ?
                AND confidence > 0.6
                ORDER BY occurrence_count DESC
                LIMIT 3
            ''', (start_date.strftime('%Y-%m-%d'),))
            
            for row in cursor.fetchall():
                pattern_name, count, confidence = row
                if pattern_name == "stress_motivation_push" and count >= 3:
                    insights.append(f"You've pushed through stress {count} times recently - classic pattern")
                elif pattern_name == "energy_training_disconnect" and count >= 2:
                    insights.append(f"Low energy but high training {count} times - body asking for attention")
            
            # Recovery success patterns
            cursor.execute('''
                SELECT pattern_name, occurrence_count
                FROM kelly_patterns
                WHERE pattern_type = 'recovery_success'
                AND last_seen >= ?
                ORDER BY occurrence_count DESC
                LIMIT 2
            ''', (start_date.strftime('%Y-%m-%d'),))
            
            for row in cursor.fetchall():
                pattern_name, count = row
                if count >= 2:
                    insights.append(f"Recovery wins when following your patterns - {count} good examples")
            
            return insights
            
        except Exception as e:
            return [f"Error generating insights: {str(e)}"]
        finally:
            conn.close()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly_memory.py patterns          # Get current patterns")
        print("  python3 welly_memory.py insights [days]   # Get pattern insights")
        print("  python3 welly_memory.py summary YYYY-MM   # Generate monthly summary")
        print("  python3 welly_memory.py learn             # Learn from recent data")
        return
    
    memory = WellyMemory()
    command = sys.argv[1]
    
    if command == "patterns":
        # Show current patterns
        test_state = {"push_risk": "moderate", "mind_body_alignment": "misaligned"}
        patterns = memory.get_relevant_patterns(test_state)
        print(json.dumps(patterns, indent=2))
        
    elif command == "insights":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        insights = memory.get_pattern_insights(days)
        print("Pattern insights:")
        for insight in insights:
            print(f"  • {insight}")
    
    elif command == "summary":
        month_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m')
        summary = memory.create_monthly_summary(month_str)
        print(json.dumps(summary, indent=2))
    
    elif command == "learn":
        print("Learning functionality would analyze recent daily_state data")
        print("Call memory.learn_from_daily_state() with interpreted states")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()