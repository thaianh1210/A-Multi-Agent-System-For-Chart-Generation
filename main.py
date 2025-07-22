import pandas as pd
from modules.chart_agents import ChartAgent, ChartAgentGemini
from modules.plotting import smart_plot, PlotChartAgent
from modules.data_processing import add_datetime_column, add_time_features
from modules.plotting import smart_plot
from modules.prompts import CHART_PROMPT_TEMPLATE
from modules.entity_mapping import map_sql_values
from openai import OpenAI
import toml

secrets = toml.load("modules/secrets.toml")
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]


# Load data
df = pd.read_csv("data/fake_tool.csv")
df = add_datetime_column(df)
df = add_time_features(df)


# Khởi tạo agent
client = OpenAI(api_key=OPENAI_API_KEY)
agent = ChartAgent(df, client)

# Nhận yêu cầu người dùng
user_request = input("Nhập yêu cầu của bạn: ")

# Sinh SQL và chart schema
sql_query, chart_schema = agent.generate_sql_and_schema(user_request)

# Truy xuất data bằng SQL
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, {"data": df})
data_filtered = pysqldf(sql_query)

# Vẽ biểu đồ
plot_agent = PlotChartAgent(client)
smart_plot(data_filtered, chart_schema, user_request, plot_agent)


#Test case: Vẽ biểu đồ thực hiện lũy kế FTTx - TB thực tăng/giảm 5 tháng cuối năm 2024 của các thành phố Hà Nội, Đà Nẵng, Hồ Chí Minh
#Vẽ biểu đồ so sánh thực hiện DT dịch vụ nhóm DV của VTT năm 2024 của 3 tỉnh Quảng Bình, Quảng Trị, Thừa Thiên Huế
#Vẽ biểu đồ so sánh thực hiện lũy kế thuê bao 4g tăng thêm TP HCM 3 tháng cuối năm 2024 với cùng kỳ năm trước