import time
import json
from pandasql import sqldf
from modules.chart_agents import ChartAgent



def run_benchmark_gemini(agent, plot_agent, df, cases):
    results = []
    times = []
    for idx, case in enumerate(cases):
        print(f"\n--- Test case {idx+1}: {case['user_request']} ---")
        start = time.time()
        try:
            sql_query, chart_schema = agent.generate_sql_and_schema(case["user_request"])
            pysqldf = lambda q: sqldf(q, {"data": df})
            data_filtered = pysqldf(sql_query)
            chart_type = chart_schema.get("chartType", "").lower()
            is_correct = chart_type == case["expected_chart_type"]

            # Phân biệt combo: multi-line vs grouped-bar nếu có
            if chart_type == "combo" and "expected_combo_type" in case:
                y_types = [y.get("type", "").lower() for y in chart_schema.get("yField", []) if isinstance(y, dict)]
                if case["expected_combo_type"] == "multi-line":
                    is_combo_type = all(t == "line" for t in y_types)
                elif case["expected_combo_type"] == "grouped-bar":
                    is_combo_type = all(t == "bar" for t in y_types)
                else:
                    is_combo_type = True
                is_correct = is_correct and is_combo_type
                print(f"Combo type: {case['expected_combo_type']} | Detected: {y_types} | {'✅' if is_combo_type else '❌'}")

            print(f"Chart type: {chart_type} | Expected: {case['expected_chart_type']} | {'✅' if is_correct else '❌'}")
            results.append(is_correct)
        except Exception as e:
            print(f"Error: {e}")
            results.append(False)
        times.append(time.time() - start)
    accuracy = sum(results) / len(results)
    print(f"\nBenchmark accuracy: {accuracy*100:.1f}% ({sum(results)}/{len(results)})")
    print(f"Avg latency: {sum(times)/len(times):.2f}s | Min: {min(times):.2f}s | Max: {max(times):.2f}s")
    return results

def run_benchmark(agent, plot_agent, df, cases):
    results = []
    times = []
    for idx, case in enumerate(cases):
        print(f"\n--- Test case {idx+1}: {case['user_request']} ---")
        start = time.time()
        try:
            sql_query, chart_schema = agent.generate_sql_and_schema(case["user_request"])
            pysqldf = lambda q: sqldf(q, {"data": df})
            data_filtered = pysqldf(sql_query)
            chart_type = chart_schema.get("chartType", "").lower()
            is_correct = chart_type == case["expected_chart_type"]

            # Phân biệt combo: multi-line vs grouped-bar nếu có
            if chart_type == "combo" and "expected_combo_type" in case:
                y_types = [y.get("type", "").lower() for y in chart_schema.get("yField", []) if isinstance(y, dict)]
                if case["expected_combo_type"] == "multi-line":
                    is_combo_type = all(t == "line" for t in y_types)
                elif case["expected_combo_type"] == "grouped-bar":
                    is_combo_type = all(t == "bar" for t in y_types)
                else:
                    is_combo_type = True
                is_correct = is_correct and is_combo_type
                print(f"Combo type: {case['expected_combo_type']} | Detected: {y_types} | {'✅' if is_combo_type else '❌'}")

            print(f"Chart type: {chart_type} | Expected: {case['expected_chart_type']} | {'✅' if is_correct else '❌'}")
            results.append(is_correct)
        except Exception as e:
            print(f"Error: {e}")
            results.append(False)
        times.append(time.time() - start)
    accuracy = sum(results) / len(results)
    print(f"\nBenchmark accuracy: {accuracy*100:.1f}% ({sum(results)}/{len(results)})")
    print(f"Avg latency: {sum(times)/len(times):.2f}s | Min: {min(times):.2f}s | Max: {max(times):.2f}s")
    return results