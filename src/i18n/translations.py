"""Translation system for multi-language support."""

from typing import Any

# English translations (default)
EN = {
    # General
    "app.name": "PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)",
    "app.tagline": "Smart Appointment Management",

    # Navigation
    "nav.home": "Home",
    "nav.bookings": "My Appointments",
    "nav.profile": "Profile",
    "nav.settings": "Settings",
    "nav.logout": "Logout",

    # Auth
    "auth.login": "Login",
    "auth.register": "Register",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.confirm_password": "Confirm Password",
    "auth.forgot_password": "Forgot Password?",
    "auth.login_success": "Login successful",
    "auth.logout_success": "Logged out successfully",
    "auth.invalid_credentials": "Invalid email or password",

    # Patient
    "patient.first_name": "First Name",
    "patient.last_name": "Last Name",
    "patient.phone": "Phone Number",
    "patient.dob": "Date of Birth",
    "patient.category": "Medical Category",
    "patient.compliance": "Compliance Level",

    # Booking
    "booking.new": "Book Appointment",
    "booking.upcoming": "Upcoming Appointments",
    "booking.past": "Past Appointments",
    "booking.cancel": "Cancel Appointment",
    "booking.reschedule": "Reschedule",
    "booking.confirm": "Confirm Booking",
    "booking.reason": "Reason for Visit",
    "booking.no_slots": "No available slots",
    "booking.success": "Appointment booked successfully",
    "booking.cancelled": "Appointment cancelled",
    "booking.rescheduled": "Appointment rescheduled",

    # Slots
    "slot.available": "Available",
    "slot.booked": "Booked",
    "slot.select_date": "Select Date",
    "slot.select_time": "Select Time",

    # Compliance Questionnaire
    "questionnaire.compliance.title": "Compliance Self-Assessment",
    "questionnaire.compliance.intro": "Please answer honestly to help us serve you better.",
    "questionnaire.compliance.q1": "How often do you miss scheduled appointments?",
    "questionnaire.compliance.q2": "How much advance notice do you give for cancellations?",
    "questionnaire.compliance.q3": "How important is maintaining your appointment schedule?",
    "questionnaire.compliance.q4": "How likely are you to reschedule if you must cancel?",
    "questionnaire.compliance.q5": "How flexible is your schedule for appointments?",
    "questionnaire.compliance.agree_24h": "I agree to give 24+ hours notice for cancellations",
    "questionnaire.compliance.agree_penalty": "I understand repeated no-shows may affect my access",
    "questionnaire.compliance.agree_reschedule": "I commit to rescheduling cancelled appointments",
    "questionnaire.compliance.agree_comms": "I agree to receive appointment reminders",

    # Triage Questionnaire
    "questionnaire.triage.title": "Cancellation/Reschedule Request",
    "questionnaire.triage.reason": "Reason for change",
    "questionnaire.triage.reason_work": "Work conflict",
    "questionnaire.triage.reason_health": "Health issue",
    "questionnaire.triage.reason_family": "Family emergency",
    "questionnaire.triage.reason_transport": "Transportation issue",
    "questionnaire.triage.reason_other": "Other",
    "questionnaire.triage.symptoms": "Have your symptoms changed?",
    "questionnaire.triage.symptoms_worse": "Symptoms have worsened",
    "questionnaire.triage.symptoms_new": "New symptoms appeared",
    "questionnaire.triage.availability": "Can you reschedule within a week?",
    "questionnaire.triage.acknowledge": "I acknowledge this may affect my compliance rating",
    "questionnaire.triage.commit": "I commit to attending my new appointment",

    # Categories
    "category.critical": "Critical",
    "category.high_risk": "High Risk",
    "category.moderate": "Moderate",
    "category.stable": "Stable",
    "category.maintenance": "Maintenance",
    "category.healthy": "Healthy",

    # Compliance Levels
    "compliance.platinum": "Platinum",
    "compliance.gold": "Gold",
    "compliance.silver": "Silver",
    "compliance.bronze": "Bronze",
    "compliance.probation": "Probation",

    # Visit Frequency
    "frequency.weekly": "Weekly",
    "frequency.biweekly": "Every 2 weeks",
    "frequency.monthly": "Monthly",
    "frequency.bimonthly": "Every 2 months",
    "frequency.quarterly": "Quarterly",
    "frequency.biannual": "Every 6 months",
    "frequency.annual": "Annual",

    # Errors
    "error.required": "This field is required",
    "error.invalid_email": "Invalid email address",
    "error.password_short": "Password must be at least 8 characters",
    "error.passwords_mismatch": "Passwords do not match",
    "error.network": "Network error. Please try again.",
    "error.server": "Server error. Please try again later.",
    "error.not_found": "Not found",
    "error.unauthorized": "Please login to continue",
    "error.forbidden": "Access denied",

    # Buttons
    "button.submit": "Submit",
    "button.cancel": "Cancel",
    "button.save": "Save",
    "button.next": "Next",
    "button.back": "Back",
    "button.close": "Close",
    "button.confirm": "Confirm",

    # Messages
    "message.loading": "Loading...",
    "message.saving": "Saving...",
    "message.success": "Success!",
    "message.no_data": "No data available",
}

# Hebrew translations
HE = {
    # General
    "app.name": "PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)",
    "app.tagline": "ניהול תורים חכם",

    # Navigation
    "nav.home": "בית",
    "nav.bookings": "התורים שלי",
    "nav.profile": "פרופיל",
    "nav.settings": "הגדרות",
    "nav.logout": "התנתק",

    # Auth
    "auth.login": "התחברות",
    "auth.register": "הרשמה",
    "auth.email": "אימייל",
    "auth.password": "סיסמה",
    "auth.confirm_password": "אימות סיסמה",
    "auth.forgot_password": "שכחת סיסמה?",
    "auth.login_success": "התחברת בהצלחה",
    "auth.logout_success": "התנתקת בהצלחה",
    "auth.invalid_credentials": "אימייל או סיסמה שגויים",

    # Patient
    "patient.first_name": "שם פרטי",
    "patient.last_name": "שם משפחה",
    "patient.phone": "טלפון",
    "patient.dob": "תאריך לידה",
    "patient.category": "קטגוריה רפואית",
    "patient.compliance": "רמת התחייבות",

    # Booking
    "booking.new": "קביעת תור",
    "booking.upcoming": "תורים קרובים",
    "booking.past": "תורים קודמים",
    "booking.cancel": "ביטול תור",
    "booking.reschedule": "שינוי מועד",
    "booking.confirm": "אישור הזמנה",
    "booking.reason": "סיבת הביקור",
    "booking.no_slots": "אין תורים פנויים",
    "booking.success": "התור נקבע בהצלחה",
    "booking.cancelled": "התור בוטל",
    "booking.rescheduled": "מועד התור שונה",

    # Slots
    "slot.available": "פנוי",
    "slot.booked": "תפוס",
    "slot.select_date": "בחר תאריך",
    "slot.select_time": "בחר שעה",

    # Compliance Questionnaire
    "questionnaire.compliance.title": "שאלון הערכה עצמית",
    "questionnaire.compliance.intro": "אנא ענה בכנות כדי שנוכל לשרת אותך טוב יותר.",
    "questionnaire.compliance.q1": "באיזו תדירות אתה מפספס תורים?",
    "questionnaire.compliance.q2": "כמה הודעה מראש אתה נותן לביטולים?",
    "questionnaire.compliance.q3": "כמה חשוב לך לשמור על לוח הזמנים שלך?",
    "questionnaire.compliance.q4": "מה הסיכוי שתקבע תור חדש אם תבטל?",
    "questionnaire.compliance.q5": "כמה גמיש לוח הזמנים שלך?",
    "questionnaire.compliance.agree_24h": "אני מתחייב להודיע 24 שעות מראש על ביטולים",
    "questionnaire.compliance.agree_penalty": "אני מבין שאי-הגעות חוזרות עלולות להשפיע על הגישה שלי",
    "questionnaire.compliance.agree_reschedule": "אני מתחייב לקבוע תור חדש במקרה של ביטול",
    "questionnaire.compliance.agree_comms": "אני מסכים לקבל תזכורות לתורים",

    # Triage Questionnaire
    "questionnaire.triage.title": "בקשת ביטול/שינוי תור",
    "questionnaire.triage.reason": "סיבת השינוי",
    "questionnaire.triage.reason_work": "קונפליקט בעבודה",
    "questionnaire.triage.reason_health": "בעיה בריאותית",
    "questionnaire.triage.reason_family": "מקרה משפחתי",
    "questionnaire.triage.reason_transport": "בעיית תחבורה",
    "questionnaire.triage.reason_other": "אחר",
    "questionnaire.triage.symptoms": "האם המצב שלך השתנה?",
    "questionnaire.triage.symptoms_worse": "התסמינים החמירו",
    "questionnaire.triage.symptoms_new": "הופיעו תסמינים חדשים",
    "questionnaire.triage.availability": "האם תוכל לקבוע תור תוך שבוע?",
    "questionnaire.triage.acknowledge": "אני מבין שזה עשוי להשפיע על דירוג ההתחייבות שלי",
    "questionnaire.triage.commit": "אני מתחייב להגיע לתור החדש",

    # Categories
    "category.critical": "קריטי",
    "category.high_risk": "סיכון גבוה",
    "category.moderate": "בינוני",
    "category.stable": "יציב",
    "category.maintenance": "תחזוקה",
    "category.healthy": "בריא",

    # Compliance Levels
    "compliance.platinum": "פלטינום",
    "compliance.gold": "זהב",
    "compliance.silver": "כסף",
    "compliance.bronze": "ארד",
    "compliance.probation": "תקופת ניסיון",

    # Visit Frequency
    "frequency.weekly": "שבועי",
    "frequency.biweekly": "כל שבועיים",
    "frequency.monthly": "חודשי",
    "frequency.bimonthly": "כל חודשיים",
    "frequency.quarterly": "רבעוני",
    "frequency.biannual": "חצי שנתי",
    "frequency.annual": "שנתי",

    # Errors
    "error.required": "שדה חובה",
    "error.invalid_email": "כתובת אימייל לא תקינה",
    "error.password_short": "הסיסמה חייבת להכיל לפחות 8 תווים",
    "error.passwords_mismatch": "הסיסמאות אינן תואמות",
    "error.network": "שגיאת רשת. נסה שוב.",
    "error.server": "שגיאת שרת. נסה שוב מאוחר יותר.",
    "error.not_found": "לא נמצא",
    "error.unauthorized": "יש להתחבר כדי להמשיך",
    "error.forbidden": "הגישה נדחתה",

    # Buttons
    "button.submit": "שלח",
    "button.cancel": "ביטול",
    "button.save": "שמור",
    "button.next": "הבא",
    "button.back": "חזרה",
    "button.close": "סגור",
    "button.confirm": "אישור",

    # Messages
    "message.loading": "טוען...",
    "message.saving": "שומר...",
    "message.success": "הצלחה!",
    "message.no_data": "אין נתונים להצגה",
}

# Russian translations
RU = {
    # General
    "app.name": "PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)",
    "app.tagline": "Умное управление записями",

    # Navigation
    "nav.home": "Главная",
    "nav.bookings": "Мои записи",
    "nav.profile": "Профиль",
    "nav.settings": "Настройки",
    "nav.logout": "Выйти",

    # Auth
    "auth.login": "Вход",
    "auth.register": "Регистрация",
    "auth.email": "Email",
    "auth.password": "Пароль",
    "auth.confirm_password": "Подтвердите пароль",
    "auth.forgot_password": "Забыли пароль?",
    "auth.login_success": "Вход выполнен успешно",
    "auth.logout_success": "Выход выполнен успешно",
    "auth.invalid_credentials": "Неверный email или пароль",

    # Patient
    "patient.first_name": "Имя",
    "patient.last_name": "Фамилия",
    "patient.phone": "Телефон",
    "patient.dob": "Дата рождения",
    "patient.category": "Медицинская категория",
    "patient.compliance": "Уровень ответственности",

    # Booking
    "booking.new": "Записаться на приём",
    "booking.upcoming": "Предстоящие приёмы",
    "booking.past": "Прошлые приёмы",
    "booking.cancel": "Отменить запись",
    "booking.reschedule": "Перенести",
    "booking.confirm": "Подтвердить запись",
    "booking.reason": "Причина визита",
    "booking.no_slots": "Нет доступных слотов",
    "booking.success": "Запись успешно создана",
    "booking.cancelled": "Запись отменена",
    "booking.rescheduled": "Запись перенесена",

    # Slots
    "slot.available": "Доступно",
    "slot.booked": "Занято",
    "slot.select_date": "Выберите дату",
    "slot.select_time": "Выберите время",

    # Compliance Questionnaire
    "questionnaire.compliance.title": "Анкета самооценки",
    "questionnaire.compliance.intro": "Пожалуйста, отвечайте честно для улучшения обслуживания.",
    "questionnaire.compliance.q1": "Как часто вы пропускаете записи?",
    "questionnaire.compliance.q2": "За сколько времени вы предупреждаете об отмене?",
    "questionnaire.compliance.q3": "Насколько важно для вас соблюдать расписание?",
    "questionnaire.compliance.q4": "Какова вероятность перезаписи при отмене?",
    "questionnaire.compliance.q5": "Насколько гибко ваше расписание?",
    "questionnaire.compliance.agree_24h": "Я обязуюсь предупреждать об отмене за 24+ часа",
    "questionnaire.compliance.agree_penalty": "Я понимаю, что неявки могут влиять на доступ",
    "questionnaire.compliance.agree_reschedule": "Я обязуюсь перезаписаться при отмене",
    "questionnaire.compliance.agree_comms": "Я согласен получать напоминания",

    # Triage Questionnaire
    "questionnaire.triage.title": "Запрос на отмену/перенос",
    "questionnaire.triage.reason": "Причина изменения",
    "questionnaire.triage.reason_work": "Рабочий конфликт",
    "questionnaire.triage.reason_health": "Проблемы со здоровьем",
    "questionnaire.triage.reason_family": "Семейные обстоятельства",
    "questionnaire.triage.reason_transport": "Проблемы с транспортом",
    "questionnaire.triage.reason_other": "Другое",
    "questionnaire.triage.symptoms": "Изменилось ли ваше состояние?",
    "questionnaire.triage.symptoms_worse": "Симптомы ухудшились",
    "questionnaire.triage.symptoms_new": "Появились новые симптомы",
    "questionnaire.triage.availability": "Можете перезаписаться в течение недели?",
    "questionnaire.triage.acknowledge": "Я понимаю влияние на мой рейтинг",
    "questionnaire.triage.commit": "Я обязуюсь явиться на новую запись",

    # Categories
    "category.critical": "Критический",
    "category.high_risk": "Высокий риск",
    "category.moderate": "Умеренный",
    "category.stable": "Стабильный",
    "category.maintenance": "Поддержка",
    "category.healthy": "Здоровый",

    # Compliance Levels
    "compliance.platinum": "Платина",
    "compliance.gold": "Золото",
    "compliance.silver": "Серебро",
    "compliance.bronze": "Бронза",
    "compliance.probation": "Испытательный",

    # Visit Frequency
    "frequency.weekly": "Еженедельно",
    "frequency.biweekly": "Раз в 2 недели",
    "frequency.monthly": "Ежемесячно",
    "frequency.bimonthly": "Раз в 2 месяца",
    "frequency.quarterly": "Ежеквартально",
    "frequency.biannual": "Раз в полгода",
    "frequency.annual": "Ежегодно",

    # Errors
    "error.required": "Обязательное поле",
    "error.invalid_email": "Неверный email",
    "error.password_short": "Пароль должен содержать минимум 8 символов",
    "error.passwords_mismatch": "Пароли не совпадают",
    "error.network": "Ошибка сети. Попробуйте снова.",
    "error.server": "Ошибка сервера. Попробуйте позже.",
    "error.not_found": "Не найдено",
    "error.unauthorized": "Необходимо войти",
    "error.forbidden": "Доступ запрещён",

    # Buttons
    "button.submit": "Отправить",
    "button.cancel": "Отмена",
    "button.save": "Сохранить",
    "button.next": "Далее",
    "button.back": "Назад",
    "button.close": "Закрыть",
    "button.confirm": "Подтвердить",

    # Messages
    "message.loading": "Загрузка...",
    "message.saving": "Сохранение...",
    "message.success": "Успешно!",
    "message.no_data": "Нет данных",
}

# All translations
TRANSLATIONS = {
    "en": EN,
    "he": HE,
    "ru": RU,
}


def get_translation(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Get a translated string by key.

    Args:
        key: Translation key (e.g., "auth.login")
        lang: Language code (en, he, ru)
        **kwargs: Formatting arguments

    Returns:
        Translated string or key if not found
    """
    translations = TRANSLATIONS.get(lang, EN)
    text = translations.get(key, EN.get(key, key))

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Shorthand for get_translation."""
    return get_translation(key, lang, **kwargs)
