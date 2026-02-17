"""Progress bar utilities for Pharos CLI.

Provides progress bars, spinners, ETA calculation, and throughput display
for long-running operations in the Pharos CLI.
"""

import time
from typing import Iterator, Optional, Any, Callable, List, Dict
from contextlib import contextmanager
from dataclasses import dataclass

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    Column,
)
from rich.text import Text
from rich.console import Console

from pharos_cli.utils.console import get_console


@dataclass
class ProgressStats:
    """Statistics for a progress operation."""
    total: int
    completed: int
    elapsed_seconds: float
    items_per_second: float
    eta_seconds: float
    
    @property
    def percent_complete(self) -> float:
        """Return percentage complete."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100
    
    def format_throughput(self) -> str:
        """Format throughput as human-readable string."""
        if self.items_per_second >= 1:
            return f"{self.items_per_second:.1f} items/s"
        elif self.items_per_second > 0:
            return f"{self.items_per_second * 60:.1f} items/min"
        return "0.0 items/s"
    
    def format_eta(self) -> str:
        """Format ETA as human-readable string."""
        if self.eta_seconds < 0:
            return "N/A"
        elif self.eta_seconds < 60:
            return f"{self.eta_seconds:.0f}s"
        elif self.eta_seconds < 3600:
            return f"{self.eta_seconds / 60:.0f}m"
        else:
            return f"{self.eta_seconds / 3600:.1f}h"


class ThroughputColumn(Column):
    """Custom column that displays throughput in items per second."""
    
    def __init__(self, unit: str = "items", width: int = 12):
        super().__init__(width=width, justify="right")
        self.unit = unit
    
    def render(self, task: "rich.progress.Task") -> Text:
        """Render the throughput column."""
        if task.speed is None:
            return Text(f"0.0 {self.unit}/s", style="progress.download")
        
        speed = task.speed
        if speed >= 1:
            return Text(f"{speed:.1f} {self.unit}/s", style="progress.download")
        elif speed > 0:
            return Text(f"{speed * 60:.1f} {self.unit}/m", style="progress.download")
        else:
            return Text(f"0.0 {self.unit}/s", style="progress.download")
    
    def __call__(self, task: "rich.progress.Task") -> Text:
        """Make the column callable for Rich's Progress."""
        return self.render(task)
    
    def get_table_column(self) -> "rich.table.Column":
        """Get the table column for display.
        
        Returns:
            Table column configuration
        """
        from rich.table import Column as TableColumn
        return TableColumn(
            width=self.width,
            min_width=self.min_width,
            max_width=self.max_width,
            ratio=self.ratio,
            overflow=self.overflow,
        )


class Spinner:
    """Spinner context manager for long-running operations.
    
    Usage:
        with Spinner("Processing...") as spinner:
            do_work()
            spinner.update("Almost done...")
    """
    
    def __init__(
        self,
        message: str,
        spinner_name: str = "dots",
        console: Optional[Console] = None
    ):
        self.message = message
        self.spinner_name = spinner_name
        self.console = console or get_console()
        self._live = None
    
    def __enter__(self):
        from rich.live import Live
        from rich.spinner import Spinner as RichSpinner
        
        spinner = RichSpinner(self.spinner_name, text=self.message)
        self._live = Live(spinner, transient=True, console=self.console)
        self._live.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._live:
            self._live.stop()
    
    def update(self, message: str) -> None:
        """Update the spinner message.
        
        Args:
            message: New message to display
        """
        if self._live:
            self._live.refresh()


def get_progress(
    description: str = "Processing",
    show_throughput: bool = True,
    throughput_unit: str = "items",
) -> Progress:
    """Get a configured progress bar instance.
    
    Args:
        description: Default description for progress tasks
        show_throughput: Whether to show throughput (items/sec)
        throughput_unit: Unit to display for throughput
        
    Returns:
        Configured Progress instance
    """
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ]
    
    if show_throughput:
        columns.append(ThroughputColumn(unit=throughput_unit))
    
    return Progress(
        *columns,
        transient=True,
        console=get_console(),
    )


def get_file_progress(description: str = "Processing files") -> Progress:
    """Get a progress bar configured for file operations.
    
    Args:
        description: Description for the progress bar
        
    Returns:
        Progress instance configured for file operations
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(show_speed=True),
        TimeRemainingColumn(),
        transient=True,
        console=get_console(),
    )


def get_batch_progress(description: str = "Processing") -> Progress:
    """Get a progress bar configured for batch operations.
    
    Includes ETA and throughput display for batch processing.
    
    Args:
        description: Description for the progress bar
        
    Returns:
        Progress instance configured for batch operations
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("("),
        ThroughputColumn(unit="items"),
        TextColumn(") "),
        TimeRemainingColumn(),
        transient=True,
        console=get_console(),
    )


@contextmanager
def progress_context(
    items: list,
    description: str = "Processing",
    show_throughput: bool = True,
):
    """Context manager for iterating with a progress bar.
    
    Args:
        items: List of items to iterate over
        description: Description for the progress bar
        show_throughput: Whether to show throughput
        
    Yields:
        Progress instance
        
    Usage:
        with progress_context(files, "Processing files") as progress:
            for file in files:
                process_file(file)
    """
    with get_progress(description, show_throughput=show_throughput) as progress:
        task = progress.add_task(description, total=len(items))
        yield progress
        # Ensure task is marked as complete
        progress.update(task, completed=len(items))


def iter_with_progress(
    items: list,
    description: str = "Processing",
    show_throughput: bool = True,
) -> Iterator[Any]:
    """Iterate over items with a progress bar.
    
    Args:
        items: List of items to iterate over
        description: Description for the progress bar
        show_throughput: Whether to show throughput
        
    Yields:
        Items from the list one at a time
        
    Usage:
        for item in iter_with_progress(items, "Processing"):
            process(item)
    """
    with get_progress(description, show_throughput=show_throughput) as progress:
        task = progress.add_task(description, total=len(items))
        for item in items:
            yield item
            progress.update(task, advance=1)


def iter_with_callback(
    items: list,
    callback: Callable[[Any], None],
    description: str = "Processing",
    show_throughput: bool = True,
) -> ProgressStats:
    """Iterate over items with a progress bar and call a callback for each.
    
    Args:
        items: List of items to iterate over
        callback: Function to call for each item
        description: Description for the progress bar
        show_throughput: Whether to show throughput
        
    Returns:
        ProgressStats with final statistics
        
    Usage:
        def process(item):
            # do work
            pass
        
        stats = iter_with_callback(items, process, "Processing")
        print(f"Processed {stats.completed} items at {stats.format_throughput()}")
    """
    start_time = time.time()
    completed = 0
    
    with get_progress(description, show_throughput=show_throughput) as progress:
        task = progress.add_task(description, total=len(items))
        
        for item in items:
            callback(item)
            completed += 1
            progress.update(task, advance=1)
    
    elapsed = time.time() - start_time
    total = len(items)
    
    # Calculate throughput
    if elapsed > 0:
        items_per_second = completed / elapsed
    else:
        items_per_second = 0
    
    # Calculate ETA
    if items_per_second > 0 and completed < total:
        remaining = total - completed
        eta_seconds = float(remaining / items_per_second)
    else:
        eta_seconds = 0.0
    
    return ProgressStats(
        total=total,
        completed=completed,
        elapsed_seconds=elapsed,
        items_per_second=items_per_second,
        eta_seconds=eta_seconds,
    )


def iter_with_status(
    items: list,
    description: str = "Processing",
    show_throughput: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Iterate over items with a progress bar, yielding status updates.
    
    Args:
        items: List of items to iterate over
        description: Description for the progress bar
        show_throughput: Whether to show throughput
        
    Yields:
        Dictionaries with item and progress stats
        
    Usage:
        for status in iter_with_status(items, "Processing"):
            item = status["item"]
            stats = status["stats"]
            print(f"Progress: {stats.percent_complete:.1f}%")
    """
    start_time = time.time()
    completed = 0
    
    with get_progress(description, show_throughput=show_throughput) as progress:
        task = progress.add_task(description, total=len(items))
        
        for item in items:
            yield {
                "item": item,
                "completed": completed,
                "total": len(items),
            }
            
            completed += 1
            progress.update(task, advance=1)
    
    # Yield final status
    elapsed = time.time() - start_time
    if elapsed > 0:
        items_per_second = completed / elapsed
    else:
        items_per_second = 0.0
    
    # Calculate ETA
    if items_per_second > 0 and completed < len(items):
        remaining = len(items) - completed
        eta_seconds = float(remaining / items_per_second)
    else:
        eta_seconds = 0.0
    
    yield {
        "item": None,
        "completed": completed,
        "total": len(items),
        "stats": ProgressStats(
            total=len(items),
            completed=completed,
            elapsed_seconds=elapsed,
            items_per_second=items_per_second,
            eta_seconds=eta_seconds,
        ),
    }


@contextmanager
def spinner_context(
    message: str,
    spinner_name: str = "dots",
):
    """Context manager for showing a spinner with a message.
    
    Args:
        message: Message to display next to the spinner
        spinner_name: Name of the spinner animation to use
        
    Usage:
        with spinner_context("Loading..."):
            result = load_data()
    """
    with Spinner(message, spinner_name):
        yield


def track_progress(
    description: str = "Processing",
    total: Optional[int] = None,
    show_throughput: bool = True,
):
    """Decorator for tracking progress of a function.
    
    Args:
        description: Description for the progress bar
        total: Total number of items (if known)
        show_throughput: Whether to show throughput
        
    Usage:
        @track_progress("Processing files")
        def process_files(files):
            for f in files:
                process(f)
            return len(files)
        
        result = process_files(["a.txt", "b.txt"])
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Try to get total from function arguments
            total_items = total
            if total_items is None:
                # Look for common parameter names
                for arg_name, arg_value in kwargs.items():
                    if arg_name in ("items", "files", "resources", "total"):
                        total_items = len(arg_value) if hasattr(arg_value, "__len__") else arg_value
                        break
                else:
                    # Try first positional argument
                    if args and hasattr(args[0], "__len__"):
                        total_items = len(args[0])
            
            if total_items is None or total_items == 0:
                # No progress tracking possible
                return func(*args, **kwargs)
            
            with get_progress(description, show_throughput=show_throughput) as progress:
                task = progress.add_task(description, total=total_items)
                result = func(*args, **kwargs)
                progress.update(task, completed=total_items)
            
            return result
        
        return wrapper
    
    return decorator