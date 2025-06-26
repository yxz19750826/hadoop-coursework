#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Web Application for E-commerce Order Analysis
电商订单分析Streamlit网页应用

This module provides a web interface for the e-commerce order analysis system.
本模块为电商订单分析系统提供网页界面。

Author: Data Analysis Team
Date: 2025-05-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# 定义数据目录（解决DATA_DIR未定义的问题）
DATA_DIR = Path(__file__).parent / "data"

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from data_utils import DataProcessor
    from analysis import OrderAnalyzer
    from visualization import DataVisualizer
    from config import *
except ImportError as e:
    st.error(f"导入自定义模块失败: {str(e)}")
    st.info("如果是开发环境，可能需要先创建这些模块或使用示例数据")

# Page configuration
st.set_page_config(
    page_title="电商订单数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.sidebar-info {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load or generate sample data"""
    try:
        processor = DataProcessor()
        
        # 确保数据目录存在
        (DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
        sample_file = DATA_DIR / "raw" / "sample_orders.csv"
        
        if not sample_file.exists():
            st.info("正在生成示例数据...")
            processor.generate_sample_data(output_file=sample_file)
        
        # Load and clean data
        df = processor.load_data(sample_file)
        cleaned_df = processor.clean_data(df)
        
        return cleaned_df, processor
    except Exception as e:
        st.error(f"加载示例数据时出错: {str(e)}")
        st.info("请检查数据目录权限或手动上传数据")
        return pd.DataFrame(), None

def create_interactive_charts(df):
    """Create interactive charts using Plotly"""
    if 'order_date' not in df.columns or 'total_amount' not in df.columns or 'order_id' not in df.columns:
        st.warning("数据缺少必要字段，无法生成趋势图表")
        return None
    
    # Daily sales trend
    daily_sales = df.groupby('order_date').agg({
        'total_amount': 'sum',
        'order_id': 'count'
    }).reset_index()
    daily_sales.columns = ['date', 'revenue', 'orders']
    
    fig_trend = make_subplots(
        rows=2, cols=1,
        subplot_titles=('日销售额趋势', '日订单数量趋势'),
        vertical_spacing=0.1
    )
    
    fig_trend.add_trace(
        go.Scatter(x=daily_sales['date'], y=daily_sales['revenue'],
                  mode='lines+markers', name='销售额',
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    fig_trend.add_trace(
        go.Bar(x=daily_sales['date'], y=daily_sales['orders'],
               name='订单数', marker_color='#ff7f0e'),
        row=2, col=1
    )
    
    fig_trend.update_layout(height=600, showlegend=False)
    fig_trend.update_xaxes(title_text="日期", row=2, col=1)
    fig_trend.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig_trend.update_yaxes(title_text="订单数", row=2, col=1)
    
    return fig_trend

def create_category_chart(df):
    """Create category distribution chart"""
    if 'product_category' not in df.columns or 'total_amount' not in df.columns:
        st.warning("数据缺少必要字段，无法生成类别图表")
        return None
    
    category_stats = df.groupby('product_category').agg({
        'total_amount': 'sum',
        'order_id': 'count',
        'quantity': 'sum'
    }).reset_index()
    category_stats.columns = ['category', 'revenue', 'orders', 'quantity']
    category_stats = category_stats.sort_values('revenue', ascending=False)
    
    fig = px.bar(category_stats, x='category', y='revenue',
                 title='产品类别销售额分布',
                 labels={'revenue': '销售额 (¥)', 'category': '产品类别'},
                 color='revenue',
                 color_continuous_scale='Blues')
    
    fig.update_layout(height=500, xaxis_tickangle=-45)
    return fig

def create_customer_analysis_chart(df):
    """Create customer analysis charts"""
    if 'age_group' not in df.columns or 'total_amount' not in df.columns or 'customer_id' not in df.columns:
        st.warning("数据缺少必要字段，无法生成客户分析图表")
        return None
    
    # Age group analysis
    age_analysis = df.groupby('age_group').agg({
        'total_amount': ['sum', 'mean'],
        'customer_id': 'nunique'
    }).reset_index()
    age_analysis.columns = ['age_group', 'total_revenue', 'avg_order_value', 'customer_count']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('年龄组销售额分布', '年龄组客户数量'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=age_analysis['age_group'], y=age_analysis['total_revenue'],
               name='总销售额', marker_color='#1f77b4'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=age_analysis['age_group'], y=age_analysis['customer_count'],
               name='客户数量', marker_color='#ff7f0e'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    fig.update_xaxes(title_text="年龄组", row=1, col=1)
    fig.update_xaxes(title_text="年龄组", row=1, col=2)
    fig.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig.update_yaxes(title_text="客户数量", row=1, col=2)
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 电商订单数据分析平台</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">E-commerce Order Analysis Platform</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-info"><h3>🔧 分析选项</h3></div>', unsafe_allow_html=True)
        
        # Data source selection
        data_source = st.radio(
            "选择数据源",
            ["使用示例数据", "上传CSV文件"]
        )
        
        # Analysis options
        st.markdown("### 📈 分析模块")
        show_basic_stats = st.checkbox("基本统计", value=True)
        show_time_analysis = st.checkbox("时间序列分析", value=True)
        show_customer_analysis = st.checkbox("客户分析", value=True)
        show_product_analysis = st.checkbox("产品分析", value=True)
        
        # Chart options
        st.markdown("### 📊 图表选项")
        chart_theme = st.selectbox(
            "图表主题",
            ["默认", "暗色", "简洁"]
        )
        
        # Date range filter
        st.markdown("### 📅 时间筛选")
        use_date_filter = st.checkbox("启用日期筛选")
    
    # Main content
    try:
        # Load data
        if data_source == "使用示例数据":
            with st.spinner("正在加载示例数据..."):
                df, processor = load_sample_data()
                if df.empty:
                    st.error("示例数据加载失败，请尝试上传自定义数据")
                    return
        else:
            uploaded_file = st.file_uploader(
                "选择CSV文件",
                type=['csv'],
                help="请上传包含订单数据的CSV文件"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    processor = DataProcessor()
                    df = processor.clean_data(df)
                    st.success(f"成功加载 {len(df)} 条订单记录")
                except Exception as e:
                    st.error(f"文件加载失败: {str(e)}")
                    return
            else:
                st.info("请上传CSV文件以开始分析")
                return
        
        # 检查数据是否包含必要字段
        required_fields = ['order_date', 'total_amount', 'customer_id']
        missing_fields = [f for f in required_fields if f not in df.columns]
        if missing_fields:
            st.warning(f"数据缺少以下必要字段: {', '.join(missing_fields)}，部分分析功能将无法使用")
        
        # Date filter
        if use_date_filter and 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
            min_date = df['order_date'].min().date()
            max_date = df['order_date'].max().date()
            
            date_range = st.sidebar.date_input(
                "选择日期范围",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['order_date'].dt.date >= start_date) & 
                       (df['order_date'].dt.date <= end_date)]
                st.info(f"已筛选 {start_date} 到 {end_date} 的数据，共 {len(df)} 条记录")
        
        # Initialize analyzer
        try:
            analyzer = OrderAnalyzer(df)
        except Exception as e:
            st.error(f"初始化分析器失败: {str(e)}")
            return
        
        # Display basic info
        st.markdown("## 📋 数据概览")
        if df.empty:
            st.warning("数据为空，无法显示概览")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("总订单数", f"{len(df):,}")
            with col2:
                st.metric("总销售额", f"¥{df['total_amount'].sum():,.2f}")
            with col3:
                st.metric("平均订单价值", f"¥{df['total_amount'].mean():.2f}")
            with col4:
                st.metric("客户数量", f"{df['customer_id'].nunique():,}")
        
        # Basic Statistics
        if show_basic_stats and not df.empty:
            st.markdown("## 📊 基本统计分析")
            
            try:
                basic_stats = analyzer.basic_statistics()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 订单统计")
                    st.json({
                        "总订单数": basic_stats['total_orders'],
                        "总收入": f"¥{basic_stats['total_revenue']:.2f}",
                        "平均订单价值": f"¥{basic_stats['average_order_value']:.2f}",
                        "订单价值中位数": f"¥{basic_stats['median_order_value']:.2f}"
                    })
                
                with col2:
                    st.markdown("### 客户与产品")
                    st.json({
                        "总客户数": basic_stats['total_customers'],
                        "总产品数": basic_stats['total_products'],
                        "产品类别数": basic_stats['total_categories']
                    })
            except Exception as e:
                st.error(f"基本统计分析出错: {str(e)}")
        
        # Time Series Analysis
        if show_time_analysis and not df.empty:
            st.markdown("## 📈 时间序列分析")
            
            # Interactive sales trend chart
            fig_trend = create_interactive_charts(df)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("无法生成时间序列图表")
            
            # Monthly analysis
            if 'order_date' in df.columns:
                try:
                    monthly_sales = df.groupby(df['order_date'].dt.to_period('M')).agg({
                        'total_amount': 'sum',
                        'order_id': 'count'
                    }).reset_index()
                    monthly_sales['month'] = monthly_sales['order_date'].astype(str)
                    
                    fig_monthly = px.line(monthly_sales, x='month', y='total_amount',
                                        title='月度销售趋势',
                                        labels={'total_amount': '销售额 (¥)', 'month': '月份'})
                    st.plotly_chart(fig_monthly, use_container_width=True)
                except Exception as e:
                    st.error(f"月度分析出错: {str(e)}")
            else:
                st.info("数据缺少日期字段，无法进行月度分析")
        
        # Customer Analysis
        if show_customer_analysis and not df.empty:
            st.markdown("## 👥 客户分析")
            
            try:
                customer_analysis = analyzer.customer_analysis()
                
                # Customer metrics
                if 'customer_value_metrics' in customer_analysis:
                    metrics = customer_analysis['customer_value_metrics']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "平均客户价值", 
                            f"¥{metrics['avg_customer_value']:.2f}"
                        )
                    with col2:
                        st.metric(
                            "客户留存率", 
                            f"{metrics['customer_retention_rate']:.1%}"
                        )
                    with col3:
                        st.metric(
                            "平均订单数/客户", 
                            f"{metrics['avg_orders_per_customer']:.1f}"
                        )
                else:
                    st.info("客户分析数据不完整")
                
                # Customer demographics chart
                fig_customer = create_customer_analysis_chart(df)
                if fig_customer:
                    st.plotly_chart(fig_customer, use_container_width=True)
                else:
                    st.info("无法生成客户分析图表")
            except Exception as e:
                st.error(f"客户分析出错: {str(e)}")
        
        # Product Analysis
        if show_product_analysis and not df.empty:
            st.markdown("## 🛍️ 产品分析")
            
            # Category distribution
            fig_category = create_category_chart(df)
            if fig_category:
                st.plotly_chart(fig_category, use_container_width=True)
            else:
                st.info("无法生成产品类别图表")
            
            # Top products
            if 'product_name' in df.columns:
                try:
                    top_products = df.groupby('product_name').agg({
                        'total_amount': 'sum',
                        'quantity': 'sum',
                        'order_id': 'count'
                    }).reset_index().sort_values('total_amount', ascending=False).head(10)
                    
                    st.markdown("### 🏆 热销产品 TOP 10")
                    st.dataframe(
                        top_products.rename(columns={
                            'product_name': '产品名称',
                            'total_amount': '销售额',
                            'quantity': '销量',
                            'order_id': '订单数'
                        }),
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"热销产品分析出错: {str(e)}")
            else:
                st.info("数据缺少产品名称字段，无法进行热销产品分析")
        
        # Export options
        st.markdown("## 📥 导出选项")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("生成完整报告") and not df.empty:
                with st.spinner("正在生成报告..."):
                    try:
                        # Generate comprehensive analysis
                        basic_stats = analyzer.basic_statistics()
                        time_analysis = analyzer.time_series_analysis()
                        customer_analysis = analyzer.customer_analysis()
                        product_analysis = analyzer.product_analysis()
                        
                        analysis_results = {
                            'basic_statistics': basic_stats,
                            'time_series_analysis': time_analysis,
                            'customer_analysis': customer_analysis,
                            'product_analysis': product_analysis
                        }
                        
                        # Generate report
                        analyzer.generate_report(analysis_results)
                        st.success("报告已生成并保存到 output/reports/ 目录")
                    except Exception as e:
                        st.error(f"生成报告出错: {str(e)}")
        
        with col2:
            # Download processed data
            if not df.empty:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8')
                st.download_button(
                    label="下载处理后数据",
                    data=csv_buffer.getvalue(),
                    file_name=f"processed_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("没有数据可下载")
        
        with col3:
            # Download analysis summary
            if not df.empty:
                if st.button("下载分析摘要"):
                    summary = {
                        "分析时间": datetime.now().isoformat(),
                        "数据记录数": len(df),
                        "分析期间": f"{df['order_date'].min()} 到 {df['order_date'].max()}",
                        "总销售额": float(df['total_amount'].sum()),
                        "平均订单价值": float(df['total_amount'].mean()),
                        "客户数量": int(df['customer_id'].nunique())
                    }
                    
                    if 'product_category' in df.columns:
                        summary["产品类别数"] = int(df['product_category'].nunique())
                    
                    json_str = json.dumps(summary, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="下载JSON摘要",
                        data=json_str,
                        file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            else:
                st.info("没有数据可摘要")
    
    except Exception as e:
        st.error(f"分析过程中发生错误: {str(e)}")
        st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">'
        '🚀 电商订单数据分析平台 | 基于 Streamlit 构建'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
