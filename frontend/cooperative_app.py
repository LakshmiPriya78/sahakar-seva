import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SAHAKAR SEVA - Cooperative",
    page_icon="🤝",
    layout="wide"
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🤝 SAHAKAR SEVA - Cooperative Dashboard")

st.write(
    "Monitor workforce, service demand, bookings, "
    "and cooperative earnings."
)

# ---------------------------------------------------------
# LOAD DASHBOARD DATA
# ---------------------------------------------------------

try:

    response = requests.get(
        f"{API_URL}/cooperative/dashboard"
    )

    response.raise_for_status()

    result = response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not connect to the backend: {e}"
    )

    st.stop()


if not result.get("success"):

    st.error(
        result.get(
            "message",
            "Unable to load cooperative dashboard."
        )
    )

    st.stop()


dashboard = result["dashboard"]

# ---------------------------------------------------------
# KEY METRICS
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 📊 Platform Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "👷 Total Workers",
        dashboard["total_workers"]
    )

with col2:

    st.metric(
        "🟢 Active Workers",
        dashboard["active_workers"]
    )

with col3:

    st.metric(
        "📋 Total Bookings",
        dashboard["total_bookings"]
    )

with col4:

    st.metric(
        "✅ Completed Jobs",
        dashboard["completed_bookings"]
    )
# ---------------------------------------------------------
# OPERATIONAL METRICS
# ---------------------------------------------------------

# ---------------------------------------------------------
# WORKER VERIFICATION
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 👷 Worker Verification")

st.info(
    "Review newly registered workers and verify their skills "
    "before they become active on the cooperative platform."
)

try:

    pending_response = requests.get(
        f"{API_URL}/cooperative/workers/pending"
    )

    pending_response.raise_for_status()

    pending_result = pending_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load pending workers: {e}"
    )

    pending_result = None


if pending_result and pending_result.get("success"):

    pending_workers = pending_result.get(
        "pending_workers",
        []
    )

    if not pending_workers:

        st.success(
            "✅ No workers are currently waiting for verification."
        )

    else:

        st.warning(
            f"⚠️ {len(pending_workers)} worker(s) "
            "waiting for verification."
        )

        for worker in pending_workers:

            with st.container():

                st.markdown(
                    f"### 👷 {worker['name']}"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Service:** "
                        f"{worker['service']}"
                    )

                    st.write(
                        f"**Skills:** "
                        f"{worker['skills']}"
                    )

                with col2:

                    st.write(
                        f"**Location:** "
                        f"{worker['location']}"
                    )

                    st.write(
                        "**Rating:** Not yet rated"
                    )

                with col3:

                    st.write(
                        "**Reliability:** "
                        "Not yet available"
                    )

                    st.write(
                        f"**Status:** "
                        f"{worker['verification_status']}"
                    )

                approve_col, reject_col = st.columns(2)

                # -------------------------------------------------
                # APPROVE WORKER
                # -------------------------------------------------

                with approve_col:

                    if st.button(
                        "✅ Approve Worker",
                        key=f"approve_worker_{worker['worker_id']}"
                    ):

                        try:

                            approve_response = requests.post(
                                f"{API_URL}/cooperative/workers/"
                                f"{worker['worker_id']}/approve"
                            )

                            approve_response.raise_for_status()

                            approve_result = (
                                approve_response.json()
                            )

                            if approve_result.get("success"):

                                st.success(
                                    f"✅ {worker['name']} "
                                    "approved successfully."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    approve_result.get(
                                        "message",
                                        "Worker approval failed."
                                    )
                                )

                        except requests.exceptions.RequestException as e:

                            st.error(
                                f"Worker approval failed: {e}"
                            )

                # -------------------------------------------------
                # REJECT WORKER
                # -------------------------------------------------

                with reject_col:

                    if st.button(
                        "❌ Reject Worker",
                        key=f"reject_worker_{worker['worker_id']}"
                    ):

                        try:

                            reject_response = requests.post(
                                f"{API_URL}/cooperative/workers/"
                                f"{worker['worker_id']}/reject"
                            )

                            reject_response.raise_for_status()

                            reject_result = (
                                reject_response.json()
                            )

                            if reject_result.get("success"):

                                st.warning(
                                    f"❌ {worker['name']} "
                                    "rejected."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    reject_result.get(
                                        "message",
                                        "Worker rejection failed."
                                    )
                                )

                        except requests.exceptions.RequestException as e:

                            st.error(
                                f"Worker rejection failed: {e}"
                            )

                st.markdown("---")

else:

    st.info(
        "Worker verification information is currently unavailable."
    )


st.markdown("---")

st.markdown("## ⚙️ Operations")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "🔧 Active Jobs",
        dashboard["active_bookings"]
    )

with col2:

    st.metric(
        "📥 New Requests",
        dashboard["requested_bookings"]
    )

with col3:

    st.metric(
        "💰 Worker Earnings",
        f"₹{dashboard['total_worker_earnings']:.2f}"
    )

with col4:

    completion_rate = 0

    if dashboard["total_bookings"] > 0:

        completion_rate = (
            dashboard["completed_bookings"]
            / dashboard["total_bookings"]
        ) * 100

    st.metric(
        "📈 Completion Rate",
        f"{completion_rate:.1f}%"
    )

# ---------------------------------------------------------
# SERVICE DEMAND
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 📊 Service Demand")

service_demand = dashboard.get(
    "service_demand",
    {}
)

if not service_demand:

    st.info(
        "No service demand data available yet."
    )

else:

    for service, count in service_demand.items():

        st.write(
            f"**{service}** — {count} booking(s)"
        )

        st.progress(
            min(
                count / max(service_demand.values()),
                1.0
            )
        )

# ---------------------------------------------------------
# COOPERATIVE INTELLIGENCE
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 🤖 AI Workforce Intelligence")

st.info(
    "AI analyzes workforce capacity and service demand "
    "to identify potential workforce gaps and recommend "
    "actions for the cooperative."
)

try:

    intelligence_response = requests.get(
        f"{API_URL}/cooperative/workforce-intelligence"
    )

    intelligence_response.raise_for_status()

    intelligence_result = intelligence_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load workforce intelligence: {e}"
    )

    st.stop()


if not intelligence_result.get("success"):

    st.error(
        intelligence_result.get(
            "message",
            "Unable to load workforce intelligence."
        )
    )

    st.stop()


intelligence_data = intelligence_result.get(
    "intelligence",
    []
)
# ---------------------------------------------------------
# AI PRIORITY SUMMARY
# ---------------------------------------------------------

if intelligence_data:

    high_priority_services = [
        item for item in intelligence_data
        if item["priority_level"] == "High Priority"
    ]

    medium_priority_services = [
        item for item in intelligence_data
        if item["priority_level"] == "Medium Priority"
    ]

    st.markdown("---")

    st.markdown("## 🎯 AI Priority Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🔴 High Priority",
            len(high_priority_services)
        )

    with col2:

        st.metric(
            "🟡 Medium Priority",
            len(medium_priority_services)
        )

    with col3:

        st.metric(
            "🔧 Services Monitored",
            len(intelligence_data)
        )

    if high_priority_services:

        st.error(
            "⚠️ Immediate Attention Required"
        )

        for item in high_priority_services:

            st.write(
                f"**{item['service']}** — "
                f"{item['recommendation']}"
            )

            st.write(
                f"🎯 **Action:** "
                f"{item['recommended_action']}"
            )

    elif medium_priority_services:

        st.warning(
            "🟡 Some services require monitoring."
        )

    else:

        st.success(
            "🟢 No services currently require immediate attention."
        )
# ---------------------------------------------------------
# WORKFORCE ACTION SIMULATOR
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 🧪 Workforce Action Simulator")

st.write(
    "Simulate how adding workers could affect "
    "service capacity and workforce pressure."
)

simulation_service = st.selectbox(
    "Select a service",
    [
        item["service"]
        for item in intelligence_data
    ]
)

selected_item = next(
    item for item in intelligence_data
    if item["service"] == simulation_service
)

additional_workers = st.number_input(
    "Additional workers to onboard",
    min_value=0,
    max_value=20,
    value=1,
    step=1
)

current_workers = selected_item["total_workers"]
active_bookings = selected_item["active_bookings"]

simulated_workers = (
    current_workers + additional_workers
)

if simulated_workers > 0:

    simulated_capacity_load = (
        active_bookings / simulated_workers
    ) * 100

else:

    simulated_capacity_load = 100


st.markdown("### 📊 Simulation Result")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Current Workers",
        current_workers
    )

with col2:

    st.metric(
        "Simulated Workers",
        simulated_workers
    )

with col3:

    st.metric(
        "Simulated Capacity Load",
        f"{simulated_capacity_load:.1f}%"
    )

st.progress(
    min(simulated_capacity_load / 100, 1.0)
)

if simulated_capacity_load >= 100:

    st.error(
        "🔴 Workforce may still be operating at full capacity."
    )

elif simulated_capacity_load >= 70:

    st.warning(
        "🟡 Workforce pressure remains high. "
        "Consider additional capacity."
    )

else:

    st.success(
        "🟢 Simulated workforce capacity appears adequate."
    )
if not intelligence_data:

    st.info(
        "No workforce intelligence data available yet."
    )

else:

    for item in intelligence_data:

        st.markdown(
            f"### 🔧 {item['service']}"
        )

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:

            st.metric(
                "👷 Total Workers",
                item["total_workers"]
            )

        with col2:

            st.metric(
                "🟢 Available Workers",
                item["available_workers"]
            )

        with col3:

            st.metric(
                "📋 Total Bookings",
                item["total_bookings"]
            )

        with col4:

            st.metric(
                "⚙️ Active Bookings",
                item["active_bookings"]
            )
        with col5:

            st.metric(
               "📊 Demand / Worker",
               f"{item['demand_per_worker']:.1f}"
         )
        with col6:

           st.metric(
             "🎯 Priority",
              item["priority_level"]
            )
        if item["priority_level"] == "High Priority":

         st.error(
           f"🔴 Priority: {item['priority_level']}"
        )

        elif item["priority_level"] == "Medium Priority":

          st.warning(
           f"🟡 Priority: {item['priority_level']}"
        )

        else:

          st.success(
          f"🟢 Priority: {item['priority_level']}"
        )
        # -------------------------------------------------
        # CAPACITY LOAD
        # -------------------------------------------------

        capacity_load = item["capacity_load"]

        st.write(
            f"**📊 Workforce Capacity Load: "
            f"{capacity_load:.1f}%**"
        )

        st.progress(
            min(capacity_load / 100, 1.0)
        )
        st.write(
          f"**📈 Demand Status:** "
          f"{item['demand_status']}"
       )
        # -------------------------------------------------
        # WORKFORCE STATUS
        # -------------------------------------------------

        if item["workforce_status"] == "Critical Gap":

            st.error(
                f"🔴 Status: {item['workforce_status']}"
            )

        elif item["workforce_status"] == "Workforce Gap":

            st.warning(
                f"🟠 Status: {item['workforce_status']}"
            )

        elif item["workforce_status"] == "High Utilization":

            st.warning(
                f"🟡 Status: {item['workforce_status']}"
            )

        else:

            st.success(
                f"🟢 Status: {item['workforce_status']}"
            )

        # -------------------------------------------------
        # RECOMMENDATION
        # -------------------------------------------------

        st.write(
            f"**🤖 Recommendation:** "
            f"{item['recommendation']}"
        )

        st.write(
            f"**🎯 Recommended Action:** "
            f"{item['recommended_action']}"
        )

        st.markdown("---")
        # AI DEMAND FORECAST
st.markdown("---")
st.markdown("## 🔮 AI Demand Forecast")

st.info(
    "Baseline forecasting uses historical booking volume "
    "to estimate the next service-demand period and "
    "recommend workforce preparation."
)

try:
    forecast_response = requests.get(
        f"{API_URL}/cooperative/demand-forecast"
    )
    forecast_response.raise_for_status()
    forecast_result = forecast_response.json()
except requests.exceptions.RequestException as e:
    st.error(
        f"Could not load demand forecast: {e}"
    )
    st.stop()

if not forecast_result.get("success"):
    st.error(
        forecast_result.get(
            "message",
            "Unable to load demand forecast."
        )
    )
    st.stop()

forecast_data = forecast_result.get(
    "forecast",
    []
)

if not forecast_data:
    st.info(
        "No demand forecast data available yet."
    )
else:
    for item in forecast_data:

        st.markdown(
            f"### 🔧 {item['service']}"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📋 Historical Bookings",
                item["historical_bookings"]
            )

        with col2:
            st.metric(
                "👷 Available Workers",
                item["available_workers"]
            )

        with col3:
            st.metric(
                "⚙️ Capacity Load",
                f"{item['capacity_load']:.1f}%"
            )

        with col4:
            st.metric(
                "🔮 Estimated Next Demand",
                item["estimated_next_period_demand"]
            )

        st.write(
            f"**📊 Demand / Worker:** "
            f"{item['demand_per_worker']:.1f}"
        )

        if item["forecast_status"] == "High Demand":
            st.error(
                f"🔴 Forecast: "
                f"{item['forecast_status']}"
            )

        elif item["forecast_status"] == "Moderate Demand":
            st.warning(
                f"🟡 Forecast: "
                f"{item['forecast_status']}"
            )

        else:
            st.success(
                f"🟢 Forecast: "
                f"{item['forecast_status']}"
            )

        st.write(
            f"**🤖 Workforce Recommendation:** "
            f"{item['workforce_recommendation']}"
        )

        st.markdown("---")
# ---------------------------------------------------------
# WORKER WELFARE & INSURANCE
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 🛡️ Worker Welfare & Insurance")

st.info(
    "Monitor worker insurance enrollment and welfare coverage "
    "across the cooperative workforce."
)

try:

    welfare_response = requests.get(
        f"{API_URL}/cooperative/workers/welfare"
    )

    welfare_response.raise_for_status()

    welfare_result = welfare_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load worker welfare information: {e}"
    )

    welfare_result = None


if welfare_result and welfare_result.get("success"):

    welfare_workers = welfare_result.get(
        "workers",
        []
    )

    total_welfare_workers = len(welfare_workers)

    insured_workers = [
        worker
        for worker in welfare_workers
        if worker["insurance_enrolled"]
    ]

    uninsured_workers = [
        worker
        for worker in welfare_workers
        if not worker["insurance_enrolled"]
    ]

    st.markdown("### 📊 Welfare Overview")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👷 Total Workers",
            total_welfare_workers
        )

    with col2:

        st.metric(
            "🛡️ Insured Workers",
            len(insured_workers)
        )

    with col3:

        st.metric(
            "⚠️ Need Welfare Support",
            len(uninsured_workers)
        )

    st.markdown("### 👥 Worker Welfare Status")

    for worker in welfare_workers:

        if worker["insurance_enrolled"]:

            st.success(
                f"✅ **{worker['worker_name']}** — "
                f"Insurance Enrolled"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"**Provider:** "
                    f"{worker['insurance_provider'] or 'N/A'}"
                )

            with col2:

                st.write(
                    f"**Coverage:** "
                    f"₹{worker['coverage_amount']:,.0f}"
                )

            with col3:

                st.write(
                    f"**Status:** "
                    f"{worker['welfare_status'].replace('_', ' ').title()}"
                )

        else:

            st.warning(
                f"⚠️ **{worker['worker_name']}** — "
                f"Insurance Not Enrolled"
            )

    st.markdown("---")

else:

    st.info(
        "No worker welfare information available yet."
    )
# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "SAHAKAR SEVA — Trusted local services. "
    "Fair opportunities. Stronger cooperatives."
)