# WS2812 Matrix GUI 使用指南

本仓库包含 WS2812 矩阵 LED 配置界面和 Streamlit 入门示例。

---

## 📦 项目结构

```
scripts/
├── streamlit_demo.py          # Streamlit 入门 Demo
├── ws2812_config_ui.py        # WS2812 配置界面（完整功能）
├── ws2812_ble_test.py         # BLE 协议测试工具
├── test_import.py             # 模块导入测试
├── requirements_demo.txt      # Demo 依赖清单
└── how-to-use.md             # 本文件
```

---

## 🚀 快速开始

### 1. 环境准备

#### 使用 Conda（推荐）

```bash
# 创建并激活环境
conda create -n embedded python=3.12 -y
conda activate embedded

# 安装依赖
conda install -c conda-forge streamlit pandas numpy -y

# 如果需要 BLE 功能（仅本地使用）
conda install -c conda-forge bleak -y
```

#### 使用 pip

```bash
# 安装 Demo 依赖
pip install -r requirements_demo.txt

# 完整功能需要额外安装
pip install bleak
```

---

## 🎮 Streamlit 入门 Demo

### 启动 Demo

```bash
cd /Users/cn/Desktop/esp_pro/scripts

# 方式 1：使用 conda（推荐）
conda activate embedded
streamlit run streamlit_demo.py

# 方式 2：指定端口
streamlit run streamlit_demo.py --server.port 8503

# 方式 3：直接用 conda run（无需手动激活）
conda run -n embedded streamlit run streamlit_demo.py
```

### 访问地址

默认地址：http://localhost:8501

### Demo 包含的功能模块

| 模块 | 功能说明 |
|------|---------|
| **1. 文本显示** | `st.write`, `st.success`, `st.info`, `st.warning`, `st.error`, Markdown 支持 |
| **2. 输入组件** | `text_input`, `number_input`, `date_input`, `time_input`, `radio`, `multiselect` |
| **3. 按钮与状态** | `st.button`, `session_state` 状态管理, `st.metric` 指标展示 |
| **4. 数据表格与图表** | `st.dataframe`, `st.line_chart`, `st.area_chart`, `@st.cache_data` 缓存 |
| **5. 进度指示器** | `st.progress`, `st.slider` 进度条控制 |
| **6. 文件上传** | `st.file_uploader` 上传 CSV 并解析显示 |
| **7. 布局组件** | `st.expander` 折叠面板, `st.tabs` 标签页, `st.columns` 多列布局 |
| **8. 交互计算器** | 实时输入 + 按钮触发计算的完整示例 |

### 学习要点

#### 状态管理（Session State）
```python
# 初始化
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# 使用
if st.button("加 1"):
    st.session_state.counter += 1
```

#### 布局控制
```python
# 多列布局
col1, col2, col3 = st.columns(3)
with col1:
    st.write("第一列")

# 侧边栏
st.sidebar.title("侧边栏标题")
```

#### 缓存优化
```python
@st.cache_data  # 缓存数据，避免重复计算
def load_data():
    return pd.read_csv('data.csv')
```

---

## 🎛️ WS2812 配置界面

### 启动完整配置界面

```bash
# 激活环境
conda activate embedded

# 运行配置界面
streamlit run ws2812_config_ui.py
```

### 功能说明

- **BLE 设备扫描与连接**：扫描并连接 ESP32 WS2812 设备
- **矩阵配置**：设置矩阵尺寸、颜色、亮度等参数
- **实时预览**：可视化显示当前配置
- **协议测试**：发送自定义命令测试设备响应

### ⚠️ 注意事项

1. **macOS BLE 权限**：首次使用需在"系统偏好设置 → 隐私与安全 → 蓝牙"中授权终端/Python
2. **仅本地运行**：BLE 功能只能在本地运行，不支持 Streamlit Cloud 部署
3. **设备要求**：需要 ESP32C3 或类似设备运行 WS2812 BLE 固件

---

## 🧪 BLE 协议测试工具

### 命令行测试

```bash
# 通过设备名称连接
python ws2812_ble_test.py --name "HOSHI-MATRIX" --event 0x10 --subevent 0x01 --payload 01

# 通过 MAC 地址连接
python ws2812_ble_test.py --address AA:BB:CC:DD:EE:FF --event 0x10 --subevent 0x01 --payload 01

# 时间同步
python ws2812_ble_test.py --name "HOSHI-MATRIX" --timesync
```

### 参数说明

- `--name`: BLE 广播名称
- `--address`: BLE MAC 地址
- `--event`: 事件代码（十六进制）
- `--subevent`: 子事件代码（十六进制）
- `--payload`: 负载数据（十六进制字符串）
- `--timesync`: 发送时间同步帧

---

## 🛠️ 常见问题

### 1. conda activate 命令不可用

```bash
# 初始化 conda（根据你的安装路径）
source ~/miniforge3/etc/profile.d/conda.sh
# 或
source ~/miniconda3/etc/profile.d/conda.sh
```

### 2. 端口被占用

```bash
# 指定其他端口
streamlit run streamlit_demo.py --server.port 8502
```

### 3. BLE 连接失败

- 检查蓝牙是否开启
- 确认设备在范围内且未连接到其他设备
- 检查 macOS 蓝牙权限设置
- 尝试重启蓝牙或设备

### 4. 模块导入错误

```bash
# 测试导入
python test_import.py

# 重新安装依赖
conda install -c conda-forge streamlit pandas numpy bleak -y
```

### 5. Streamlit Cloud 部署空白页

- **原因**：BLE 功能在云端无法使用
- **解决**：仅部署 Demo 版本，或在代码中添加模拟模式
- **检查**：查看 Streamlit Cloud 的日志（Manage app → Logs）

---

## 📖 扩展学习资源

- **Streamlit 官方文档**: https://docs.streamlit.io
- **组件库**: https://streamlit.io/components
- **示例库**: https://streamlit.io/gallery
- **API 参考**: https://docs.streamlit.io/library/api-reference
- **Bleak 文档**: https://bleak.readthedocs.io/

---

## 🔧 停止服务器

在终端按 `Ctrl + C` 停止运行

或者如果在后台运行：
```bash
# 查找进程
ps aux | grep streamlit

# 停止进程（替换 PID）
kill <PID>
```

---

## 📝 版本信息

- Python: 3.12+
- Streamlit: 1.28.0+
- Bleak: 最新版本
- Pandas: 2.0.0+
- NumPy: 1.24.0+

---

## 💡 进阶实践建议

1. 试试修改 demo 中的参数（颜色、范围、文本）观察变化
2. 添加自己的数据源（CSV / JSON）并可视化
3. 尝试组合不同组件实现自定义功能
4. 学习使用 `st.form` 创建表单提交
5. 探索 `st.plotly_chart` / `st.altair_chart` 高级图表
6. 为 WS2812 配置界面添加新的控制功能

---

## 📞 支持

如有问题或建议，请在 GitHub 仓库提交 Issue：
https://github.com/EmbeddedEvery/matrix_gui
