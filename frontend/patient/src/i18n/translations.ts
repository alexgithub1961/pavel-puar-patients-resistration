// Translations for Patient PWA - EN, HE, RU

export type Language = 'en' | 'he' | 'ru';

export interface Translations {
  [key: string]: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    // App
    'app.name': 'PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)',
    'app.tagline': 'Smart Appointment Management',

    // Navigation
    'nav.home': 'Home',
    'nav.bookings': 'My Appointments',
    'nav.book': 'Book Now',
    'nav.profile': 'Profile',
    'nav.logout': 'Logout',

    // Auth
    'auth.login': 'Login',
    'auth.register': 'Register',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.confirmPassword': 'Confirm Password',
    'auth.firstName': 'First Name',
    'auth.lastName': 'Last Name',
    'auth.phone': 'Phone Number',
    'auth.dob': 'Date of Birth',
    'auth.noAccount': "Don't have an account?",
    'auth.haveAccount': 'Already have an account?',

    // Dashboard
    'dashboard.welcome': 'Welcome back',
    'dashboard.nextAppointment': 'Next Appointment',
    'dashboard.noUpcoming': 'No upcoming appointments',
    'dashboard.bookNow': 'Book an Appointment',
    'dashboard.complianceScore': 'Compliance Score',
    'dashboard.category': 'Your Category',
    'dashboard.visitFrequency': 'Visit Frequency',

    // Bookings
    'bookings.title': 'My Appointments',
    'bookings.upcoming': 'Upcoming',
    'bookings.past': 'Past',
    'bookings.cancel': 'Cancel',
    'bookings.reschedule': 'Reschedule',
    'bookings.noBookings': 'No appointments found',

    // New Booking
    'booking.title': 'Book Appointment',
    'booking.selectDate': 'Select a Date',
    'booking.selectTime': 'Select a Time',
    'booking.reason': 'Reason for Visit',
    'booking.confirm': 'Confirm Booking',
    'booking.success': 'Appointment booked successfully!',
    'booking.noSlots': 'No available slots for this period',

    // Profile
    'profile.title': 'My Profile',
    'profile.personalInfo': 'Personal Information',
    'profile.medicalInfo': 'Medical Information',
    'profile.compliance': 'Compliance Status',
    'profile.save': 'Save Changes',

    // Compliance Questionnaire
    'compliance.title': 'Compliance Self-Assessment',
    'compliance.intro': 'Please answer honestly to help us serve you better.',
    'compliance.q1': 'How often do you miss scheduled appointments?',
    'compliance.q2': 'How much advance notice do you give for cancellations?',
    'compliance.q3': 'How important is maintaining your appointment schedule?',
    'compliance.q4': 'How likely are you to reschedule if you must cancel?',
    'compliance.q5': 'How flexible is your schedule for appointments?',
    'compliance.scale.1': 'Very Poor',
    'compliance.scale.2': 'Poor',
    'compliance.scale.3': 'Average',
    'compliance.scale.4': 'Good',
    'compliance.scale.5': 'Excellent',
    'compliance.agree24h': 'I agree to give 24+ hours notice for cancellations',
    'compliance.agreePenalty': 'I understand repeated no-shows may affect my access',
    'compliance.agreeReschedule': 'I commit to rescheduling cancelled appointments',
    'compliance.agreeComms': 'I agree to receive appointment reminders',

    // Triage
    'triage.title': 'Cancellation Request',
    'triage.reason': 'Reason for cancellation',
    'triage.work': 'Work conflict',
    'triage.health': 'Health issue',
    'triage.family': 'Family emergency',
    'triage.transport': 'Transportation issue',
    'triage.other': 'Other',
    'triage.symptomsChanged': 'Have your symptoms changed?',
    'triage.symptomsWorse': 'Symptoms have worsened',
    'triage.newSymptoms': 'New symptoms appeared',
    'triage.acknowledge': 'I acknowledge this may affect my compliance rating',

    // Feature Tour
    'tour.title': 'Feature Tour',
    'tour.subtitle': 'Discover what you can do in this app',
    'tour.tryIt': 'Try it:',
    'tour.skip': 'Skip',
    'tour.next': 'Next',
    'tour.start': 'Start Exploring',
    'tour.feature.booking.title': 'Self-Booking Appointments',
    'tour.feature.booking.desc': 'Book appointments into time slots defined by your doctor. Your eligibility depends on your category and visit frequency rules.',
    'tour.feature.booking.try': 'Go to "Book Now" and select an available slot to schedule your appointment.',
    'tour.feature.compliance.title': 'Compliance Tracking',
    'tour.feature.compliance.desc': 'Your compliance score reflects your appointment discipline. Higher scores mean better access to appointment slots.',
    'tour.feature.compliance.try': 'Complete the Compliance Questionnaire to establish your initial score.',
    'tour.feature.triage.title': 'Smart Cancellation Triage',
    'tour.feature.triage.desc': 'Need to cancel? A short questionnaire evaluates urgency and commitment to help decide next steps.',
    'tour.feature.triage.try': 'Book an appointment first, then try the "Cancel" option to see the triage flow.',
    'tour.feature.frequency.title': 'Visit Frequency Rules',
    'tour.feature.frequency.desc': 'Your patient category determines how often you can book: from weekly (critical patients) to annual (healthy patients).',
    'tour.feature.frequency.try': 'Check your dashboard to see your category and when you can book next.',
    'tour.feature.priority.title': 'Fair Prioritisation',
    'tour.feature.priority.desc': 'When slots are scarce, the system fairly prioritises patients based on urgency, compliance, and wait time.',
    'tour.feature.priority.try': 'Maintain good compliance to improve your priority in slot allocation.',
    'tour.showAgain': 'Show Feature Tour',

    // Demo Mode
    'demo.title': 'Demo Mode',
    'demo.description': 'Try the app with a demo account',
    'demo.newPatient': 'New Patient Demo',
    'demo.newPatientDesc': 'No appointments yet',
    'demo.regularPatient': 'Regular Patient Demo',
    'demo.regularPatientDesc': 'Has appointment history',
    'demo.banner': 'DEMO MODE',
    'demo.bannerHint': 'Explore all features with sample data',
    'demo.hint.welcome.title': 'Welcome to Demo Mode!',
    'demo.hint.welcome.desc': 'Explore the patient portal. Your compliance score and category affect booking priority.',
    'demo.hint.book.title': 'Try Booking an Appointment',
    'demo.hint.book.desc': 'Click "Book Now" to see available slots and schedule a demo appointment.',

    // General
    'button.submit': 'Submit',
    'button.cancel': 'Cancel',
    'button.save': 'Save',
    'button.next': 'Next',
    'button.back': 'Back',
    'loading': 'Loading...',
    'error': 'An error occurred',
  },

  he: {
    // App
    'app.name': 'PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)',
    'app.tagline': 'ניהול תורים חכם',

    // Navigation
    'nav.home': 'בית',
    'nav.bookings': 'התורים שלי',
    'nav.book': 'קביעת תור',
    'nav.profile': 'פרופיל',
    'nav.logout': 'התנתק',

    // Auth
    'auth.login': 'התחברות',
    'auth.register': 'הרשמה',
    'auth.email': 'אימייל',
    'auth.password': 'סיסמה',
    'auth.confirmPassword': 'אימות סיסמה',
    'auth.firstName': 'שם פרטי',
    'auth.lastName': 'שם משפחה',
    'auth.phone': 'טלפון',
    'auth.dob': 'תאריך לידה',
    'auth.noAccount': 'אין לך חשבון?',
    'auth.haveAccount': 'יש לך כבר חשבון?',

    // Dashboard
    'dashboard.welcome': 'ברוך הבא',
    'dashboard.nextAppointment': 'התור הבא',
    'dashboard.noUpcoming': 'אין תורים קרובים',
    'dashboard.bookNow': 'קביעת תור',
    'dashboard.complianceScore': 'ציון התחייבות',
    'dashboard.category': 'הקטגוריה שלך',
    'dashboard.visitFrequency': 'תדירות ביקורים',

    // Bookings
    'bookings.title': 'התורים שלי',
    'bookings.upcoming': 'קרובים',
    'bookings.past': 'קודמים',
    'bookings.cancel': 'ביטול',
    'bookings.reschedule': 'שינוי מועד',
    'bookings.noBookings': 'לא נמצאו תורים',

    // New Booking
    'booking.title': 'קביעת תור חדש',
    'booking.selectDate': 'בחר תאריך',
    'booking.selectTime': 'בחר שעה',
    'booking.reason': 'סיבת הביקור',
    'booking.confirm': 'אישור הזמנה',
    'booking.success': 'התור נקבע בהצלחה!',
    'booking.noSlots': 'אין תורים פנויים בתקופה זו',

    // Profile
    'profile.title': 'הפרופיל שלי',
    'profile.personalInfo': 'מידע אישי',
    'profile.medicalInfo': 'מידע רפואי',
    'profile.compliance': 'סטטוס התחייבות',
    'profile.save': 'שמור שינויים',

    // Compliance Questionnaire
    'compliance.title': 'שאלון הערכה עצמית',
    'compliance.intro': 'אנא ענה בכנות כדי שנוכל לשרת אותך טוב יותר.',
    'compliance.q1': 'באיזו תדירות אתה מפספס תורים?',
    'compliance.q2': 'כמה הודעה מראש אתה נותן לביטולים?',
    'compliance.q3': 'כמה חשוב לך לשמור על לוח הזמנים שלך?',
    'compliance.q4': 'מה הסיכוי שתקבע תור חדש אם תבטל?',
    'compliance.q5': 'כמה גמיש לוח הזמנים שלך?',
    'compliance.scale.1': 'גרוע מאוד',
    'compliance.scale.2': 'גרוע',
    'compliance.scale.3': 'ממוצע',
    'compliance.scale.4': 'טוב',
    'compliance.scale.5': 'מעולה',
    'compliance.agree24h': 'אני מתחייב להודיע 24 שעות מראש על ביטולים',
    'compliance.agreePenalty': 'אני מבין שאי-הגעות חוזרות עלולות להשפיע על הגישה שלי',
    'compliance.agreeReschedule': 'אני מתחייב לקבוע תור חדש במקרה של ביטול',
    'compliance.agreeComms': 'אני מסכים לקבל תזכורות לתורים',

    // Triage
    'triage.title': 'בקשת ביטול',
    'triage.reason': 'סיבת הביטול',
    'triage.work': 'קונפליקט בעבודה',
    'triage.health': 'בעיה בריאותית',
    'triage.family': 'מקרה משפחתי',
    'triage.transport': 'בעיית תחבורה',
    'triage.other': 'אחר',
    'triage.symptomsChanged': 'האם המצב שלך השתנה?',
    'triage.symptomsWorse': 'התסמינים החמירו',
    'triage.newSymptoms': 'הופיעו תסמינים חדשים',
    'triage.acknowledge': 'אני מבין שזה עשוי להשפיע על דירוג ההתחייבות שלי',

    // Feature Tour
    'tour.title': 'סיור בתכונות',
    'tour.subtitle': 'גלה מה אפשר לעשות באפליקציה',
    'tour.tryIt': 'נסה זאת:',
    'tour.skip': 'דלג',
    'tour.next': 'הבא',
    'tour.start': 'התחל לחקור',
    'tour.feature.booking.title': 'קביעת תורים עצמאית',
    'tour.feature.booking.desc': 'קבע תורים בזמנים שהוגדרו על ידי הרופא. הזכאות תלויה בקטגוריה ובכללי תדירות הביקורים.',
    'tour.feature.booking.try': 'לך ל"קביעת תור" ובחר זמן פנוי לקביעת התור.',
    'tour.feature.compliance.title': 'מעקב התחייבות',
    'tour.feature.compliance.desc': 'ציון ההתחייבות משקף את המשמעת שלך בתורים. ציון גבוה = גישה טובה יותר לתורים.',
    'tour.feature.compliance.try': 'מלא את שאלון ההתחייבות כדי לקבוע את הציון ההתחלתי.',
    'tour.feature.triage.title': 'מיון ביטולים חכם',
    'tour.feature.triage.desc': 'צריך לבטל? שאלון קצר מעריך דחיפות ומחויבות כדי להחליט על הצעדים הבאים.',
    'tour.feature.triage.try': 'קבע תור קודם, ואז נסה את אפשרות "ביטול" לראות את תהליך המיון.',
    'tour.feature.frequency.title': 'כללי תדירות ביקורים',
    'tour.feature.frequency.desc': 'הקטגוריה שלך קובעת באיזו תדירות ניתן לקבוע תור: משבועי (מטופלים קריטיים) עד שנתי (בריאים).',
    'tour.feature.frequency.try': 'בדוק את לוח הבקרה לראות את הקטגוריה שלך ומתי תוכל לקבוע תור.',
    'tour.feature.priority.title': 'תעדוף הוגן',
    'tour.feature.priority.desc': 'כשיש מחסור בתורים, המערכת מתעדפת בצורה הוגנת לפי דחיפות, התחייבות וזמן המתנה.',
    'tour.feature.priority.try': 'שמור על התחייבות טובה כדי לשפר את העדיפות שלך בהקצאת תורים.',
    'tour.showAgain': 'הצג סיור בתכונות',

    // Demo Mode
    'demo.title': 'מצב הדגמה',
    'demo.description': 'נסה את האפליקציה עם חשבון הדגמה',
    'demo.newPatient': 'מטופל חדש להדגמה',
    'demo.newPatientDesc': 'ללא תורים עדיין',
    'demo.regularPatient': 'מטופל קבוע להדגמה',
    'demo.regularPatientDesc': 'עם היסטוריית תורים',
    'demo.banner': 'מצב הדגמה',
    'demo.bannerHint': 'חקור את כל התכונות עם נתוני דוגמה',
    'demo.hint.welcome.title': 'ברוכים הבאים למצב הדגמה!',
    'demo.hint.welcome.desc': 'חקור את פורטל המטופלים. ציון ההתחייבות והקטגוריה שלך משפיעים על עדיפות ההזמנה.',
    'demo.hint.book.title': 'נסה לקבוע תור',
    'demo.hint.book.desc': 'לחץ על "קביעת תור" לראות תורים פנויים ולקבוע תור להדגמה.',

    // General
    'button.submit': 'שלח',
    'button.cancel': 'ביטול',
    'button.save': 'שמור',
    'button.next': 'הבא',
    'button.back': 'חזרה',
    'loading': 'טוען...',
    'error': 'אירעה שגיאה',
  },

  ru: {
    // App
    'app.name': 'PUAR-Patients v1.0 (deployed 2026-02-08 13:45 UTC)',
    'app.tagline': 'Умное управление записями',

    // Navigation
    'nav.home': 'Главная',
    'nav.bookings': 'Мои записи',
    'nav.book': 'Записаться',
    'nav.profile': 'Профиль',
    'nav.logout': 'Выйти',

    // Auth
    'auth.login': 'Вход',
    'auth.register': 'Регистрация',
    'auth.email': 'Email',
    'auth.password': 'Пароль',
    'auth.confirmPassword': 'Подтвердите пароль',
    'auth.firstName': 'Имя',
    'auth.lastName': 'Фамилия',
    'auth.phone': 'Телефон',
    'auth.dob': 'Дата рождения',
    'auth.noAccount': 'Нет аккаунта?',
    'auth.haveAccount': 'Уже есть аккаунт?',

    // Dashboard
    'dashboard.welcome': 'Добро пожаловать',
    'dashboard.nextAppointment': 'Следующий приём',
    'dashboard.noUpcoming': 'Нет предстоящих приёмов',
    'dashboard.bookNow': 'Записаться на приём',
    'dashboard.complianceScore': 'Рейтинг ответственности',
    'dashboard.category': 'Ваша категория',
    'dashboard.visitFrequency': 'Частота визитов',

    // Bookings
    'bookings.title': 'Мои записи',
    'bookings.upcoming': 'Предстоящие',
    'bookings.past': 'Прошлые',
    'bookings.cancel': 'Отменить',
    'bookings.reschedule': 'Перенести',
    'bookings.noBookings': 'Записей не найдено',

    // New Booking
    'booking.title': 'Новая запись',
    'booking.selectDate': 'Выберите дату',
    'booking.selectTime': 'Выберите время',
    'booking.reason': 'Причина визита',
    'booking.confirm': 'Подтвердить запись',
    'booking.success': 'Запись успешно создана!',
    'booking.noSlots': 'Нет доступных слотов',

    // Profile
    'profile.title': 'Мой профиль',
    'profile.personalInfo': 'Личная информация',
    'profile.medicalInfo': 'Медицинская информация',
    'profile.compliance': 'Статус ответственности',
    'profile.save': 'Сохранить изменения',

    // Compliance Questionnaire
    'compliance.title': 'Анкета самооценки',
    'compliance.intro': 'Пожалуйста, отвечайте честно.',
    'compliance.q1': 'Как часто вы пропускаете записи?',
    'compliance.q2': 'За сколько предупреждаете об отмене?',
    'compliance.q3': 'Насколько важно соблюдать расписание?',
    'compliance.q4': 'Какова вероятность перезаписи при отмене?',
    'compliance.q5': 'Насколько гибко ваше расписание?',
    'compliance.scale.1': 'Очень плохо',
    'compliance.scale.2': 'Плохо',
    'compliance.scale.3': 'Средне',
    'compliance.scale.4': 'Хорошо',
    'compliance.scale.5': 'Отлично',
    'compliance.agree24h': 'Обязуюсь предупреждать за 24+ часа',
    'compliance.agreePenalty': 'Понимаю влияние неявок на доступ',
    'compliance.agreeReschedule': 'Обязуюсь перезаписываться при отмене',
    'compliance.agreeComms': 'Согласен получать напоминания',

    // Triage
    'triage.title': 'Запрос на отмену',
    'triage.reason': 'Причина отмены',
    'triage.work': 'Рабочий конфликт',
    'triage.health': 'Проблемы со здоровьем',
    'triage.family': 'Семейные обстоятельства',
    'triage.transport': 'Проблемы с транспортом',
    'triage.other': 'Другое',
    'triage.symptomsChanged': 'Изменилось ли состояние?',
    'triage.symptomsWorse': 'Симптомы ухудшились',
    'triage.newSymptoms': 'Появились новые симптомы',
    'triage.acknowledge': 'Понимаю влияние на рейтинг',

    // Feature Tour
    'tour.title': 'Обзор функций',
    'tour.subtitle': 'Узнайте, что можно делать в приложении',
    'tour.tryIt': 'Попробуйте:',
    'tour.skip': 'Пропустить',
    'tour.next': 'Далее',
    'tour.start': 'Начать',
    'tour.feature.booking.title': 'Самостоятельная запись',
    'tour.feature.booking.desc': 'Записывайтесь на приём в слоты, определённые врачом. Доступность зависит от категории и правил частоты визитов.',
    'tour.feature.booking.try': 'Перейдите в "Записаться" и выберите свободный слот.',
    'tour.feature.compliance.title': 'Отслеживание ответственности',
    'tour.feature.compliance.desc': 'Ваш рейтинг отражает дисциплину посещений. Высокий рейтинг = лучший доступ к слотам.',
    'tour.feature.compliance.try': 'Заполните анкету самооценки для установления начального рейтинга.',
    'tour.feature.triage.title': 'Умная отмена записи',
    'tour.feature.triage.desc': 'Нужно отменить? Короткая анкета оценит срочность и поможет определить следующие шаги.',
    'tour.feature.triage.try': 'Сначала запишитесь, затем попробуйте "Отменить" для просмотра процесса.',
    'tour.feature.frequency.title': 'Правила частоты визитов',
    'tour.feature.frequency.desc': 'Ваша категория определяет частоту записи: от еженедельной (критические) до ежегодной (здоровые).',
    'tour.feature.frequency.try': 'Проверьте главную страницу, чтобы увидеть категорию и когда можно записаться.',
    'tour.feature.priority.title': 'Справедливая приоритизация',
    'tour.feature.priority.desc': 'При нехватке слотов система справедливо приоритизирует по срочности, ответственности и времени ожидания.',
    'tour.feature.priority.try': 'Поддерживайте хороший рейтинг для улучшения приоритета.',
    'tour.showAgain': 'Показать обзор функций',

    // Demo Mode
    'demo.title': 'Демо-режим',
    'demo.description': 'Попробуйте приложение с демо-аккаунтом',
    'demo.newPatient': 'Демо: Новый пациент',
    'demo.newPatientDesc': 'Без записей',
    'demo.regularPatient': 'Демо: Постоянный пациент',
    'demo.regularPatientDesc': 'С историей записей',
    'demo.banner': 'ДЕМО-РЕЖИМ',
    'demo.bannerHint': 'Исследуйте все функции с тестовыми данными',
    'demo.hint.welcome.title': 'Добро пожаловать в демо-режим!',
    'demo.hint.welcome.desc': 'Изучите портал пациента. Ваш рейтинг и категория влияют на приоритет записи.',
    'demo.hint.book.title': 'Попробуйте записаться',
    'demo.hint.book.desc': 'Нажмите "Записаться" чтобы увидеть доступные слоты и создать демо-запись.',

    // General
    'button.submit': 'Отправить',
    'button.cancel': 'Отмена',
    'button.save': 'Сохранить',
    'button.next': 'Далее',
    'button.back': 'Назад',
    'loading': 'Загрузка...',
    'error': 'Произошла ошибка',
  },
};

export function t(key: string, lang: Language = 'en'): string {
  return translations[lang][key] || translations.en[key] || key;
}

export function isRTL(lang: Language): boolean {
  return lang === 'he';
}
