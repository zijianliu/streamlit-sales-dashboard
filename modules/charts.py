import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


class ChartGenerator:
    def __init__(self, color_theme: str = 'plotly'):
        self.color_theme = color_theme
        self.colors = px.colors.qualitative.Plotly

    def sales_trend_chart(self, df: pd.DataFrame, freq: str = 'M') -> Optional[go.Figure]:
        if df.empty:
            return None

        df_trend = df.copy()
        df_trend['年月'] = df_trend['订单日期'].dt.to_period(freq)
        
        trend_data = df_trend.groupby('年月').agg({
            '销售额': 'sum',
            '利润': 'sum'
        }).reset_index()
        
        trend_data['年月'] = trend_data['年月'].astype(str)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['年月'],
            y=trend_data['销售额'],
            mode='lines+markers',
            name='销售额',
            line=dict(color=self.colors[0], width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['年月'],
            y=trend_data['利润'],
            mode='lines+markers',
            name='利润',
            line=dict(color=self.colors[2], width=2),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='销售趋势分析',
            xaxis_title='日期',
            yaxis_title='销售额',
            yaxis2=dict(
                title='利润',
                overlaying='y',
                side='right'
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig

    def region_comparison_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        if df.empty:
            return None

        region_data = df.groupby('地区').agg({
            '销售额': 'sum',
            '利润': 'sum'
        }).reset_index()
        
        region_data = region_data.sort_values('销售额', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=region_data['地区'],
            y=region_data['销售额'],
            name='销售额',
            marker_color=self.colors[0],
            text=region_data['销售额'].round(0),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=region_data['地区'],
            y=region_data['利润'],
            name='利润',
            marker_color=self.colors[2],
            text=region_data['利润'].round(0),
            textposition='auto'
        ))
        
        fig.update_layout(
            title='地区销售对比',
            xaxis_title='地区',
            yaxis_title='金额',
            barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            template='plotly_white'
        )
        
        return fig

    def category_pie_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        if df.empty:
            return None

        category_data = df.groupby('类别').agg({
            '销售额': 'sum'
        }).reset_index()
        
        fig = px.pie(
            category_data,
            values='销售额',
            names='类别',
            title='类别销售额占比',
            color_discrete_sequence=self.colors,
            hole=0.4
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>销售额: %{value:,.0f}<br>占比: %{percent}'
        )
        
        fig.update_layout(
            template='plotly_white',
            showlegend=True
        )
        
        return fig

    def top_products_chart(self, df: pd.DataFrame, top_n: int = 10) -> Optional[go.Figure]:
        if df.empty:
            return None

        product_data = df.groupby('产品名').agg({
            '销售额': 'sum',
            '利润': 'sum'
        }).reset_index()
        
        product_data = product_data.sort_values('销售额', ascending=False).head(top_n)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=product_data['产品名'],
            x=product_data['销售额'],
            name='销售额',
            orientation='h',
            marker_color=self.colors[0],
            text=product_data['销售额'].round(0),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            y=product_data['产品名'],
            x=product_data['利润'],
            name='利润',
            orientation='h',
            marker_color=self.colors[2],
            text=product_data['利润'].round(0),
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'Top {top_n} 产品销售排行',
            xaxis_title='金额',
            yaxis_title='产品名',
            yaxis=dict(autorange='reversed'),
            barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            template='plotly_white'
        )
        
        return fig

    def salesperson_performance_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        if df.empty:
            return None

        salesperson_data = df.groupby('销售人员').agg({
            '销售额': 'sum',
            '利润': 'sum'
        }).reset_index()
        
        salesperson_data = salesperson_data.sort_values('销售额', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=salesperson_data['销售人员'],
            y=salesperson_data['销售额'],
            name='销售额',
            marker_color=self.colors[0],
            text=salesperson_data['销售额'].round(0),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=salesperson_data['销售人员'],
            y=salesperson_data['利润'],
            name='利润',
            marker_color=self.colors[2],
            text=salesperson_data['利润'].round(0),
            textposition='auto'
        ))
        
        fig.update_layout(
            title='销售人员业绩对比',
            xaxis_title='销售人员',
            yaxis_title='金额',
            barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            template='plotly_white'
        )
        
        return fig
