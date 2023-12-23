import os
import requests

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from flask import send_file

rankIds = {
    'beijing': 'd5036cf54fcb57e9dceb9fefe3917fff71862f838d1255ea693b953b1d49c7c0',
    'shanghai': 'fce2e3a36450422b7fad3f2b90370efd71862f838d1255ea693b953b1d49c7c0',
}


sns.set(style="whitegrid")  # 设置图表风格
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置图表字体


def get_data(city):
    url = f'https://www.dianping.com/mylist/ajax/shoprank?rankId={rankIds[city]}'
    response = requests.get(url)
    data = response.json()
    shops = data['shopBeans']
    return pd.DataFrame(shops)


def draw_chart(data, city, chart):
    if chart == 'percentage_of_categories':
        top_categories = data['mainCategoryName'].value_counts().nlargest(9)
        other_categories_count = data['mainCategoryName'].value_counts().sum() - top_categories.sum()
        top_categories['其他'] = other_categories_count

        # 创建饼图
        plt.figure(figsize=(10, 10))
        plt.pie(top_categories, labels=top_categories.index, autopct='%1.1f%%', pctdistance=0.85, startangle=45)
        plt.title('餐厅类型占比', fontsize=24, y=1.05)

        # 添加中心圆，实现环形图的效果
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

    elif chart == 'region_average_prices':
        avg_prices_by_region = data.groupby("mainRegionName")["avgPrice"].mean().sort_values()
        plt.figure(figsize=(32, 18))
        sns.barplot(x=avg_prices_by_region.index, y=avg_prices_by_region.values, palette='coolwarm')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("商区", fontsize=18)
        plt.ylabel("平均价格", fontsize=18, labelpad=36)
        plt.title('各商区平均价格', fontsize=32, y=1.05)

    elif chart == 'region_most_popular_types':
        grouped_data = data.groupby(["mainRegionName", "mainCategoryName"]).size().reset_index(name='shopCount')
        pivot_data = pd.pivot_table(grouped_data, values='shopCount', index='mainRegionName',
                                    columns='mainCategoryName', fill_value=0)
        most_popular_types_by_region = pivot_data.idxmax(axis=1)
        most_popular_counts_by_region = pivot_data.max(axis=1)
        result_df = pd.DataFrame({
            'mainRegionName': most_popular_types_by_region.index,
            'shopCount': grouped_data.groupby('mainRegionName')['shopCount'].sum(),
            'mostPopularCategory': most_popular_types_by_region.values,
            'mostPopularCategoryCount': most_popular_counts_by_region.values
        })

        fig, ax = plt.subplots(figsize=(32, 24))
        sns.barplot(x='shopCount', y='mainRegionName', data=result_df, color='lightblue', label='总餐厅数')
        sns.barplot(x='mostPopularCategoryCount', y='mainRegionName', data=result_df, color='b', label='最受欢迎的餐厅类型的餐厅数')
        for rect, label in zip(ax.patches[len(result_df):], result_df['mostPopularCategory']):
            width = rect.get_width()
            ax.text(width, rect.get_y() + rect.get_height() / 2, f'{label}', ha='left', va='center', fontsize=10, color='black')
        plt.xlabel("受欢迎指数", fontsize=18, labelpad=36)
        plt.ylabel("餐厅类型", fontsize=18, labelpad=36)
        plt.title('各商区最受欢迎的餐厅类型', fontsize=32., y=1.05)
        ax.legend()
    # else:
    #     pass

    # 保存图表为图片
    os.makedirs(f'charts/{city}', exist_ok=True)
    image_path = f'charts/{city}/{chart}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()


def get_chart(city, chart):
    # 检查图片是否存在
    chart_path = f'charts/{city}/{chart}.png'
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype='image/png')

    # 图片不存在，获取数据
    data = get_data(city)

    # 绘制图表并保存图片
    draw_chart(data, city, chart)

    # 返回图片
    return send_file(chart_path, mimetype='image/png')
