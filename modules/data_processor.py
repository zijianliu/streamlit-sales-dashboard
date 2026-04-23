import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from datetime import datetime


class DataProcessor:
    REQUIRED_COLUMNS = ['订单日期', '地区', '类别', '产品名', '销售额', '利润', '销售人员']
    
    def __init__(self):
        self.raw_data = None
        self.clean_data = None
        self.cleaning_stats = {}

    def load_data(self, file_path) -> Tuple[bool, str]:
        try:
            if file_path is None:
                return False, "请上传 CSV 文件"

            self.raw_data = pd.read_csv(file_path)
            return True, "数据加载成功"
        except Exception as e:
            return False, f"数据加载失败: {str(e)}"

    def validate_columns(self) -> Tuple[bool, str]:
        if self.raw_data is None:
            return False, "数据未加载"

        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in self.raw_data.columns]
        if missing_columns:
            return False, f"缺少必需列: {', '.join(missing_columns)}"

        return True, "列验证通过"

    def clean_data(self) -> Dict[str, Any]:
        if self.raw_data is None:
            return {'success': False, 'message': '数据未加载'}

        df = self.raw_data.copy()
        original_count = len(df)

        self.cleaning_stats = {
            'original_count': original_count,
            'duplicates_removed': 0,
            'null_rows_removed': 0,
            'final_count': 0
        }

        duplicates = df.duplicated()
        if duplicates.any():
            self.cleaning_stats['duplicates_removed'] = duplicates.sum()
            df = df.drop_duplicates()

        key_columns = ['订单日期', '地区', '类别', '产品名', '销售额', '利润', '销售人员']
        null_mask = df[key_columns].isnull().any(axis=1)
        if null_mask.any():
            self.cleaning_stats['null_rows_removed'] = null_mask.sum()
            df = df[~null_mask]

        df['订单日期'] = pd.to_datetime(df['订单日期'], errors='coerce')
        invalid_dates = df['订单日期'].isnull()
        if invalid_dates.any():
            self.cleaning_stats['null_rows_removed'] += invalid_dates.sum()
            df = df[~invalid_dates]

        for col in ['销售额', '利润']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            invalid_nums = df[col].isnull()
            if invalid_nums.any():
                self.cleaning_stats['null_rows_removed'] += invalid_nums.sum()
                df = df[~invalid_nums]

        df['年份'] = df['订单日期'].dt.year
        df['月份'] = df['订单日期'].dt.month
        df['年月'] = df['订单日期'].dt.to_period('M')

        self.clean_data = df.reset_index(drop=True)
        self.cleaning_stats['final_count'] = len(self.clean_data)

        return {
            'success': True,
            'message': '数据清洗完成',
            'stats': self.cleaning_stats
        }

    def filter_data(
        self,
        date_range: Tuple[datetime, datetime] = None,
        regions: list = None,
        categories: list = None,
        salespeople: list = None
    ) -> pd.DataFrame:
        if self.clean_data is None:
            return pd.DataFrame()

        df = self.clean_data.copy()

        if date_range:
            start_date, end_date = date_range
            df = df[(df['订单日期'] >= pd.Timestamp(start_date)) & (df['订单日期'] <= pd.Timestamp(end_date))]

        if regions and len(regions) > 0:
            df = df[df['地区'].isin(regions)]

        if categories and len(categories) > 0:
            df = df[df['类别'].isin(categories)]

        if salespeople and len(salespeople) > 0:
            df = df[df['销售人员'].isin(salespeople)]

        return df

    def get_unique_values(self) -> Dict[str, list]:
        if self.clean_data is None:
            return {}

        return {
            'regions': sorted(self.clean_data['地区'].unique().tolist()),
            'categories': sorted(self.clean_data['类别'].unique().tolist()),
            'salespeople': sorted(self.clean_data['销售人员'].unique().tolist()),
            'date_range': (self.clean_data['订单日期'].min(), self.clean_data['订单日期'].max())
        }

    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                'total_sales': 0,
                'total_profit': 0,
                'order_count': 0,
                'avg_order_sales': 0
            }

        return {
            'total_sales': df['销售额'].sum(),
            'total_profit': df['利润'].sum(),
            'order_count': len(df),
            'avg_order_sales': df['销售额'].mean()
        }
