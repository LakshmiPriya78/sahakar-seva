import streamlit as st
import requests

import os

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000"
)


# ---------------------------------------------------------
# CACHED API FUNCTIONS
# ---------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def get_workers():
    response = requests.get(
        f"{API_URL}/workers",
        timeout=3
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def get_worker_profile(worker_id):
    response = requests.get(
        f"{API_URL}/workers/{worker_id}/profile",
        timeout=3
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def get_worker_welfare(worker_id):
    try:
        response = requests.get(
            f"{API_URL}/workers/{worker_id}/welfare",
            timeout=3
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


st.set_page_config(
    page_title="SAHAKAR SEVA - Worker",
    page_icon="👷",
    layout="wide"
)
# ---------------------------------------------------------
# WORKER SELECTION
# ---------------------------------------------------------

try:
    workers_response = requests.get(
        f"{API_URL}/workers"
    )
    workers_response.raise_for_status()
    workers_result = workers_response.json()

except requests.exceptions.RequestException as e:
    st.error(f"Could not load workers: {e}")
    st.stop()


workers = workers_result

if not workers:
    st.error("No workers available.")
    st.stop()

worker_options = {
    worker["name"]: worker["id"]
    for worker in workers
}


st.sidebar.markdown("## 👷 Worker Login")

selected_worker_name = st.sidebar.selectbox(
    "Select worker",
    list(worker_options.keys())
)
WORKER_ID = worker_options[selected_worker_name]
WORKER_NAME = selected_worker_name


if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("👷 SAHAKAR SEVA - Worker Dashboard")

st.subheader(
    f"Welcome, {WORKER_NAME}"
)

st.write(
    "Manage your service requests, accept jobs, "
    "and track your earnings."
)


# ---------------------------------------------------------
# WORKER PROFILE
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 👤 My Profile")


try:

    profile_response = requests.get(
        f"{API_URL}/workers/{WORKER_ID}/profile"
    )

    profile_response.raise_for_status()

    profile_result = profile_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load worker profile: {e}"
    )

    st.stop()


if not profile_result.get("success"):

    st.error(
        profile_result.get(
            "message",
            "Unable to load worker profile."
        )
    )

    st.stop()


worker = profile_result["worker"]


profile_col1, profile_col2 = st.columns(2)


with profile_col1:

    st.markdown(
        f"### 👷 {worker['name']}"
    )

    st.write(
        f"🛠️ **Service:** "
        f"{worker['service']}"
    )

    st.write(
        f"🔧 **Skills:** "
        f"{worker['skills']}"
    )

    st.write(
        f"📍 **Location:** "
        f"{worker['location']}"
    )

    st.write(
        f"⭐ **Rating:** "
        f"{worker['rating']}/5"
    )


with profile_col2:

    st.metric(
        "🛡️ Reliability",
        f"{worker['reliability_score']:.0f}%"
    )

    st.metric(
        "✅ Completed Jobs",
        worker["completed_jobs"]
    )

    if worker["verification_status"] == "verified":

        st.success(
            "✔️ Worker Verified"
        )

    else:

        st.warning(
            "⚠️ Verification Pending"
        )


# ---------------------------------------------------------
# AVAILABILITY
# ---------------------------------------------------------

st.markdown("### 🟢 Work Availability")

current_availability = worker["availability"]


new_availability = st.toggle(
    "Available for new jobs",
    value=current_availability
)


if new_availability != current_availability:

    try:

        availability_response = requests.put(
            f"{API_URL}/workers/"
            f"{WORKER_ID}/availability",
            json={
                "availability": new_availability
            }
        )

        availability_response.raise_for_status()

        availability_result = (
            availability_response.json()
        )

    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not update availability: {e}"
        )

        st.stop()


    if availability_result.get("success"):

        if new_availability:

            st.success(
                "🟢 You are now available for new jobs."
            )

        else:

            st.warning(
                "🔴 You are now unavailable for new jobs."
            )

        st.rerun()

    else:

        st.error(
            availability_result.get(
                "message",
                "Unable to update availability."
            )
        )


# ---------------------------------------------------------
# LOAD BOOKINGS
# ---------------------------------------------------------

try:

    response = requests.get(
        f"{API_URL}/bookings/worker/{WORKER_ID}"
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
            "Unable to load bookings."
        )
    )

    st.stop()


bookings = result.get(
    "bookings",
    []
)

# ---------------------------------------------------------
# WORKER EARNINGS
# ---------------------------------------------------------

try:

    earnings_response = requests.get(
        f"{API_URL}/workers/{WORKER_ID}/earnings"
    )

    earnings_response.raise_for_status()

    earnings_result = earnings_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load worker earnings: {e}"
    )

    st.stop()


if not earnings_result.get("success"):

    st.error(
        earnings_result.get(
            "message",
            "Unable to load worker earnings."
        )
    )

    st.stop()


earnings = earnings_result


# ---------------------------------------------------------
# EARNINGS
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 💰 My Earnings")

earnings_col1, earnings_col2 = st.columns(2)

with earnings_col1:

    st.metric(
        "✅ Completed Jobs",
        earnings["completed_jobs"]
    )

with earnings_col2:

    st.subheader("💰 Earnings")

earnings_response = requests.get(
    f"{API_URL}/workers/{WORKER_ID}/earnings"
)

if earnings_response.status_code == 200:

    earnings_data = earnings_response.json()

    if earnings_data.get("success"):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Earnings",
                f"₹{earnings_data['total_earnings']:.2f}"
            )

        with col2:
            st.metric(
                "Completed Jobs",
                earnings_data["completed_jobs"]
            )

        with col3:
            st.metric(
                "Paid Jobs",
                earnings_data["paid_jobs"]
            )

    else:
        st.warning("Unable to load earnings.")

else:
    st.error("Could not connect to the earnings API.")
# ---------------------------------------------------------
# EARNINGS HISTORY
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 📜 Earnings History")

try:

    breakdown_response = requests.get(
        f"{API_URL}/workers/{WORKER_ID}/earnings/breakdown"
    )

    breakdown_response.raise_for_status()

    breakdown_result = breakdown_response.json()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load earnings history: {e}"
    )

    st.stop()


if not breakdown_result.get("success"):

    st.error(
        breakdown_result.get(
            "message",
            "Unable to load earnings history."
        )
    )

    st.stop()


earnings_history = breakdown_result.get(
    "breakdown",
    []
)


if not earnings_history:

    st.info(
        "No completed jobs available in earnings history."
    )

else:

    for earning in earnings_history:

        st.markdown(
            f"### 🔧 Booking #{earning['booking_id']}"
        )

        history_col1, history_col2 = st.columns(2)

        with history_col1:

            st.write(
                f"**Service:** "
                f"{earning['service']}"
            )

            st.write(
                f"**📍 Location:** "
                f"{earning['location']}"
            )

            st.write(
                f"**⏰ Scheduled:** "
                f"{earning['scheduled_time']}"
            )

            if earning["customer_payment"] is not None:

                st.write(
                    f"**💳 Customer Payment:** "
                    f"₹{earning['customer_payment']:.2f}"
                )

            else:

                st.write(
                    "**💳 Customer Payment:** "
                    "Not generated"
                )

        with history_col2:

            if earning["worker_amount"] is not None:

                st.metric(
                    "💰 Your Earnings",
                    f"₹{earning['worker_amount']:.2f}"
                )

            else:

                st.metric(
                    "💰 Your Earnings",
                    "Not generated"
                )

            if earning["payment_status"] == "pending":

                st.warning(
                    "⏳ Payment Pending"
                )

            elif earning["payment_status"] == "paid":

                st.success(
                    "✅ Payment Paid"
                )

            elif earning["payment_status"] == "not_generated":

                st.info(
                    "ℹ️ Payment Not Generated"
                )

            else:

                st.info(
                    f"Payment Status: "
                    f"{earning['payment_status'].upper()}"
                )

        st.success(
            f"✅ {earning['status'].capitalize()}"
        )

        st.markdown("---")
# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

requested_bookings = [
    booking
    for booking in bookings
    if booking["status"] == "requested"
]

active_statuses = [
    "accepted",
    "on_the_way",
    "arrived",
    "in_progress"
]

active_bookings = [
    booking
    for booking in bookings
    if booking["status"] in active_statuses
]

completed_bookings = [
    booking
    for booking in bookings
    if booking["status"] == "completed"
]


st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "📥 New Requests",
        len(requested_bookings)
    )

with col2:

    st.metric(
    "🔧 Active Jobs",
    len(active_bookings)
)

with col3:

    st.metric(
        "✅ Completed Jobs",
        len(completed_bookings)
    )
st.subheader("🛡️ Welfare & Insurance")

welfare_data = get_worker_welfare(WORKER_ID)

if welfare_data and welfare_data.get("success"):
    welfare = welfare_data["welfare"]

    if welfare.get("insurance_enrolled"):
        st.success("✅ Insurance Enrolled")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Provider:** {welfare.get('insurance_provider', 'N/A')}"
            )
            st.write(
                f"**Policy Number:** {welfare.get('policy_number', 'N/A')}"
            )

        with col2:
            st.write(
                f"**Coverage:** ₹{welfare.get('coverage_amount', 0):,.0f}"
            )
            st.write(
                f"**Status:** {welfare.get('welfare_status', 'N/A').title()}"
            )

        st.write(
            f"**Valid From:** {welfare.get('policy_start_date', 'N/A')}"
        )
        st.write(
            f"**Valid Until:** {welfare.get('policy_end_date', 'N/A')}"
        )

    else:
        st.warning("⚠️ Insurance not enrolled")

else:
    st.info("ℹ️ Welfare information is not available yet.")

# ---------------------------------------------------------
# NEW JOB REQUESTS
# ---------------------------------------------------------

st.markdown("---")

st.markdown("## 📥 New Job Requests")

try:
    request_response = requests.get(
        f"{API_URL}/workers/{WORKER_ID}/requests"
    )
    request_response.raise_for_status()
    request_result = request_response.json()

except requests.exceptions.RequestException as e:
    st.error(f"Could not load job requests: {e}")
    request_result = {
        "success": False,
        "requests": []
    }

if not request_result.get("success"):
    st.error(
        request_result.get(
            "message",
            "Unable to load job requests."
        )
    )

else:
    job_requests = request_result.get("requests", [])

    if not job_requests:
        st.info("No new job requests at the moment.")

    else:
        st.success(
            f"You have {len(job_requests)} new job request(s)."
        )

        for request in job_requests:

            if request.get("is_emergency", False):
                st.error("🚨 EMERGENCY REQUEST")

                st.markdown(
                  f"### 📋 Booking #{request['booking_id']}"
                )

            request_col1, request_col2 = st.columns([2, 1])

            with request_col1:
                st.write(
                    f"👤 **Customer:** "
                    f"{request['customer_name']}"
                )
                st.write(
                    f"🛠️ **Service:** "
                    f"{request['service']}"
                )
                st.write(
                    f"📍 **Location:** "
                    f"{request['location']}"
                )
                st.write(
                    f"⏰ **Scheduled:** "
                    f"{request['scheduled_time']}"
                )
                st.write(
                    f"💰 **Estimated Price:** "
                    f"₹{request['estimated_price']}"
                )
                st.write(
                    f"📌 **Status:** "
                    f"{request['status']}"
                )

            with request_col2:
                st.markdown("#### Respond")

                if st.button(
                    "✅ Accept",
                    key=f"accept_{request['booking_id']}",
                    use_container_width=True
                ):
                    try:
                        response = requests.put(
                            f"{API_URL}/bookings/"
                            f"{request['booking_id']}/respond",
                            json={
                                "response": "accepted"
                            }
                        )
                        response.raise_for_status()
                        result = response.json()

                    except requests.exceptions.RequestException as e:
                        st.error(
                            f"Could not respond to booking: {e}"
                        )
                        st.stop()

                    if result.get("success"):
                        st.success(
                            "Booking accepted successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            result.get(
                                "message",
                                "Unable to accept booking."
                            )
                        )

                if st.button(
                    "❌ Reject",
                    key=f"reject_{request['booking_id']}",
                    use_container_width=True
                ):
                    try:
                        response = requests.put(
                            f"{API_URL}/bookings/"
                            f"{request['booking_id']}/respond",
                            json={
                                "response": "rejected"
                            }
                        )
                        response.raise_for_status()
                        result = response.json()

                    except requests.exceptions.RequestException as e:
                        st.error(
                            f"Could not respond to booking: {e}"
                        )
                        st.stop()

                    if result.get("success"):
                        st.success(
                            "Booking rejected successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            result.get(
                                "message",
                                "Unable to reject booking."
                            )
                        )

            st.markdown("---")

# ---------------------------------------------------------
# ACTIVE JOBS
# ---------------------------------------------------------

st.markdown(
    "## 🔧 Active Jobs"
)

if not active_bookings:

    st.info(
        "No active jobs."
    )

else:

    for booking in active_bookings:

        st.markdown(
            f"### 📋 Booking #{booking['id']}"
        )

        job_col1, job_col2 = st.columns(
            [3, 1]
        )

        # -------------------------------------------------
        # BASIC JOB INFORMATION
        # -------------------------------------------------

        with job_col1:

            st.write(
                f"🛠️ **Service:** "
                f"{booking['service']}"
            )

            st.write(
                f"📍 **Location:** "
                f"{booking['location']}"
            )

            st.write(
                f"📌 **Status:** "
                f"{booking['status']}"
            )

            st.write(
                f"💰 **Estimated Price:** "
                f"₹{booking['estimated_price']}"
            )

        # -------------------------------------------------
        # VIEW JOB DETAILS
        # -------------------------------------------------

        with job_col2:

            if st.button(
                "🔎 View Job Details",
                key=f"view_job_{booking['id']}",
                use_container_width=True
            ):

                try:

                    detail_response = requests.get(
                        f"{API_URL}/workers/"
                        f"{WORKER_ID}/bookings/"
                        f"{booking['id']}"
                    )

                    detail_response.raise_for_status()

                    detail_result = (
                        detail_response.json()
                    )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not load job details: {e}"
                    )

                    st.stop()

                if not detail_result.get("success"):

                    st.error(
                        detail_result.get(
                            "message",
                            "Unable to load job details."
                        )
                    )

                else:

                    st.session_state.selected_job = (
                        detail_result["booking"]
                    )

        st.markdown("---")


# ---------------------------------------------------------
# SELECTED JOB DETAILS
# ---------------------------------------------------------

if st.session_state.selected_job:

    job = st.session_state.selected_job
    st.markdown("---")
    st.markdown("### 🔄 Update Job Status")

    current_status = job["status"]

    next_status = {
        "accepted": "on_the_way",
        "on_the_way": "arrived",
        "arrived": "in_progress",
        "in_progress": "completed"
    }.get(current_status)

    if next_status:

        status_labels = {
            "on_the_way": "🚗 Start Journey",
            "arrived": "📍 Mark as Arrived",
            "in_progress": "🔧 Start Work",
            "completed": "✅ Mark as Completed"
        }

        button_label = status_labels[next_status]

        if st.button(
            button_label,
            use_container_width=True
        ):

            try:

                status_response = requests.put(
                    f"{API_URL}/bookings/"
                    f"{job['id']}/status",
                    json={
                        "status": next_status
                    }
                )

                status_response.raise_for_status()

                status_result = status_response.json()

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not update job status: {e}"
                )

                st.stop()

            if not status_result.get("success"):

                st.error(
                    status_result.get(
                        "message",
                        "Unable to update job status."
                    )
                )

            else:

                st.success(
                    f"Job status updated to "
                    f"'{next_status}'."
                )

                updated_booking = status_result["booking"]

                updated_booking["customer_name"] = job["customer_name"]
                updated_booking["service"] = job["service"]
                updated_booking["final_price"] = job.get("final_price")

                st.session_state.selected_job = updated_booking

                st.rerun()

    else:

        if current_status == "completed":

            st.success(
                "✅ This job has been completed."
            )

        elif current_status == "rejected":

            st.warning(
                "❌ This job was rejected."
            )

        else:

            st.info(
                f"Current status: {current_status}"
            )

    st.markdown("## 🔎 Job Details")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.write(
            f"**Booking ID:** "
            f"#{job['id']}"
        )

        st.write(
            f"**Customer:** "
            f"{job['customer_name']}"
        )

        st.write(
            f"**Service:** "
            f"{job['service']}"
        )

        st.write(
            f"**📍 Location:** "
            f"{job['location']}"
        )

    with detail_col2:

        st.write(
            f"**Status:** "
            f"{job['status']}"
        )

        st.write(
            f"**⏰ Scheduled Time:** "
            f"{job['scheduled_time']}"
        )

        st.write(
            f"**💰 Estimated Price:** "
            f"₹{job['estimated_price']}"
        )

        final_price = job["final_price"]

        if final_price is None:

            st.write(
                "**Final Price:** Not finalized"
            )

        else:

            st.write(
                f"**Final Price:** "
                f"₹{final_price}"
            )
# ---------------------------------------------------------
# COMPLETED JOBS
# ---------------------------------------------------------

st.markdown(
    "## ✅ Completed Jobs"
)


if not completed_bookings:

    st.info(
        "No completed jobs yet."
    )

else:

    for booking in completed_bookings:

        st.write(
            f"Booking #{booking['id']} | "
            f"{booking['service']} | "
            f"₹{booking['estimated_price']} | "
            f"{booking['location']}"
        )