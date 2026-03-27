"""
Performance Benchmarking Utilities for Kai Capabilities
Provides tools to measure and track performance improvements.
"""

import time
import functools
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    name: str
    execution_time: float
    iterations: int
    average_time: float
    min_time: float
    max_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PerformanceBenchmark:
    """Benchmark performance of functions and operations."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self._warmup_iterations = 3
    
    def benchmark(self, name: str, func: Callable, iterations: int = 10, 
                  warmup: bool = True, *args, **kwargs) -> BenchmarkResult:
        """
        Benchmark a function execution.
        
        Args:
            name: Name of the benchmark
            func: Function to benchmark
            iterations: Number of iterations to run
            warmup: Whether to run warmup iterations
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            BenchmarkResult with timing statistics
        """
        # Warmup
        if warmup:
            for _ in range(self._warmup_iterations):
                func(*args, **kwargs)
        
        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        result = BenchmarkResult(
            name=name,
            execution_time=sum(times),
            iterations=iterations,
            average_time=sum(times) / len(times),
            min_time=min(times),
            max_time=max(times)
        )
        
        self.results.append(result)
        return result
    
    def compare(self, name1: str, func1: Callable, name2: str, func2: Callable,
                iterations: int = 10, *args, **kwargs) -> Dict:
        """
        Compare performance of two functions.
        
        Returns:
            Dictionary with comparison results
        """
        result1 = self.benchmark(name1, func1, iterations, *args, **kwargs)
        result2 = self.benchmark(name2, func2, iterations, *args, **kwargs)
        
        speedup = result1.average_time / result2.average_time if result2.average_time > 0 else 0
        
        return {
            'function1': name1,
            'function2': name2,
            'avg_time1': result1.average_time,
            'avg_time2': result2.average_time,
            'speedup': speedup,
            'faster': name2 if speedup > 1 else name1,
            'improvement': f"{abs(speedup - 1) * 100:.1f}%"
        }
    
    def get_summary(self) -> Dict:
        """Get summary of all benchmarks."""
        if not self.results:
            return {'message': 'No benchmarks run yet'}
        
        return {
            'total_benchmarks': len(self.results),
            'results': [
                {
                    'name': r.name,
                    'average_time': f"{r.average_time:.6f}s",
                    'min_time': f"{r.min_time:.6f}s",
                    'max_time': f"{r.max_time:.6f}s",
                    'iterations': r.iterations
                }
                for r in self.results
            ]
        }
    
    def clear(self):
        """Clear all benchmark results."""
        self.results.clear()


def timing_decorator(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f}s")
        return result
    return wrapper


class CacheStats:
    """Track cache performance statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1
        self.total_requests += 1
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
        self.total_requests += 1
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        if self.total_requests == 0:
            return {
                'hits': 0,
                'misses': 0,
                'total_requests': 0,
                'hit_rate': 0.0
            }
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': self.total_requests,
            'hit_rate': self.hits / self.total_requests
        }
    
    def reset(self):
        """Reset cache statistics."""
        self.hits = 0
        self.misses = 0
        self.total_requests = 0


# Example usage and testing
if __name__ == "__main__":
    print("Performance Benchmarking Utilities")
    print("=" * 50)
    
    # Example benchmark
    benchmark = PerformanceBenchmark()
    
    # Test function
    def test_function(n=1000):
        return sum(range(n))
    
    # Run benchmark
    result = benchmark.benchmark("Sum Range", test_function, iterations=100)
    print(f"\nBenchmark: {result.name}")
    print(f"  Average time: {result.average_time:.6f}s")
    print(f"  Min time: {result.min_time:.6f}s")
    print(f"  Max time: {result.max_time:.6f}s")
    print(f"  Iterations: {result.iterations}")
    
    # Cache stats example
    cache_stats = CacheStats()
    cache_stats.record_hit()
    cache_stats.record_hit()
    cache_stats.record_miss()
    
    print(f"\nCache Stats: {cache_stats.get_stats()}")
