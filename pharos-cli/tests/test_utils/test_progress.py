"""Tests for progress bar utilities."""

import pytest
import time
from unittest.mock import MagicMock, patch
from typing import Generator

from pharos_cli.utils.progress import (
    Spinner,
    get_progress,
    get_file_progress,
    get_batch_progress,
    progress_context,
    iter_with_progress,
    iter_with_callback,
    iter_with_status,
    spinner_context,
    track_progress,
    ProgressStats,
    ThroughputColumn,
)


class TestProgressStats:
    """Tests for ProgressStats dataclass."""
    
    def test_percent_complete_zero_total(self):
        """Test percent complete with zero total."""
        stats = ProgressStats(
            total=0,
            completed=0,
            elapsed_seconds=1.0,
            items_per_second=0.0,
            eta_seconds=0.0,
        )
        assert stats.percent_complete == 100.0
    
    def test_percent_complete_partial(self):
        """Test percent complete with partial progress."""
        stats = ProgressStats(
            total=100,
            completed=50,
            elapsed_seconds=5.0,
            items_per_second=10.0,
            eta_seconds=5.0,
        )
        assert stats.percent_complete == 50.0
    
    def test_percent_complete_full(self):
        """Test percent complete with full progress."""
        stats = ProgressStats(
            total=100,
            completed=100,
            elapsed_seconds=10.0,
            items_per_second=10.0,
            eta_seconds=0.0,
        )
        assert stats.percent_complete == 100.0
    
    def test_format_throughput_items_per_second(self):
        """Test formatting throughput as items per second."""
        stats = ProgressStats(
            total=100,
            completed=100,
            elapsed_seconds=10.0,
            items_per_second=10.0,
            eta_seconds=0.0,
        )
        assert stats.format_throughput() == "10.0 items/s"
    
    def test_format_throughput_items_per_minute(self):
        """Test formatting throughput as items per minute."""
        stats = ProgressStats(
            total=100,
            completed=100,
            elapsed_seconds=10.0,
            items_per_second=0.5,  # 30 per minute
            eta_seconds=0.0,
        )
        assert stats.format_throughput() == "30.0 items/min"
    
    def test_format_throughput_zero(self):
        """Test formatting zero throughput."""
        stats = ProgressStats(
            total=100,
            completed=0,
            elapsed_seconds=0.0,
            items_per_second=0.0,
            eta_seconds=0.0,
        )
        assert stats.format_throughput() == "0.0 items/s"
    
    def test_format_eta_seconds(self):
        """Test formatting ETA in seconds."""
        stats = ProgressStats(
            total=100,
            completed=50,
            elapsed_seconds=5.0,
            items_per_second=10.0,
            eta_seconds=30.0,
        )
        assert stats.format_eta() == "30s"
    
    def test_format_eta_minutes(self):
        """Test formatting ETA in minutes."""
        stats = ProgressStats(
            total=100,
            completed=50,
            elapsed_seconds=5.0,
            items_per_second=1.0,
            eta_seconds=120.0,
        )
        assert stats.format_eta() == "2m"
    
    def test_format_eta_hours(self):
        """Test formatting ETA in hours."""
        stats = ProgressStats(
            total=1000,
            completed=100,
            elapsed_seconds=10.0,
            items_per_second=10.0,
            eta_seconds=5400.0,  # 1.5 hours
        )
        assert stats.format_eta() == "1.5h"
    
    def test_format_eta_negative(self):
        """Test formatting negative ETA (unknown)."""
        stats = ProgressStats(
            total=100,
            completed=0,
            elapsed_seconds=0.0,
            items_per_second=0.0,
            eta_seconds=-1.0,
        )
        assert stats.format_eta() == "N/A"


class TestThroughputColumn:
    """Tests for ThroughputColumn."""
    
    def test_init(self):
        """Test ThroughputColumn initialization."""
        col = ThroughputColumn(unit="files", width=15)
        assert col.unit == "files"
        assert col.width == 15
    
    def test_default_width(self):
        """Test ThroughputColumn default width."""
        col = ThroughputColumn(unit="items")
        assert col.width == 12


class TestSpinner:
    """Tests for Spinner class."""
    
    def test_init(self):
        """Test Spinner initialization."""
        spinner = Spinner("Processing...")
        assert spinner.message == "Processing..."
        assert spinner.spinner_name == "dots"
    
    def test_init_custom_spinner(self):
        """Test Spinner with custom spinner name."""
        spinner = Spinner("Loading...", spinner_name="line")
        assert spinner.spinner_name == "line"
    
    def test_context_manager_no_error(self):
        """Test Spinner as context manager without errors."""
        with Spinner("Processing..."):
            pass  # No-op
    
    def test_context_manager_with_work(self):
        """Test Spinner context manager with actual work."""
        with Spinner("Processing..."):
            time.sleep(0.01)  # Brief delay
    
    def test_update_message(self):
        """Test updating spinner message."""
        spinner = Spinner("Initial message")
        # Mock the _live attribute
        spinner._live = MagicMock()
        spinner.update("New message")
        spinner._live.refresh.assert_called_once()


class TestGetProgress:
    """Tests for get_progress function."""
    
    def test_get_progress_default(self):
        """Test get_progress with default parameters."""
        progress = get_progress()
        assert progress is not None
    
    def test_get_progress_custom_description(self):
        """Test get_progress with custom description."""
        progress = get_progress("Custom description")
        assert progress is not None
    
    def test_get_progress_no_throughput(self):
        """Test get_progress without throughput."""
        progress = get_progress(show_throughput=False)
        assert progress is not None
    
    def test_get_progress_custom_unit(self):
        """Test get_progress with custom throughput unit."""
        progress = get_progress(throughput_unit="files")
        assert progress is not None


class TestGetFileProgress:
    """Tests for get_file_progress function."""
    
    def test_get_file_progress(self):
        """Test get_file_progress returns a Progress instance."""
        progress = get_file_progress("Processing files")
        assert progress is not None


class TestGetBatchProgress:
    """Tests for get_batch_progress function."""
    
    def test_get_batch_progress(self):
        """Test get_batch_progress returns a Progress instance."""
        progress = get_batch_progress("Processing batch")
        assert progress is not None


class TestProgressContext:
    """Tests for progress_context context manager."""
    
    def test_progress_context_empty_list(self):
        """Test progress_context with empty list."""
        with progress_context([], "Processing"):
            pass
    
    def test_progress_context_with_items(self):
        """Test progress_context with items."""
        items = [1, 2, 3]
        result = []
        with progress_context(items, "Processing") as progress:
            for item in items:
                result.append(item)
        assert result == items
    
    def test_progress_context_no_throughput(self):
        """Test progress_context without throughput."""
        items = [1, 2, 3]
        with progress_context(items, "Processing", show_throughput=False):
            for item in items:
                pass


class TestIterWithProgress:
    """Tests for iter_with_progress function."""
    
    def test_iter_with_progress_empty(self):
        """Test iter_with_progress with empty list."""
        result = list(iter_with_progress([], "Processing"))
        assert result == []
    
    def test_iter_with_progress_items(self):
        """Test iter_with_progress with items."""
        items = [1, 2, 3, 4, 5]
        result = list(iter_with_progress(items, "Processing"))
        assert result == items
    
    def test_iter_with_progress_generator(self):
        """Test iter_with_progress returns a generator."""
        items = [1, 2, 3]
        gen = iter_with_progress(items, "Processing")
        assert hasattr(gen, "__iter__")
        assert hasattr(gen, "__next__")


class TestIterWithCallback:
    """Tests for iter_with_callback function."""
    
    def test_iter_with_callback_empty(self):
        """Test iter_with_callback with empty list."""
        callback = MagicMock()
        stats = iter_with_callback([], callback, "Processing")
        assert stats.total == 0
        assert stats.completed == 0
        callback.assert_not_called()
    
    def test_iter_with_callback_with_items(self):
        """Test iter_with_callback with items."""
        callback = MagicMock()
        items = [1, 2, 3]
        stats = iter_with_callback(items, callback, "Processing")
        assert stats.total == 3
        assert stats.completed == 3
        assert callback.call_count == 3
    
    def test_iter_with_callback_stats(self):
        """Test iter_with_callback returns correct stats."""
        callback = MagicMock()
        items = [1, 2, 3]
        stats = iter_with_callback(items, callback, "Processing")
        assert stats.total == 3
        assert stats.completed == 3
        assert stats.elapsed_seconds >= 0
        assert stats.items_per_second > 0 or stats.completed == 0
        assert isinstance(stats.eta_seconds, float)


class TestIterWithStatus:
    """Tests for iter_with_status function."""
    
    def test_iter_with_status_empty(self):
        """Test iter_with_status with empty list."""
        results = list(iter_with_status([], "Processing"))
        assert len(results) == 1
        assert results[0]["completed"] == 0
        assert results[0]["total"] == 0
    
    def test_iter_with_status_with_items(self):
        """Test iter_with_status with items."""
        items = [1, 2, 3]
        results = list(iter_with_status(items, "Processing"))
        
        # Should have one result per item + final status
        assert len(results) == len(items) + 1
        
        # Check first result
        assert results[0]["item"] == 1
        assert results[0]["completed"] == 0
        assert results[0]["total"] == 3
        
        # Check final result
        final = results[-1]
        assert final["item"] is None
        assert final["completed"] == 3
        assert "stats" in final
    
    def test_iter_with_status_progress_increases(self):
        """Test iter_with_status shows increasing progress."""
        items = [1, 2, 3]
        results = list(iter_with_status(items, "Processing"))
        
        completed_values = [r["completed"] for r in results[:-1]]  # Exclude final
        assert completed_values == [0, 1, 2]


class TestSpinnerContext:
    """Tests for spinner_context function."""
    
    def test_spinner_context_empty(self):
        """Test spinner_context with no work."""
        with spinner_context("Processing..."):
            pass
    
    def test_spinner_context_with_work(self):
        """Test spinner_context with work."""
        with spinner_context("Loading..."):
            time.sleep(0.01)
    
    def test_spinner_context_custom_spinner(self):
        """Test spinner_context with custom spinner."""
        with spinner_context("Loading...", spinner_name="line"):
            pass


class TestTrackProgress:
    """Tests for track_progress decorator."""
    
    def test_track_progress_empty_list(self):
        """Test track_progress with empty list."""
        @track_progress("Processing")
        def process_items(items):
            return len(items)
        
        result = process_items([])
        assert result == 0
    
    def test_track_progress_with_items(self):
        """Test track_progress with items."""
        @track_progress("Processing")
        def process_items(items):
            return [item * 2 for item in items]
        
        result = process_items([1, 2, 3])
        assert result == [2, 4, 6]
    
    def test_track_progress_with_kwargs(self):
        """Test track_progress with keyword arguments."""
        @track_progress("Processing")
        def process_files(files=None):
            return len(files) if files else 0
        
        result = process_files(files=["a.txt", "b.txt"])
        assert result == 2
    
    def test_track_progress_with_return(self):
        """Test track_progress preserves return value."""
        @track_progress("Processing")
        def my_function():
            return "success"
        
        result = my_function()
        assert result == "success"


class TestProgressIntegration:
    """Integration tests for progress utilities."""
    
    def test_full_iteration_workflow(self):
        """Test complete iteration workflow with progress."""
        items = list(range(10))
        results = []
        
        for item in iter_with_progress(items, "Processing items"):
            results.append(item)
            time.sleep(0.001)  # Brief delay
        
        assert results == items
    
    def test_callback_workflow_with_stats(self):
        """Test callback workflow and verify stats."""
        items = [1, 2, 3, 4, 5]
        processed = []
        
        def process(item):
            processed.append(item)
            time.sleep(0.001)
        
        stats = iter_with_callback(items, process, "Processing")
        
        assert stats.completed == len(items)
        assert processed == items
        assert stats.percent_complete == 100.0
    
    def test_multiple_progress_bars(self):
        """Test using multiple progress bars in sequence."""
        items1 = [1, 2, 3]
        items2 = ["a", "b", "c"]
        
        results1 = list(iter_with_progress(items1, "First batch"))
        results2 = list(iter_with_progress(items2, "Second batch"))
        
        assert results1 == items1
        assert results2 == items2