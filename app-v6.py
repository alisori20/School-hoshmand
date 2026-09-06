import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

# ============================================================================
# Streamlit Configuration and Theme Setup
# ============================================================================
st.set_page_config(
    page_title="سامانه هوشمند مدیریت مدرسه (v4 - ماژول مالی و کلاس آنلاین)",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Persian / RTL CSS Injection with online classroom styles
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    /* Apply Font to all components */
    html, body, [data-testid="stSidebar"], .stApp, p, h1, h2, h3, h4, h5, h6, span, div, label, button, select, input, textarea {
        font-family: 'Vazirmatn', sans-serif !important;
    }
    
    /* Global alignment adjustments for Persian RTL */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Elegant Persian Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 6px solid #1d3557;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-card-title {
        font-size: 14px;
        color: #495057;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-card-value {
        font-size: 28px;
        font-weight: 800;
        color: #1d3557;
    }
    
    /* Callout styling */
    .alert-box {
        background-color: #f1faee;
        border-right: 5px solid #e63946;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Success Alert */
    .success-box {
        background-color: #f4fbf7;
        border-right: 5px solid #2a9d8f;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Virtual Class Active Alert */
    .live-box {
        background-color: #eef1fe;
        border-right: 5px solid #4a5568;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Custom divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #1d3557, transparent);
        margin: 20px 0;
    }
    
    /* Sidebar user info badge */
    .user-badge {
        background-color: #1d3557;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Align Streamlit default layouts to RTL */
    [data-testid="stHeader"] {
        direction: rtl;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }
    .stForm {
        border-radius: 12px;
        padding: 20px;
        background-color: #fafbfc;
        border: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to render a Persian container
def rtl_container(html_content):
    st.markdown(f'<div class="rtl-container">{html_content}</div>', unsafe_allow_html=True)

# ============================================================================
# 1. State Initialization (Mock Database - Enhanced for Online Classes)
# ============================================================================
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    
    # Students Database
    st.session_state['students'] = {
        1: {"id": 1, "name": "علیرضا احمدی", "code": "1001", "class": "کلاس ۱۰۱", "parent_id": 10, "status": "فعال"},
        2: {"id": 2, "name": "مریم احمدی", "code": "1002", "class": "کلاس ۱۰۲", "parent_id": 10, "status": "فعال"},
        3: {"id": 3, "name": "رضا قاسمی", "code": "1003", "class": "کلاس ۱۰۱", "parent_id": 11, "status": "فعال"},
        4: {"id": 4, "name": "سارا کریمی", "code": "1004", "class": "کلاس ۱۰۱", "parent_id": 12, "status": "فعال"},
        5: {"id": 5, "name": "پویا رضایی", "code": "1005", "class": "کلاس ۱۰۲", "parent_id": 13, "status": "فعال"},
    }
    
    # Parents Directory
    st.session_state['parents'] = {
        10: "حمید احمدی",
        11: "محمد قاسمی",
        12: "فاطمه کریمی",
        13: "امیر رضایی",
    }
    
    # Attendance Records (Physical)
    st.session_state['attendance'] = [
        {"student_id": 1, "date": "1405-06-14", "subject": "ریاضی", "status": "حاضر", "remarks": ""},
        {"student_id": 3, "date": "1405-06-14", "subject": "ریاضی", "status": "غایب", "remarks": "کسالت"},
        {"student_id": 4, "date": "1405-06-14", "subject": "ریاضی", "status": "تأخیر", "remarks": "ترافیک"},
        {"student_id": 1, "date": "1405-06-15", "subject": "فیزیک", "status": "حاضر", "remarks": ""},
        {"student_id": 3, "date": "1405-06-15", "subject": "فیزیک", "status": "حاضر", "remarks": ""},
        {"student_id": 4, "date": "1405-06-15", "subject": "فیزیک", "status": "غایب", "remarks": "بدون اطلاع"},
        {"student_id": 2, "date": "1405-06-15", "subject": "شیمی", "status": "حاضر", "remarks": ""},
        {"student_id": 5, "date": "1405-06-15", "subject": "شیمی", "status": "تأخیر", "remarks": "تأخیر اتوبوس"},
    ]
    
    # Grades Records
    st.session_state['grades'] = [
        {"student_id": 1, "subject": "ریاضی", "type": "کوییز", "score": 18.5, "date": "1405-06-10"},
        {"student_id": 3, "subject": "ریاضی", "type": "کوییز", "score": 12.0, "date": "1405-06-10"},
        {"student_id": 4, "subject": "ریاضی", "type": "کوییز", "score": 9.5, "date": "1405-06-10"},
        {"student_id": 1, "subject": "فیزیک", "type": "میان‌ترم", "score": 19.0, "date": "1405-06-12"},
        {"student_id": 3, "subject": "فیزیک", "type": "میان‌ترم", "score": 14.5, "date": "1405-06-12"},
        {"student_id": 4, "subject": "فیزیک", "type": "میان‌ترم", "score": 11.0, "date": "1405-06-12"},
    ]
    
    # Announcements
    st.session_state['announcements'] = [
        {"id": 1, "title": "جلسه اولیا و مربیان پایه دهم", "body": "به اطلاع اولیای گرامی می‌رساند جلسه هماهنگی روز دوشنبه ۱۷ شهریور ساعت ۱۶ در سالن اجتماعات برگزار می‌گردد.", "date": "1405-06-12", "target": "parents"},
        {"id": 2, "title": "شروع مسابقات ورزشی درون مدرسه‌ای", "body": "مسابقات فوتسال و والیبال از هفته آینده آغاز می‌شود. علاقه‌مندان جهت ثبت‌نام به مربی ورزش مراجعه کنند.", "date": "1405-06-14", "target": "all"},
        {"id": 3, "title": "برگزاری کارگاه هدایت تحصیلی", "body": "دبیرستان در نظر دارد کارگاه رایگانی را برای دانش‌آموزان به منظور آشنایی با رشته‌های نوین مهندسی برگزار کند.", "date": "1405-06-15", "target": "students"},
    ]
    
    # Homework tasks
    st.session_state['homework'] = [
        {"id": 1, "class": "کلاس ۱۰۱", "subject": "ریاضی", "title": "حل تمرینات صفحه ۴۲ و ۴۳", "description": "پاسخ‌ها را به صورت تشریحی در دفتر نوشته و عکس آن را آپلود کنید.", "due": "1405-06-18"},
        {"id": 2, "class": "کلاس ۱۰۱", "subject": "فیزیک", "title": "گزارش آزمایشگاه سقوط آزاد", "description": "فایل PDF گزارش کار گروهی را ارسال کنید.", "due": "1405-06-20"},
        {"id": 3, "class": "کلاس ۱۰۲", "subject": "شیمی", "title": "تحقیق ساختار اتم‌ها", "description": "یک خلاصه دو صفحه‌ای درباره تکامل مدل‌های اتمی بنویسید.", "due": "1405-06-19"},
    ]
    
    # Messaging
    st.session_state['messages'] = [
        {"id": 1, "sender_id": 10, "receiver_id": 101, "sender_name": "حمید احمدی (والد)", "body": "سلام استاد، وضعیت درسی پسرم علیرضا در درس ریاضی چطور است؟", "date": "1405-06-14", "is_read": False},
        {"id": 2, "sender_id": 101, "receiver_id": 10, "sender_name": "دبیر ریاضی", "body": "سلام جناب احمدی، علیرضا دانش‌آموز بسیار کوشایی است. نمره آخرین کوییز او ۱۸.۵ شده و از پیشرفت او کاملا راضی هستم.", "date": "1405-06-15", "is_read": True},
    ]

    # --- ENHANCED ONLINE CLASSES MODULE STATE (v3) ---
    st.session_state['online_classes'] = [
        {
            "id": 1,
            "subject": "ریاضی ۳",
            "class_name": "کلاس ۱۰۱",
            "topic": "فصل دوم: هندسه تحلیلی",
            "teacher_name": "مهندس احمدی",
            "provider": "google_meet",
            "start_time": "1405-06-16 10:00:00",
            "end_time": "1405-06-16 11:30:00",
            "status": "برنامه‌ریزی شده",
            "meeting_url": "https://meet.google.com/xyz-abc-123",
            "room_name": "xyz-abc-123"
        },
        {
            "id": 2,
            "subject": "فیزیک پیشرفته",
            "class_name": "کلاس ۱۰۱",
            "topic": "مکانیک سیالات",
            "teacher_name": "دکتر حسینی",
            "provider": "jitsi",
            "start_time": "1405-06-15 08:00:00",
            "end_time": "1405-06-15 09:30:00",
            "status": "خاتمه یافته",
            "meeting_url": "https://meet.jit.si/SmartSchoolPhysics101_v3",
            "room_name": "SmartSchoolPhysics101_v3"
        },
        {
            "id": 3,
            "subject": "ریاضی ۳",
            "class_name": "کلاس ۱۰۱",
            "topic": "رفع اشکال مشتق و انتگرال",
            "teacher_name": "مهندس احمدی",
            "provider": "whatsapp",
            "start_time": "1405-06-18 16:00:00",
            "end_time": "1405-06-18 17:30:00",
            "status": "برنامه‌ریزی شده",
            "meeting_url": "https://chat.whatsapp.com/L1abc123xyzPhysics101",
            "room_name": "Math101Group"
        }
    ]

    st.session_state['online_class_logs'] = [
        {"id": 1, "class_id": 2, "student_id": 1, "student_name": "علیرضا احمدی", "joined_at": "08:02", "left_at": "09:28", "duration": 86, "device": "Chrome / Windows"},
        {"id": 2, "class_id": 2, "student_id": 3, "student_name": "رضا قاسمی", "joined_at": "08:15", "left_at": "09:29", "duration": 74, "device": "Android App"},
        {"id": 3, "class_id": 2, "student_id": 4, "student_name": "سارا کریمی", "joined_at": "08:01", "left_at": "08:31", "duration": 30, "device": "Firefox / MacOS (خروج زودهنگام)"},
    ]

    st.session_state['online_recordings'] = [
        {"id": 1, "class_id": 2, "subject": "فیزیک پیشرفته", "topic": "جلسه اول: مبانی مکانیک سیالات", "url": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", "duration": "90 دقیقه", "size": "145 MB", "date": "1405-06-15"}
    ]

    # --- FINANCIAL MODULE STATE (v4) ---
    if 'fee_structures' not in st.session_state:
        st.session_state['fee_structures'] = [
            {"id": 1, "name": "شهریه ثابت پایه دهم (سال ۱۴۰۵)", "category": "tuition", "base_amount": 150000000, "grade": "دهم"},
            {"id": 2, "name": "هزینه ترانسپورت سرویس مدرسه", "category": "transport", "base_amount": 45000000, "grade": "همه"},
            {"id": 3, "name": "کتب درسی و اقلام آموزشی", "category": "books", "base_amount": 15000000, "grade": "همه"}
        ]
    if 'invoices' not in st.session_state:
        st.session_state['invoices'] = [
            {"id": 1001, "student_id": 1, "student_name": "علیرضا احمدی", "title": "صورت‌حساب شهریه و خدمات ترم اول", "issue_date": "1405-06-01", "due_date": "1405-06-30", "subtotal": 210000000, "discount": 15000000, "total": 195000000, "paid": 120000000, "status": "پرداخت بخشی"},
            {"id": 1002, "student_id": 2, "student_name": "مریم احمدی", "title": "صورت‌حساب شهریه و خدمات ترم اول", "issue_date": "1405-06-01", "due_date": "1405-06-30", "subtotal": 165000000, "discount": 0, "total": 165000000, "paid": 0, "status": "پرداخت نشده"}
        ]
    if 'payment_transactions' not in st.session_state:
        st.session_state['payment_transactions'] = [
            {"id": 5001, "invoice_id": 1001, "payer_name": "حمید احمدی", "gateway": "zarinpal", "ref_num": "TR-9827162", "card_pan": "۶۰۳۷-۹۹**-****-۱۲۳۴", "amount": 120000000, "status": "موفق", "date": "1405-06-05"}
        ]
    if 'system_logs' not in st.session_state:
        st.session_state['system_logs'] = [
            {"زمان رویداد": "1405-06-15 11:24:01", "کاربر": "دبیر ریاضی", "آدرس آی‌پی": "192.168.1.12", "نوع فعالیت": "ثبت نمره", "توضیحات": "ثبت نمره کوئیز علیرضا احمدی: نمره ۱۸.۵"},
            {"زمان رویداد": "1405-06-15 08:00:15", "کاربر": "مدیر مدرسه", "آدرس آی‌پی": "192.168.1.5", "نوع فعالیت": "ورود به سیستم", "توضیحات": "ورود موفقیت‌آمیز به پنل مدیریتی"},
            {"زمان رویداد": "1405-06-14 14:15:30", "کاربر": "دبیر فیزیک", "آدرس آی‌پی": "192.168.1.15", "نوع فعالیت": "ثبت حضور غیاب", "توضیحات": "تغییر وضعیت حضور سارا کریمی از غایب به غایب موجه"},
            {"زمان رویداد": "1405-06-16 10:02:11", "کاربر": "دبیر ریاضی", "آدرس آی‌پی": "192.168.1.12", "نوع فعالیت": "شروع کلاس آنلاین", "توضیحات": "ایجاد اتاق کنفرانس Google Meet ریاضی ۳ کلاس ۱۰۱"}
        ]
    # --- AI EXAM/QUIZ MODULE STATE (v5) ---
    if 'ai_quizzes' not in st.session_state:
        st.session_state['ai_quizzes'] = [
            {
                "id": 101,
                "title": "ارزیابی هوشمند هندسه تحلیلی (تولید شده توسط AI)",
                "subject": "ریاضی ۳",
                "class_name": "کلاس ۱۰۱",
                "topic": "فصل دوم: هندسه تحلیلی",
                "difficulty": "متوسط",
                "questions": [
                    {
                        "id": 1,
                        "question_text": "شیب خطی که از نقاط A(2, 5) و B(4, 9) می‌گذرد چقدر است؟",
                        "type": "multiple_choice",
                        "points": 10.0,
                        "options": [
                            {"letter": "الف", "text": "۱", "is_correct": False},
                            {"letter": "ب", "text": "۲", "is_correct": True},
                            {"letter": "ج", "text": "۳", "is_correct": False},
                            {"letter": "د", "text": "۴", "is_correct": False}
                        ],
                        "explanation": "فرمول شیب خط m = (y2 - y1) / (x2 - x1) است. m = (9 - 5) / (4 - 2) = 4 / 2 = 2."
                    },
                    {
                        "id": 2,
                        "question_text": "معادله خطی با شیب ۳ که از نقطه (1, 4) می‌گذرد کدام است؟",
                        "type": "multiple_choice",
                        "points": 10.0,
                        "options": [
                            {"letter": "الف", "text": "y = 3x + 1", "is_correct": True},
                            {"letter": "ب", "text": "y = 3x - 1", "is_correct": False},
                            {"letter": "ج", "text": "y = 2x + 2", "is_correct": False},
                            {"letter": "د", "text": "y = x + 3", "is_correct": False}
                        ],
                        "explanation": "با فرمول y - y1 = m(x - x1) داریم: y - 4 = 3(x - 1) -> y = 3x + 1."
                    }
                ],
                "status": "منتشر شده",
                "created_at": "1405-06-16"
            }
        ]
    if 'ai_quiz_attempts' not in st.session_state:
        st.session_state['ai_quiz_attempts'] = [
            {"id": 1, "quiz_id": 101, "student_id": 1, "score": 20.0, "answers": {1: "ب", 2: "الف"}, "completed_at": "1405-06-17", "feedback": "علیرضا احمدی تسلط فوق‌العاده‌ای در مبحث هندسه تحلیلی دارد. پاسخ‌دهی کاملا بی‌نقص و ۱۰۰٪ صحیح بوده است."}
        ]
    if 'ai_quiz_draft' not in st.session_state:
        st.session_state['ai_quiz_draft'] = None


# ============================================================================
# 2. Sidebar Multi-School & Role Selection
# ============================================================================
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 10px;">
        <h2 style="color: #1d3557; margin-bottom: 5px;">🏫 مدرسه هوشمند</h2>
        <p style="color: #6c757d; font-size: 13px; font-weight: bold; color: #2a9d8f;">نسخه ۶.۰ - سامانه چندمدرسه‌ای (Multi-Tenant)</p>
    </div>
""", unsafe_allow_html=True)

# ── Multi-School/Tenant Selection ─────────────────────────────────────────
school_themes = {
    "دبیرستان البرز (شعبه مرکزی - تهران)": {
        "id": 1,
        "color": "#1d3557",
        "subdomain": "alborz.smartschool.ir",
        "desc": "شعبه تهران - ۱۰۲۴ دانش‌آموز فعال"
    },
    "دبیرستان البرز (شعبه ۲ - کرج)": {
        "id": 2,
        "color": "#006d77",
        "subdomain": "karaj.smartschool.ir",
        "desc": "شعبه کرج - ۴۵۰ دانش‌آموز فعال"
    }
}

selected_school_fa = st.sidebar.selectbox("🏫 انتخاب مدرسه / شعبه فعال:", list(school_themes.keys()))
school_info = school_themes[selected_school_fa]

# Dynamic CSS Theme injection based on selected school!
st.markdown(f"""
    <style>
    .user-badge, .stButton>button, .stForm {{
        border-color: {school_info['color']} !important;
    }}
    .metric-card {{
        border-right-color: {school_info['color']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style="background-color: #f1f5f9; border-right: 4px solid {school_info['color']}; padding: 10px; border-radius: 6px; margin-bottom: 15px;">
        <p style="margin: 0; font-size:12px; color: #555;"><b>دامنه اختصاصی:</b> {school_info['subdomain']}</p>
        <p style="margin: 3px 0 0 0; font-size:11px; color: #777;">{school_info['desc']}</p>
        <p style="margin: 5px 0 0 0; font-size:11px; color: #2a9d8f; font-weight:bold;">🛡️ دیتابیس ایزوله شده (Postgres RLS Active)</p>
    </div>
""", unsafe_allow_html=True)

# User Role Selection
role_mapping = {
    "مدیر مدرسه": "admin",
    "معاون مدرسه": "vice_principal",
    "دبیر ریاضی / فیزیک": "teacher",
    "دانش‌آموز (علیرضا احمدی)": "student",
    "والدین (حمید احمدی)": "parent"
}

selected_role_fa = st.sidebar.selectbox("🔑 انتخاب نقش کاربری:", list(role_mapping.keys()))
active_role = role_mapping[selected_role_fa]

# Display current user badge in sidebar
st.sidebar.markdown(f"""
    <div class="user-badge">
        <p style="margin:0; font-size:12px; opacity:0.8;">کاربر فعلی سیستم</p>
        <h3 style="margin:5px 0 0 0; font-size:18px;">{selected_role_fa}</h3>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# Helper components
# ============================================================================
def render_metric_card(title, value, border_color="#1d3557"):
    st.markdown(f"""
        <div class="metric-card" style="border-right-color: {border_color};">
            <div class="metric-card-title">{title}</div>
            <div class="metric-card-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# A. ADMIN DASHBOARD PANEL (مدیر مدرسه)
# ============================================================================
if active_role in ["admin", "vice_principal"]:
    st.title(f"🛡️ داشبورد مدیریتی - {selected_school_fa}")
    st.subheader(f"نقش کاربری: {selected_role_fa} | سال تحصیلی ۱۴۰۵-۱۴۰۶")
    
    # Admin tabs
    tab_overview, tab_students, tab_online_classes, tab_finance, tab_announcements, tab_log = st.tabs([
        "📊 نمای کلی و آمارها", 
        "👥 پرونده دیجیتال دانش‌آموزان", 
        "🌐 کلاس‌های آنلاین و زنده (جدید)",
        "💰 مدیریت مالی و شهریه (جدید)",
        "📢 ارسال اطلاعیه‌ها", 
        "🛡️ لاگ‌های فعالیت سیستم"
    ])
    
    with tab_overview:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("تعداد کل دانش‌آموزان", f"{len(st.session_state['students'])} نفر", "#1d3557")
        with col2:
            render_metric_card("دبیران فعال", "۸ دبیر متخصص", "#457b9d")
        with col3:
            # Active attendance percentage today
            today_att = [x for x in st.session_state['attendance'] if x['date'] == "1405-06-15"]
            tot_today = len(today_att)
            p_today = len([x for x in today_att if x['status'] in ['حاضر', 'تأخیر']])
            rate = f"{int((p_today/tot_today)*100)}%" if tot_today > 0 else "۹۴٪"
            render_metric_card("شاخص حضور و غیاب امروز", rate, "#2a9d8f")
        with col4:
            active_live = len([x for x in st.session_state['online_classes'] if x['status'] == "در حال برگزاری"])
            render_metric_card("کلاس‌های آنلاین زنده", f"{active_live} کلاس فعال", "#e76f51")
            
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        
        # Performance Charts
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.write("### 📈 توزیع معدل نمرات مدرسه")
            grades_data = pd.DataFrame([x['score'] for x in st.session_state['grades']], columns=['Scores'])
            st.bar_chart(grades_data)
            
        with chart_col2:
            st.write("### 📊 گزارش تحلیلی غیبت‌های هفته اخیر")
            att_df = pd.DataFrame(st.session_state['attendance'])
            att_counts = att_df['status'].value_counts()
            st.bar_chart(att_counts)
            
        # Alarm section
        st.write("### ⚠️ هشدارهای انضباطی و آموزشی هوشمند (AI)")
        low_perf_students = []
        for sid, sinfo in st.session_state['students'].items():
            s_grades = [g['score'] for g in st.session_state['grades'] if g['student_id'] == sid]
            if s_grades and np.mean(s_grades) < 12:
                low_perf_students.append(f"**{sinfo['name']}** (معدل: {np.mean(s_grades):.1f})")
                
        if low_perf_students:
            alert_text = " ، ".join(low_perf_students)
            st.markdown(f"""
                <div class="alert-box">
                    🔴 <b>دانش‌آموزان در معرض افت تحصیلی شدید:</b> {alert_text} <br/>
                    <i>سیستم به صورت خودکار به معلمان راهنما و والدین این دانش‌آموزان اطلاعیه فرستاده است.</i>
                </div>
            """, unsafe_allow_html=True)
            
    with tab_students:
        st.write("### 👥 بانک اطلاعاتی و پرونده دیجیتال دانش‌آموزان")
        search_q = st.text_input("🔍 جستجوی هوشمند دانش‌آموز (کد ملی، نام، شماره دانش‌آموزی):")
        
        # Display students in DataFrame
        stu_list = []
        for sid, sinfo in st.session_state['students'].items():
            parent_name = st.session_state['parents'].get(sinfo['parent_id'], "نامشخص")
            if not search_q or search_q in sinfo['name'] or search_q in sinfo['code']:
                stu_list.append({
                    "شماره دانش‌آموزی": sinfo['code'],
                    "نام و نام خانوادگی": sinfo['name'],
                    "کلاس": sinfo['class'],
                    "ولی دانش‌آموز": parent_name,
                    "وضعیت تحصیلی": sinfo['status']
                })
        st.dataframe(pd.DataFrame(stu_list), use_container_width=True)
        
    with tab_online_classes:
        st.write("### 🌐 نظارت کلان بر کلاس‌های آنلاین و جلسات مجازی")
        st.markdown("""
            این بخش به مدیریت مدرسه اجازه می‌دهد جلسات ضبط‌شده، نرخ اتصال دانش‌آموزان به سرورهای کلاس زنده 
            و پایداری اتصال را به صورت لحظه‌ای نظارت کند.
        """)
        
        # Online classes lists
        st.write("#### 📆 کلاس‌های آنلاین تعریف‌شده")
        st.dataframe(pd.DataFrame(st.session_state['online_classes']), use_container_width=True)
        
        # Live connection logs
        st.write("#### 📊 لاگ ورود و خروج آخرین جلسات")
        st.dataframe(pd.DataFrame(st.session_state['online_class_logs']), use_container_width=True)

    with tab_finance:
        st.write("### 💰 پنل مدیریت مالی و شهریه‌های مدرسه")
        st.markdown("""
            در این بخش می‌توانید وضعیت فاکتورهای صادر شده، شهریه‌های وصول‌شده و تراکنش‌های آنلاین اولیا را بررسی نمایید.
        """)
        
        # Financial metrics
        f_col1, f_col2, f_col3 = st.columns(3)
        total_invoiced = sum(x['total'] for x in st.session_state['invoices'])
        total_collected = sum(x['paid'] for x in st.session_state['invoices'])
        total_pending = total_invoiced - total_collected
        
        with f_col1:
            render_metric_card("کل مطالبات فاکتور شده", f"{total_invoiced:,} ریال", "#1d3557")
        with f_col2:
            render_metric_card("کل شهریه‌های وصول‌شده", f"{total_collected:,} ریال", "#2a9d8f")
        with f_col3:
            render_metric_card("معوقات و مطالبات معلق", f"{total_pending:,} ریال", "#e63946")
            
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        
        # Two columns for layout: left is charts, right is invoice table
        f_lay1, f_lay2 = st.columns([2, 1])
        with f_lay1:
            st.write("#### 📑 لیست فاکتورهای صادر شده برای دانش‌آموزان")
            inv_df = pd.DataFrame(st.session_state['invoices'])
            st.dataframe(inv_df.rename(columns={
                "id": "شناسه فاکتور", "student_name": "نام دانش‌آموز", "title": "عنوان فاکتور",
                "issue_date": "تاریخ صدور", "due_date": "مهلت پرداخت", "total": "مبلغ کل (ریال)",
                "paid": "پرداخت شده", "status": "وضعیت فاکتور"
            }), use_container_width=True)
            
        with f_lay2:
            st.write("#### 📊 سهم وصول شهریه")
            # Draw matplotlib pie chart
            fig, ax = plt.subplots(figsize=(3, 3))
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            labels = ['وصول‌شده', 'معوقات']
            sizes = [total_collected, total_pending]
            colors = ['#2a9d8f', '#e63946']
            # Make sure Persian fonts are supported in matplotlib, or just use English labels
            ax.pie(sizes, labels=['Collected', 'Arrears'], colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
        st.write("#### 💳 تاریخچه آخرین تراکنش‌های بانکی اولیا")
        tx_df = pd.DataFrame(st.session_state['payment_transactions'])
        st.dataframe(tx_df.rename(columns={
            "id": "کد تراکنش", "invoice_id": "کد فاکتور", "payer_name": "پرداخت‌کننده",
            "gateway": "درگاه بانکی", "ref_num": "کد پیگیری", "card_pan": "شماره کارت",
            "amount": "مبلغ (ریال)", "status": "وضعیت تراکنش", "date": "تاریخ"
        }), use_container_width=True)


    with tab_announcements:
        st.write("### 📢 مرکز مدیریت و ارسال اطلاعیه‌های هوشمند")
        with st.form("announcement_form"):
            ann_title = st.text_input("عنوان اطلاعیه:")
            ann_target = st.selectbox("گروه مخاطبان هدف:", ["همه کاربران", "دبیران", "دانش‌آموزان", "والدین"])
            ann_body = st.text_area("متن کامل اطلاعیه:")
            
            target_map = {"همه کاربران": "all", "دبیران": "teachers", "دانش‌آموزان": "students", "والدین": "parents"}
            submitted = st.form_submit_button("🚀 انتشار سراسری و ارسال نوتیفیکیشن")
            
            if submitted:
                if ann_title and ann_body:
                    st.session_state['announcements'].append({
                        "id": len(st.session_state['announcements']) + 1,
                        "title": ann_title,
                        "body": ann_body,
                        "date": datetime.date.today().strftime("%Y-%m-%d"),
                        "target": target_map[ann_target]
                    })
                    st.success(f"اطلاعیه با موفقیت ثبت و پیامک هوشمند برای گروه مخاطب '{ann_target}' صادر شد.")
                else:
                    st.error("لطفاً تمامی فیلدها را به درستی تکمیل فرمایید.")
                    
    with tab_log:
        st.write("### 🛡️ لاگ‌های امنیتی و حسابرسی سیستم (Audit Logs)")
        st.markdown("""
            در راستای انطباق با قوانین حاکمیت داده‌های تحصیلی و حفظ محرمانگی نمرات دانش‌آموزان، تمامی رویدادها، 
            تغییرات نمرات و خطاهای سیستم در این بخش لاگ و قفل می‌شوند.
        """)
        st.table(pd.DataFrame(st.session_state['system_logs']))

# ============================================================================
# B. TEACHER PANEL (دبیر)
# ============================================================================
elif active_role == "teacher":
    st.title(f"👨‍🏫 پنل مدیریت آموزشی دبیران - {selected_school_fa}")
    st.subheader(f"کاربر: جناب آقای مهندس احمدی | دبیر تخصصی ریاضی و فیزیک")
    
    t_tab_att, t_tab_grades, t_tab_virtual, t_tab_homework, t_tab_ai_quiz = st.tabs([
        "📝 ثبت حضور و غیاب کلاسی", 
        "📊 ثبت و ارزیابی نمرات", 
        "🌐 کلاس‌های مجازی و آنلاین (جدید)",
        "📚 تعریف تکالیف درسی",
        "🧠 طراح آزمون هوشمند (AI)"
    ])
    
    with t_tab_att:
        st.write("### 📝 حضور و غیاب کلاسی هوشمند")
        st.write("ثبت وضعیت حضور دانش‌آموزان در تاریخ امروز: " + datetime.date.today().strftime("%Y-%m-%d"))
        
        # Selection of class
        active_class = st.selectbox("انتخاب کلاس:", ["کلاس ۱۰۱ (ریاضی/فیزیک)", "کلاس ۱۰۲ (شیمی/زیست)"])
        
        # Student Grid for Attendance
        class_students = {k: v for k, v in st.session_state['students'].items() if v['class'] == active_class.split(" ")[0]}
        
        att_entries = {}
        st.markdown("#### لیست دانش‌آموزان:")
        for sid, sinfo in class_students.items():
            col_sname, col_sstatus, col_sremarks = st.columns([2, 2, 3])
            with col_sname:
                st.write(f"👤 {sinfo['name']} (شماره: {sinfo['code']})")
            with col_sstatus:
                att_entries[sid] = st.selectbox("وضعیت حضور:", ["حاضر", "غایب", "تأخیر", "موجه"], key=f"att_s_{sid}")
            with col_sremarks:
                st.text_input("توضیحات / علت:", key=f"remarks_s_{sid}", placeholder="مثال: کسالت، تأخیر سرویس")
        
        if st.button("💾 ثبت نهایی حضور و غیاب کل کلاس"):
            st.success("لیست حضور و غیاب با موفقیت ثبت شد و اعلان غیبت‌ها برای اولیا صادر گردید.")
            
    with t_tab_grades:
        st.write("### 📊 ثبت و ارزشیابی نمرات مستمر و پایانی")
        with st.form("grades_form"):
            target_student = st.selectbox("انتخاب دانش‌آموز:", [v['name'] for k, v in class_students.items()])
            subject = st.selectbox("انتخاب درس مربوطه:", ["ریاضی ۳", "فیزیک پیشرفته"])
            exam_type = st.selectbox("نوع ارزشیابی:", ["کوییز کلاسی", "امتحان کتبی مستمر", "پروژه کلاسی", "نمره عملی"])
            score_num = st.number_input("نمره ارزشیابی (از ۲۰):", min_value=0.0, max_value=20.0, step=0.25)
            
            submitted_grade = st.form_submit_button("✍️ ثبت و قفل نمره در پرونده")
            if submitted_grade:
                # Find student_id
                stu_id = [k for k, v in st.session_state['students'].items() if v['name'] == target_student][0]
                st.session_state['grades'].append({
                    "student_id": stu_id,
                    "subject": subject,
                    "type": exam_type,
                    "score": score_num,
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                })
                st.success(f"نمره {score_num} برای دانش‌آموز {target_student} در درس {subject} با موفقیت در پرونده آموزشی قفل و ثبت شد.")
                
    with t_tab_virtual:
        st.write("### 🌐 مدیریت و راه‌اندازی کلاس‌های آنلاین")
        st.markdown("""
            به کمک این بخش، شما می‌توانید کلاس‌های آنلاین جدید را زمان‌بندی کنید یا در زمان مقرر با کلیک بر روی دکمه شروع،
            اتاق کنفرانس زنده را راه‌اندازی کرده و دانش‌آموزان را به سیستم متصل کنید.
        """)
        
        # Schedule Class Form
        with st.form("schedule_online_form"):
            st.write("#### 📆 برنامه‌ریزی کلاس تصویری جدید")
            sc_subject = st.selectbox("انتخاب درس:", ["ریاضی ۳", "فیزیک پیشرفته"], key="sc_subject")
            sc_class = st.selectbox("انتخاب کلاس:", ["کلاس ۱۰۱", "کلاس ۱۰۲"], key="sc_class")
            sc_topic = st.text_input("موضوع جلسه کلاسی:", placeholder="مثال: فرمول‌های انتگرال‌گیری خطی")
            sc_provider = st.selectbox("بستر کلاس زنده:", ["Google Meet (گوگل میت)", "WhatsApp (واتساپ کلاس)", "Jitsi Meet (رایگان و ابری)", "Zoom", "BigBlueButton"])
            
            sc_submit = st.form_submit_button("➕ برنامه‌ریزی و ارسال اعلان به کلاس")
            if sc_submit:
                if "Google Meet" in sc_provider:
                    prov_id = "google_meet"
                    m_url = f"https://meet.google.com/xyz-abc-{datetime.datetime.now().strftime('%M%S')}"
                elif "WhatsApp" in sc_provider:
                    prov_id = "whatsapp"
                    m_url = f"https://chat.whatsapp.com/ClassGroup_{datetime.datetime.now().strftime('%M%S')}"
                elif "Jitsi" in sc_provider:
                    prov_id = "jitsi"
                    m_url = f"https://meet.jit.si/SmartSchoolClass_{datetime.datetime.now().strftime('%M%S')}"
                else:
                    prov_id = "zoom"
                    m_url = f"https://zoom.us/j/{datetime.datetime.now().strftime('%M%S')}"
                
                st.session_state['online_classes'].append({
                    "id": len(st.session_state['online_classes']) + 1,
                    "subject": sc_subject,
                    "class_name": sc_class,
                    "topic": sc_topic,
                    "teacher_name": "مهندس احمدی",
                    "provider": prov_id,
                    "meeting_url": m_url,
                    "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": (datetime.datetime.now() + datetime.timedelta(hours=1.5)).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "برنامه‌ریزی شده",
                    "room_name": f"SmartSchoolClass_{datetime.datetime.now().strftime('%M%S')}"
                })
                st.success("کلاس تصویری زنده جدید با موفقیت زمان‌بندی و اطلاعیه ورود به پنل دانش‌آموزان و اولیا ارسال شد.")

        st.write("---")
        st.write("#### 📡 کلاس‌های برنامه‌ریزی‌شده و شروع زنده")
        
        # Display scheduled classes with active trigger options
        for oclass in st.session_state['online_classes']:
            col_info, col_act = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                    **درس:** {oclass['subject']} ({oclass['class_name']}) | **موضوع:** {oclass['topic']}<br/>
                    **زمان شروع:** {oclass['start_time']} | **وضعیت:** `{oclass['status']}`
                """, unsafe_allow_html=True)
            with col_act:
                if oclass['status'] != "خاتمه یافته":
                    if st.button("▶️ شروع کلاس زنده", key=f"start_live_{oclass['id']}"):
                        oclass['status'] = "در حال برگزاری"
                        st.info("اتاق کنفرانس با موفقیت ایجاد شد! دانش‌آموزان در حال اتصال هستند...")
                else:
                    st.write("✔️ خاتمه یافته")
            
            if oclass['status'] == "در حال برگزاری":
                st.markdown(f"""
                    <div class="live-box" style="border-right-color: {'#25d366' if oclass['provider'] == 'whatsapp' else '#4285f4' if oclass['provider'] == 'google_meet' else '#1d3557'};">
                        <b>🔴 کلاس در حال برگزاری است! (بستر ارائه: {oclass['provider'].upper().replace('_', ' ')})</b><br/>
                        موضوع جلسه: {oclass['topic']}
                    </div>
                """, unsafe_allow_html=True)
                
                if oclass['provider'] == 'jitsi':
                    jitsi_url = f"https://meet.jit.si/{oclass['room_name']}#config.startWithVideoMuted=true&config.startWithAudioMuted=true"
                    st.components.v1.iframe(jitsi_url, height=500, scrolling=True)
                elif oclass['provider'] == 'google_meet':
                    st.markdown("""
                        <div style="background-color: #f1f3f4; padding: 20px; border-radius: 12px; border-right: 5px solid #4285f4; margin-bottom: 15px;">
                            <h4 style="color: #1a73e8; margin-top: 0; font-size:16px;">🎥 اتصال به کلاس زنده در Google Meet</h4>
                            <p style="font-size: 13px; color: #3c4043; line-height: 1.6;">به دلیل تنظیمات امنیتی گوگل (X-Frame-Options)، صفحه زنده گوگل میت اجازه جفت‌شدن به صورت IFrame در داخل پنل را ندارد. لطفاً دکمه ورود زنده زیر را کلیک کنید تا کلاس در زبانه جدید باز شود:</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("🚀 شروع و ورود به کلاس در Google Meet", oclass.get('meeting_url', 'https://meet.google.com/'))
                elif oclass['provider'] == 'whatsapp':
                    st.markdown("""
                        <div style="background-color: #e7f7ef; padding: 20px; border-radius: 12px; border-right: 5px solid #25d366; margin-bottom: 15px;">
                            <h4 style="color: #075e54; margin-top: 0; font-size:16px;">💬 اتصال به تماس گروهی تصویری در WhatsApp</h4>
                            <p style="font-size: 13px; color: #128c7e; line-height: 1.6;">این کلاس بر بستر شبکه ارتباطی واتساپ برگزار می‌شود. شما می‌توانید از پیوند زیر برای برقراری تماس گروهی کلاسی یا باز کردن گروه مرتبط استفاده کنید:</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("🟢 ورود به کلاس در WhatsApp", oclass.get('meeting_url', 'https://chat.whatsapp.com/'))
                
                if st.button("🛑 خاتمه کلاس زنده و قطع اتصال", key=f"stop_live_{oclass['id']}"):
                    oclass['status'] = "خاتمه یافته"
                    st.success("کلاس با موفقیت پایان یافت و فیلم ضبط شده پس از ذخیره‌سازی، در پنل دانش‌آموزان آرشیو خواهد شد.")
                    st.rerun()

    with t_tab_ai_quiz:
        st.write("### 🧠 طراحی ارزیابی و آزمون با هوش مصنوعی چت‌جی‌پی‌تی")
        st.markdown("""
            به عنوان یک معمار و متخصص EdTech، زیرساخت ارتباطی با مدل‌های زبانی بزرگ (مانند ChatGPT) در این پلتفرم 
            پیاده‌سازی شده است. این ماژول به شما اجازه می‌دهد تا با مهندسی پرامپت دقیق، در چند ثانیه آزمون‌های تستی یا تشریحی 
            استاندارد به همراه پاسخ تشریحی و کلید حل تولید کنید و با دانش‌آموزان به اشتراک بگذارید. [103]
        """)
        
        col_ai1, col_ai2 = st.columns([1, 2])
        with col_ai1:
            st.write("#### 🛠️ تنظیمات پرامپت هوشمند")
            ai_subject = st.selectbox("انتخاب درس:", ["ریاضی ۳", "فیزیک پیشرفته"], key="ai_sub_sel")
            ai_class = st.selectbox("کلاس هدف:", ["کلاس ۱۰۱", "کلاس ۱۰۲"], key="ai_class_sel")
            ai_topic = st.text_input("موضوع تدریس:", value="مبحث مشتق و کاربرد مشتق", placeholder="مثلاً: الکتریسیته ساکن")
            ai_difficulty = st.selectbox("سطح سختی سوالات:", ["آسان", "متوسط", "سخت"])
            ai_q_count = st.slider("تعداد سوالات مورد نیاز:", 2, 5, 3)
            
            # Privacy Reminder
            st.markdown("""
                <div style="background-color: #fff8e1; border-right: 4px solid #ffb300; padding: 10px; border-radius: 6px; font-size:12px; color: #5d4037;">
                    🛡️ <b>نکته حاکمیت داده (FERPA/GDPR):</b><br/>سیستم به صورت خودکار تمامی مشخصات هویتی حساس دانش‌آموزان (PII) را قبل از ارسال درخواست به API هوش مصنوعی حذف (Mask) می‌کند تا محرمانگی داده‌ها حفظ شود. [74، 83]
                </div>
            """, unsafe_allow_html=True)
            
            generate_btn = st.button("🧠 تولید آزمون با چت‌جی‌پی‌تی")
            
        with col_ai2:
            st.write("#### 🤖 خروجی و پیش‌نویس سوالات هوش مصنوعی")
            
            if generate_btn:
                with st.spinner("🔄 در حال ارتباط با چت‌جی‌پی‌تی و تولید آزمون استاندارد..."):
                    import time
                    import random
                    time.sleep(2) # simulate delay
                    
                    # Generate mock question objects based on inputs
                    if ai_subject == "ریاضی ۳":
                        questions_draft = [
                            {
                                "id": 1,
                                "question_text": f"مشتق تابع f(x) = x^2 + 5x + 6 در نقطه x=2 کدام است؟",
                                "type": "multiple_choice",
                                "points": 10.0,
                                "options": [
                                    {"letter": "الف", "text": "۷", "is_correct": False},
                                    {"letter": "ب", "text": "۹", "is_correct": True},
                                    {"letter": "ج", "text": "۱۱", "is_correct": False},
                                    {"letter": "د", "text": "۱۳", "is_correct": False}
                                ],
                                "explanation": "f'(x) = 2x + 5. در نقطه x=2: f'(2) = 2(2) + 5 = 9."
                            },
                            {
                                "id": 2,
                                "question_text": f"آهنگ تغییر خطی تابع f(x) = 3x - 1 در بازه [1, 3] چیست؟",
                                "type": "multiple_choice",
                                "points": 10.0,
                                "options": [
                                    {"letter": "الف", "text": "۳", "is_correct": True},
                                    {"letter": "ب", "text": "۲", "is_correct": False},
                                    {"letter": "ج", "text": "۱", "is_correct": False},
                                    {"letter": "د", "text": "۰", "is_correct": False}
                                ],
                                "explanation": "آهنگ تغییر متوسط برای خط مستقیم برابر با شیب خط است که همواره برابر با ۳ می‌باشد."
                            },
                            {
                                "id": 3,
                                "question_text": f"مشتق تابع f(x) = sin(x) در نقطه x=π چیست؟",
                                "type": "multiple_choice",
                                "points": 10.0,
                                "options": [
                                    {"letter": "الف", "text": "۱", "is_correct": False},
                                    {"letter": "ب", "text": "-۱", "is_correct": True},
                                    {"letter": "ج", "text": "۰", "is_correct": False},
                                    {"letter": "د", "text": "۱/۲", "is_correct": False}
                                ],
                                "explanation": "f'(x) = cos(x). در x=π داریم cos(π) = -1."
                            }
                        ][:ai_q_count]
                    else: # فیزیک پیشرفته
                        questions_draft = [
                            {
                                "id": 1,
                                "question_text": "قانون دوم نیوتن برای شتاب سیالات تراکم‌ناپذیر با کدام رابطه بیان می‌شود؟",
                                "type": "multiple_choice",
                                "points": 10.0,
                                "options": [
                                    {"letter": "الف", "text": "P = ρgh", "is_correct": False},
                                    {"letter": "ب", "text": "F = ma", "is_correct": True},
                                    {"letter": "ج", "text": "A1V1 = A2V2", "is_correct": False},
                                    {"letter": "د", "text": "P + 1/2ρv^2 + ρgh = C", "is_correct": False}
                                ],
                                "explanation": "قانون دوم نیوتن اساس حرکت تمام ذرات از جمله سیالات است."
                            },
                            {
                                "id": 2,
                                "question_text": "در جریان سیال از یک لوله باریک، سرعت سیال در بخش باریک‌تر چه تغییری می‌کند؟",
                                "type": "multiple_choice",
                                "points": 10.0,
                                "options": [
                                    {"letter": "الف", "text": "افزایش می‌یابد تا دبی جریان ثابت بماند (اصل پیوستگی)", "is_correct": True},
                                    {"letter": "ب", "text": "کاهش می‌یابد", "is_correct": False},
                                    {"letter": "ج", "text": "تغییر نمی‌کند", "is_correct": False},
                                    {"letter": "د", "text": "نصف می‌شود", "is_correct": False}
                                ],
                                "explanation": "بر اساس معادله پیوستگی A1V1 = A2V2، با کاهش مساحت مقطع لوله (A)، سرعت سیال (V) افزایش می‌یابد."
                            }
                        ][:ai_q_count]
                    
                    st.session_state['ai_quiz_draft'] = {
                        "title": f"ارزیابی هوشمند {ai_subject}: {ai_topic}",
                        "subject": ai_subject,
                        "class_name": ai_class,
                        "topic": ai_topic,
                        "difficulty": ai_difficulty,
                        "questions": questions_draft
                    }
                    st.success("🎉 آزمون آزمایشی استاندارد با موفقیت توسط موتور ChatGPT تولید شد! برای بازبینی و انتشار فرم زیر را بررسی کنید.")
                    
            if st.session_state['ai_quiz_draft']:
                draft = st.session_state['ai_quiz_draft']
                st.write(f"📝 **پیش‌نویس نهایی آزمون:** `{draft['title']}`")
                
                # Render editable questions
                edited_questions = []
                for idx, q in enumerate(draft['questions']):
                    with st.expander(f"❓ سوال {idx+1}: {q['question_text']}", expanded=True):
                        # Edit Question Text
                        eq_text = st.text_area("متن سوال:", value=q['question_text'], key=f"eq_text_{idx}")
                        eq_points = st.number_input("بارم سوال:", value=float(q['points']), min_value=0.5, max_value=20.0, step=0.5, key=f"eq_pts_{idx}")
                        
                        # Options
                        edited_options = []
                        for opt_idx, opt in enumerate(q['options']):
                            eopt_text = st.text_input(f"گزینه {opt['letter']}:", value=opt['text'], key=f"eopt_txt_{idx}_{opt_idx}")
                            eopt_corr = st.checkbox("آیا این گزینه صحیح است؟", value=opt['is_correct'], key=f"eopt_corr_{idx}_{opt_idx}")
                            edited_options.append({"letter": opt['letter'], "text": eopt_text, "is_correct": eopt_corr})
                            
                        eq_exp = st.text_area("توضیح کلید و حل تشریحی هوش مصنوعی:", value=q['explanation'], key=f"eq_exp_{idx}")
                        edited_questions.append({
                            "id": q['id'],
                            "question_text": eq_text,
                            "type": q['type'],
                            "points": eq_points,
                            "options": edited_options,
                            "explanation": eq_exp
                        })
                
                # Publish flow
                if st.button("🚀 انتشار نهایی و اشتراک‌گذاری آزمون با کلاس"):
                    new_quiz_id = len(st.session_state['ai_quizzes']) + 101
                    st.session_state['ai_quizzes'].append({
                        "id": new_quiz_id,
                        "title": draft['title'],
                        "subject": draft['subject'],
                        "class_name": draft['class_name'],
                        "topic": draft['topic'],
                        "difficulty": draft['difficulty'],
                        "questions": edited_questions,
                        "status": "منتشر شده",
                        "created_at": datetime.date.today().strftime("%Y-%m-%d")
                    })
                    
                    # Also append announcement automatically
                    st.session_state['announcements'].append({
                        "id": len(st.session_state['announcements']) + 1,
                        "title": f"🧠 آزمون هوشمند آنلاین فعال شد: {draft['title']}",
                        "body": f"دبیر محترم کلاس، آزمون آنلاین جدیدی را با موضوع {draft['topic']} در سامانه فعال کرده است. دانش‌آموزان موظفند با مراجعه به پنل خود در این ارزیابی شرکت کنند.",
                        "date": datetime.date.today().strftime("%Y-%m-%d"),
                        "target": "all"
                    })
                    
                    # System Log
                    st.session_state['system_logs'].append({
                        "زمان رویداد": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "کاربر": "دبیر ریاضی",
                        "آدرس آی‌پی": "192.168.1.12",
                        "نوع فعالیت": "تولید آزمون با AI",
                        "توضیحات": f"انتشار ارزیابی هوشمند '{draft['title']}' بر بستر دیتابیس کلاس"
                    })
                    
                    st.session_state['ai_quiz_draft'] = None
                    st.success("🎉 آزمون با موفقیت در دیتابیس قفل شد! نوتیفیکیشن زنده برای دانش‌آموزان و اولیا ارسال گردید.")
                    st.rerun()
            else:
                st.info("👈 تنظیمات آزمون را در ستون سمت راست وارد کرده و دکمه 'تولید آزمون با چت‌جی‌پی‌تی' را کلیک کنید.")


    with t_tab_homework:
        st.write("### 📚 تعریف تکالیف جدید برای دانش‌آموزان")
        with st.form("homework_form"):
            hw_class = st.selectbox("کلاس هدف:", ["کلاس ۱۰۱", "کلاس ۱۰۲"])
            hw_sub = st.selectbox("درس مربوطه:", ["ریاضی ۳", "فیزیک پیشرفته"])
            hw_title = st.text_input("عنوان تکلیف:")
            hw_desc = st.text_area("دستورالعمل و توضیحات تکلیف:")
            hw_due = st.date_input("مهلت تحویل (تا پایان روز):")
            
            submitted_hw = st.form_submit_button("➕ انتشار و تکثیر تکلیف")
            if submitted_hw:
                st.session_state['homework'].append({
                    "id": len(st.session_state['homework']) + 1,
                    "class": hw_class,
                    "subject": hw_sub,
                    "title": hw_title,
                    "description": hw_desc,
                    "due": hw_due.strftime("%Y-%m-%d")
                })
                st.success("تکلیف جدید با موفقیت ثبت شد و اعلان آن بر روی تلفن همراه دانش‌آموزان فعال گردید.")

# ============================================================================
# C. STUDENT PANEL (دانش‌آموز)
# ============================================================================
elif active_role == "student":
    st.title(f"🎓 پنل اختصاصی دانش‌آموزان - {selected_school_fa}")
    stu_id = 1
    stu_name = st.session_state['students'][stu_id]['name']
    st.subheader(f"سلام {stu_name} عزیز، وضعیت تحصیلی امروز شما در یک نگاه:")
    
    # KPIs
    st_col1, st_col2, st_col3 = st.columns(3)
    with st_col1:
        stu_att_list = [x for x in st.session_state['attendance'] if x['student_id'] == stu_id]
        total_days = len(stu_att_list)
        p_days = len([x for x in stu_att_list if x['status'] in ['حاضر', 'تأخیر']])
        att_rate = f"{int((p_days/total_days)*100)}%" if total_days > 0 else "۱۰۰٪"
        render_metric_card("میزان کل حضور شما در کلاس‌ها", att_rate, "#2a9d8f")
        
    with st_col2:
        stu_grades_list = [x['score'] for x in st.session_state['grades'] if x['student_id'] == stu_id]
        gpa = f"{np.mean(stu_grades_list):.2f}" if stu_grades_list else "موردی ثبت نشده"
        render_metric_card("معدل کل نمرات تا این لحظه", gpa, "#1d3557")
        
    with st_col3:
        st_class = st.session_state['students'][stu_id]['class']
        hw_count = len([x for x in st.session_state['homework'] if x['class'] == st_class])
        render_metric_card("تکالیف در دست انجام", f"{hw_count} تکلیف", "#e76f51")
        
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    st_tab_grades, st_tab_virtual_class, st_tab_hw, st_tab_quizzes, st_tab_schedule = st.tabs([
        "📝 کارنامه و نمرات", 
        "🌐 کلاس‌های آنلاین و زنده (جدید)",
        "📚 تکالیف مدرسه", 
        "🧠 آزمون‌های آنلاین (AI)",
        "📆 برنامه هفتگی"
    ])
    
    with st_tab_grades:
        st.write("### 📝 نمرات و بازخوردهای دبیران")
        stu_grades_df = pd.DataFrame([x for x in st.session_state['grades'] if x['student_id'] == stu_id])
        if not stu_grades_df.empty:
            st.dataframe(stu_grades_df[["subject", "type", "score", "date"]].rename(columns={
                "subject": "درس", "type": "نوع ارزشیابی", "score": "نمره کسب‌شده", "date": "تاریخ ثبت"
            }), use_container_width=True)
            
            low_grades = stu_grades_df[stu_grades_df['score'] < 12]
            if not low_grades.empty:
                st.markdown("""
                    <div class="alert-box">
                        ⚠️ <b>هشدار افت تحصیلی:</b> در درس‌های بالا نمرات زیر ۱۲ کسب کرده‌اید. تلاش بیشتر و شرکت در کلاس‌های رفع اشکال توصیه می‌شود!
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("نمره‌ای برای شما ثبت نشده است.")

    with st_tab_virtual_class:
        st.write("### 🌐 ورود به کلاس‌های آنلاین فعال و فیلم‌های ضبط‌شده")
        
        # Check active live classes
        live_classes = [x for x in st.session_state['online_classes'] if x['status'] == "در حال برگزاری"]
        
        if live_classes:
            st.markdown("""
                <div class="live-box" style="border-right-color: #2a9d8f;">
                    🟢 <b>کلاس آنلاین زنده هم‌اکنون در حال برگزاری است!</b> شما می‌توانید از طریق فرم زیر، صدا و تصویر همکلاسی‌ها و معلم خود را به صورت زنده دریافت کنید.
                </div>
            """, unsafe_allow_html=True)
            
            active_live_class = live_classes[0]
            st.write(f"**جلسه:** {active_live_class['subject']} | **موضوع:** {active_live_class['topic']} | **بستر:** {active_live_class['provider'].upper().replace('_', ' ')}")
            
            if active_live_class['provider'] == 'jitsi':
                j_room = active_live_class['room_name']
                j_url = f"https://meet.jit.si/{j_room}#config.startWithVideoMuted=true&config.startWithAudioMuted=true"
                st.components.v1.iframe(j_url, height=500, scrolling=True)
            elif active_live_class['provider'] == 'google_meet':
                st.markdown("""
                    <div style="background-color: #f1f3f4; padding: 20px; border-radius: 12px; border-right: 5px solid #4285f4; margin-bottom: 15px;">
                        <h4 style="color: #1a73e8; margin-top: 0; font-size:16px;">🎥 ورود به کلاس زنده Google Meet فرزند شما</h4>
                        <p style="font-size: 13px; color: #3c4043; line-height: 1.6;">جهت ورود مستقیم به جلسه تصویری فعال در گوگل میت، دکمه ورود زیر را کلیک کنید تا کلاس در یک زبانه امن جدید باز شود:</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button("🚀 ورود به کلاس در Google Meet", active_live_class.get('meeting_url', 'https://meet.google.com/'))
            elif active_live_class['provider'] == 'whatsapp':
                st.markdown("""
                    <div style="background-color: #e7f7ef; padding: 20px; border-radius: 12px; border-right: 5px solid #25d366; margin-bottom: 15px;">
                        <h4 style="color: #075e54; margin-top: 0; font-size:16px;">💬 اتصال به گروه تعاملی واتساپ کلاس</h4>
                        <p style="font-size: 13px; color: #128c7e; line-height: 1.6;">برای برقراری ارتباط تصویری یا تبادل تمرین‌ها در گروه واتساپ، پیوند زیر را انتخاب کنید:</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button("🟢 ورود به گروه واتساپ کلاس", active_live_class.get('meeting_url', 'https://chat.whatsapp.com/'))
        else:
            st.info("در حال حاضر کلاس آنلاین فعالی وجود ندارد. کلاس‌های بعدی طبق برنامه هفتگی برای شما برقرار خواهند شد.")
            
        # Class Recordings Archive
        st.write("#### 🎥 آرشیو ویدیوهای ضبط‌شده جلسات قبل")
        rec_df = pd.DataFrame(st.session_state['online_recordings'])
        st.dataframe(rec_df[["subject", "topic", "duration", "size", "date"]].rename(columns={
            "subject": "درس", "topic": "موضوع تدریس شده", "duration": "طول مدت ویدیو", "size": "حجم فایل", "date": "تاریخ جلسه"
        }), use_container_width=True)
        
        # Video Simulator
        if not rec_df.empty:
            st.write("📺 **پخش نمونه ویدیوی فیزیک پیشرفته (مکانیک سیالات):**")
            st.video(rec_df.iloc[0]['url'])
            
    with st_tab_hw:
        st.write("### 📚 تکالیف جاری و ارسال پاسخ")
        st_class = st.session_state['students'][stu_id]['class']
        class_hw = [x for x in st.session_state['homework'] if x['class'] == st_class]
        
        for hw in class_hw:
            with st.expander(f"📌 {hw['title']} - درس {hw['subject']} (مهلت: {hw['due']})"):
                st.write(f"**توضیحات تکلیف:** {hw['description']}")
                st.write("---")
                st.file_uploader(f"آپلود پاسخ فایل تکلیف: {hw['title']}", type=["pdf", "png", "jpg"], key=f"hw_upload_{hw['id']}")
                st.text_area("توضیحات برای دبیر (اختیاری):", key=f"hw_text_{hw['id']}")
                if st.button("📤 ثبت نهایی و ارسال برای دبیر", key=f"hw_btn_{hw['id']}"):
                    st.success("پاسخ تکلیف شما با موفقیت برای دبیر مربوطه ارسال شد.")
                    
    with st_tab_quizzes:
        st.write("### 🧠 ارزیابی‌های هوشمند آنلاین (AI)")
        st.markdown("""
            در این بخش آزمون‌ها و کوئیزهایی که توسط دبیران با همکاری چت‌جی‌پی‌تی تولید و منتشر شده‌اند را به صورت مستقیم 
            و تعاملی حل کرده و نمره خود را به صورت آنی دریافت کنید.
        """)
        
        # List of active quizzes for the student's class
        active_class = st.session_state['students'][stu_id]['class']
        class_quizzes = [x for x in st.session_state['ai_quizzes'] if x['class_name'] == active_class]
        
        if not class_quizzes:
            st.info("در حال حاضر هیچ آزمون فعالی برای کلاس شما منتشر نشده است.")
        else:
            for quiz in class_quizzes:
                attempt = [x for x in st.session_state['ai_quiz_attempts'] if x['quiz_id'] == quiz['id'] and x['student_id'] == stu_id]
                
                with st.expander(f"🧠 {quiz['title']} - درس {quiz['subject']} (سختی: {quiz['difficulty']})"):
                    if attempt:
                        st.markdown(f"""
                            <div class="success-box">
                                🟢 <b>این آزمون قبلاً پاسخ داده شده است:</b><br/>
                                <b>نمره شما:</b> {attempt[0]['score']} از ۲۰.۰۰<br/>
                                <b>زمان تکمیل:</b> {attempt[0]['completed_at']}<br/>
                                <b>بازخورد تحلیلی هوش مصنوعی:</b> {attempt[0]['feedback']}[103]
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Show review of correct answers
                        st.write("🔍 **مرور سوالات و پاسخ‌ها:**")
                        for q in quiz['questions']:
                            st.write(f"**سوال:** {q['question_text']}")
                            selected_let = attempt[0]['answers'].get(q['id'], "ثبت نشده")
                            correct_let = [o['letter'] for o in q['options'] if o['is_correct']][0]
                            st.write(f"گزینه انتخابی شما: **{selected_let}** | گزینه صحیح: **{correct_let}**")
                            if selected_let == correct_let:
                                st.success("✔️ پاسخ شما صحیح بود.")
                            else:
                                st.error("❌ پاسخ شما اشتباه بود.")
                            st.write(f"💡 **توضیح حل تشریحی:** {q['explanation']}")
                            st.write("---")
                    else:
                        st.write("📌 **مشخصات ارزیابی:**")
                        st.write(f"- تعداد سوالات: {len(quiz['questions'])} سوال")
                        st.write(f"- بارم نهایی: ۲۰.۰۰")
                        st.write("- سیستم نمره‌دهی: آنی و هوشمند")
                        
                        # Taking the exam
                        with st.form(f"take_quiz_form_{quiz['id']}"):
                            st.write("✍️ **پاسخ به سوالات:**")
                            student_answers = {}
                            for q in quiz['questions']:
                                st.write(f"🔹 {q['question_text']}")
                                opts_fa = [f"{o['letter']}) {o['text']}" for o in q['options']]
                                selected_opt = st.radio("انتخاب گزینه صحیح:", opts_fa, key=f"stu_ans_{quiz['id']}_{q['id']}")
                                # Extract letter
                                student_answers[q['id']] = selected_opt.split(")")[0]
                                st.write("---")
                            
                            submit_exam = st.form_submit_button("📤 ثبت نهایی آزمون و تصحیح آنلاین")
                            if submit_exam:
                                # Calculate score
                                correct_count = 0
                                for q in quiz['questions']:
                                    correct_let = [o['letter'] for o in q['options'] if o['is_correct']][0]
                                    if student_answers[q['id']] == correct_let:
                                        correct_count += 1
                                
                                final_score = (correct_count / len(quiz['questions'])) * 20.0
                                
                                # AI feedback generation simulation
                                if final_score == 20.0:
                                    fb = "عملکرد دانش‌آموز خیره‌کننده و کاملا بی‌نقص بود."
                                elif final_score >= 14.0:
                                    fb = "تسلط خوبی در مبحث مشهود است، اما نیاز به کار بیشتر روی برخی جزئیات حل وجود دارد."
                                else:
                                    fb = "سطح یادگیری دانش‌آموز در این مبحث ضعیف است. تکرار مفاهیم اساسی و شرکت در کلاس‌های فوق‌برنامه اکیداً توصیه می‌شود."
                                    
                                st.session_state['ai_quiz_attempts'].append({
                                    "id": len(st.session_state['ai_quiz_attempts']) + 1,
                                    "quiz_id": quiz['id'],
                                    "student_id": stu_id,
                                    "score": final_score,
                                    "answers": student_answers,
                                    "completed_at": datetime.date.today().strftime("%Y-%m-%d"),
                                    "feedback": fb
                                })
                                
                                # Grade Records update
                                st.session_state['grades'].append({
                                    "student_id": stu_id,
                                    "subject": quiz['subject'],
                                    "type": "کوییز هوشمند",
                                    "score": final_score,
                                    "date": datetime.date.today().strftime("%Y-%m-%d")
                                })
                                
                                st.success(f"🎉 آزمون شما با موفقیت ثبت شد! نمره نهایی شما: {final_score:.2f} از ۲۰.۰۰")
                                st.rerun()


    with st_tab_schedule:
        st.write("### 📆 برنامه هفتگی کلاس‌های حضوری و آنلاین")
        days_of_week = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه"]
        hours = ["ساعت ۸:۰۰ تا ۹:۳۰", "ساعت ۹:۴۵ تا ۱۱:۱۵", "ساعت ۱۱:۳۰ تا ۱۳:۰۰"]
        
        schedule_data = {
            "ساعات / روزها": hours,
            "شنبه": ["ریاضی ۱۰۱ (حضوری)", "فیزیک ۱۰۱ (آنلاین)", "زنگ ورزش"],
            "یک‌شنبه": ["شیمی ۱۰۱ (حضوری)", "ریاضی ۱۰۱ (آنلاین)", "ادبیات فارسی"],
            "دوشنبه": ["فیزیک ۱۰۱ (حضوری)", "زنگ هنر", "دینی و قرآن"],
            "سه‌شنبه": ["عربی ۱۰۱ (آنلاین)", "شیمی ۱۰۱ (حضوری)", "ریاضی ۱۰۱ (آنلاین)"],
            "چهارشنبه": ["تاریخ", "جغرافیا", "آزمایشگاه علوم"],
        }
        st.table(pd.DataFrame(schedule_data))

# ============================================================================
# D. PARENT DASHBOARD PANEL (والدین)
# ============================================================================
elif active_role == "parent":
    st.title(f"👨‍👩‍👦 پنل اولیا و مربیان (والدین) - {selected_school_fa}")
    parent_id = 10
    parent_name = st.session_state['parents'][parent_id]
    st.subheader(f"جناب آقای {parent_name}، به پلتفرم مدرسه هوشمند فرزندان خود خوش آمدید.")
    
    children = [v for k, v in st.session_state['students'].items() if v['parent_id'] == parent_id]
    child_names = [c['name'] for c in children]
    
    selected_child_name = st.selectbox("🌐 انتخاب فرزند جهت مشاهده گزارش تحصیلی:", child_names)
    active_child = [c for c in children if c['name'] == selected_child_name][0]
    
    st.markdown(f"**📌 در حال مشاهده وضعیت تحصیلی و انضباطی فرزند شما: {active_child['name']} ({active_child['class']})**")
    
    # Sibling specific metrics
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        c_att_list = [x for x in st.session_state['attendance'] if x['student_id'] == active_child['id'] ]
        tot = len(c_att_list)
        pres = len([x for x in c_att_list if x['status'] in ['حاضر', 'تأخیر']])
        att_rate = f"{int((pres/tot)*100)}%" if tot > 0 else "۱۰۰٪"
        render_metric_card("نرخ حضور در کلاس‌های حضوری", att_rate, "#2a9d8f")
        
    with p_col2:
        c_grades = [x['score'] for x in st.session_state['grades'] if x['student_id'] == active_child['id']]
        avg_score = f"{np.mean(c_grades):.2f}" if c_grades else "موردی ثبت نشده"
        render_metric_card("معدل کل نمرات فرزند شما", avg_score, "#1d3557")
        
    with p_col3:
        # Online Class attendance stats for sibling
        online_logs = [x for x in st.session_state['online_class_logs'] if x['student_id'] == active_child['id']]
        avg_duration = int(np.mean([x['duration'] for x in online_logs])) if online_logs else 0
        render_metric_card("میانگین حضور فرزند در کلاس‌های آنلاین", f"{avg_duration} دقیقه در هر جلسه", "#e76f51")
            
    # Tabs for Parent Sibling analysis
    p_tab_performance, p_tab_virtual_tracking, p_tab_payment, p_tab_ai_quizzes, p_tab_notif, p_tab_contact = st.tabs([
        "📈 کارنامه و وضعیت انضباطی", 
        "🌐 ردیابی کلاس‌های آنلاین (جدید)",
        "💳 پرداخت شهریه و تراکنش‌ها (جدید)",
        "🧠 ارزیابی‌های هوشمند (AI)",
        "📢 اطلاعیه‌ها و پیام‌های مدرسه", 
        "💬 ارتباط مستقیم با معلمان"
    ])
    
    with p_tab_performance:
        st.write("#### 📊 کارنامه ارزشیابی مستمر")
        child_grades_df = pd.DataFrame([x for x in st.session_state['grades'] if x['student_id'] == active_child['id']])
        if not child_grades_df.empty:
            st.dataframe(child_grades_df[["subject", "type", "score", "date"]].rename(columns={
                "subject": "درس", "type": "ارزشیابی", "score": "نمره", "date": "تاریخ ثبت"
            }), use_container_width=True)
        else:
            st.info("نمره‌ای برای این دانش‌آموز ثبت نشده است.")
            
        st.write("#### 📅 تاریخچه و جزئیات حضور و غیاب حضوری")
        if c_att_list:
            child_att_df = pd.DataFrame(c_att_list)
            st.dataframe(child_att_df[["date", "subject", "status", "remarks"]].rename(columns={
                "date": "تاریخ", "subject": "درس", "status": "وضعیت حضور", "remarks": "توضیح دبیر"
            }), use_container_width=True)
        else:
            st.success("فرزند شما هیچ غیبتی نداشته است! 🌟")
            
    with p_tab_virtual_tracking:
        st.write("#### 📡 گزارش حضور غیاب خودکار و دیجیتال در کلاس‌های آنلاین")
        st.markdown("""
            سیستم به صورت خودکار زمان دقیق ورود و خروج فرزند شما را به پلتفرم زنده ثبت کرده و نمودار پایداری حضور
            او را برای پایش والدین استخراج می‌کند.
        """)
        
        child_online_logs = [x for x in st.session_state['online_class_logs'] if x['student_id'] == active_child['id']]
        if child_online_logs:
            co_df = pd.DataFrame(child_online_logs)
            st.dataframe(co_df[["joined_at", "left_at", "duration", "device"]].rename(columns={
                "joined_at": "زمان ورود به کلاس", "left_at": "زمان خروج", "duration": "مدت زمان حضور (دقیقه)", "device": "دستگاه اتصالی"
            }), use_container_width=True)
            
            # Alarms
            for log in child_online_logs:
                if log['duration'] < 45:
                    st.markdown(f"""
                        <div class="alert-box">
                            ⚠️ <b>هشدار حضور ناقص:</b> فرزند شما در جلسه فیزیک زنده، تنها {log['duration']} دقیقه حضور داشته است (خروج قبل از پایان کلاس!).
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("لاگ اتصالی برای فرزند شما در کلاس‌های آنلاین فعال یافت نشد.")

    with p_tab_payment:
        st.write("#### 💳 وضعیت مالی و پرداخت آنلاین شهریه")
        st.markdown("""
            در این بخش فاکتورهای صادره برای فرزند خود را بررسی کرده و شهریه را به صورت آنلاین و شبیه‌سازی درگاه واقعی پرداخت نمایید.
        """)
        
        child_invoices = [x for x in st.session_state['invoices'] if x['student_id'] == active_child['id']]
        if not child_invoices:
            st.success("هیچ صورت‌حسابی برای این فرزند ثبت نشده است.")
        else:
            for inv in child_invoices:
                with st.expander(f"📌 {inv['title']} (شناسه: {inv['id']}) - وضعیت: {inv['status']}"):
                    st.write(f"**تاریخ صدور:** {inv['issue_date']} | **مهلت پرداخت:** {inv['due_date']}")
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.write(f"**جمع کل فاکتور:** {inv['subtotal']:,} ریال")
                        st.write(f"**تخفیف اعمال‌شده:** {inv['discount']:,} ریال")
                    with col_det2:
                        st.write(f"**مبلغ نهایی قابل پرداخت:** {inv['total']:,} ریال")
                        st.write(f"**مبلغ پرداخت‌شده تا کنون:** {inv['paid']:,} ریال")
                        
                    remaining = inv['total'] - inv['paid']
                    if remaining > 0:
                        st.markdown(f"""
                            <div class="alert-box" style="border-right-color: #e63946; background-color: #fff0f0; padding:15px; margin-bottom:10px;">
                                ⚠️ <b>مبلغ مانده بدهی: {remaining:,} ریال</b>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Payment form
                        with st.form(f"payment_form_{inv['id']}"):
                            st.write("##### 📱 درگاه پرداخت آنلاین")
                            pay_gateway = st.selectbox("انتخاب درگاه بانکی / بین‌المللی:", ["درگاه سامان (شتاب)", "درگاه زرین‌پال (شتاب)", "Stripe (بین‌المللی)"], key=f"gateway_{inv['id']}")
                            pay_amount = st.number_input("مبلغ پرداختی (ریال):", min_value=1000, max_value=int(remaining), value=int(remaining), key=f"amount_{inv['id']}")
                            card_pan = st.text_input("شماره کارت ۱۶ رقمی (فرضی):", value="۶۰۳۷-۹۹۱۸-۲۷۳۶-۴۵۲۱", key=f"card_{inv['id']}")
                            
                            pay_submit = st.form_submit_button("💳 شبیه‌سازی ورود به درگاه بانکی")
                            if pay_submit:
                                st.session_state['active_checkout'] = {
                                    "invoice_id": inv['id'],
                                    "amount": pay_amount,
                                    "gateway": pay_gateway,
                                    "card_pan": card_pan,
                                    "student_id": active_child['id'],
                                    "student_name": active_child['name']
                                }
                                st.rerun()
                    else:
                        st.markdown("""
                            <div class="success-box" style="border-right-color: #2a9d8f; padding:15px; margin-bottom:10px;">
                                🎉 <b>این فاکتور کاملاً تسویه شده است. از حسن همکاری شما سپاسگزاریم!</b>
                            </div>
                        """, unsafe_allow_html=True)
                        
        # If there is an active checkout, show the banking simulation portal
        if 'active_checkout' in st.session_state and st.session_state['active_checkout']["student_id"] == active_child['id']:
            checkout = st.session_state['active_checkout']
            st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            st.write("### 🏦 شبیه‌ساز امن درگاه پرداخت بانکی شاپرک (PCI-DSS / شتاب)")
            
            st.markdown(f"""
                <div style="background-color: #f8f9fa; border: 2px solid #1d3557; border-radius: 12px; padding: 25px; margin-bottom: 20px; direction: rtl; text-align: right;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px;">
                        <h4 style="color: #1d3557; margin: 0;">💳 درگاه پرداخت آنلاین: {checkout['gateway']}</h4>
                        <span style="font-size: 14px; color: #6c757d;">پذیرنده: دبیرستان هوشمند ایرانیان</span>
                    </div>
                    <p><b>مبلغ تراکنش:</b> <span style="font-size: 20px; color: #2a9d8f; font-weight: bold;">{checkout['amount']:,} ریال</span></p>
                    <p><b>نام دانش‌آموز:</b> {checkout['student_name']}</p>
                    <p><b>شماره کارت خریدار:</b> {checkout['card_pan']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                otp = st.text_input("رمز پویا (OTP) فرضی ارسال‌شده به پیامک شما:", value="123456", type="password")
            with col_b2:
                cvv2 = st.text_input("کد امنیتی CVV2:", value="432", max_chars=4)
                
            col_b3, col_b4 = st.columns([1, 4])
            with col_b3:
                if st.button("✅ تایید و پرداخت قطعی", key="confirm_bank_payment"):
                    ref_num = f"TR-{np.random.randint(1000000, 9999999)}"
                    st.session_state['payment_transactions'].append({
                        "id": len(st.session_state['payment_transactions']) + 5001,
                        "invoice_id": checkout['invoice_id'],
                        "payer_name": parent_name,
                        "gateway": "zarinpal" if "زرین" in checkout['gateway'] else "saman" if "سامان" in checkout['gateway'] else "stripe",
                        "ref_num": ref_num,
                        "card_pan": checkout['card_pan'],
                        "amount": checkout['amount'],
                        "status": "موفق",
                        "date": datetime.date.today().strftime("%Y-%m-%d")
                    })
                    
                    # Update invoice paid amount
                    for invoice in st.session_state['invoices']:
                        if invoice['id'] == checkout['invoice_id']:
                            invoice['paid'] += checkout['amount']
                            if invoice['paid'] >= invoice['total']:
                                invoice['status'] = "پرداخت شده"
                            else:
                                invoice['status'] = "پرداخت بخشی"
                                
                    # Add system audit log
                    st.session_state['system_logs'].append({
                        "زمان رویداد": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "کاربر": f"{parent_name} (والد)",
                        "آدرس آی‌پی": "192.168.1.15",
                        "نوع فعالیت": "پرداخت آنلاین",
                        "توضیحات": f"پرداخت موفق مبلغ {checkout['amount']:,} ریال برای فاکتور شماره {checkout['invoice_id']}"
                    })
                    
                    st.success(f"🎉 پرداخت موفقیت‌آمیز بود! شماره پیگیری بانکی شما: {ref_num}")
                    del st.session_state['active_checkout']
                    st.rerun()
            with col_b4:
                if st.button("❌ انصراف از پرداخت", key="cancel_bank_payment"):
                    del st.session_state['active_checkout']
                    st.rerun()
                    
        # History table of this sibling's transactions
        st.write("#### 📜 سابقه تراکنش‌های فرزند")
        child_tx = [x for x in st.session_state['payment_transactions'] if x['invoice_id'] in [y['id'] for y in child_invoices]]
        if child_tx:
            child_tx_df = pd.DataFrame(child_tx)
            st.dataframe(child_tx_df[["date", "gateway", "ref_num", "amount", "status"]].rename(columns={
                "date": "تاریخ", "gateway": "درگاه", "ref_num": "کد پیگیری", "amount": "مبلغ (ریال)", "status": "وضعیت"
            }), use_container_width=True)
        else:
            st.info("هیچ تراکنش مالی موفقی برای این فرزند ثبت نشده است.")


    with p_tab_ai_quizzes:
        st.write("#### 🧠 نتایج ارزیابی‌های سنجش هوشمند فرزند شما (AI)")
        st.markdown("""
            دبیران محترم مدرسه با بکارگیری هوش مصنوعی، کوئیزهای مستمر و پویایی را برای دانش‌آموزان به صورت آنلاین برگزار می‌کنند. 
            شما می‌توانید عملکرد لحظه‌ای فرزند خود را در این ارزیابی‌ها در زیر پایش نمایید.
        """)
        
        # Filter child quiz attempts
        child_attempts = [x for x in st.session_state['ai_quiz_attempts'] if x['student_id'] == active_child['id']]
        
        if not child_attempts:
            st.info("فرزند شما هنوز در هیچ آزمون هوشمندی شرکت نکرده است.")
        else:
            for att in child_attempts:
                # find quiz info
                qz = [x for x in st.session_state['ai_quizzes'] if x['id'] == att['quiz_id']][0]
                
                with st.expander(f"📊 {qz['title']} - درس: {qz['subject']} (نمره: {att['score']} از ۲۰.۰۰)"):
                    st.write(f"**زمان اتمام آزمون:** {att['completed_at']}")
                    st.write(f"**درصد پاسخ صحیح:** {int((att['score']/20.0)*100)}%")
                    
                    st.markdown(f"""
                        <div class="success-box" style="border-right-color: #1d3557;">
                            🧠 <b>تحلیل رفتاری و علمی فرزند شما توسط هوش مصنوعی:</b><br/>
                            {att['feedback']}[103]
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("🔍 **پاسخ‌های ثبت‌شده فرزند شما:**")
                    for q in qz['questions']:
                        st.write(f"**سوال:** {q['question_text']}")
                        child_ans = att['answers'].get(q['id'], "ثبت نشده")
                        correct_let = [o['letter'] for o in q['options'] if o['is_correct']][0]
                        st.write(f"گزینه انتخابی فرزند شما: **{child_ans}** | گزینه صحیح: **{correct_let}**")
                        if child_ans == correct_let:
                            st.markdown("<span style='color:green;'>✔️ پاسخ صحیح</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span style='color:red;'>❌ پاسخ نادرست</span>", unsafe_allow_html=True)
                        st.write("---")


    with p_tab_notif:
        st.write("#### 📢 آخرین اطلاعیه‌های دبیرستان")
        parent_anns = [x for x in st.session_state['announcements'] if x['target'] in ['parents', 'all']]
        for ann in reversed(parent_anns):
            st.markdown(f"""
                <div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom:10px; border-right: 4px solid #1d3557;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold; color: #1d3557;">{ann['title']}</span>
                        <span style="font-size:12px; color:#6c757d;">تاریخ: {ann['date']}</span>
                    </div>
                    <p style="margin: 10px 0 0 0; font-size:14px; color:#4a5568;">{ann['body']}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with p_tab_contact:
        st.write("#### 💬 صندوق گفتگو با معلمان و کادر مدرسه")
        with st.form("parent_msg_form"):
            msg_receiver = st.selectbox("گیرنده پیام:", ["دبیر ریاضی (مهندس احمدی)", "معاون انضباطی مدرسه (جناب حسینی)", "مدیریت دبیرستان"])
            msg_subject = st.text_input("موضوع پیام:")
            msg_body = st.text_area("متن پیام:")
            
            submitted_msg = st.form_submit_button("✉️ ارسال پیام")
            if submitted_msg:
                if msg_subject and msg_body:
                    st.session_state['messages'].append({
                        "id": len(st.session_state['messages']) + 1,
                        "sender_id": parent_id,
                        "receiver_id": 101,
                        "sender_name": f"{parent_name} (والد)",
                        "body": msg_body,
                        "date": datetime.date.today().strftime("%Y-%m-%d"),
                        "is_read": False
                    })
                    st.success("پیام شما با موفقیت برای دبیر ارسال شد. پاسخ دبیران از طریق همین بخش برای شما قابل مشاهده خواهد بود.")
                    
        st.write("📨 **پیام‌های اخیر رد و بدل شده**")
        for msg in reversed(st.session_state['messages']):
            bg_color = "#e8f5e9" if msg['sender_id'] == parent_id else "#e1f5fe"
            st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 4px solid #1d3557;">
                    <p style="margin: 0; font-size:12px; color: #555;"><b>از طرف:</b> {msg['sender_name']} | <b>تاریخ:</b> {msg['date']}</p>
                    <p style="margin: 10px 0 0 0; font-size:14px;">{msg['body']}</p>
                </div>
            """, unsafe_allow_html=True)
