-- ============================================================================
-- SQL Schema for Smart School Management System (سامانه هوشمند مدیریت مدرسه)
-- Database: PostgreSQL (15+)
-- Description: Robust, secure, and modular schema supporting multi-tenant/single-school,
--              Role-Based Access Control (RBAC), student-parent relations, attendance logs,
--              assessments, homework, and audit logging.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Enums & Custom Types
-- ----------------------------------------------------------------------------

CREATE TYPE user_role AS ENUM ('admin', 'vice_principal', 'teacher', 'student', 'parent');
CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'tardy', 'excused', 'unexcused');
CREATE TYPE assessment_type AS ENUM ('homework', 'quiz', 'midterm', 'final', 'practical', 'project');
CREATE TYPE announcement_target AS ENUM ('all', 'teachers', 'students', 'parents', 'class_specific');

-- ----------------------------------------------------------------------------
-- 0. Tenants & Multi-School Structure (مدارس و ساختار چندمستاجری)
-- ----------------------------------------------------------------------------

CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL, -- نام مدرسه
    subdomain VARCHAR(50) UNIQUE NOT NULL, -- ساب‌دومین اختصاصی برای مسیریابی (e.g., melli.smartschool.ir)
    logo_url VARCHAR(255), -- لوگوی اختصاصی مدرسه
    theme_settings JSONB DEFAULT '{"primary_color": "#1d3557", "secondary_color": "#2a9d8f"}'::jsonb, -- تنظیمات پوسته اختصاصی مدرسه
    address TEXT, -- آدرس مدرسه
    phone_number VARCHAR(15), -- تلفن تماس مدرسه
    is_active BOOLEAN DEFAULT TRUE, -- وضعیت فعال/غیرفعال بودن مستاجر
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_schools_subdomain ON schools(subdomain);

-- ----------------------------------------------------------------------------
-- 2. Core Users & RBAC
-- ----------------------------------------------------------------------------

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15) UNIQUE NOT NULL, -- Core for SMS notifications and authentication
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    national_id VARCHAR(10) UNIQUE NOT NULL, -- کد ملی
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_national_id ON users(national_id);

-- ----------------------------------------------------------------------------
-- 3. Academic Structure
-- ----------------------------------------------------------------------------

CREATE TABLE academic_years (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    name VARCHAR(20) NOT NULL UNIQUE, -- e.g., "1405-1406"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE
);

CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- e.g., "دهم", "یازدهم", "دوازدهم"
    stage VARCHAR(50) NOT NULL -- e.g., "متوسطه دوم"
);

CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL -- e.g., "ریاضی فیزیک", "علوم تجربی", "علوم انسانی"
);

CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    name VARCHAR(50) NOT NULL, -- e.g., "کلاس ۱۰۱"
    grade_id INTEGER REFERENCES grades(id) ON DELETE RESTRICT,
    branch_id INTEGER REFERENCES branches(id) ON DELETE RESTRICT,
    academic_year_id INTEGER REFERENCES academic_years(id) ON DELETE CASCADE,
    capacity INTEGER DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_class_per_year UNIQUE (school_id, name, academic_year_id)
);

CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    name VARCHAR(100) NOT NULL, -- e.g., "ریاضی ۳", "فیزیک پیشرفته"
    code VARCHAR(20) UNIQUE NOT NULL,
    grade_id INTEGER REFERENCES grades(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4. User Profiles & Relations
-- ----------------------------------------------------------------------------

-- Admin & Vice Principal Profiles
CREATE TABLE staff_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    specialty VARCHAR(100),
    hire_date DATE
);

-- Teacher Profile
CREATE TABLE teacher_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    teacher_code VARCHAR(20) UNIQUE NOT NULL,
    degree VARCHAR(50), -- مدرک تحصیلی
    specialty VARCHAR(100),
    hire_date DATE
);

-- Student Profile
CREATE TABLE student_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    student_code VARCHAR(20) UNIQUE NOT NULL, -- شماره دانش‌آموزی
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    enrollment_date DATE,
    status VARCHAR(20) DEFAULT 'active' -- active, suspended, graduated
);

CREATE INDEX idx_student_class ON student_profiles(class_id);

-- Parent-Student Relationship (Many-to-Many to support both father/mother and multiple siblings)
CREATE TABLE parent_student_relations (
    parent_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    relationship_type VARCHAR(30) NOT NULL, -- e.g., "father", "mother", "guardian"
    is_emergency_contact BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (parent_id, student_id)
);

-- ----------------------------------------------------------------------------
-- 5. Academic Assignments & Weekly Schedule
-- ----------------------------------------------------------------------------

-- Course Assignment (Linking Teacher to Subject and Class)
CREATE TABLE course_assignments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    academic_year_id INTEGER REFERENCES academic_years(id) ON DELETE CASCADE,
    CONSTRAINT unique_assignment UNIQUE (teacher_id, class_id, subject_id, academic_year_id)
);

-- Weekly Schedule slots
CREATE TABLE schedule_slots (
    id SERIAL PRIMARY KEY,
    course_assignment_id INTEGER REFERENCES course_assignments(id) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0: Saturday (Iran context), 6: Friday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom_identifier VARCHAR(50), -- e.g., "کارگاه کامپیوتر"
    CONSTRAINT check_time_order CHECK (start_time < end_time)
);

-- ----------------------------------------------------------------------------
-- 6. Core Daily Logs: Attendance & Assessments
-- ----------------------------------------------------------------------------

-- Attendance Table
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    course_assignment_id INTEGER REFERENCES course_assignments(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status attendance_status NOT NULL DEFAULT 'present',
    remarks TEXT, -- علت غیبت یا تاخیر
    recorded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_attendance_session UNIQUE (student_id, course_assignment_id, date)
);

CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_student ON attendance(student_id);

-- Attendance History (Audit Log)
CREATE TABLE attendance_audit_log (
    id SERIAL PRIMARY KEY,
    attendance_id INTEGER NOT NULL,
    old_status attendance_status,
    new_status attendance_status NOT NULL,
    old_remarks TEXT,
    new_remarks TEXT,
    modified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Homework/Assignments
CREATE TABLE homework (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    course_assignment_id INTEGER REFERENCES course_assignments(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    attachment_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Homework Submissions
CREATE TABLE homework_submissions (
    id SERIAL PRIMARY KEY,
    homework_id INTEGER REFERENCES homework(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    submission_text TEXT,
    attachment_url VARCHAR(255),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    grade NUMERIC(4,2) CHECK (grade >= 0 AND grade <= 20),
    teacher_feedback TEXT,
    graded_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_submission UNIQUE (homework_id, student_id)
);

-- Assessments (Exams/Quizzes)
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    course_assignment_id INTEGER REFERENCES course_assignments(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    type assessment_type NOT NULL,
    max_score NUMERIC(4,2) NOT NULL DEFAULT 20.00 CHECK (max_score > 0),
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grades/Scores
CREATE TABLE grades_records (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score NUMERIC(4,2) CHECK (score >= 0 AND score <= 20),
    is_absent BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    recorded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_grade UNIQUE (assessment_id, student_id)
);

CREATE INDEX idx_grades_student ON grades_records(student_id);

-- ----------------------------------------------------------------------------
-- 7. Communication & Announcements
-- ----------------------------------------------------------------------------

-- Messaging System
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    sender_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    receiver_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    subject VARCHAR(150),
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_receiver ON messages(receiver_id);

-- Announcements
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    target_role announcement_target NOT NULL DEFAULT 'all',
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE, -- If target is class_specific
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at DATE
);

-- ----------------------------------------------------------------------------
-- 8. General Logs & Audit Trails
-- ----------------------------------------------------------------------------

CREATE TABLE system_activity_logs (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ip_address VARCHAR(45),
    action_type VARCHAR(50) NOT NULL, -- e.g., "LOGIN", "GRADE_UPDATE", "ATTENDANCE_CHANGE"
    description TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 9. Future Integration: AI Readiness Schema
-- ----------------------------------------------------------------------------

-- Predictive metrics stored for model training & predictions (e.g., risk of dropping out, grades prediction)
CREATE TABLE ai_student_metrics (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    prediction_date DATE DEFAULT CURRENT_DATE,
    academic_risk_score NUMERIC(3,2), -- 0.00 (Safe) to 1.00 (High Risk)
    predicted_gpa NUMERIC(4,2),
    attendance_rate NUMERIC(5,2), -- current running attendance rate (percentage)
    behavioral_score NUMERIC(3,2), -- assessment based on comments and discipline logs
    model_version VARCHAR(50),
    key_risk_factors TEXT -- JSON array of factors, e.g., ["low math grade", "absent twice this week"]
);

CREATE INDEX idx_ai_student ON ai_student_metrics(student_id);

-- ----------------------------------------------------------------------------
-- 10. Database Triggers for Updated Timestamp & Attendance Audits
-- ----------------------------------------------------------------------------

-- Function to auto-update timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_users_modtime BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_attendance_modtime BEFORE UPDATE ON attendance FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

-- Function to audit attendance edits
CREATE OR REPLACE FUNCTION audit_attendance_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.status IS DISTINCT FROM NEW.status OR OLD.remarks IS DISTINCT FROM NEW.remarks) THEN
        INSERT INTO attendance_audit_log(attendance_id, old_status, new_status, old_remarks, new_remarks, modified_by, modified_at)
        VALUES(OLD.id, OLD.status, NEW.status, OLD.remarks, NEW.remarks, NEW.recorded_by, now());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER audit_attendance_mod BEFORE UPDATE ON attendance FOR EACH ROW EXECUTE PROCEDURE audit_attendance_changes();


-- ----------------------------------------------------------------------------
-- 11. Online Classes & Video Conferencing (ماژول کلاس‌های آنلاین و جلسات تصویری)
-- ----------------------------------------------------------------------------

-- ارائه‌دهندگان کلاس آنلاین پشتیبانی‌شده در سیستم
CREATE TYPE online_class_provider AS ENUM ('jitsi', 'bigbluebutton', 'zoom', 'google_meet', 'whatsapp', 'custom');

-- وضعیت‌های مختلف یک کلاس آنلاین
CREATE TYPE online_class_status AS ENUM ('scheduled', 'live', 'completed', 'cancelled');

-- جدول اصلی جلسات کلاس‌های آنلاین
CREATE TABLE online_classes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    course_assignment_id INTEGER REFERENCES course_assignments(id) ON DELETE CASCADE, -- اتصال به درس، دبیر و کلاس مربوطه
    schedule_slot_id INTEGER REFERENCES schedule_slots(id) ON DELETE SET NULL, -- اختیاری: اتصال به زنگ یا اسلات برنامه هفتگی
    title VARCHAR(150) NOT NULL, -- عنوان کلاس (مثلاً: «حل تمرین ریاضی مبحث مشتق»)
    description TEXT, -- توضیحات کلاس
    provider online_class_provider NOT NULL DEFAULT 'jitsi', -- بستر ارائه کلاس آنلاین
    meeting_id VARCHAR(100) NOT NULL, -- شناسه یکتای جلسه در سیستم سرویس‌دهنده (مانند Room Name در Jitsi یا UUID در Zoom)
    host_join_url TEXT NOT NULL, -- لینک ورود اختصاصی و امن دبیر/برگزارکننده (دارای توکن امضا شده)
    participant_join_url TEXT NOT NULL, -- لینک ورود اختصاصی یا عمومی دانش‌آموزان
    scheduled_start TIMESTAMP WITH TIME ZONE NOT NULL, -- زمان شروع برنامه‌ریزی‌شده
    scheduled_end TIMESTAMP WITH TIME ZONE NOT NULL, -- زمان پایان برنامه‌ریزی‌شده
    actual_start TIMESTAMP WITH TIME ZONE, -- زمان شروع واقعی (وقتی دبیر کلاس را آغاز می‌کند)
    actual_end TIMESTAMP WITH TIME ZONE, -- زمان پایان واقعی
    status online_class_status NOT NULL DEFAULT 'scheduled', -- وضعیت جلسه
    settings JSONB DEFAULT '{}'::jsonb, -- تنظیمات اختصاصی کلاس (مثلاً: {"mute_on_join": true, "record_class": false, "allow_chat": true})
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL, -- ایجادکننده کلاس (مثلاً مدیر یا دبیر)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_scheduled_times CHECK (scheduled_start < scheduled_end),
    CONSTRAINT check_actual_times CHECK (actual_start IS NULL OR actual_end IS NULL OR actual_start < actual_end)
);

CREATE INDEX idx_online_classes_course ON online_classes(course_assignment_id);
CREATE INDEX idx_online_classes_status ON online_classes(status);
CREATE INDEX idx_online_classes_start ON online_classes(scheduled_start);

-- جدول لاگ حضور و غیاب هوشمند در کلاس آنلاین
CREATE TABLE online_class_logs (
    id SERIAL PRIMARY KEY,
    online_class_id INTEGER REFERENCES online_classes(id) ON DELETE CASCADE, -- اتصال به کلاس آنلاین
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- کاربر وارد شده (دبیر یا دانش‌آموز)
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- زمان ورود به کلاس
    left_at TIMESTAMP WITH TIME ZONE, -- زمان خروج از کلاس
    duration_minutes INTEGER, -- مدت زمان حضور بر حسب دقیقه (در زمان خروج محاسبه و ذخیره می‌شود)
    device_info VARCHAR(255), -- اطلاعات مرورگر یا دستگاه کاربر (به جهت عیب‌یابی مشکلات فنی)
    ip_address VARCHAR(45), -- آدرس آی‌پی کاربر
    CONSTRAINT check_log_times CHECK (left_at IS NULL OR joined_at <= left_at)
);

CREATE INDEX idx_online_class_logs_class ON online_class_logs(online_class_id);
CREATE INDEX idx_online_class_logs_user ON online_class_logs(user_id);

-- جدول ضبط ویدیوهای کلاس‌های آنلاین (آرشیو ویدیوها برای مرور دانش‌آموزان)
CREATE TABLE online_class_recordings (
    id SERIAL PRIMARY KEY,
    online_class_id INTEGER REFERENCES online_classes(id) ON DELETE CASCADE, -- اتصال به کلاس مربوطه
    recording_url TEXT NOT NULL, -- لینک دانلود یا پخش ویدیوی ضبط شده (مثلاً در S3)
    file_size_bytes BIGINT, -- حجم فایل ضبط شده بر حسب بایت
    duration_seconds INTEGER, -- مدت زمان ویدیوی ضبط شده بر حسب ثانیه
    is_published BOOLEAN DEFAULT TRUE, -- دسترسی یا عدم دسترسی دانش‌آموزان به فایل ضبط شده
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_online_class_recordings_class ON online_class_recordings(online_class_id);

-- اضافه کردن ماشه (Trigger) برای به‌روزرسانی خودکار ستون updated_at در جدول online_classes
CREATE TRIGGER update_online_classes_modtime 
BEFORE UPDATE ON online_classes 
FOR EACH ROW 
EXECUTE PROCEDURE update_modified_column();


-- ----------------------------------------------------------------------------
-- 12. Fee & Financial Management (ماژول مدیریت مالی، شهریه و پرداخت آنلاین)
-- ----------------------------------------------------------------------------

-- انواع اقلام هزینه و شهریه
CREATE TYPE fee_category AS ENUM ('tuition', 'transport', 'books', 'activities', 'uniform', 'meals', 'other');

-- وضعیت‌های فاکتور مالی
CREATE TYPE invoice_status AS ENUM ('unpaid', 'partially_paid', 'paid', 'overpaid', 'cancelled');

-- وضعیت‌های تراکنش بانکی
CREATE TYPE transaction_status AS ENUM ('pending', 'success', 'failed', 'reversed');

-- درگاه‌های پرداخت پشتیبانی‌شده
CREATE TYPE payment_gateway_provider AS ENUM ('saman', 'mellat', 'zarinpal', 'stripe', 'paystack', 'custom_bank');

-- تعریف ساختار هزینه‌های پایه (مثلاً شهریه ثابت دهم تجربی)
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    name VARCHAR(150) NOT NULL, -- e.g., «شهریه پایه دهم - سال ۱۴۰۵»
    category fee_category NOT NULL DEFAULT 'tuition',
    grade_id INTEGER REFERENCES grades(id) ON DELETE CASCADE,
    branch_id INTEGER REFERENCES branches(id) ON DELETE CASCADE, -- اختیاری برای رشته‌های مختلف
    academic_year_id INTEGER REFERENCES academic_years(id) ON DELETE CASCADE,
    base_amount NUMERIC(12, 2) NOT NULL CHECK (base_amount >= 0), -- مبلغ پایه به ریال یا واحد پیش‌فرض
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- تخفیف‌ها یا اضافه‌هزینه‌های اختصاصی هر دانش‌آموز (مثلاً تخفیف رتبه برتر یا هزینه ایاب و ذهاب اختصاصی)
CREATE TABLE student_fee_allocations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    fee_structure_id INTEGER REFERENCES fee_structures(id) ON DELETE CASCADE,
    custom_amount NUMERIC(12, 2), -- در صورت وجود مبلغ اختصاصی (جاگزین مبلغ پایه)
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00 CHECK (discount_percentage >= 0 AND discount_percentage <= 100), -- درصد تخفیف
    discount_remarks VARCHAR(255), -- دلیل اعمال تخفیف
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_student_fee UNIQUE (student_id, fee_structure_id)
);

-- فاکتورهای صادر شده برای دانش‌آموزان
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    academic_year_id INTEGER REFERENCES academic_years(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL, -- عنوان فاکتور (مثلاً «صورت‌حساب نیم‌سال اول شهریه»)
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    subtotal_amount NUMERIC(12, 2) NOT NULL CHECK (subtotal_amount >= 0), -- جمع اقلام قبل تخفیف
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0), -- کل مبلغ تخفیف‌های اعمال شده
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0), -- مبلغ نهایی قابل پرداخت (subtotal - discount)
    paid_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0), -- مبلغ پرداخت‌شده تا این لحظه
    status invoice_status NOT NULL DEFAULT 'unpaid',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_invoice_due CHECK (issue_date <= due_date),
    CONSTRAINT check_invoice_totals CHECK (total_amount = subtotal_amount - discount_amount)
);

CREATE INDEX idx_invoices_student ON invoices(student_id);
CREATE INDEX idx_invoices_status ON invoices(status);

-- اقلام ریز هر فاکتور
CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
    fee_structure_id INTEGER REFERENCES fee_structures(id) ON DELETE SET NULL,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0), -- مبلغ قبل تخفیف
    discount_applied NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (discount_applied >= 0)
);

-- تراکنش‌های پرداخت آنلاین
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE SET NULL,
    payer_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- والدی که پرداخت را انجام داده
    gateway payment_gateway_provider NOT NULL,
    transaction_ref VARCHAR(100) UNIQUE, -- شماره پیگیری/مرجع درگاه بانکی
    card_pan_masked VARCHAR(19), -- شماره کارت ماسک شده پرداخت‌کننده (به جهت پیگیری و مسائل امنیتی PCI-DSS)
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) DEFAULT 'IRR', -- ارز تراکنش (مثلاً ریال یا تومان)
    status transaction_status NOT NULL DEFAULT 'pending',
    raw_response JSONB, -- لاگ پاسخ خام درگاه (مفید برای رفع خطای وب‌هوک و امنیت سیستم)
    ip_address VARCHAR(45), -- آی‌پی پرداخت‌کننده
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transactions_invoice ON payment_transactions(invoice_id);
CREATE INDEX idx_transactions_status ON payment_transactions(status);

-- جدول تطابق و رفع مغایرت‌های مالی (Reconciliation Ledger)
-- جهت اطمینان از صحت پرداخت‌ها و هندل کردن خطاها یا تراکنش‌های دوبار ثبت‌شده
CREATE TABLE financial_reconciliation_ledger (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES payment_transactions(id) ON DELETE CASCADE,
    reconciled_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- کارشناس یا مدیر مالی
    reconciliation_status VARCHAR(50) NOT NULL DEFAULT 'reconciled', -- reconciled, discrepancy_found, refunded
    audit_comments TEXT, -- توضیحات بررسی مالی مغایرت
    reconciled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- بروزرسانی خودکارupdated_at برای فاکتورها
CREATE TRIGGER update_invoices_modtime 
BEFORE UPDATE ON invoices 
FOR EACH ROW 
EXECUTE PROCEDURE update_modified_column();


-- ----------------------------------------------------------------------------
-- 15. AI Exam & Quiz Generation Module (ماژول هوشمند طراحی آزمون با هوش مصنوعی)
-- ----------------------------------------------------------------------------

-- جدول تاریخچه درخواست‌های تولید آزمون توسط دبیر با هوش مصنوعی چت‌جی‌پی‌تی
CREATE TABLE ai_quiz_generations (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- دبیری که درخواست داده است
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE, -- درس مربوطه
    prompt_used TEXT NOT NULL, -- متنی که دبیر به عنوان ورودی برای هوش مصنوعی مشخص کرده است
    topic VARCHAR(150) NOT NULL, -- موضوع تدریس (مثلاً مشتق)
    difficulty_level VARCHAR(30) NOT NULL, -- آسان، متوسط، سخت
    question_count INTEGER NOT NULL CHECK (question_count > 0),
    raw_response JSONB NOT NULL, -- پاسخ خام بازگردانده شده از API هوش مصنوعی (OpenAI ChatGPT)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_quiz_gen_teacher ON ai_quiz_generations(teacher_id);

-- جدول سوالات آزمون (اتصال به جدول ارزیابی‌های اصلی سیستم)
CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id) ON DELETE CASCADE, -- آزمون یا کوئیزی که سوال به آن تعلق دارد
    question_text TEXT NOT NULL, -- متن سوال صادر شده توسط AI
    question_type VARCHAR(30) NOT NULL DEFAULT 'multiple_choice', -- 'multiple_choice' (چند گزینه‌ای) یا 'essay' (تشریحی)
    points NUMERIC(4,2) DEFAULT 1.00 CHECK (points >= 0), -- بارم سوال
    correct_explanation TEXT, -- توضیح و کلید حل سوال توسط هوش مصنوعی
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quiz_questions_assessment ON quiz_questions(assessment_id);

-- جدول گزینه‌های سوال تستی چهارگزینه‌ای
CREATE TABLE quiz_question_options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES quiz_questions(id) ON DELETE CASCADE, -- اتصال به سوال مربوطه
    option_letter CHAR(1) NOT NULL, -- الف، ب، ج، د (یا A, B, C, D)
    option_text TEXT NOT NULL, -- متن گزینه مربوطه
    is_correct BOOLEAN DEFAULT FALSE, -- آیا گزینه صحیح است؟
    CONSTRAINT unique_option_per_question UNIQUE (question_id, option_letter)
);

CREATE INDEX idx_quiz_options_question ON quiz_question_options(question_id);

-- جدول ثبت تلاش‌ها و پاسخ‌های دانش‌آموزان به آزمون آنلاین
CREATE TABLE student_quiz_attempts (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE, -- شناسه مدرسه جهت جداسازی داده‌ها (Tenant ID)
    assessment_id INTEGER REFERENCES assessments(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE, -- زمان ثبت نهایی آزمون
    calculated_score NUMERIC(4,2) CHECK (calculated_score >= 0 AND calculated_score <= 20.00), -- نمره نهایی کسب‌شده از ۲۰
    is_graded BOOLEAN DEFAULT FALSE, -- آیا تصحیح و نمره‌دهی تکمیل شده است؟
    CONSTRAINT unique_student_attempt UNIQUE (assessment_id, student_id)
);

CREATE INDEX idx_quiz_attempts_student ON student_quiz_attempts(student_id);

-- جدول پاسخ‌های ثبت‌شده دانش‌آموز به تک‌تک سوالات آزمون
CREATE TABLE student_question_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES student_quiz_attempts(id) ON DELETE CASCADE, -- اتصال به تلاش دانش‌آموز
    question_id INTEGER REFERENCES quiz_questions(id) ON DELETE CASCADE, -- اتصال به سوال
    selected_option_id INTEGER REFERENCES quiz_question_options(id) ON DELETE SET NULL, -- گزینه انتخابی برای سوال تستی
    submitted_essay_text TEXT, -- متن پاسخ ارسالی برای سوال تشریحی
    is_correct BOOLEAN DEFAULT FALSE, -- آیا پاسخ صحیح بوده است؟ (برای سوالات تستی بلافاصله محاسبه می‌شود)
    score_earned NUMERIC(4,2) DEFAULT 0.00 CHECK (score_earned >= 0), -- نمره داده شده به این سوال
    graded_by INTEGER REFERENCES users(id) ON DELETE SET NULL, -- چه کسی نمره داده (سیستم برای تستی، دبیر برای تشریحی)
    graded_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_student_answers_attempt ON student_question_answers(attempt_id);


-- ============================================================================
-- 15. PostgreSQL Row Level Security (RLS) for Multi-Tenancy
-- ============================================================================

-- فعال‌سازی RLS برای جدول‌های اصلی سیستم جهت جلوگیری از نشت داده‌ها بین مدارس (Cross-Tenant Data Leak)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE homework ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE fee_structures ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE online_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_quiz_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_quiz_attempts ENABLE ROW LEVEL SECURITY;

-- تعریف سیاست امنیت سطح سطر (RLS Policy) بر اساس متغیر نشست جاری کاربر (current_setting('app.current_school_id'))
-- این سیاست تضمین می‌کند که هر مدرسه تنها به داده‌های متعلق به خود دسترسی داشته باشد.
CREATE POLICY school_isolation_policy ON users 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON academic_years 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON classes 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON subjects 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON course_assignments 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON attendance 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON homework 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON assessments 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON fee_structures 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON invoices 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON payment_transactions 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON online_classes 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON ai_quiz_generations 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

CREATE POLICY school_isolation_policy ON student_quiz_attempts 
    USING (school_id = NULLIF(current_setting('app.current_school_id', true), '')::integer);

-- راهنمای نحوه تنظیم شناسه مدرسه جاری در اپلیکیشن (Laravel/Node/Python):
-- SET LOCAL app.current_school_id = '1';
-- SELECT * FROM students; -- تنها دانش‌آموزان مدرسه شماره ۱ را بازمی‌گرداند.
