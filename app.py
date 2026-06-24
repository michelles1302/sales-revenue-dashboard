import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Sales & Revenue Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Sales & Revenue Analytics Dashboard")
st.markdown("### Interactive Business Intelligence Solution")

# ---------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    try:
        # ---------------------------------------------------
        # LOAD DATA
        # ---------------------------------------------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # ---------------------------------------------------
        # DATA CLEANING
        # ---------------------------------------------------
        df.drop_duplicates(inplace=True)

        df["Date"] = pd.to_datetime(df["Date"])
        df["Sales"] = pd.to_numeric(df["Sales"])

        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"])

        # ---------------------------------------------------
        # SIDEBAR FILTERS
        # ---------------------------------------------------
        st.sidebar.header("Filters")

        # Date Filter
        start_date = st.sidebar.date_input(
            "Start Date",
            df["Date"].min()
        )

        end_date = st.sidebar.date_input(
            "End Date",
            df["Date"].max()
        )

        region_filter = st.sidebar.multiselect(
            "Region",
            options=df["Region"].unique(),
            default=df["Region"].unique()
        )

        category_filter = st.sidebar.multiselect(
            "Category",
            options=df["Category"].unique(),
            default=df["Category"].unique()
        )

        product_filter = st.sidebar.multiselect(
            "Product",
            options=df["Product"].unique(),
            default=df["Product"].unique()
        )

        # ---------------------------------------------------
        # APPLY FILTERS
        # ---------------------------------------------------
        filtered_df = df[
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date)) &
            (df["Region"].isin(region_filter)) &
            (df["Category"].isin(category_filter)) &
            (df["Product"].isin(product_filter))
        ]

        # ---------------------------------------------------
        # KPI CALCULATIONS
        # ---------------------------------------------------
        total_revenue = filtered_df["Sales"].sum()

        total_orders = filtered_df["Order ID"].nunique()

        avg_order_value = (
            total_revenue / total_orders
            if total_orders > 0 else 0
        )

        total_quantity = (
            filtered_df["Quantity"].sum()
            if "Quantity" in filtered_df.columns
            else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💰 Total Revenue",
            f"₹{total_revenue:,.0f}"
        )

        col2.metric(
            "🧾 Total Orders",
            total_orders
        )

        col3.metric(
            "📦 Avg Order Value",
            f"₹{avg_order_value:,.0f}"
        )

        col4.metric(
            "📊 Quantity Sold",
            f"{total_quantity:,.0f}"
        )

        st.divider()

        # ---------------------------------------------------
        # REVENUE TREND
        # ---------------------------------------------------
        st.subheader("📈 Revenue Trend")

        monthly_sales = (
            filtered_df
            .groupby(filtered_df["Date"].dt.to_period("M"))["Sales"]
            .sum()
            .reset_index()
        )

        monthly_sales["Date"] = monthly_sales["Date"].astype(str)

        fig_trend = px.line(
            monthly_sales,
            x="Date",
            y="Sales",
            markers=True,
            title="Monthly Revenue Trend"
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True
        )

        # ---------------------------------------------------
        # TOP PRODUCTS & REGION SALES
        # ---------------------------------------------------
        col5, col6 = st.columns(2)

        with col5:

            st.subheader("🏆 Top Products")

            top_products = (
                filtered_df
                .groupby("Product")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            fig_products = px.bar(
                top_products,
                x="Sales",
                y="Product",
                orientation="h",
                title="Top Products by Revenue"
            )

            st.plotly_chart(
                fig_products,
                use_container_width=True
            )

        with col6:

            st.subheader("🌎 Sales by Region")

            region_sales = (
                filtered_df
                .groupby("Region")["Sales"]
                .sum()
                .reset_index()
            )

            fig_region = px.pie(
                region_sales,
                names="Region",
                values="Sales",
                title="Revenue Distribution by Region"
            )

            st.plotly_chart(
                fig_region,
                use_container_width=True
            )

        # ---------------------------------------------------
        # CATEGORY ANALYSIS
        # ---------------------------------------------------
        st.subheader("📦 Category Analysis")

        category_sales = (
            filtered_df
            .groupby("Category")["Sales"]
            .sum()
            .reset_index()
        )

        fig_category = px.bar(
            category_sales,
            x="Category",
            y="Sales",
            title="Revenue by Category"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

        # ---------------------------------------------------
        # TOP 5 & BOTTOM 5 PRODUCTS
        # ---------------------------------------------------
        col7, col8 = st.columns(2)

        with col7:

            st.subheader("🔥 Top 5 Products")

            top5 = (
                filtered_df
                .groupby("Product")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            st.dataframe(top5)

        with col8:

            st.subheader("⚠ Bottom 5 Products")

            bottom5 = (
                filtered_df
                .groupby("Product")["Sales"]
                .sum()
                .sort_values()
                .head(5)
            )

            st.dataframe(bottom5)

        # ---------------------------------------------------
        # BUSINESS INSIGHTS
        # ---------------------------------------------------
        st.subheader("💡 Business Insights")

        if not filtered_df.empty:

            best_product = (
                filtered_df.groupby("Product")["Sales"]
                .sum()
                .idxmax()
            )

            best_region = (
                filtered_df.groupby("Region")["Sales"]
                .sum()
                .idxmax()
            )

            best_category = (
                filtered_df.groupby("Category")["Sales"]
                .sum()
                .idxmax()
            )

            highest_month = (
                monthly_sales.loc[
                    monthly_sales["Sales"].idxmax(),
                    "Date"
                ]
            )

            growth = (
                monthly_sales["Sales"]
                .pct_change()
                .mean() * 100
            )

            st.success(f"🏆 Top Product: {best_product}")
            st.success(f"🌎 Best Region: {best_region}")
            st.success(f"📦 Best Category: {best_category}")
            st.info(f"📅 Highest Revenue Month: {highest_month}")
            st.info(f"📈 Average Monthly Growth: {growth:.2f}%")

        # ---------------------------------------------------
        # DATA TABLE
        # ---------------------------------------------------
        st.subheader("📋 Sales Data")

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        # ---------------------------------------------------
        # DOWNLOAD SECTION
        # ---------------------------------------------------
        st.subheader("⬇ Download Reports")

        csv_data = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="sales_report.csv",
            mime="text/csv"
        )

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            filtered_df.to_excel(
                writer,
                index=False
            )

        st.download_button(
            label="Download Excel",
            data=excel_buffer.getvalue(),
            file_name="sales_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")

else:

    st.info("Upload a CSV or Excel file to begin.")

    st.markdown("""
    ### Required Columns

    - Order ID
    - Date
    - Product
    - Category
    - Region
    - Quantity
    - Sales

    ### Example Dataset

    | Order ID | Date | Product | Category | Region | Quantity | Sales |
    |----------|------|----------|----------|--------|----------|--------|
    | 1001 | 2025-01-01 | Laptop | Electronics | North | 2 | 80000 |
    | 1002 | 2025-01-02 | Mouse | Accessories | South | 5 | 2500 |
    """)