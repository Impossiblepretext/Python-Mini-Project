import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

# ─── LOAD & CLEAN DATA ───────────────────────────────────────────────────────
df = pd.read_csv(r'C:\Users\vishu\OneDrive\Desktop\Codes\PY mp\onlinedeliverydata.csv')
df_clean = df.drop_duplicates()
df_clean.to_csv(r'C:\Users\vishu\OneDrive\Desktop\Codes\PY mp\cleaned_data.csv', index=False)

df = pd.read_csv(r'C:\Users\vishu\OneDrive\Desktop\Codes\PY mp\cleaned_data.csv')

# Fix wait time — force convert regardless of type
df['Maximum wait time'] = df['Maximum wait time'].astype(str).str.extract(r'(\d+)')
df['Maximum wait time'] = pd.to_numeric(df['Maximum wait time'], errors='coerce')

# Fix Reviews to numeric
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Age Group column
df['Age Group'] = pd.cut(
    df['Age'],
    bins=[0, 18, 25, 35, 50, 100],
    labels=['Teen', 'Young Adult', 'Adult', 'Middle Age', 'Senior']
)

# ─── KEY METRICS ─────────────────────────────────────────────────────────────
total_users            = len(df)
avg_age                = df['Age'].mean()
avg_family_size        = df['Family size'].mean()
avg_income             = df['Monthly Income'].value_counts().idxmax()
most_common_order_time = df['Order Time'].value_counts().idxmax()
avg_wait_time          = df['Maximum wait time'].mean()
online_users           = df['Output'].value_counts().get('Yes', 0)
adoption_rate          = round(online_users / total_users * 100, 1)

print(f"Total Users: {total_users}")
print(f"Average Age: {avg_age:.2f}")
print(f"Average Family Size: {avg_family_size:.2f}")
print(f"Most Common Income Group: {avg_income}")
print(f"Most Common Order Time: {most_common_order_time}")
print(f"Average Wait Time: {avg_wait_time:.2f}")
print(f"People using Online Delivery: {online_users}")

family_orders = df.groupby('Family size')['Output'].value_counts().unstack().fillna(0)
print(family_orders)
income_orders = df.groupby('Monthly Income')['Output'].value_counts().unstack().fillna(0)
print(income_orders)

# ─── PREPARE CHART DATA ───────────────────────────────────────────────────────
orders_by_category = df.groupby('Meal(P1)').size().reset_index(name='Total Orders').sort_values('Total Orders', ascending=False)
orders_by_occupation = df.groupby('Occupation').size().reset_index(name='Total Orders').sort_values('Total Orders', ascending=False)
orders_by_income = df.groupby('Monthly Income').size().reset_index(name='Total Orders').sort_values('Total Orders', ascending=False)
wait_time_by_food = df.groupby('Meal(P1)')['Maximum wait time'].mean().sort_values(ascending=False)
popularity_by_food = df['Perference(P1)'].value_counts()
popular_restaurants = df['Meal(P1)'].value_counts().head(10)
top_foods = df['Meal(P1)'].value_counts().head(5).index
filtered_df = df[df['Meal(P1)'].isin(top_foods)]
cuisine_age_plot = filtered_df.groupby(['Age Group', 'Meal(P1)'], observed=True).size().unstack().fillna(0)
order_time_counts = df['Order Time'].value_counts()
output_counts = df['Output'].value_counts()

# ─── FIGURE: wider, taller, more breathing room ───────────────────────────────
fig = plt.figure(figsize=(22, 18))
fig.patch.set_facecolor('#f0f2f5')

fig.suptitle('Online Food Delivery — Data Analysis Dashboard',
             fontsize=18, fontweight='bold', y=0.99, color='#1a1a2e')

# ── METRIC CARDS (6 cards, pushed down so title breathes) ─────────────────────
metrics = [
    ('Total Users',     f'{total_users}',          '#4c9be8'),
    ('Adoption Rate',   f'{adoption_rate}%',        '#3ecf8e'),
    ('Average Age',     f'{avg_age:.1f} yrs',       '#f5a623'),
    ('Avg Wait Time',   f'{avg_wait_time:.0f} min', '#a78bfa'),
    ('Online Users',    f'{online_users}',           '#f87171'),
    ('Avg Family Size', f'{avg_family_size:.1f}',   '#4ec9b0'),
]
for i, (label, value, color) in enumerate(metrics):
    ax_m = fig.add_axes([0.01 + i * 0.165, 0.895, 0.15, 0.062])
    ax_m.set_facecolor('white')
    for spine in ax_m.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax_m.set_xticks([])
    ax_m.set_yticks([])
    ax_m.text(0.5, 0.62, value, transform=ax_m.transAxes,
              ha='center', va='center', fontsize=17, fontweight='bold', color=color)
    ax_m.text(0.5, 0.18, label, transform=ax_m.transAxes,
              ha='center', va='center', fontsize=8, color='#555555')

# ── CHART GRID: 2 rows x 5 cols, with more vertical space per chart ───────────
# Row 1: y from 0.52 to 0.86, Row 2: y from 0.06 to 0.46
# Each chart: width=0.165, height=0.30, with gap of 0.025 between cols

def make_ax(col, row):
    """col: 0-4, row: 0 (top) or 1 (bottom)"""
    x = 0.05 + col * 0.192
    y = 0.535 if row == 0 else 0.08
    return fig.add_axes([x, y, 0.165, 0.32])

# ── ROW 1 ─────────────────────────────────────────────────────────────────────

# Chart 1: Top Meal Types by Orders
ax1 = make_ax(0, 0)
orders_by_category.head(10).plot(kind='bar', x='Meal(P1)', y='Total Orders',
                                  ax=ax1, legend=False, color='steelblue', width=0.6)
ax1.set_title("Top Meal Types by Orders", fontsize=9, fontweight='bold', pad=6)
ax1.set_xlabel("Meal Type", fontsize=8)
ax1.set_ylabel("Number of Orders", fontsize=8)
ax1.tick_params(axis='x', rotation=20, labelsize=7)
ax1.tick_params(axis='y', labelsize=7)

# Chart 2: Orders by Occupation
ax2 = make_ax(1, 0)
orders_by_occupation.plot(kind='bar', x='Occupation', y='Total Orders',
                           ax=ax2, legend=False, color='coral', width=0.6)
ax2.set_title("Orders by Occupation", fontsize=9, fontweight='bold', pad=6)
ax2.set_xlabel("Occupation", fontsize=8)
ax2.set_ylabel("Number of Orders", fontsize=8)
ax2.tick_params(axis='x', rotation=20, labelsize=7)
ax2.tick_params(axis='y', labelsize=7)

# Chart 3: Orders by Income Group
ax3 = make_ax(2, 0)
orders_by_income.plot(kind='bar', x='Monthly Income', y='Total Orders',
                       ax=ax3, legend=False, color='mediumpurple', width=0.6)
ax3.set_title("Orders by Income Group", fontsize=9, fontweight='bold', pad=6)
ax3.set_xlabel("Income Group", fontsize=8)
ax3.set_ylabel("Number of Orders", fontsize=8)
ax3.tick_params(axis='x', rotation=25, labelsize=6)
ax3.tick_params(axis='y', labelsize=7)

# Chart 4: Avg Wait Time by Meal Type
ax4 = make_ax(3, 0)
wait_time_by_food.head(10).plot(kind='bar', ax=ax4, color='teal', width=0.6)
ax4.set_title("Avg Wait Time by Meal Type", fontsize=9, fontweight='bold', pad=6)
ax4.set_xlabel("Meal Type", fontsize=8)
ax4.set_ylabel("Avg Wait Time (min)", fontsize=8)
ax4.tick_params(axis='x', rotation=20, labelsize=7)
ax4.tick_params(axis='y', labelsize=7)

# Chart 5: Food Preference Distribution
ax5 = make_ax(4, 0)
popularity_by_food.head(5).plot(kind='bar', ax=ax5, color='mediumseagreen', width=0.6)
ax5.set_title("Food Preference Distribution", fontsize=9, fontweight='bold', pad=6)
ax5.set_xlabel("Food Preference", fontsize=8)
ax5.set_ylabel("Count", fontsize=8)
ax5.tick_params(axis='x', rotation=25, labelsize=6)
ax5.tick_params(axis='y', labelsize=7)

# ── ROW 2 ─────────────────────────────────────────────────────────────────────

# Chart 6: Most Popular Meal Types
ax6 = make_ax(0, 1)
popular_restaurants.plot(kind='bar', ax=ax6, color='tomato', width=0.6)
ax6.set_title("Most Popular Meal Types", fontsize=9, fontweight='bold', pad=6)
ax6.set_xlabel("Meal Type", fontsize=8)
ax6.set_ylabel("Number of Orders", fontsize=8)
ax6.tick_params(axis='x', rotation=20, labelsize=7)
ax6.tick_params(axis='y', labelsize=7)

# Chart 7: Meal Preference by Age Group
ax7 = make_ax(1, 1)
cuisine_age_plot.plot(kind='bar', ax=ax7)
ax7.set_title("Meal Pref. by Age Group", fontsize=9, fontweight='bold', pad=6)
ax7.set_xlabel("Age Group", fontsize=8)
ax7.set_ylabel("Number of Orders", fontsize=8)
ax7.tick_params(axis='x', rotation=20, labelsize=7)
ax7.tick_params(axis='y', labelsize=7)
ax7.legend(title="Meal", fontsize=6, title_fontsize=7, loc='upper right')

# Chart 8: Wait Time Distribution Histogram
ax8 = make_ax(2, 1)
ax8.hist(df['Maximum wait time'].dropna(), bins=8, color='slateblue', edgecolor='white')
ax8.set_title("Wait Time Distribution", fontsize=9, fontweight='bold', pad=6)
ax8.set_xlabel("Wait Time (minutes)", fontsize=8)
ax8.set_ylabel("Frequency", fontsize=8)
ax8.tick_params(labelsize=7)

# Chart 9: Orders by Time of Day
ax9 = make_ax(3, 1)
order_time_counts.plot(kind='bar', ax=ax9, color='darkorange', width=0.6)
ax9.set_title("Orders by Time of Day", fontsize=9, fontweight='bold', pad=6)
ax9.set_xlabel("Order Time", fontsize=8)
ax9.set_ylabel("Number of Orders", fontsize=8)
ax9.tick_params(axis='x', rotation=20, labelsize=7)
ax9.tick_params(axis='y', labelsize=7)

# Chart 10: Delivery Usage Pie — labels pushed outward, no legend
ax10 = make_ax(4, 1)
ax10.pie(
    output_counts,
    labels=output_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=['mediumseagreen', 'tomato', 'steelblue'],
    labeldistance=1.15,        # pushes labels outward so they don't overlap
    pctdistance=0.75,          # keeps % inside the slice
    textprops={'fontsize': 8}
)
ax10.set_title("Online Delivery Usage", fontsize=9, fontweight='bold', pad=6)

plt.show()