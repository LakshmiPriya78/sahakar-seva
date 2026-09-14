
import streamlit as st
import requests
import io
import hashlib
import speech_recognition as sr


def transcribe_audio(audio_bytes, language_code):
    recognizer = sr.Recognizer()

    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio = recognizer.record(source)

    return recognizer.recognize_google(
        audio,
        language=language_code
    )


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SAHAKAR SEVA",
    page_icon="🤝",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "matches" not in st.session_state:
    st.session_state.matches = []

if "service" not in st.session_state:
    st.session_state.service = ""

if "problem" not in st.session_state:
    st.session_state.problem = ""

if "booking" not in st.session_state:
    st.session_state.booking = None

if "booking_id" not in st.session_state:
    st.session_state.booking_id = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "request_text" not in st.session_state:
    st.session_state.request_text = ""

if "is_complex_service" not in st.session_state:
    st.session_state.is_complex_service = False

if "team_result" not in st.session_state:
    st.session_state.team_result = None

if "last_voice_key" not in st.session_state:
    st.session_state.last_voice_key = None
if "rating_submitted" not in st.session_state:
    st.session_state.rating_submitted = False

# =========================================================
# RECOVER BOOKING ID FROM URL
# =========================================================

if st.session_state.booking_id is None:

    booking_id_from_url = st.query_params.get("booking_id")

    if booking_id_from_url:

        try:
            st.session_state.booking_id = int(
                booking_id_from_url
            )

        except ValueError:
            st.session_state.booking_id = None


# =========================================================
# REFRESH CURRENT BOOKING STATUS
# =========================================================

if st.session_state.booking_id:

    try:

        status_response = requests.get(
            f"{API_URL}/bookings/"
            f"{st.session_state.booking_id}",
            timeout=10
        )

        status_response.raise_for_status()

        status_result = status_response.json()

        if status_result.get("success"):

            st.session_state.booking = (
                status_result["booking"]
            )

    except requests.exceptions.RequestException as e:

        st.warning(
            f"Could not refresh booking status: {e}"
        )


# =========================================================
# HEADER
# =========================================================

st.title("🤝 SAHAKAR SEVA")

st.subheader(
    "Trusted local services. Fair opportunities. Stronger cooperatives."
)

st.write(
    "Describe what you need in your own words. "
    "SAHAKAR SEVA will understand your requirement "
    "and find the best available worker."
)


# =========================================================
# CUSTOMER REQUEST
# =========================================================

st.markdown("### 🌐 Choose Your Language")

language = st.selectbox(
    "Service request language",
    [
        "English",
        "తెలుగు (Telugu)",
        "हिन्दी (Hindi)"
    ]
)


# =========================================================
# VOICE INPUT
# =========================================================

language_codes = {
    "English": "en-IN",
    "తెలుగు (Telugu)": "te-IN",
    "हिन्दी (Hindi)": "hi-IN"
}


st.subheader("🎤 Voice Input")

audio_value = st.audio_input(
    "Speak your service requirement",
    sample_rate=16000
)


if audio_value is not None:

    audio_bytes = audio_value.getvalue()

    audio_hash = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    voice_key = f"{language}_{audio_hash}"

    if st.session_state.get("last_voice_key") != voice_key:

        try:

            with st.spinner(
                "Converting your speech to text..."
            ):

                recognized_text = transcribe_audio(
                    audio_bytes,
                    language_codes[language]
                )

            # Store recognized speech BEFORE the text-area
            # widget is created on this rerun.
            st.session_state["request_text"] = (
                recognized_text
            )

            st.session_state["last_voice_key"] = (
                voice_key
            )

            st.success(
                "Voice converted to text successfully."
            )

        except sr.UnknownValueError:

            st.error(
                "Sorry, I could not understand the speech."
            )

        except sr.RequestError:

            st.error(
                "Speech recognition service is unavailable. "
                "Please check your internet connection."
            )

        except Exception as e:

            st.error(
                f"Voice recognition failed: {e}"
            )


# =========================================================
# TEXT REQUEST
# =========================================================

request_text = st.text_area(
    "Describe your requirement",
    height=100,
    key="request_text",
    placeholder="Example: My kitchen pipe is leaking."
)


# =========================================================
# CUSTOMER LOCATION
# =========================================================

st.markdown("---")

st.markdown("### 📍 Your Location")

location_col1, location_col2 = st.columns(2)

with location_col1:

    latitude = st.number_input(
        "Latitude",
        value=13.6288,
        format="%.4f",
        key="customer_latitude"
    )

with location_col2:

    longitude = st.number_input(
        "Longitude",
        value=79.4192,
        format="%.4f",
        key="customer_longitude"
    )


# =========================================================
# FIND HELP
# =========================================================

if st.button(
    "🔍 Find Help",
    use_container_width=True
):

    if not request_text.strip():

        st.warning(
            "Please describe your requirement."
        )

    else:

        # -------------------------------------------------
        # CLEAR PREVIOUS RESULTS
        # -------------------------------------------------

        st.session_state.matches = []

        st.session_state.team_result = None

        # Clear previous booking for a new request
        st.session_state.booking = None
        st.session_state.booking_id = None

        if "booking_id" in st.query_params:
            del st.query_params["booking_id"]


        # -------------------------------------------------
        # AI SERVICE UNDERSTANDING
        # -------------------------------------------------

        with st.spinner(
            "Understanding your requirement..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/ai/analyze-request",
                    json={
                        "request": request_text,
                        "language": language
                    },
                    timeout=10
                )

                response.raise_for_status()

                ai_result = response.json()

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to the backend: {e}"
                )

                st.stop()


        if not ai_result.get("success"):

            st.error(
                ai_result.get(
                    "message",
                    "Unable to analyze request."
                )
            )

            st.stop()


        # -------------------------------------------------
        # SAVE AI ANALYSIS
        # -------------------------------------------------

        analysis = ai_result["analysis"]

        service = analysis.get(
            "service",
            "Unknown"
        )

        problem = analysis.get(
            "problem",
            "Unknown"
        )

        is_complex_service = (
            analysis.get("request_type")
            == "complex_service"
        )


        st.session_state.analysis = analysis

        st.session_state.service = service

        st.session_state.problem = problem

        st.session_state.is_complex_service = (
            is_complex_service
        )


        # -------------------------------------------------
        # COMPLEX SERVICE MATCHING
        # -------------------------------------------------

        if is_complex_service:

            with st.spinner(
                "Finding the best available team..."
            ):

                try:

                    team_response = requests.post(
                        f"{API_URL}/ai/match-team",
                        json={
                            "request": request_text,
                            "customer_lat": latitude,
                            "customer_lon": longitude
                        },
                        timeout=10
                    )

                    team_response.raise_for_status()

                    team_result = team_response.json()

                    st.session_state.team_result = (
                        team_result
                    )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to team matching service: {e}"
                    )

                    st.stop()


        # -------------------------------------------------
        # NORMAL SERVICE MATCHING
        # -------------------------------------------------

        else:

            with st.spinner(
                "Finding the best available workers..."
            ):

                try:

                    match_response = requests.post(
                        f"{API_URL}/ai/match-workers",
                        json={
                            "service": service,
                            "problem": problem,
                            "latitude": latitude,
                            "longitude": longitude
                        },
                        timeout=10
                    )

                    match_response.raise_for_status()

                    match_result = match_response.json()

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to worker matching service: {e}"
                    )

                    st.stop()


            if match_result.get("success"):

                st.session_state.matches = (
                    match_result.get(
                        "matches",
                        []
                    )
                )

            else:

                st.error(
                    match_result.get(
                        "message",
                        "Worker matching failed."
                    )
                )


# =========================================================
# DISPLAY SAVED AI ANALYSIS
# =========================================================

if st.session_state.analysis:

    analysis = st.session_state.analysis

    service = st.session_state.service

    problem = st.session_state.problem

    is_complex_service = (
        st.session_state.is_complex_service
    )


    # =====================================================
    # COMPLEX SERVICE UNDERSTANDING
    # =====================================================

    if is_complex_service:

        st.markdown("---")

        st.markdown(
            "### 🚚 Complex Service Understanding"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Service",
                service
            )

        with col2:

            st.metric(
                "Property",
                analysis.get(
                    "property_type",
                    "Not specified"
                )
            )

        with col3:

            st.metric(
                "Team Required",
                analysis.get(
                    "team_size",
                    1
                )
            )


        st.write(
            f"📍 **Origin:** "
            f"{(analysis.get('origin') or 'Not specified').title()}"
        )

        st.write(
            f"📍 **Destination:** "
            f"{(analysis.get('destination') or 'Not specified').title()}"
        )

        st.write(
            f"🚛 **Vehicle Required:** "
            f"{'Yes' if analysis.get('vehicle_required') else 'No'}"
        )

        st.write(
            "🧰 **Required Components:** "
            + ", ".join(
                analysis.get(
                    "required_components",
                    []
                )
            )
        )

        st.info(
            "SAHAKAR SEVA identified this as a "
            "complex service requiring coordinated "
            "team and resource matching."
        )


    # =====================================================
    # NORMAL AI UNDERSTANDING
    # =====================================================

    else:

        st.markdown("---")

        st.markdown(
            "### 🧠 AI Understanding"
        )

        urgency = analysis.get(
            "urgency",
            "Normal"
        )

        confidence = analysis.get(
            "confidence",
            0
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Service",
                service
            )

        with col2:

            st.metric(
                "Problem",
                problem
            )

        with col3:

            st.metric(
                "Urgency",
                urgency
            )

        with col4:

            st.metric(
                "Confidence",
                f"{confidence * 100:.0f}%"
            )


# =========================================================
# COMPLEX TEAM MATCHING DISPLAY
# =========================================================

if (
    st.session_state.analysis
    and st.session_state.is_complex_service
    and st.session_state.team_result
):

    team_result = st.session_state.team_result


    if team_result.get("success"):

        team_matching = team_result.get(
            "team_matching",
            {}
        )

        recommendation = team_result.get(
            "recommendation",
            {}
        )

        service_plan = team_result.get(
            "service_plan",
            {}
        )

        analysis = st.session_state.analysis


        # -------------------------------------------------
        # TEAM REQUIREMENTS
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### 👷 Intelligent Team Matching"
        )


        required = team_matching.get(
            "team_size_requested",
            analysis.get(
                "team_size",
                1
            )
        )

        selected = team_matching.get(
            "team_size_selected",
            0
        )

        shortage = recommendation.get(
            "shortage",
            max(
                required - selected,
                0
            )
        )

        complete = team_matching.get(
            "team_complete",
            False
        )


        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Workers Required",
                required
            )

        with col2:

            st.metric(
                "Workers Available",
                selected
            )

        with col3:

            st.metric(
                "Shortage",
                shortage
            )


        if complete:

            st.success(
                "✅ Required team is available."
            )

        else:

            st.warning(
                f"⚠️ Team incomplete. "
                f"{shortage} additional "
                f"worker(s) required."
            )


        # -------------------------------------------------
        # SERVICE RESOURCES
        # -------------------------------------------------

        st.markdown(
            "#### 🧰 Service Resources"
        )

        resources = service_plan.get(
            "resources",
            analysis.get(
                "resources",
                []
            )
        )

        if resources:

            st.write(
                " • ".join(resources)
            )

        else:

            st.info(
                "No additional resources specified."
            )


        # -------------------------------------------------
        # SELECTED TEAM
        # -------------------------------------------------

        st.markdown(
            "#### 👷 Selected Team"
        )

        team_members = team_matching.get(
            "team_members",
            []
        )


        if team_members:

            for member in team_members:

                worker_name = (
                    member.get("worker_name")
                    or member.get("name")
                    or "Worker"
                )

                match_score = (
                    member.get("final_score")
                    if member.get("final_score") is not None
                    else member.get(
                        "match_score",
                        0
                    )
                )

                st.write(
                    f"**{worker_name}** "
                    f"— Match Score: "
                    f"{float(match_score):.2f}"
                )

        else:

            st.info(
                "No additional workers "
                "are currently available."
            )


        # -------------------------------------------------
        # COOPERATIVE RECOMMENDATION
        # -------------------------------------------------

        st.markdown(
            "#### 🤖 Cooperative Recommendation"
        )

        recommendation_text = (
            recommendation.get(
                "recommendation",
                "No recommendation available."
            )
        )

        st.info(
            recommendation_text
        )


        # -------------------------------------------------
        # CREATE COMPLEX BOOKING
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            "#### 📋 Create Service Booking"
        )


        # Don't create another booking if one already exists
        if st.session_state.booking_id:

            st.info(
                f"Booking #{st.session_state.booking_id} "
                "already exists for this request."
            )

        else:

            if st.button(
                "📋 Create Booking & Request Team",
                use_container_width=True,
                key="create_complex_booking"
            ):

                with st.spinner(
                    "Creating your service booking..."
                ):

                    try:

                        booking_response = requests.post(
                            f"{API_URL}/ai/create-complex-booking",
                            json={
                                "customer_id": 8,
                                "request": (
                                    st.session_state.request_text
                                ),
                                "scheduled_time": (
                                    "2026-09-15 10:00"
                                ),
                                "estimated_price": 2500,
                                "location": "Tirupati",
                                "latitude": latitude,
                                "longitude": longitude
                            },
                            timeout=10
                        )

                        booking_response.raise_for_status()

                        booking_result = (
                            booking_response.json()
                        )

                    except requests.exceptions.RequestException as e:

                        st.error(
                            f"Could not create complex booking: {e}"
                        )

                        st.stop()


                if not booking_result.get("success"):

                    st.error(
                        booking_result.get(
                            "message",
                            "Unable to create complex booking."
                        )
                    )

                else:

                    booking = booking_result.get(
                        "booking",
                        {}
                    )

                    st.session_state.booking = booking

                    st.session_state.booking_id = (
                        booking.get("id")
                    )

                    if booking.get("id"):

                        st.query_params["booking_id"] = (
                            str(booking["id"])
                        )

                    st.success(
                        "🎉 Complex service booking "
                        "created successfully!"
                    )


# =========================================================
# NORMAL SERVICE MATCHING DISPLAY
# =========================================================

if (
    st.session_state.analysis
    and not st.session_state.is_complex_service
    and st.session_state.matches
):

    st.markdown("---")

    st.success(
        f"Found {len(st.session_state.matches)} "
        "available worker(s) matching your requirement."
    )


    for index, worker in enumerate(
        st.session_state.matches
    ):

        if index == 0:

            st.markdown(
                "## 🥇 Recommended Worker"
            )

        else:

            st.markdown(
                f"### 🥈 Alternative {index}"
            )


        worker_col1, worker_col2 = st.columns(
            [2, 1]
        )


        # -------------------------------------------------
        # WORKER INFORMATION
        # -------------------------------------------------

        with worker_col1:

            st.markdown(
                f"### 👷 "
                f"{worker.get('worker_name', 'Worker')}"
            )

            st.write(
                f"📍 **Distance:** "
                f"{worker.get('distance_km', 0)} km"
            )

            st.write(
                f"⭐ **Rating:** "
                f"{worker.get('rating_score', 0) / 20:.1f}/5"
            )

            st.write(
                f"🛠️ **Skill Match:** "
                f"{worker.get('skill_score', 0):.0f}%"
            )

            st.write(
                f"⚡ **Availability:** "
                f"{worker.get('availability_score', 0):.0f}%"
            )

            st.write(
                f"🛡️ **Reliability:** "
                f"{worker.get('reliability_score', 0):.0f}%"
            )

            st.write(
                f"🤝 **Fair Opportunity:** "
                f"{worker.get('fair_opportunity_score', 0):.0f}%"
            )


        # -------------------------------------------------
        # SELECT WORKER
        # -------------------------------------------------

        with worker_col2:

            st.metric(
                "FairMatch Score",
                f"{worker.get('final_score', 0):.2f}"
            )


            if index == 0:

                button_text = (
                    "✅ Select Recommended Worker"
                )

            else:

                button_text = "Select Worker"


            if st.button(
                button_text,
                key=f"select_{worker.get('worker_id')}",
                use_container_width=True
            ):

                with st.spinner(
                    "Creating your booking..."
                ):

                    try:

                        booking_response = requests.post(
                            f"{API_URL}/bookings",
                            json={
                                "customer_id": 1,
                                "worker_id": (
                                    worker["worker_id"]
                                ),
                                "service": (
                                    st.session_state.service
                                ),
                                "location": "Tirupati",
                                "scheduled_time": (
                                    "2026-09-15 10:00"
                                ),
                                "estimated_price": 500
                            },
                            timeout=10
                        )

                        booking_response.raise_for_status()

                        booking_result = (
                            booking_response.json()
                        )

                    except requests.exceptions.RequestException as e:

                        st.error(
                            f"Could not create booking: {e}"
                        )

                        st.stop()


                if not booking_result.get("success"):

                    st.error(
                        booking_result.get(
                            "message",
                            "Unable to create booking."
                        )
                    )

                else:

                    booking = booking_result["booking"]

                    st.session_state.booking = booking

                    st.session_state.booking_id = (
                        booking["id"]
                    )

                    st.query_params["booking_id"] = (
                        str(booking["id"])
                    )

                    st.success(
                        "🎉 Booking created successfully!"
                    )


# =========================================================
# CURRENT BOOKING
# =========================================================

if st.session_state.booking:

    booking = st.session_state.booking

    st.markdown("---")

    st.success(
        "🎉 Booking created successfully!"
    )

    st.markdown(
        "### 📋 Booking Confirmation"
    )


    confirmation_col1, confirmation_col2 = (
        st.columns(2)
    )


    with confirmation_col1:

        st.write(
            f"**Booking ID:** "
            f"#{booking.get('id', '-')}"
        )

        st.write(
            f"**Service:** "
            f"{booking.get('service', '-')}"
        )

        st.write(
            f"**Worker:** "
            f"{booking.get('worker_name', 'Team Assigned')}"
        )


    with confirmation_col2:

        st.write(
            f"**Location:** "
            f"{booking.get('location', '-')}"
        )

        st.write(
            f"**Scheduled:** "
            f"{booking.get('scheduled_time', '-')}"
        )

        st.write(
            f"**Estimated Price:** "
            f"₹{booking.get('estimated_price', 0)}"
        )


    status = booking.get(
        "status",
        "unknown"
    )


    # =========================================================
    # BOOKING LIFECYCLE TRACKER
    # =========================================================

    st.markdown("### 📍 Booking Journey")

    lifecycle = [
        ("requested", "📋", "Requested"),
        ("accepted", "✅", "Accepted"),
        ("on_the_way", "🚗", "On the Way"),
        ("arrived", "📍", "Arrived"),
        ("in_progress", "🔧", "In Progress"),
        ("completed", "🎉", "Completed")
    ]

    status_order = [
        "requested",
        "accepted",
        "on_the_way",
        "arrived",
        "in_progress",
        "completed"
    ]


    if status in status_order:

        current_index = status_order.index(status)

        lifecycle_cols = st.columns(
            len(lifecycle)
        )

        for index, (state, icon, label) in enumerate(
            lifecycle
        ):

            with lifecycle_cols[index]:

                if index < current_index:

                    st.success(
                        f"{icon}\n\n{label}"
                    )

                elif index == current_index:

                    st.info(
                        f"{icon}\n\n**{label}**"
                    )

                else:

                    st.write(
                        f"⚪\n\n{label}"
                    )


    # =========================================================
    # CURRENT STATUS MESSAGE
    # =========================================================

    if status == "requested":

        st.info(
            "⏳ Current Status: "
            "**Waiting for worker response**"
        )


    elif status == "awaiting_team":

        st.warning(
            "👷 Current Status: "
            "**Awaiting Team Completion**"
        )


    elif status == "accepted":

        st.success(
            "✅ Current Status: "
            "**Booking Accepted**"
        )


    elif status == "rejected":

        st.error(
            "❌ Current Status: "
            "**Booking Rejected**"
        )


    elif status == "on_the_way":

        st.info(
            "🚗 Current Status: "
            "**Worker is on the way**"
        )


    elif status == "arrived":

        st.info(
            "📍 Current Status: "
            "**Worker has arrived**"
        )


    elif status == "in_progress":

        st.warning(
            "🔧 Current Status: "
            "**Service in progress**"
        )


    elif status == "completed":

        st.success(
            "🎉 Current Status: "
            "**Service Completed**"
        )


    else:

        st.write(
            f"Current Status: **{status}**"
        )


    # =========================================================
    # REFRESH BOOKING STATUS
    # =========================================================

    if st.button(
        "🔄 Refresh Booking Status",
        use_container_width=True,
        key="refresh_booking_status"
    ):

        st.rerun()


    # =========================================================
    # PAYMENT & INVOICE
    # =========================================================

    st.markdown("### 🧾 Payment & Invoice")

    if status == "completed":

        # Create payment record if it does not already exist
        payment_response = requests.post(
            f"{API_URL}/payments/create",
            json={
                "booking_id": st.session_state.booking_id
            },
            timeout=10
        )

        if payment_response.status_code == 200:

            payment_data = payment_response.json()

            if payment_data.get("success"):

                st.success(
                    "💳 Payment record created successfully."
                )

                st.markdown(
                    "#### 💰 Payment Distribution"
                )

                payment = payment_data.get(
                    "payment",
                    payment_data
                )

                amount = payment.get(
                    "amount",
                    0
                )

                worker_amount = payment.get(
                    "worker_amount",
                    0
                )

                cooperative_amount = payment.get(
                    "cooperative_amount",
                    0
                )

                platform_amount = payment.get(
                    "platform_amount",
                    0
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Total",
                        f"₹{amount:.2f}"
                    )

                with col2:

                    st.metric(
                        "👷 Worker",
                        f"₹{worker_amount:.2f}"
                    )

                with col3:

                    st.metric(
                        "🤝 Cooperative",
                        f"₹{cooperative_amount:.2f}"
                    )

                with col4:

                    st.metric(
                        "Platform",
                        f"₹{platform_amount:.2f}"
                    )

            else:

                st.info(
                    payment_data.get(
                        "message",
                        "Payment record already exists."
                    )
                )

        else:

            st.warning(
                "Unable to create payment record."
            )


        # -----------------------------------------------------
        # INVOICE
        # -----------------------------------------------------

        invoice_response = requests.get(
            f"{API_URL}/bookings/"
            f"{st.session_state.booking_id}/invoice",
            timeout=10
        )

        if invoice_response.status_code == 200:

            invoice_data = invoice_response.json()

            if invoice_data.get("success"):

                st.markdown(
                    "#### 🧾 Invoice"
                )

                invoice = invoice_data.get(
                    "invoice",
                    invoice_data
                )

                st.write(
                    f"**Invoice ID:** "
                    f"{invoice.get('invoice_id', 'N/A')}"
                )

                st.write(
                    f"**Booking ID:** "
                    f"#{invoice.get('booking_id', 'N/A')}"
                )

                st.write(
                    f"**Service:** "
                    f"{invoice.get('service', 'N/A')}"
                )

                st.write(
                    f"**Worker:** "
                    f"{invoice.get('worker', 'N/A')}"
                )

                st.write(
                    f"**Amount:** "
                    f"₹{invoice.get('total_amount', 0):.2f}"
                )

                st.success(
                    "✅ Invoice generated successfully."
                )

            else:

                st.info(
                    invoice_data.get(
                        "message",
                        "Invoice is not available yet."
                    )
                )

        else:

            st.info(
                "Invoice is not available yet."
            )

    else:

        st.info(
            "💳 Payment and invoice will be generated "
            "after the service is completed."
        )
# =========================================================
# ⭐ RATE WORKER
# =========================================================

if (
    st.session_state.booking
    and status == "completed"
):

    st.markdown("---")

    st.markdown("### ⭐ Rate Your Worker")

    worker_name = booking.get(
        "worker_name",
        "Worker"
    )

    worker_id = booking.get(
        "worker_id"
    )

    booking_id = booking.get(
        "id"
    )

    st.write(
        f"**Worker:** {worker_name}"
    )

    if worker_id:

        if st.session_state.rating_submitted:

            st.success(
                "✅ Thank you! Your rating has been submitted."
            )

        else:

            rating = st.slider(
                "How would you rate the service?",
                min_value=1,
                max_value=5,
                value=5,
                step=1,
                key="customer_rating"
            )

            feedback = st.text_area(
                "Your feedback",
                placeholder="Example: Excellent service and very professional.",
                key="customer_feedback"
            )

            if st.button(
                "⭐ Submit Rating",
                use_container_width=True,
                key="submit_rating"
            ):

                try:

                    rating_response = requests.post(
                        f"{API_URL}/ratings",
                        json={
                            "booking_id": booking_id,
                            "customer_id": 1,
                            "worker_id": worker_id,
                            "rating": rating,
                            "feedback": feedback
                        },
                        timeout=10
                    )

                    rating_response.raise_for_status()

                    rating_result = (
                        rating_response.json()
                    )

                    if rating_result.get("success"):

                        st.session_state.rating_submitted = True

                        st.success(
                            "✅ Rating submitted successfully!"
                        )

                    else:

                        st.error(
                            rating_result.get(
                                "message",
                                "Unable to submit rating."
                            )
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not submit rating: {e}"
                    )

    else:

        st.info(
            "Worker information is not available "
            "for this booking."
        )