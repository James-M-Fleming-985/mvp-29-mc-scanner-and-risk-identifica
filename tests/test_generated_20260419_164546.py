import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from layer_mvp_0029 import (
    RegulatoryDataIngester,
    RegulatoryEventProcessor,
    RiskClassificationEngine,
    RegulatoryDashboard,
    ComplianceFrameworkManager,
    APIDataSource,
    RSSDataSource,
    WebScrapingDataSource,
    RegulatoryEvent,
    RiskLevel,
    EventStorage,
    EventRetrieval,
    RegulatoryChangeDetector,
    RiskAssessmentDashboard
)


class TestRegulatoryDataIngestion:
    """Unit tests for regulatory data ingestion from multiple sources."""

    def test_api_data_source_ingestion(self):
        """Test ingestion of regulatory data from API sources."""
        api_source = APIDataSource("https://api.example.gov/regulations")
        ingester = RegulatoryDataIngester()
        
        mock_api_data = {
            "regulations": [
                {"id": "REG-001", "title": "Chemical Safety Update", "date": "2024-01-15"}
            ]
        }
        
        with patch.object(api_source, 'fetch_data', return_value=mock_api_data):
            result = ingester.ingest_from_api(api_source)
            
        assert len(result) == 1
        assert result[0]["id"] == "REG-001"
        assert result[0]["title"] == "Chemical Safety Update"

    def test_rss_feed_ingestion(self):
        """Test ingestion of regulatory data from RSS feeds."""
        rss_source = RSSDataSource("https://example.gov/regulations.rss")
        ingester = RegulatoryDataIngester()
        
        mock_rss_data = [
            {"title": "New REACH Regulation", "link": "https://example.gov/reach-001", "pubDate": "2024-01-15"}
        ]
        
        with patch.object(rss_source, 'fetch_feed', return_value=mock_rss_data):
            result = ingester.ingest_from_rss(rss_source)
            
        assert len(result) == 1
        assert result[0]["title"] == "New REACH Regulation"
        assert result[0]["link"] == "https://example.gov/reach-001"

    def test_web_scraping_ingestion(self):
        """Test ingestion of regulatory data from web scraping."""
        scraping_source = WebScrapingDataSource("https://example.gov/regulations")
        ingester = RegulatoryDataIngester()
        
        mock_scraped_data = [
            {"regulation_id": "WS-001", "content": "Updated chemical restrictions", "source_url": "https://example.gov/ws-001"}
        ]
        
        with patch.object(scraping_source, 'scrape_data', return_value=mock_scraped_data):
            result = ingester.ingest_from_web_scraping(scraping_source)
            
        assert len(result) == 1
        assert result[0]["regulation_id"] == "WS-001"
        assert result[0]["content"] == "Updated chemical restrictions"


class TestRegulatoryEventProcessing:
    """Unit tests for converting raw regulatory signals into structured events."""

    def test_raw_signal_to_structured_event_conversion(self):
        """Test conversion of raw regulatory data to structured events."""
        processor = RegulatoryEventProcessor()
        
        raw_data = {
            "id": "REG-001",
            "title": "Chemical Safety Update",
            "content": "New restrictions on chemical XYZ",
            "date": "2024-01-15",
            "source": "API"
        }
        
        structured_event = processor.process_raw_data(raw_data)
        
        assert isinstance(structured_event, RegulatoryEvent)
        assert structured_event.event_id == "REG-001"
        assert structured_event.title == "Chemical Safety Update"
        assert structured_event.content == "New restrictions on chemical XYZ"
        assert structured_event.source_type == "API"

    def test_risk_classification_assignment(self):
        """Test risk classification of regulatory events."""
        classifier = RiskClassificationEngine()
        
        high_risk_event = RegulatoryEvent(
            event_id="REG-HIGH-001",
            title="Immediate Chemical Ban",
            content="Chemical XYZ banned effective immediately",
            keywords=["ban", "immediate", "chemical"]
        )
        
        risk_level = classifier.classify_risk(high_risk_event)
        
        assert risk_level == RiskLevel.HIGH
        assert high_risk_event.risk_level == RiskLevel.HIGH

    def test_event_metadata_enrichment(self):
        """Test enrichment of events with metadata and keywords."""
        processor = RegulatoryEventProcessor()
        
        raw_event = {
            "title": "REACH Compliance Update",
            "content": "New SVHC substances added to candidate list"
        }
        
        enriched_event = processor.enrich_event_metadata(raw_event)
        
        assert "REACH" in enriched_event.keywords
        assert "SVHC" in enriched_event.keywords
        assert enriched_event.compliance_framework == "UK_REACH"


class TestDashboardVisualization:
    """Unit tests for dashboard display and visualization capabilities."""

    def test_regulatory_event_feed_display(self):
        """Test display of regulatory event feed in dashboard."""
        dashboard = RegulatoryDashboard()
        
        mock_events = [
            RegulatoryEvent(event_id="E001", title="Event 1", risk_level=RiskLevel.HIGH),
            RegulatoryEvent(event_id="E002", title="Event 2", risk_level=RiskLevel.MEDIUM)
        ]
        
        feed_data = dashboard.get_event_feed(mock_events)
        
        assert len(feed_data) == 2
        assert feed_data[0]["event_id"] == "E001"
        assert feed_data[0]["risk_level"] == "HIGH"
        assert feed_data[1]["event_id"] == "E002"

    def test_risk_level_filtering(self):
        """Test filtering of events by risk level."""
        dashboard = RegulatoryDashboard()
        
        events = [
            RegulatoryEvent(event_id="E001", risk_level=RiskLevel.HIGH),
            RegulatoryEvent(event_id="E002", risk_level=RiskLevel.MEDIUM),
            RegulatoryEvent(event_id="E003", risk_level=RiskLevel.LOW)
        ]
        
        high_risk_events = dashboard.filter_by_risk_level(events, RiskLevel.HIGH)
        
        assert len(high_risk_events) == 1
        assert high_risk_events[0].event_id == "E001"

    def test_risk_visualization_data(self):
        """Test generation of risk visualization data."""
        dashboard = RegulatoryDashboard()
        
        events = [
            RegulatoryEvent(event_id="E001", risk_level=RiskLevel.HIGH),
            RegulatoryEvent(event_id="E002", risk_level=RiskLevel.HIGH),
            RegulatoryEvent(event_id="E003", risk_level=RiskLevel.MEDIUM)
        ]
        
        viz_data = dashboard.generate_risk_visualization(events)
        
        assert viz_data["risk_distribution"]["HIGH"] == 2
        assert viz_data["risk_distribution"]["MEDIUM"] == 1
        assert viz_data["risk_distribution"]["LOW"] == 0


class TestModularComplianceFrameworks:
    """Unit tests for modular expansion of compliance frameworks."""

    def test_uk_reach_framework_support(self):
        """Test support for UK REACH compliance framework."""
        framework_manager = ComplianceFrameworkManager()
        
        uk_reach_framework = framework_manager.get_framework("UK_REACH")
        
        assert uk_reach_framework.name == "UK_REACH"
        assert uk_reach_framework.is_active == True
        assert "chemical_substances" in uk_reach_framework.regulated_areas

    def test_framework_expansion_capability(self):
        """Test ability to add new compliance frameworks."""
        framework_manager = ComplianceFrameworkManager()
        
        new_framework_config = {
            "name": "EU_GDPR",
            "regulated_areas": ["data_protection", "privacy"],
            "risk_keywords": ["data breach", "privacy violation"]
        }
        
        framework_manager.add_framework(new_framework_config)
        gdpr_framework = framework_manager.get_framework("EU_GDPR")
        
        assert gdpr_framework.name == "EU_GDPR"
        assert "data_protection" in gdpr_framework.regulated_areas

    def test_cross_framework_event_classification(self):
        """Test classification of events across multiple frameworks."""
        framework_manager = ComplianceFrameworkManager()
        classifier = RiskClassificationEngine()
        
        event = RegulatoryEvent(
            event_id="MULTI-001",
            content="Chemical data privacy requirements updated",
            keywords=["chemical", "data", "privacy"]
        )
        
        applicable_frameworks = framework_manager.identify_applicable_frameworks(event)
        
        assert "UK_REACH" in applicable_frameworks
        assert len(applicable_frameworks) >= 1


class TestIntegrationDataPipeline:
    """Integration tests for complete data flow from ingestion through risk classification to API output."""

    def test_api_ingestion_to_structured_event(self):
        """Test complete flow from API ingestion to structured event creation."""
        ingester = RegulatoryDataIngester()
        processor = RegulatoryEventProcessor()
        
        mock_api_data = [{
            "id": "API-001",
            "title": "New Chemical Regulation",
            "content": "Updated restrictions on substance ABC",
            "date": "2024-01-15"
        }]
        
        with patch.object(ingester, 'ingest_from_api', return_value=mock_api_data):
            raw_data = ingester.ingest_from_api(Mock())
            structured_event = processor.process_raw_data(raw_data[0])
            
        assert structured_event.event_id == "API-001"
        assert structured_event.title == "New Chemical Regulation"
        assert isinstance(structured_event, RegulatoryEvent)

    def test_risk_classification_engine(self):
        """Test risk classification engine with various event types."""
        classifier = RiskClassificationEngine()
        
        high_risk_event = RegulatoryEvent(
            event_id="HIGH-001",
            content="Immediate ban on chemical substance",
            keywords=["ban", "immediate", "prohibited"]
        )
        
        medium_risk_event = RegulatoryEvent(
            event_id="MED-001",
            content="Updated reporting requirements",
            keywords=["reporting", "requirements", "update"]
        )
        
        high_risk = classifier.classify_risk(high_risk_event)
        medium_risk = classifier.classify_risk(medium_risk_event)
        
        assert high_risk == RiskLevel.HIGH
        assert medium_risk == RiskLevel.MEDIUM

    def test_event_storage_and_retrieval(self):
        """Test storage and retrieval of processed regulatory events."""
        storage = EventStorage()
        retrieval = EventRetrieval()
        
        event = RegulatoryEvent(
            event_id="STORE-001",
            title="Storage Test Event",
            risk_level=RiskLevel.MEDIUM
        )
        
        storage.store_event(event)
        retrieved_event = retrieval.get_event_by_id("STORE-001")
        
        assert retrieved_event.event_id == "STORE-001"
        assert retrieved_event.title == "Storage Test Event"
        assert retrieved_event.risk_level == RiskLevel.MEDIUM


class TestE2ERiskDiscovery:
    """End-to-end tests for complete user journey from regulatory change detection to risk assessment dashboard."""

    def test_regulatory_change_detection_and_dashboard_display(self):
        """Test complete workflow from change detection to dashboard display."""
        detector = RegulatoryChangeDetector()
        dashboard = RiskAssessmentDashboard()
        
        mock_regulatory_change = {
            "source": "gov_api",
            "change_type": "new_regulation",
            "content": "New chemical safety requirements effective March 2024",
            "detected_at": datetime.now()
        }
        
        with patch.object(detector, 'detect_changes', return_value=[mock_regulatory_change]):
            changes = detector.detect_changes()
            processed_events = detector.process_changes_to_events(changes)
            dashboard_data = dashboard.display_events(processed_events)
            
        assert len(dashboard_data["events"]) == 1
        assert dashboard_data["events"][0]["change_type"] == "new_regulation"
        assert "risk_assessment" in dashboard_data["events"][0]

    def test_risk_filtering_and_prioritization_workflow(self):
        """Test risk filtering and prioritization in user workflow."""
        dashboard = RiskAssessmentDashboard()
        
        events = [
            RegulatoryEvent(event_id="E001", title="Critical Ban", risk_level=RiskLevel.HIGH, priority_score=95),
            RegulatoryEvent(event_id="E002", title="Minor Update", risk_level=RiskLevel.LOW, priority_score=15),
            RegulatoryEvent(event_id="E003", title="Important Change", risk_level=RiskLevel.MEDIUM, priority_score=60)
        ]
        
        filtered_high_risk = dashboard.filter_events_by_risk(events, min_risk_level=RiskLevel.MEDIUM)
        prioritized_events = dashboard.prioritize_events(filtered_high_risk)
        
        assert len(filtered_high_risk) == 2
        assert prioritized_events[0].event_id == "E001"
        assert prioritized_events[0].priority_score == 95
        assert prioritized_events[1].event_id == "E003"
