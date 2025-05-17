import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Analytics | DominionMailer",
    page_icon="📊",
    layout="wide"
)

# Check if database is initialized
if "db" not in st.session_state:
    st.error("Database not initialized. Please restart the application.")
    st.stop()

db = st.session_state.db

# Header
st.title("📊 Email Campaign Analytics")

# Get all campaigns
campaigns = db.get_campaigns()

# If we have campaigns, show analytics
if campaigns and len(campaigns) > 0:
    # Convert campaign list to DataFrame for easier manipulation
    campaigns_df = pd.DataFrame([dict(c) for c in campaigns])
    
    # Campaign selector
    st.subheader("Select Campaign")
    
    # Format options for selectbox
    campaign_options = [(c['id'], c['name']) for c in campaigns]
    
    selected_campaign_id = st.selectbox(
        "Choose a campaign to analyze:",
        options=[c[0] for c in campaign_options],
        format_func=lambda x: next((c[1] for c in campaign_options if c[0] == x), ""),
        key="analytics_campaign_select"
    )
    
    # Get selected campaign details
    selected_campaign = db.get_campaign_by_id(selected_campaign_id)
    
    if selected_campaign:
        st.header(f"Campaign: {selected_campaign['name']}")
        
        # Campaign stats
        stats = db.get_campaign_stats(selected_campaign_id)
        
        if stats:
            # Convert to Python dict if it's a sqlite Row
            stats_dict = dict(stats)
            
            # Calculate derived metrics
            total_sent = stats_dict.get('total_sent', 0) or 0
            delivered = stats_dict.get('delivered', 0) or 0
            failed = stats_dict.get('failed', 0) or 0
            opened = stats_dict.get('opened', 0) or 0
            clicked = stats_dict.get('clicked', 0) or 0
            
            # Calculate rates
            delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
            open_rate = (opened / delivered * 100) if delivered > 0 else 0
            click_rate = (clicked / opened * 100) if opened > 0 else 0
            click_to_open_rate = (clicked / opened * 100) if opened > 0 else 0
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Sent", total_sent)
                st.metric("Delivery Rate", f"{delivery_rate:.1f}%")
            
            with col2:
                st.metric("Delivered", delivered)
                st.metric("Failed", failed)
            
            with col3:
                st.metric("Opened", opened)
                st.metric("Open Rate", f"{open_rate:.1f}%")
            
            with col4:
                st.metric("Clicked", clicked)
                st.metric("Click Rate", f"{click_rate:.1f}%")
            
            # Create visualizations
            st.subheader("Campaign Performance")
            
            # Funnel chart
            funnel_data = [
                {"stage": "Sent", "count": total_sent},
                {"stage": "Delivered", "count": delivered},
                {"stage": "Opened", "count": opened},
                {"stage": "Clicked", "count": clicked}
            ]
            
            funnel_df = pd.DataFrame(funnel_data)
            
            fig_funnel = px.funnel(
                funnel_df, 
                x='count', 
                y='stage',
                title="Email Campaign Funnel"
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Get tracking details for this campaign
            tracking_data = db.get_email_tracking_by_campaign(selected_campaign_id)
            
            if tracking_data and len(tracking_data) > 0:
                # Convert to DataFrame for analysis
                tracking_df = pd.DataFrame([dict(t) for t in tracking_data])
                
                # Convert timestamp columns to datetime
                for col in ['sent_at', 'opened_at', 'clicked_at']:
                    if col in tracking_df.columns:
                        tracking_df[col] = pd.to_datetime(tracking_df[col])
                
                # Analytics by domain
                if 'domain' in tracking_df.columns:
                    st.subheader("Performance by Domain")
                    
                    # Group by domain and calculate counts
                    domain_stats = tracking_df.groupby('domain').agg({
                        'id': 'count',
                        'opened': 'sum',
                        'clicked': 'sum'
                    }).reset_index()
                    
                    domain_stats.columns = ['Domain', 'Sent', 'Opens', 'Clicks']
                    
                    # Calculate rates
                    domain_stats['Open Rate'] = domain_stats['Opens'] / domain_stats['Sent'] * 100
                    domain_stats['Click Rate'] = domain_stats['Clicks'] / domain_stats['Sent'] * 100
                    
                    # Sort by sent count
                    domain_stats = domain_stats.sort_values('Sent', ascending=False)
                    
                    # Display top domains
                    st.dataframe(domain_stats.head(10), hide_index=True)
                    
                    # Bar chart for open rates by domain
                    fig_domain = px.bar(
                        domain_stats.head(10),
                        x='Domain',
                        y='Open Rate',
                        title="Open Rates by Domain",
                        text_auto='.1f',
                        color='Open Rate',
                        color_continuous_scale='Viridis'
                    )
                    
                    fig_domain.update_traces(texttemplate='%{text}%', textposition='outside')
                    fig_domain.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                    
                    st.plotly_chart(fig_domain, use_container_width=True)
                
                # Detailed tracking data
                st.subheader("Detailed Email Tracking")
                
                # Add filters
                st.markdown("#### Filter Tracking Data")
                
                # Status filter
                status_options = ['All'] + sorted(tracking_df['status'].unique().tolist())
                selected_status = st.selectbox("Filter by Status", status_options)
                
                # Activity filter
                activity_filter = st.radio(
                    "Filter by Activity",
                    ["All", "Opened", "Not Opened", "Clicked", "Not Clicked"],
                    horizontal=True
                )
                
                # Apply filters
                filtered_df = tracking_df.copy()
                
                if selected_status != 'All':
                    filtered_df = filtered_df[filtered_df['status'] == selected_status]
                
                if activity_filter == "Opened":
                    filtered_df = filtered_df[filtered_df['opened'] == 1]
                elif activity_filter == "Not Opened":
                    filtered_df = filtered_df[filtered_df['opened'] == 0]
                elif activity_filter == "Clicked":
                    filtered_df = filtered_df[filtered_df['clicked'] == 1]
                elif activity_filter == "Not Clicked":
                    filtered_df = filtered_df[filtered_df['clicked'] == 0]
                
                # Show filtered data
                if len(filtered_df) > 0:
                    # Select columns to display
                    display_cols = ['email', 'name', 'sent_at', 'status', 'opened', 'opened_at', 'clicked', 'clicked_at']
                    display_cols = [col for col in display_cols if col in filtered_df.columns]
                    
                    st.dataframe(
                        filtered_df[display_cols],
                        hide_index=True
                    )
                    
                    # Export option
                    csv = filtered_df[display_cols].to_csv(index=False)
                    st.download_button(
                        label="Export Filtered Data to CSV",
                        data=csv,
                        file_name=f"{selected_campaign['name']}_tracking.csv",
                        mime="text/csv"
                    )
                else:
                    st.write("No data matches the selected filters.")
            else:
                st.info("No detailed tracking data available for this campaign.")
        else:
            st.info("No analytics data available for this campaign. This could be because the campaign hasn't been sent yet.")
    else:
        st.error("Selected campaign not found. Please select another campaign.")

    # Campaign comparison
    st.header("Campaign Comparison")
    
    # Get aggregate stats for all campaigns
    all_stats = db.get_all_campaign_stats()
    
    if all_stats and len(all_stats) > 0:
        # Convert to DataFrame for visualization
        stats_df = pd.DataFrame([dict(s) for s in all_stats])
        
        # Calculate rates
        stats_df['delivery_rate'] = stats_df['delivered'] / stats_df['total_sent'] * 100
        stats_df['open_rate'] = stats_df['opened'] / stats_df['delivered'] * 100
        stats_df['click_rate'] = stats_df['clicked'] / stats_df['opened'] * 100
        
        # Replace NaN values
        stats_df = stats_df.fillna(0)
        
        # Bar chart comparing open rates
        fig_comparison = px.bar(
            stats_df,
            x='name',
            y='open_rate',
            title="Open Rate Comparison Across Campaigns",
            labels={'name': 'Campaign', 'open_rate': 'Open Rate (%)'},
            text_auto='.1f',
            color='open_rate',
            color_continuous_scale='Viridis'
        )
        
        fig_comparison.update_traces(texttemplate='%{text}%', textposition='outside')
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Radar chart for campaign comparison
        selected_campaigns = st.multiselect(
            "Select campaigns to compare:",
            options=stats_df['name'].tolist(),
            default=stats_df['name'].head(3).tolist() if len(stats_df) >= 3 else stats_df['name'].tolist()
        )
        
        if selected_campaigns:
            # Filter data for selected campaigns
            comparison_df = stats_df[stats_df['name'].isin(selected_campaigns)]
            
            # Create radar chart
            categories = ['delivery_rate', 'open_rate', 'click_rate']
            
            fig_radar = go.Figure()
            
            for _, campaign in comparison_df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[campaign['delivery_rate'], campaign['open_rate'], campaign['click_rate']],
                    theta=['Delivery Rate', 'Open Rate', 'Click Rate'],
                    fill='toself',
                    name=campaign['name']
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Campaign Performance Comparison"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("No comparison data available. This could be because no campaigns have been sent yet.")

else:
    # No campaigns found
    st.info("No campaigns found. Create your first campaign from the **Campaigns** page.")
    
    if st.button("Go to Campaigns"):
        st.switch_page("pages/1_Campaigns.py")

# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *Design like a creator. Deliver like a machine.*")
