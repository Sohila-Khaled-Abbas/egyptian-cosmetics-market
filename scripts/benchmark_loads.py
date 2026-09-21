"""
Benchmark Pipeline Loads: Full Load vs Incremental Load
Measures execution duration, throughput (rows/sec), and resource performance.
"""
import sys
import time
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config.database import get_sqlalchemy_engine
from src.loading.warehouse_loader import WarehouseLoader
from src.utils.logger import get_logger

logger = get_logger("benchmark_loads")

def benchmark():
    engine = get_sqlalchemy_engine()
    wh = WarehouseLoader(batch_id="BENCHMARK_RUN")

    print("\n" + "=" * 75)
    print("  CLEOPATRA COSMETICS — LOAD PERFORMANCE BENCHMARK")
    print("=" * 75)

    # 1. Full Load Fact Benchmark
    print("\n[1/2] Benchmarking Full Load (Fact Tables Truncate + Reload)...")
    start_time = time.time()
    wh.load_facts(batch_id="BENCHMARK_FULL", is_incremental=False)
    full_duration = time.time() - start_time

    with engine.connect() as conn:
        full_rows = conn.execute(text("SELECT COUNT(*) FROM warehouse.fact_sales")).scalar()

    full_throughput = full_rows / full_duration if full_duration > 0 else 0
    print(f"Full Load: {full_rows:,} rows in {full_duration:.2f}s ({full_throughput:,.0f} rows/sec)")

    # 2. Incremental Load Benchmark (No new rows to insert -> deduplication / delta check)
    print("\n[2/2] Benchmarking Incremental Load (Delta Change Detection)...")
    start_time = time.time()
    wh.load_facts(batch_id="BENCHMARK_INC", is_incremental=True)
    inc_duration = time.time() - start_time

    inc_throughput = full_rows / inc_duration if inc_duration > 0 else 0
    print(f"Incremental Check: {full_rows:,} evaluated in {inc_duration:.2f}s ({inc_throughput:,.0f} rows/sec)")

    # 3. Print Comparison Table
    speedup = (full_duration / inc_duration) if inc_duration > 0 else 1.0
    print("\n" + "-" * 75)
    print(f"{'Metric':<30} {'Full Load':<20} {'Incremental Load':<20}")
    print("-" * 75)
    print(f"{'Target Table':<30} {'warehouse.fact_sales':<20} {'warehouse.fact_sales':<20}")
    print(f"{'Total Rows Processed':<30} {f'{full_rows:,}':<20} {f'{full_rows:,}':<20}")
    print(f"{'Execution Time (s)':<30} {f'{full_duration:.2f}s':<20} {f'{inc_duration:.2f}s':<20}")
    print(f"{'Throughput (rows/sec)':<30} {f'{full_throughput:,.0f}':<20} {f'{inc_throughput:,.0f}':<20}")
    print(f"{'Performance Ratio':<30} {'1.0x (Baseline)':<20} {f'{speedup:.2f}x Faster':<20}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    benchmark()
