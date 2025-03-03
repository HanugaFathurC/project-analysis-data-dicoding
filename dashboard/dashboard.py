import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        'order_id': 'count',
        'price': 'sum'
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        'order_id': 'order_count',
        'price': 'revenue'
    }, inplace= True)

    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = (df.groupby('product_category_name_english')
                          .order_item_id.sum().sort_values(ascending=False)).reset_index()
    return sum_order_items_df

def create_bycity_df(df):
    bycity_df = (df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
                 .sort_values(by="customer_unique_id", ascending=False))
    bycity_df.rename(columns={'customer_unique_id': 'total_customer'}, inplace=True)
    return bycity_df

def create_bystate_df(df):
    bystate_df = (df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
                  .sort_values(by="customer_unique_id", ascending=False))
    bystate_df.rename(columns={'customer_unique_id': 'total_customer'}, inplace=True)
    return bystate_df

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='ME', on='order_approved_at').agg({
        'order_id': 'count',
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%B')
    monthly_orders_df.rename(columns={'order_id': 'total_order'}, inplace=True)

    monthly_orders_df = monthly_orders_df.groupby(by='order_approved_at').total_order.sum().reset_index()

    month_orders = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                    'November', 'December']
    monthly_orders_df['order_approved_at'] = pd.Categorical(monthly_orders_df['order_approved_at'],
                                                            categories=month_orders, ordered=True)
    return monthly_orders_df.sort_values(by='order_approved_at')

def create_monthly_revenue_df(df):
    monthly_revenue_df = df.resample(rule='ME', on='order_approved_at').agg({
        'price': 'sum'
    })
    monthly_revenue_df.index = monthly_revenue_df.index.strftime('%B')
    monthly_revenue_df.rename(columns={'price': 'total_revenue'}, inplace=True)

    monthly_revenue_df = monthly_revenue_df.groupby(by='order_approved_at').total_revenue.sum().reset_index()
    month_orders = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                    'November', 'December']
    monthly_revenue_df['order_approved_at'] = pd.Categorical(monthly_revenue_df['order_approved_at'],
                                                            categories=month_orders, ordered=True)
    return monthly_revenue_df.sort_values(by='order_approved_at')

def create_most_loyal_customer_df(df):
    most_loyal_customer_df = df.groupby('customer_unique_id').agg({
        'order_id': 'count',
        'price': 'sum'
    }).sort_values(by='price', ascending=False)
    most_loyal_customer_df.rename(columns={
        'order_id': 'total_order',
        'price': 'total_spending'
    }, inplace=True)
    return most_loyal_customer_df

def create_rfm_df(df):
    rfm_df = df.groupby(by='customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'price': 'sum'
    })
    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']

    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = pd.to_datetime(all_df['order_purchase_timestamp']).dt.date.max()
    rfm_df['recency'] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Load the dataset
all_df = pd.read_csv('main_data.csv')

datetime_columns = ['order_approved_at', 'order_purchase_timestamp']
all_df.sort_values(by='order_approved_at', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df['order_approved_at'].min()
max_date = all_df['order_approved_at'].max()

#
# Sidebar
#
with st.sidebar:
    st.image("https://media.datacamp.com/legacy/v1727712679/image_0dd3c66c35.png")

    # Take start_date and end_date from date_input
    start_date, end_date = st.date_input(
        label="Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Convert to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)


main_df = all_df[(all_df['order_approved_at'] >= start_date) & (all_df['order_approved_at'] <= end_date)]

# Create DataFrames
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
monthly_orders_df = create_monthly_orders_df(main_df)
monthly_revenue_df = create_monthly_revenue_df(main_df)
most_loyal_customer_df = create_most_loyal_customer_df(main_df)
rfm_df = create_rfm_df(main_df)

# Create Header for daily orders
st.header('E-commerce Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric(label='Total Orders', value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), 'AUD', locale='es_CO')
    st.metric(label='Total Revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df['order_approved_at'],
    daily_orders_df['order_count'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=20)

st.pyplot(fig)

# Create Product Performance
st.subheader('Best & Worst Performing Products')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x='order_item_id',
    y='product_category_name_english',
    data=sum_order_items_df.head(5),
    hue='product_category_name_english',
    legend=False,
    palette=colors,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel('Number of Sales', fontsize=30)
ax[0].set_title('Top 5 Best Products by Sales', loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(
    x='order_item_id',
    y='product_category_name_english',
    hue='product_category_name_english',
    legend=False,
    data=sum_order_items_df.tail(5),
    palette=colors,
    ax=ax[1]
)
ax[0].set_ylabel(None)
ax[1].set_xlabel('Number of Sales', fontsize=30)
ax[1].set_title('Top 5 Worst Products by Sales', loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()

st.pyplot(fig)

# Customer demographic
st.subheader('Customer Demographics')
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x='total_customer',
        y='customer_city',
        hue='customer_city',
        legend=False,
        data=bycity_df.sort_values(by='total_customer', ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by City", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x='total_customer',
        y='customer_state',
        hue='customer_state',
        legend=False,
        data=bystate_df.sort_values(by='total_customer', ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by State", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# Monthly Orders Performance using Line Chart
st.subheader('Monthly Orders Performance')
fig, ax = plt.subplots(figsize=(20, 10))
plt.plot(
    monthly_orders_df['order_approved_at'],
    monthly_orders_df['total_order'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.title("Monthly Orders Performance", fontsize=50)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

# Monthly Revenue Performance using Line Chart
st.subheader('Monthly Revenue Performance')
fig, ax = plt.subplots(figsize=(20, 10))
plt.plot(
    monthly_revenue_df['order_approved_at'],
    monthly_revenue_df['total_revenue'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.title("Monthly Revenue Performance", fontsize=50)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

# Most Loyal Customer using Table
st.subheader('Most Loyal Customer')
most_loyal_customer_df = most_loyal_customer_df.head(5)
most_loyal_customer_df['total_spending'] = most_loyal_customer_df['total_spending'].apply(lambda x: format_currency(x, 'AUD', locale='es_CO'))
st.table(most_loyal_customer_df)

# Best Customer Segmentation using RFM Analysis
st.subheader('Best Customer Segmentation using RFM Parameters')
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric(label='Average Recency (Days)', value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 1)
    st.metric(label='Average Frequency', value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), 'AUD', locale='es_CO')
    st.metric(label='Average Monetary', value=avg_monetary)


colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])
with tab1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(y="recency", x="customer_id", hue="recency", legend=False, data=rfm_df.sort_values(by='recency', ascending=True).head(5),
                palette=colors[:1])
    plt.ylabel(None)
    plt.xlabel("customer_id", fontsize=30)
    plt.title("Top 5 Customers by Recency", loc="center", fontsize=50)
    plt.tick_params(axis='y', labelsize=15)
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(y="frequency", x="customer_id", hue="recency", legend=False, data=rfm_df.sort_values(by='frequency', ascending=False).head(5),
                palette=colors)
    plt.ylabel(None)
    plt.xlabel("customer_id", fontsize=30)
    plt.title("Top 5 Customers by Frequency", loc="center", fontsize=50)
    plt.tick_params(axis='y', labelsize=15)
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(y="monetary", x="customer_id", hue="recency", legend=False, data=rfm_df.sort_values(by='monetary', ascending=False).head(5), palette=colors)
    plt.ylabel(None)
    plt.xlabel("customer_id", fontsize=30)
    plt.title("Top 5 Customers by Monetary", loc="center", fontsize=50)
    plt.tick_params(axis='y', labelsize=15)
    st.pyplot(fig)

st.caption('© 2025 - Hanuga Fathur C.')



















