"""
Unit tests for recurrence utilities
"""
import pytest
from datetime import datetime, timedelta
from utils.recurrence import RecurrenceRule


class TestRecurrenceRuleParsing:
    """Test recurrence rule parsing"""
    
    def test_parse_simple_daily(self):
        """Test parsing simple daily rule"""
        result = RecurrenceRule.parse_simple_rule("daily")
        assert result['freq'] == 'DAILY'
        assert result['interval'] == 1
    
    def test_parse_simple_weekly(self):
        """Test parsing simple weekly rule"""
        result = RecurrenceRule.parse_simple_rule("weekly")
        assert result['freq'] == 'WEEKLY'
        assert result['interval'] == 1
    
    def test_parse_rrule_format(self):
        """Test parsing RRULE format"""
        result = RecurrenceRule.parse_simple_rule("FREQ=DAILY;INTERVAL=2")
        assert result['FREQ'] == 'DAILY'
        assert result['INTERVAL'] == '2'
    
    def test_parse_empty_rule(self):
        """Test parsing empty rule"""
        result = RecurrenceRule.parse_simple_rule("")
        assert result == {}


class TestRecurrenceRuleCreation:
    """Test recurrence rule creation"""
    
    def test_create_daily_rule(self):
        """Test creating daily rule"""
        rule = RecurrenceRule.create_rule("daily", 1)
        assert rule == "FREQ=DAILY;INTERVAL=1"
    
    def test_create_weekly_rule(self):
        """Test creating weekly rule"""
        rule = RecurrenceRule.create_rule("weekly", 2)
        assert rule == "FREQ=WEEKLY;INTERVAL=2"
    
    def test_create_monthly_rule(self):
        """Test creating monthly rule"""
        rule = RecurrenceRule.create_rule("monthly", 1)
        assert rule == "FREQ=MONTHLY;INTERVAL=1"


class TestNextOccurrence:
    """Test next occurrence calculation"""
    
    def test_daily_next_occurrence(self):
        """Test daily recurrence next occurrence"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=DAILY;INTERVAL=1"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 1)
        assert next_date == datetime(2024, 1, 2, 12, 0, 0)
    
    def test_weekly_next_occurrence(self):
        """Test weekly recurrence next occurrence"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=WEEKLY;INTERVAL=1"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 1)
        assert next_date == datetime(2024, 1, 8, 12, 0, 0)
    
    def test_monthly_next_occurrence(self):
        """Test monthly recurrence next occurrence"""
        base_date = datetime(2024, 1, 15, 12, 0, 0)
        rule = "FREQ=MONTHLY;INTERVAL=1"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 1)
        assert next_date == datetime(2024, 2, 15, 12, 0, 0)
    
    def test_yearly_next_occurrence(self):
        """Test yearly recurrence next occurrence"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=YEARLY;INTERVAL=1"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 1)
        assert next_date == datetime(2025, 1, 1, 12, 0, 0)
    
    def test_multiple_occurrences(self):
        """Test calculating multiple occurrences"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=DAILY;INTERVAL=1"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 3)
        assert next_date == datetime(2024, 1, 4, 12, 0, 0)
    
    def test_invalid_rule(self):
        """Test with invalid rule"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "INVALID"
        
        next_date = RecurrenceRule.get_next_occurrence(base_date, rule, 1)
        assert next_date is None


class TestGenerateOccurrences:
    """Test generating multiple occurrences"""
    
    def test_generate_daily_occurrences(self):
        """Test generating daily occurrences"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=DAILY;INTERVAL=1"
        
        occurrences = RecurrenceRule.generate_occurrences(base_date, rule, 5)
        
        assert len(occurrences) == 5
        assert occurrences[0] == datetime(2024, 1, 2, 12, 0, 0)
        assert occurrences[4] == datetime(2024, 1, 6, 12, 0, 0)
    
    def test_generate_weekly_occurrences(self):
        """Test generating weekly occurrences"""
        base_date = datetime(2024, 1, 1, 12, 0, 0)
        rule = "FREQ=WEEKLY;INTERVAL=1"
        
        occurrences = RecurrenceRule.generate_occurrences(base_date, rule, 3)
        
        assert len(occurrences) == 3
        assert occurrences[0] == datetime(2024, 1, 8, 12, 0, 0)
        assert occurrences[2] == datetime(2024, 1, 22, 12, 0, 0)
