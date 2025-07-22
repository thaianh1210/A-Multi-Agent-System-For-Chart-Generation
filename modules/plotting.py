import plotly.express as px
import plotly.graph_objs as go
from sentence_transformers import SentenceTransformer
from modules.prompts import PLOT_PROMPT_TEMPLATE
import json
import pandas as pd





def fast_plot(data_filtered, chart_schema):
    import plotly.express as px
    import plotly.graph_objs as go

    FIELD_LABELS = {
        "DATETIME": "Thời gian",
        "YEAR": "Năm",
        "MONTH": "Tháng",
        "QUARTER": "Quý",
        "DAY": "Ngày",
        "OBJ_NAME": "Tỉnh/Thành phố",
        "SERVICE_NAME": "Dịch vụ",
        "PLAN": "Kế hoạch",
        "PLAN_ACC": "Kế hoạch lũy kế",
        "VAL": "Số thực hiện",
        "VAL_ACC": "Số thực hiện lũy kế",
        "P_PLAN": "Phần trăm hoàn thành",
        "P_PLAN_ACC": "Phần trăm hoàn thành lũy kế",
        "LAST_VAL_YEAR": "Số thực hiện năm trước",
        "LAST_VAL_ACC_YEAR": "Số thực hiện lũy kế năm trước"
    }

    chart_type = chart_schema.get("chartType", "").lower()
    x = chart_schema.get("xField")
    y_raw = chart_schema.get("yField")
    title = chart_schema.get("title", "")

    # Lấy nhãn tự nhiên cho trục x
    x_label = FIELD_LABELS.get(x, x)
    # Lấy nhãn tự nhiên cho trục y
    if isinstance(y_raw, list):
        if isinstance(y_raw[0], dict):
            y_labels = [FIELD_LABELS.get(y.get("field", ""), y.get("field", "")) for y in y_raw]
            y_fields = [y.get("field", "") for y in y_raw]
        else:
            y_labels = [FIELD_LABELS.get(y, y) for y in y_raw]
            y_fields = y_raw
    else:
        y_labels = [FIELD_LABELS.get(y_raw, y_raw)]
        y_fields = [y_raw]

    # Multi-line: x là thời gian, yField là 1 trường số, có cột phân loại (OBJ_NAME hoặc SERVICE_NAME)
    time_cols = ["DATETIME", "MONTH", "YEAR", "QUARTER", "DAY"]
    cat_col = None
    for col in ["OBJ_NAME", "SERVICE_NAME"]:
        if col in data_filtered.columns and col != x:
            cat_col = col
            break

    # Trường hợp multi-line đúng chuẩn
    if (
        chart_type in ["combo", "line"]
        and x in time_cols
        and cat_col
        and isinstance(y_raw, list)
        and len(y_raw) == 1
        and isinstance(y_raw[0], dict)
    ):
        y_field = y_raw[0]["field"]
        y_label = FIELD_LABELS.get(y_field, y_field)
        df_agg = data_filtered.groupby([x, cat_col], as_index=False)[y_field].sum()
        pivot_df = df_agg.pivot(index=x, columns=cat_col, values=y_field)
        fig = go.Figure()
        for col in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[col],
                mode="lines+markers",
                name=str(col)
            ))
        fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label)
        fig.show()
        return

    # Trường hợp multi-metric (nhiều trường số trên cùng x, không cần phân loại)
    if (
        chart_type in ["combo", "line", "bar"]
        and isinstance(y_raw, list)
        and all(isinstance(y, dict) for y in y_raw)
        and (not cat_col or cat_col == x)
    ):
        df_long = data_filtered.melt(id_vars=[x], value_vars=y_fields, var_name="variable", value_name="value")
        label_map = {x: x_label, "value": "Giá trị", "variable": "Chỉ tiêu"}
        label_map.update({f: l for f, l in zip(y_fields, y_labels)})
        y_types = [yinfo.get("type", "bar").lower() for yinfo in y_raw]
        if all(t == "bar" for t in y_types):
            fig = px.bar(df_long, x=x, y="value", color="variable", barmode="group", title=title, labels=label_map)
        else:
            fig = px.line(df_long, x=x, y="value", color="variable", title=title, labels=label_map)
        fig.update_layout(xaxis_title=x_label)
        fig.show()
        return

    # Trường hợp group theo cat_col (grouped bar/multi-line theo nhóm)
    if (
        chart_type == "combo"
        and cat_col
        and isinstance(y_raw, list)
        and len(y_raw) == 1
        and isinstance(y_raw[0], dict)
    ):
        y_field = y_raw[0]["field"]
        y_label = FIELD_LABELS.get(y_field, y_field)
        y_type = y_raw[0].get("type", "bar").lower()
        fig = go.Figure()
        for val in data_filtered[cat_col].unique():
            sub_df = data_filtered[data_filtered[cat_col] == val]
            if y_type == "bar":
                fig.add_trace(go.Bar(x=sub_df[x], y=sub_df[y_field], name=str(val)))
            else:
                fig.add_trace(go.Scatter(x=sub_df[x], y=sub_df[y_field], mode="lines+markers", name=str(val)))
        fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label, barmode="group" if y_type == "bar" else None)
        fig.show()
        return

    # Basic chart types
    plotly_chart_map = {
        "line": px.line,
        "bar": px.bar,
        "scatter": px.scatter,
        "pie": px.pie,
        "area": px.area,
    }
    plot_func = plotly_chart_map.get(chart_type)
    if plot_func:
        if chart_type == "pie":
            y_col = y_fields[0]
            fig = plot_func(
                data_filtered,
                names=x,
                values=y_col,
                title=title,
                labels={x: x_label, y_col: y_labels[0]}
            )
        else:
            fig = plot_func(
                data_filtered,
                x=x,
                y=y_fields if len(y_fields) > 1 else y_fields[0],
                title=title,
                labels={x: x_label, **{f: l for f, l in zip(y_fields, y_labels)}}
            )
        fig.update_layout(xaxis_title=x_label)
        if len(y_labels) == 1:
            fig.update_layout(yaxis_title=y_labels[0])
        fig.show()
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

def smart_plot(data_filtered, chart_schema, user_prompt, llm_plot_agent):
    common_types = {"line", "bar", "pie", "scatter", "area", "combo"}
    chart_type = chart_schema.get("chartType", "").lower()
    if chart_type in common_types:
        try:
            fast_plot(data_filtered, chart_schema)
            return
        except Exception as e:
            print("Lỗi khi mapping thủ công:", e)
            print("Chuyển sang dùng LLM...")
    llm_plot_agent.plot(data_filtered, chart_schema, user_prompt)


class PlotChartAgent:
    def __init__(self, openai_client):
        self.client = openai_client

    def generate_plot_code(self, data_filtered, chart_schema, user_prompt):
        # Lấy 5 dòng đầu để LLM hiểu cấu trúc dữ liệu
        data_sample = data_filtered.head().to_dict()
        columns_info = {col: str(dtype) for col, dtype in data_filtered.dtypes.items()}
        prompt = PLOT_PROMPT_TEMPLATE.format(
            data_sample=json.dumps(data_sample, indent=2),
            chart_schema=json.dumps(chart_schema, indent=2),
            user_prompt=user_prompt,
            columns_info=json.dumps(columns_info, indent=2)
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        code = response.choices[0].message.content
        # Loại bỏ markdown nếu có
        code = code.replace("```python", "").replace("```", "").strip()
        return code

    def plot(self, data_filtered, chart_schema, user_prompt, globals_=None):
        code = self.generate_plot_code(data_filtered, chart_schema, user_prompt)
        print("Code sinh bởi LLM:\n", code)
        # Thực thi code (cẩn thận với bảo mật)
        exec(code, {"df": data_filtered, "pd": pd, **(globals_ or {})})
