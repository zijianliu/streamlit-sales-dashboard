import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from modules import DataProcessor, ChartGenerator

st.set_page_config(
    page_title="销售数据分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)


def format_currency(value):
    if value >= 100000000:
        return f"¥{value/100000000:.2f}亿"
    elif value >= 10000:
        return f"¥{value/10000:.2f}万"
    else:
        return f"¥{value:,.2f}"


def to_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    return output.getvalue()


def main():
    st.markdown('<h1 class="main-header">📊 销售数据分析看板</h1>', unsafe_allow_html=True)

    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    if 'chart_generator' not in st.session_state:
        st.session_state.chart_generator = ChartGenerator()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    with st.sidebar:
        st.header("📁 数据导入")
        uploaded_file = st.file_uploader("请上传 CSV 文件", type=['csv'])
        
        if uploaded_file is not None:
            with st.spinner("正在加载数据..."):
                success, message = st.session_state.data_processor.load_data(uploaded_file)
                
                if not success:
                    st.error(message)
                else:
                    success, message = st.session_state.data_processor.validate_columns()
                    if not success:
                        st.error(message)
                        st.info("必需字段：订单日期、地区、类别、产品名、销售额、利润、销售人员")
                    else:
                        result = st.session_state.data_processor.clean_data()
                        if result['success']:
                            st.session_state.data_loaded = True
                            st.success("数据加载和清洗完成！")
                            
                            with st.expander("📊 数据清洗统计"):
                                stats = result['stats']
                                st.metric("原始数据条数", f"{stats['original_count']:,}")
                                st.metric("删除重复记录", f"{stats['duplicates_removed']:,}")
                                st.metric("删除无效记录", f"{stats['null_rows_removed']:,}")
                                st.metric("最终有效数据", f"{stats['final_count']:,}")

    if not st.session_state.data_loaded:
        st.info("👋 欢迎使用销售数据分析看板！")
        st.write("请在左侧上传您的销售数据 CSV 文件，或者下载示例数据进行测试。")
        
        st.markdown("### 📋 必需字段说明")
        st.write("您的 CSV 文件需要包含以下字段：")
        
        sample_cols = pd.DataFrame({
            '字段名': ['订单日期', '地区', '类别', '产品名', '销售额', '利润', '销售人员'],
            '说明': ['订单日期，如：2024-01-15', '销售地区，如：华东、华北', '产品类别，如：电子产品、服装', '具体产品名称', '销售金额（数值）', '利润金额（数值）', '销售人员姓名'],
            '示例': ['2024-01-15', '华东', '电子产品', 'iPhone 15', '8999', '2000', '张三']
        })
        st.table(sample_cols)
        
        st.markdown("### 📥 下载示例数据")
        if st.button("生成并下载示例 CSV"):
            sample_data = generate_sample_data()
            csv_data = to_csv(sample_data)
            st.download_button(
                label="下载示例数据",
                data=csv_data,
                file_name="sample_sales_data.csv",
                mime="text/csv"
            )
        return

    data_processor = st.session_state.data_processor
    chart_generator = st.session_state.chart_generator

    unique_values = data_processor.get_unique_values()

    with st.sidebar:
        st.header("🔍 数据筛选")
        
        min_date, max_date = unique_values['date_range']
        date_range = st.date_input(
            "选择日期范围",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        regions = st.multiselect(
            "选择地区",
            options=unique_values['regions'],
            default=[]
        )

        categories = st.multiselect(
            "选择类别",
            options=unique_values['categories'],
            default=[]
        )

        salespeople = st.multiselect(
            "选择销售人员",
            options=unique_values['salespeople'],
            default=[]
        )

        st.markdown("---")
        st.markdown("### 💡 提示")
        st.markdown("不选择任何筛选条件时，将显示全部数据。")

    if len(date_range) == 2:
        filtered_df = data_processor.filter_data(
            date_range=date_range,
            regions=regions if regions else None,
            categories=categories if categories else None,
            salespeople=salespeople if salespeople else None
        )
    else:
        filtered_df = data_processor.filter_data()

    metrics = data_processor.calculate_metrics(filtered_df)

    st.markdown("## 📈 核心指标")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_currency(metrics['total_sales'])}</div>
            <div class="metric-label">💰 总销售额</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_currency(metrics['total_profit'])}</div>
            <div class="metric-label">📊 总利润</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['order_count']:,}</div>
            <div class="metric-label">📋 订单数</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_currency(metrics['avg_order_sales'])}</div>
            <div class="metric-label">📌 平均订单销售额</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📊 数据分析图表")

    tab1, tab2, tab3 = st.tabs(["📈 销售趋势 & 地区对比", "🥧 类别分布 & 产品排行", "👥 销售人员业绩"])

    with tab1:
        col_trend, col_region = st.columns(2)
        
        with col_trend:
            fig_trend = chart_generator.sales_trend_chart(filtered_df)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning("暂无数据可显示")
        
        with col_region:
            fig_region = chart_generator.region_comparison_chart(filtered_df)
            if fig_region:
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.warning("暂无数据可显示")

    with tab2:
        col_pie, col_top10 = st.columns(2)
        
        with col_pie:
            fig_pie = chart_generator.category_pie_chart(filtered_df)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("暂无数据可显示")
        
        with col_top10:
            fig_top10 = chart_generator.top_products_chart(filtered_df)
            if fig_top10:
                st.plotly_chart(fig_top10, use_container_width=True)
            else:
                st.warning("暂无数据可显示")

    with tab3:
        fig_salesperson = chart_generator.salesperson_performance_chart(filtered_df)
        if fig_salesperson:
            st.plotly_chart(fig_salesperson, use_container_width=True)
        else:
            st.warning("暂无数据可显示")

    st.markdown("---")
    st.markdown("## 📋 数据明细")

    display_cols = ['订单日期', '地区', '类别', '产品名', '销售额', '利润', '销售人员']
    
    if not filtered_df.empty:
        display_df = filtered_df[display_cols].copy()
        display_df['订单日期'] = display_df['订单日期'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                '销售额': st.column_config.NumberColumn('销售额', format="¥%.2f"),
                '利润': st.column_config.NumberColumn('利润', format="¥%.2f")
            }
        )
        
        st.markdown(f"**共 {len(filtered_df)} 条记录**")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            csv_data = to_csv(display_df)
            st.download_button(
                label="📥 导出当前数据",
                data=csv_data,
                file_name="sales_data_export.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.warning("当前筛选条件下没有数据")


def generate_sample_data():
    np.random.seed(42)
    
    n_rows = 500
    
    regions = ['华东', '华北', '华南', '西南', '西北', '东北']
    categories = ['电子产品', '服装', '家居用品', '食品饮料', '美妆护肤']
    salespeople = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
    
    products = {
        '电子产品': ['iPhone 15', 'MacBook Pro', 'iPad Air', 'AirPods Pro', '小米手机', '华为Mate', '三星Galaxy', '联想笔记本'],
        '服装': ['Nike运动鞋', 'Adidas卫衣', 'Levis牛仔裤', 'Uniqlo外套', '安踏跑步鞋', '李宁T恤', '波司登羽绒服', '海澜之家衬衫'],
        '家居用品': ['宜家沙发', '慕思床垫', '全友衣柜', '美的空调', '海尔冰箱', '小米电视', '戴森吸尘器', '飞利浦电动牙刷'],
        '食品饮料': ['蒙牛牛奶', '伊利酸奶', '农夫山泉', '可口可乐', '康师傅方便面', '统一奶茶', '三只松鼠坚果', '良品铺子零食'],
        '美妆护肤': ['兰蔻小黑瓶', '雅诗兰黛眼霜', 'SK-II神仙水', '资生堂防晒', '欧莱雅精华', '玉兰油面霜', '完美日记口红', '花西子粉饼']
    }
    
    data = []
    
    start_date = pd.Timestamp('2024-01-01')
    end_date = pd.Timestamp('2024-12-31')
    
    for _ in range(n_rows):
        days = (end_date - start_date).days
        random_days = np.random.randint(0, days)
        order_date = start_date + pd.Timedelta(days=random_days)
        
        category = np.random.choice(categories)
        product = np.random.choice(products[category])
        
        if category == '电子产品':
            sales_amount = np.random.uniform(2000, 15000)
        elif category == '家居用品':
            sales_amount = np.random.uniform(1000, 10000)
        elif category == '服装':
            sales_amount = np.random.uniform(200, 3000)
        elif category == '美妆护肤':
            sales_amount = np.random.uniform(100, 2000)
        else:
            sales_amount = np.random.uniform(50, 500)
        
        profit_rate = np.random.uniform(0.1, 0.3)
        profit = sales_amount * profit_rate
        
        region = np.random.choice(regions)
        salesperson = np.random.choice(salespeople)
        
        data.append({
            '订单日期': order_date.strftime('%Y-%m-%d'),
            '地区': region,
            '类别': category,
            '产品名': product,
            '销售额': round(sales_amount, 2),
            '利润': round(profit, 2),
            '销售人员': salesperson
        })
    
    df = pd.DataFrame(data)
    
    for _ in range(5):
        idx = np.random.randint(0, len(df))
        df.loc[idx, '利润'] = np.nan
    
    for _ in range(5):
        idx = np.random.randint(0, len(df))
        df.loc[idx, '销售额'] = '无效数据'
    
    df = pd.concat([df, df.head(10)], ignore_index=True)
    
    return df


if __name__ == "__main__":
    main()
