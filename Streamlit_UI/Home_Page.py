import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import os
import base64
import seaborn as sns
import pandas as pd


st.set_page_config(page_title="Sales Analytics", layout="wide")


df = pd.read_csv("Wallmart.csv")

df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
df.columns = df.columns.str.strip()
df["Revenue"] = df["Revenue"].replace('[\$,]', '', regex=True).astype(float)
df["Profit"] = df["Profit"].replace('[\$,]', '', regex=True).astype(float)

user_data_file = "user_data.csv"

# Create user data file if not exists
if not os.path.exists(user_data_file):
    auth_df = pd.DataFrame(columns=['Email', 'Password'])
    auth_df.to_csv(user_data_file, index=False)
else:
    auth_df = pd.read_csv(user_data_file, dtype={'Email': str, 'Password': str})

# Ensure all values are treated as strings
auth_df['Email'] = auth_df['Email'].astype(str).str.strip()
auth_df['Password'] = auth_df['Password'].astype(str).str.strip()

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Sidebar Navigation
with st.sidebar:
    if st.session_state.authenticated:
        selected = option_menu("Dashboard Sections", ["Welcome", "Sales Overview", "Customer Insights",
                        "Product Performance", "Branch Performance","Key Insights", "Dataset", "Logout"],
                               icons=["house", "bar-chart", "grid", "globe", "briefcase","key", "database", "lock"],
                               default_index=0)
    else:
        selected = option_menu("🔐 Access Panel", ["Register", "Login"],
                               icons=["person-plus", "key"], menu_icon="house",
                               default_index=0)

# 📌 **Register Page**
if selected == "Register":
    st.header("📝 Create an Account")
    reg_email = st.text_input("📧Enter Your Email").strip()
    reg_password = st.text_input("🔒Enter Your Password", type="password").strip()
    register_button = st.button("Register")

    if register_button:
        if reg_email and reg_password:
            if reg_email in auth_df['Email'].values:
                st.error("⚠️ Email Already Exists. Please Login")
            else:
                new_entry = pd.DataFrame({'Email': [reg_email], 'Password': [reg_password]})
                auth_df = pd.concat([auth_df, new_entry], ignore_index=True)
                auth_df.to_csv(user_data_file, index=False)
                st.success("✅ Registration Successful! You can now log in.")
        else:
            st.error("Please enter both email and password")

# 🔓 **Login Page**
if selected == "Login":
    st.header("🔓 Login to Dashboard")
    email = st.text_input("📧Enter Your Email").strip()
    password = st.text_input("🔒Enter Your Password", type="password").strip()
    login_button = st.button("Login")

    if login_button:
        email = str(email).strip()
        password = str(password).strip()

        user = auth_df[(auth_df['Email'] == email) & (auth_df['Password'] == password)]
        if not user.empty:
            st.session_state.authenticated = True
            st.session_state.user_id = email
            st.success("✅ Login Successful! Redirecting to Welcome Page...")
            st.rerun()  # Refresh page after login
        else:
            st.error("❌ Invalid email or password")

# 🏠 **Welcome Page After Login**
if selected == "Welcome" and st.session_state.authenticated:
    st.markdown(
        """
        <style>
        .welcome-header {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(to right, #ff6a00, #ee0979);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sub-header {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #444;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f'<h1 class="welcome-header">🎉 Welcome to 🛒 <br>'
                f'Intelligent Sales Analytics Dashboard </h1>', unsafe_allow_html=True)
    st.markdown('<h5 class="sub-header">Explore dynamic sales trends, customer behavior, and performance insights.<br>'
                'Use the sidebar to navigate and discover deep analytics through interactive visualizations.</h5>',
                unsafe_allow_html=True)

    # Info Message in a Styled Container
    # st.header("🎉 Welcome to Sales Analytics Dashboard")
    # st.subheader(f"Hello, {st.session_state.user_id} 👋")
    st.info("✅ You are now logged in and can explore the dashboard. Use the sidebar to navigate different sections of the dashboard.")

# -----------------------------------------------------------------------------------------------------------------------#

if selected == "Sales Overview":
    st.header("Overview of Walmart Sales Analytics Dashboard!")

    col1, col2, col3 = st.columns(3)
    # 🔍 **Filter: Select Region**
    with col1:
        selected_city = st.selectbox("🌍 Select City:", options=["All"] + sorted(df["City"].unique()), index=0)

    with col2:
        selected_category = st.selectbox(" Select Category", options=["All"] + sorted(df["category"].unique()), index=0)

    # 📅 **Filter to Select Date Range**
    with col3:
        min_date, max_date = df["date"].min(), df["date"].max()
        date_range = st.date_input("📅 Select Date Range:", [min_date, max_date])

    #Apply Filters to City
    filtered_df = df.copy()
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]

    #Apply Filters to Categories
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]

    # Filter to date range
    filtered_df = filtered_df[
        (filtered_df["date"] >= pd.to_datetime(date_range[0])) & (filtered_df["date"] <= pd.to_datetime(date_range[1]))]

    st.markdown("### 🧮 Key Metrics")


    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
    kpi2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.2f}")
    kpi3.metric("Average Rating", f"{filtered_df['rating'].mean():.2f} ⭐")

    with st.expander("📊 Explore Sales Overview Charts"):
        col1, col2 = st.columns(2)
        with col1:
            # 📊 **Revenue Trend Over Time**
            revenue_by_year = (filtered_df.dropna(subset=["date"]).groupby(filtered_df["date"].dt.year)["Revenue"].sum().reset_index(name="Revenue"))
            fig1 = px.line(revenue_by_year, x="date", y="Revenue", markers=True,
                            title="📊 Revenue Trends Over Time", color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig1, use_container_width=True)


        with col2:
            # 📌 **Sales Distribution by Category**
            revenue_by_category = filtered_df.groupby("category")["Revenue"].sum().reset_index()
            fig2 = px.pie(revenue_by_category, names="category", values="Revenue",
                            title="📌 Revenue Distribution by Category", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)


        # 💰 **Revenue Distribution Histogram**
        st.subheader("💰 Revenue Distribution")
        fig3 = px.histogram(filtered_df, x="Revenue", nbins=20,
                            title="📊 Revenue Distribution Across Orders",
                            color_discrete_sequence=["#0077B6"], opacity=0.8)
        fig3.update_layout(xaxis_title="Revenue ($)", yaxis_title="Frequency", template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)


# -----------------------------------------------------------------------------------------------------------------------#

if selected == "Customer Insights":
        st.title("👥Customer Behavior")
        st.write("This Section helps to analyze customer satisfaction and buying patterns using filters like city and payment method — useful for CMO of company, marketing and CX teams.")

        with st.expander("🧠 Dive into Customer Insights"):
            col1, col2 = st.columns(2)
            # 🔍 **Filter: Select Region**
            with col1:
                selected_city = st.selectbox("🌍 Select City:", options=["All"] + sorted(df["City"].unique()), index=0)

            with col2:
                selected_payment = st.selectbox("💳Select Payment", options=["All"] + sorted(df["payment_method"].unique()),
                                                 index=0)

            # Apply Filters to City
            filtered_df = df.copy()
            if selected_city != "All":
                filtered_df = filtered_df[filtered_df["City"] == selected_city]

            # Apply Filters to Categories
            if selected_payment != "All":
                filtered_df = filtered_df[filtered_df["payment_method"] == selected_payment]

            st.markdown(f"### Insights for City: `{selected_city}` | Payment Method: `{selected_payment}`")

            col1, col2 = st.columns(2)
            with col1:
                # --- Chart 4: Customer Rating Distribution ---
                fig4 = px.histogram(filtered_df, x="rating", nbins=20, color="payment_method",
                                            title="Customer Ratings Distribution (Filtered)")
                st.plotly_chart(fig4, use_container_width=True)
            with col2:
                # --- Chart 5: Revenue by Payment Method ---
                fig5 = px.pie(filtered_df, names="payment_method", values="Revenue",
                                title="Revenue Share by Payment Method")
                st.plotly_chart(fig5, use_container_width=True )

            # --- Chart 3: Area Chart of Customer Rating Distribution ---
            # filtered_df_sorted = filtered_df.sort_values(by="rating")
            # filtered_df_sorted["Index"] = range(len(filtered_df_sorted))  # x-axis
            #
            # fig6 = px.area(filtered_df_sorted,x="Index", y="rating", color="City",
            #     title="Customer Ratings Distribution (Filtered Area Chart)")
            # st.plotly_chart(fig6,use_container_width=True )

            # --- Chart 6: Average Rating by City ---
            top_15_cities = (df.groupby("City")["Revenue"].mean().sort_values(ascending=False).head(15).reset_index())

            fig6 = px.bar(top_15_cities, x="City", y="Revenue", color="City",
                             title="Top 15 Cities By Revenue",  text_auto='.2s')
            fig6.update_layout(showlegend=False)
            st.plotly_chart(fig6, use_container_width=True)


# -----------------------------------------------------------------------------------------------------------------------

if selected == "Product Performance":
    st.header("Product Performance")
    st.write("This Section Identifies which products/categories are driving sales and profit — key for inventory and pricing decisions.")

    with st.expander("📦 Product Performance Analyticss"):
        # 🔍 **Filter: Select Category**
        selected_category = st.selectbox("Select category:", options=["All"] + sorted(df["category"].unique()), index=0)

        # st.markdown(f"### Product Performance for Category `{selected_category}`")

        # --- Chart 7: Avg Profit by Category Over Time ---
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)
        profit_trend = (df.groupby([df["date"].dt.to_period("M").astype(str), "category"])["Profit"].mean().reset_index()
            .rename(columns={"date": "Month"})
        )

        fig7 = px.line(
            profit_trend[profit_trend["category"] == selected_category],
            x="Month", y="Profit", title="Avg Profit Over Time by Category",
            markers=True
        )
        st.plotly_chart(fig7, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            # --- Chart 8: Donut Chart - Profit Share by Category ---
            quantity_sold = df.groupby("category")["quantity"].sum().reset_index()

            fig8 = px.pie(quantity_sold,names="category", values="quantity", hole=0.5,
                title="Distribution of Quantity sold in Product Category")
            fig8.update_layout(showlegend=False)
            st.plotly_chart(fig8, use_container_width=True)

        # --- Chart 9: Line Chart - Average Unit Price Over Time by Category ---
        # quantity_sold = (
        #     filtered_df.groupby(["date", "category"])["quantity"]
        #     .mean()
        #     .reset_index()
        # )
        #
        # fig9 = px.line(
        #     quantity_sold,
        #     x="date", y="quantity", color="category",
        #     title="Quantity Sold Over Time in Category"
        # )
        # st.plotly_chart(fig9, use_container_width=True)

        with col2:
            # --- Chart 9: Total Revenue by Product Category ---
            revenue_by_category = (df.groupby("category")["Revenue"].sum().sort_values(ascending=False).reset_index())

            fig9 = px.bar(revenue_by_category,x="Revenue", y="category", color="category",
                                title="Total Revenue by Product Category",  text_auto='.2s' )
            fig9.update_layout(
                showlegend=False,
                xaxis_title="Total Revenue",
                yaxis_title="Product Category",
                template="plotly_white"
            )
            st.plotly_chart(fig9, use_container_width=True)

        #plot tree map
        fig10 = px.treemap(df, path=["category"], values="quantity", title="📌 Sales Breakdown by Category")
        st.plotly_chart(fig10, use_container_width=True)

#-----------------------------------------------------------------------------------------------------------------------

if selected == "Branch Performance":

    # --- Branch Search ---
    st.header("🔍 Search Branch to get Insights!!")
    branch_query = st.text_input("Enter Branch Code (e.g., WALM001, WALM067):")

    if branch_query:
        result_df = df[df["Branch"].str.contains(branch_query, case=False, na=False)]

        if not result_df.empty:
            st.markdown(f"### 🧮 Key Metrics of  `{branch_query}` :")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Revenue", f"${result_df['Revenue'].sum():,.2f}")
            kpi2.metric("Total Profit", f"${result_df['Profit'].sum():,.2f}💰")
            kpi3.metric("Total Quantity Sold", f"{result_df['quantity'].sum():,.2f}")
            kpi4.metric("Average Rating", f"{result_df['rating'].mean():.2f} ⭐")

            st.dataframe(result_df)
        else:
            st.warning(f"No data found for Branch Code: {branch_query}")

    # --- Chart 1: Average Profit per Transaction by Branch ---
    branch_profit = df.groupby("Branch")["Profit"].sum().reset_index()

    top_branches = branch_profit.sort_values(by="Profit", ascending=False).head(15)

    fig11 = px.bar(
        top_branches,
        x="Branch",
        y="Profit",
        color="Branch",
        title="Top 15 Most Profitable Branches",
        text_auto='.2s'  # shows numbers on top of bars, auto formatted
    )

    fig11.update_layout(
        xaxis_title="Branch",
        yaxis_title="Total Profit",
        showlegend=False,
    )
    st.plotly_chart(fig11, use_container_width=True)

    # 💰 **Revenue Distribution Histogram**
    st.subheader("💰 Rating Distribution over Branches")
    fig12 = px.histogram(df, x="rating", nbins=20,
                        title="📊 Rating Distribution Across Branches")
    fig12.update_layout(xaxis_title="Ratings", yaxis_title="Frequency")
    st.plotly_chart(fig12, use_container_width=True)


    # # Group by Branch and calculate total Revenue and Profit
    # branch_performance = df.groupby("Branch")[["Revenue", "Profit"]].sum().reset_index()
    #
    # # Sort by Revenue and pick top 10 branches
    # top10_branch_performance = branch_performance.sort_values(by="Revenue", ascending=False).head(10)
    #
    # # Create a vertical grouped bar chart
    # fig12 = px.bar(
    #     top10_branch_performance,
    #     x="Branch",
    #     y=["Revenue", "Profit"],
    #     barmode='group',  # Group bars side-by-side
    #     title="Top 10 Branches: Total Revenue vs Profit",
    #     labels={"value": "Amount", "variable": "Metric"},
    #     color_discrete_sequence=["#636EFA", "#EF553B"]  # Custom colors for Revenue and Profit
    # )
    #
    # # Beautify layout
    # fig12.update_layout(
    #     xaxis_title="Branch",
    #     yaxis_title="Amount (Revenue / Profit)",
    #     legend_title="Metric",
    #     template="plotly_white"
    # )
    #
    # # Display the chart
    # st.plotly_chart(fig12, use_container_width=True)

#-----------------------------------------------------------------------------------------------------------------------

if selected == "Dataset":

    # Section 6: Dataset Display
    st.header("📊 Dataset Explorer")
    st.markdown("### 🗂️ Full Dataset Viewer")

    # --- Expandable Summary ---
    with st.expander("📈 View Summary Statistics"):
        st.dataframe(df.describe())

    # --- Simple Filters ---
    st.markdown("### 🔍 Filter Dataset")
    col1, col2 = st.columns(2)

    with col1:
        filter_category = st.selectbox(
            "Filter by Category", options=["All"] + sorted(df["category"].unique())
        )
    with col2:
        filter_branch = st.selectbox(
            "Filter by Branch", options=["All"] + sorted(df["Branch"].unique())
        )

    # --- Apply Filters ---
    filtered_data = df.copy()
    if filter_category != "All":
        filtered_data = filtered_data[filtered_data["category"] == filter_category]
    if filter_branch != "All":
        filtered_data = filtered_data[filtered_data["Branch"] == filter_branch]

    # --- Display Filtered Data ---
    st.markdown(f"### 🧾 Showing {len(filtered_data)} Records")
    st.dataframe(filtered_data)


#-----------------------------------------------------------------------------------------------------------------------

if selected == "Key Insights":
    st.header("🔍 Key Business Insights")

    with st.expander("📘 Key Business Insights Summary", expanded=True):
        insights_md = """
        ### 🎯 **Key Insights**

        #### 🏙️ **City-Level Performance**
        - 🌆 **Top Performing City by Revenue**: `San Antonio`
        - 🌇 **Most Profitable City**: `San Antonio`, followed by `Harlingen` and `Haltom City`
        - 🔻 **Least Profitable City**: Cities with lower order volumes like `Bedford` and `Garland`

        #### 📦 **Product Categories**
        - 🥇 **Best-Selling Category**: `Health and beauty`
        - 💰 **Most Profitable Category**: `Electronic accessories` due to high margins
        - 📉 **Low Performance**: `Sports and travel` has fewer transactions in comparison

        #### 🧾 **Sales & Revenue Trends**
        - 📆 **Peak Sales Months**: Mid-year (May to August)
        - 📈 **Revenue spikes** observed during weekends and evenings
        - 🕐 **Most Active Hours**: Between 12:00 PM – 3:00 PM

        #### 💳 **Payment Insights**
        - 💳 **Popular Payment Method**: `Ewallet` (preferred for quick transactions)
        - 💵 **High-Spending Customers**: Often choose `Credit Card`
        - 💸 **Low-Spending Range**: More common with `Cash` payments

        #### 🤝 **Customer Behavior**
        - ⭐ **Average Customer Rating**: 7.3 / 10
        - 👍 **High Satisfaction**: Majority rated 8 or higher
        - 📊 **Ratings skew positively** across all cities and payment types

        #### 💹 **Profitability**
        - 💎 **High Profit Margin Products**: Often belong to `Home and lifestyle`
        - 🔍 **Low Margins**: Seen in bulk quantity orders, especially with `Sports and travel`
        """

        st.markdown(insights_md)

        st.download_button("📥 Download Key Insights", insights_md, file_name="Walmart_Key_Insights.md")


#-----------------------------------------------------------------------------------------------------------------------


if selected == "Logout":
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.query_params.clear()

    st.markdown("## 👋 Thank You for Visiting!")
    st.markdown("We hope you found the insights valuable and actionable.")

    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3RkdTQ4OWs3NHM1OTd2NDEyenZ2c2J0NXR4aTF4d2xseWcwZ2QxMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jUwpNzg9IcyrK/giphy.gif", width=300)

    st.success("✅ Session Completed. You're safe to log out.")

    # --- Optional Logout Confirmation Button ---
    if st.button("🔒 Logout Now"):
        st.warning("You have logged out successfully.")
        st.stop()

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



