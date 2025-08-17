#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坏习惯统计器 - 安卓App版本
基于Kivy框架开发
"""

import json
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
import chinese_calendar

# 导入字体助手
from font_helper import DEFAULT_CHINESE_FONT

class DataManager:
    """数据管理类"""
    
    def __init__(self):
        self.data_file = os.path.join(os.getcwd(), 'habit_data.json')
        self.data = self.load_data()
    
    def load_data(self):
        """加载数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据格式完整
                    if 'score' not in data:
                        data['score'] = 100
                    if 'streak' not in data:
                        data['streak'] = 0
                    if 'records' not in data:
                        data['records'] = {}
                    if 'first_record_date' not in data:
                        data['first_record_date'] = None
                    return data
        except Exception as e:
            print(f"加载数据失败: {e}")
        
        # 初始化数据
        return {
            'score': 100,
            'streak': 0,
            'records': {},
            'first_record_date': None
        }
    
    def save_data(self):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def get_today_str(self):
        """获取今日日期字符串"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def auto_check_in(self):
        """自动打卡"""
        today_str = self.get_today_str()
        
        if today_str not in self.data['records']:
            self.data['records'][today_str] = {
                'color': 'green',
                'count': 0,
                'timestamp': datetime.now().isoformat()
            }
            self.data['streak'] += 1
            
            # 检查连续奖励
            self.check_reward()
            
            # 设置首次记录日期
            if not self.data['first_record_date']:
                self.data['first_record_date'] = today_str
            
            self.save_data()
            return True
        return False
    
    def record_bad_habit(self):
        """记录坏习惯"""
        today_str = self.get_today_str()
        
        if today_str not in self.data['records']:
            self.data['records'][today_str] = {
                'color': 'red',
                'count': 1,
                'timestamp': datetime.now().isoformat()
            }
        else:
            self.data['records'][today_str]['count'] += 1
            self.data['records'][today_str]['color'] = 'red'
        
        # 扣除积分
        self.data['score'] = max(0, self.data['score'] - 10)
        
        # 重置连续天数
        self.data['streak'] = 0
        
        # 设置首次记录日期
        if not self.data['first_record_date']:
            self.data['first_record_date'] = today_str
        
        self.save_data()
        return self.data['records'][today_str]['count']
    
    def undo_today(self):
        """撤销当天记录"""
        today_str = self.get_today_str()
        
        if today_str not in self.data['records']:
            return False
        
        today_record = self.data['records'][today_str]
        
        # 恢复积分
        if today_record['color'] == 'green':
            self.data['score'] = max(0, self.data['score'] - 1)
            self.data['streak'] = max(0, self.data['streak'] - 1)
        else:
            self.data['score'] = min(200, self.data['score'] + today_record['count'] * 10)
            self.data['streak'] = self.calculate_streak()
        
        # 删除当天记录
        del self.data['records'][today_str]
        
        # 如果没有记录了，清除首次记录日期
        if not self.data['records']:
            self.data['first_record_date'] = None
        
        self.save_data()
        return True
    
    def calculate_streak(self):
        """计算连续天数"""
        if not self.data['first_record_date']:
            return 0
        
        sorted_dates = sorted(self.data['records'].keys(), reverse=True)
        streak = 0
        prev_date = None
        
        for date_str in sorted_dates:
            record = self.data['records'][date_str]
            
            if record['color'] != 'green':
                break
            
            if prev_date:
                prev = datetime.strptime(prev_date, '%Y-%m-%d')
                prev = prev - timedelta(days=1)
                prev_date_str = prev.strftime('%Y-%m-%d')
                
                if date_str != prev_date_str:
                    break
            
            streak += 1
            prev_date = date_str
        
        return streak
    
    def check_reward(self):
        """检查连续奖励"""
        if self.data['streak'] >= 5 and self.data['streak'] % 5 == 0:
            self.data['score'] = min(200, self.data['score'] + 10)
            self.save_data()
            return True
        return False
    
    def get_year_records(self, year):
        """获取指定年份的记录"""
        year_str = str(year)
        year_records = {}
        
        for date_str, record in self.data['records'].items():
            if date_str.startswith(year_str):
                year_records[date_str] = record
        
        return year_records
    
    def get_available_years(self):
        """获取可用的年份"""
        if not self.data['first_record_date']:
            return [datetime.now().year]
        
        first_year = int(self.data['first_record_date'][:4])
        current_year = datetime.now().year
        
        return list(range(first_year, current_year + 1))

class MainScreen(Screen):
    """主屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = App.get_running_app().data_manager
        self.build_ui()
        
        # 自动打卡
        Clock.schedule_once(self.auto_check_in, 0.5)
    
    def build_ui(self):
        """构建UI"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 标题
        title = Label(
            text='坏习惯统计器',
            font_size=dp(24),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # 分数显示
        score_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        score_label = Label(
            text='当前积分:',
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.4
        )
        self.score_value = Label(
            text=str(self.data_manager.data['score']),
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.6
        )
        score_layout.add_widget(score_label)
        score_layout.add_widget(self.score_value)
        layout.add_widget(score_layout)
        
        # 连续天数显示
        streak_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        streak_label = Label(
            text='连续天数:',
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.4
        )
        self.streak_value = Label(
            text=str(self.data_manager.data['streak']),
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.6
        )
        streak_layout.add_widget(streak_label)
        streak_layout.add_widget(self.streak_value)
        layout.add_widget(streak_layout)
        
        # 今日状态
        today_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        today_label = Label(
            text='今日状态:',
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.4
        )
        self.today_status = Label(
            text=self.get_today_status(),
            font_size=dp(18),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_x=0.6
        )
        today_layout.add_widget(today_label)
        today_layout.add_widget(self.today_status)
        layout.add_widget(today_layout)
        
        # 按钮区域
        buttons_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        # 记录坏习惯按钮
        bad_btn = Button(
            text='记录坏习惯',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        bad_btn.bind(on_press=self.record_bad_habit)
        buttons_layout.add_widget(bad_btn)
        
        # 撤销按钮
        undo_btn = Button(
            text='撤销今日记录',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        undo_btn.bind(on_press=self.undo_today)
        buttons_layout.add_widget(undo_btn)
        
        # 热力图按钮
        heatmap_btn = Button(
            text='打卡热力图',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT
        )
        heatmap_btn.bind(on_press=self.show_heatmap)
        buttons_layout.add_widget(heatmap_btn)
        
        # 退出按钮
        exit_btn = Button(
            text='退出应用',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT
        )
        exit_btn.bind(on_press=self.exit_app)
        buttons_layout.add_widget(exit_btn)
        
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def get_today_status(self):
        """获取今日状态"""
        today_str = self.data_manager.get_today_str()
        if today_str in self.data_manager.data['records']:
            record = self.data_manager.data['records'][today_str]
            if record['color'] == 'green':
                return '已打卡'
            else:
                return f'坏习惯x{record["count"]}'
        return '未打卡'
    
    def auto_check_in(self, dt):
        """自动打卡"""
        if self.data_manager.auto_check_in():
            self.show_message('自动打卡成功！+1分')
        self.update_display()
    
    def record_bad_habit(self, instance):
        """记录坏习惯"""
        count = self.data_manager.record_bad_habit()
        self.show_message(f'记录坏习惯成功！扣除{count * 10}分')
        self.update_display()
    
    def undo_today(self, instance):
        """撤销今日记录"""
        if self.data_manager.undo_today():
            self.show_message('撤销成功！')
            self.update_display()
        else:
            self.show_message('今日无记录可撤销')
    
    def show_heatmap(self, instance):
        """显示热力图"""
        self.manager.current = 'heatmap'
    
    def exit_app(self, instance):
        """退出应用"""
        App.get_running_app().stop()
    
    def update_display(self):
        """更新显示"""
        self.score_value.text = str(self.data_manager.data['score'])
        self.streak_value.text = str(self.data_manager.data['streak'])
        self.today_status.text = self.get_today_status()
    
    def show_message(self, message):
        """显示消息"""
        popup = Popup(
            title='提示',
            content=Label(text=message, font_name=DEFAULT_CHINESE_FONT),
            size_hint=(0.8, 0.3),
            title_font=DEFAULT_CHINESE_FONT
        )
        popup.open()
        Clock.schedule_once(popup.dismiss, 2)


class HeatmapScreen(Screen):
    """热力图屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = App.get_running_app().data_manager
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 标题
        title = Label(
            text='打卡热力图',
            font_size=dp(24),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # 统计信息
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        total_days = len(self.data_manager.data['records'])
        green_days = sum(1 for r in self.data_manager.data['records'].values() if r['color'] == 'green')
        red_days = sum(1 for r in self.data_manager.data['records'].values() if r['color'] == 'red')
        
        stats_label = Label(
            text=f'总记录: {total_days}天 | 打卡: {green_days}天 | 坏习惯: {red_days}天',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(stats_label)
        
        # 热力图区域
        scroll = ScrollView(size_hint=(1, 1))
        heatmap_layout = GridLayout(cols=7, spacing=dp(2), size_hint_y=None)
        heatmap_layout.bind(minimum_height=heatmap_layout.setter('height'))
        
        # 生成热力图
        self.generate_heatmap(heatmap_layout)
        
        scroll.add_widget(heatmap_layout)
        layout.add_widget(scroll)
        
        # 返回按钮
        back_btn = Button(
            text='返回',
            font_size=dp(16),
            font_name=DEFAULT_CHINESE_FONT,
            size_hint_y=None,
            height=dp(50)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def generate_heatmap(self, layout):
        """生成热力图"""
        if not self.data_manager.data['records']:
            no_data = Label(
                text='暂无数据',
                font_size=dp(16),
                font_name=DEFAULT_CHINESE_FONT
            )
            layout.add_widget(no_data)
            return
        
        # 获取所有日期并排序
        sorted_dates = sorted(self.data_manager.data['records'].keys())
        
        # 添加日期标签
        for date_str in sorted_dates[-84:]:  # 最近12周
            record = self.data_manager.data['records'][date_str]
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_label = Label(
                text=f"{date_obj.month}/{date_obj.day}",
                font_size=dp(12),
                font_name=DEFAULT_CHINESE_FONT,
                size_hint_y=None,
                height=dp(40)
            )
            
            if record['color'] == 'green':
                day_label.color = (0.2, 0.8, 0.2, 1)
            else:
                day_label.color = (0.8, 0.2, 0.2, 1)
            
            layout.add_widget(day_label)
    
    def go_back(self, instance):
        """返回"""
        self.manager.current = 'main'


class BadHabitTrackerApp(App):
    """主应用类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()
    
    def build(self):
        """构建应用"""
        # 设置窗口标题
        self.title = '坏习惯统计器'
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加屏幕
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(HeatmapScreen(name='heatmap'))
        
        return sm


if __name__ == '__main__':
    BadHabitTrackerApp().run()