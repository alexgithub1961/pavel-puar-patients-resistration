import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { format, startOfDay, addDays, parseISO, isSameDay } from 'date-fns';
import { Calendar, Clock, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { slotsApi, bookingsApi, patientApi } from '../api/client';
import { t } from '../i18n/translations';

interface Slot {
  id: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  doctor_name: string;
  slot_type: 'first_visit' | 'follow_up' | 'emergency';
}

export default function NewBookingPage() {
  const navigate = useNavigate();
  const { language } = useAuthStore();
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [reason, setReason] = useState('');
  const [step, setStep] = useState(1);

  // Emergency booking state
  const [isEmergency, setIsEmergency] = useState(false);
  const [urgencyReason, setUrgencyReason] = useState('');

  // Hardcoded doctor ID for MVP (single doctor)
  const doctorId = 'a926a78f-3c8d-4c67-8618-cdce3d06ee05';  // Demo doctor UUID

  const { data: bookingWindow } = useQuery({
    queryKey: ['bookingWindow'],
    queryFn: async () => {
      const response = await patientApi.getBookingWindow();
      return response.data;
    },
  });

  // Fetch dates with available slots for calendar
  const { data: availableDatesData } = useQuery({
    queryKey: ['availableDates', isEmergency],
    queryFn: async () => {
      if (isEmergency) {
        const response = await slotsApi.getEmergencySlots(doctorId);
        // Extract unique dates from emergency slots
        const dates = [...new Set(
          response.data.map((slot: Slot) =>
            startOfDay(parseISO(slot.start_time)).toISOString()
          )
        )];
        return { dates, total_slots: response.data.length };
      }
      const response = await slotsApi.getAvailableDates(doctorId);
      return response.data;
    },
    enabled: bookingWindow?.can_book || isEmergency,
  });

  // Parse available dates for calendar highlighting
  const availableDateSet = useMemo(() => {
    if (!availableDatesData?.dates) return new Set<string>();
    return new Set(
      availableDatesData.dates.map((d: string) =>
        startOfDay(parseISO(d)).toISOString()
      )
    );
  }, [availableDatesData]);

  const { data: slots, isLoading: slotsLoading } = useQuery({
    queryKey: ['slots', selectedDate, isEmergency],
    queryFn: async () => {
      if (!selectedDate) return { items: [] };
      const start = startOfDay(selectedDate).toISOString();
      const end = startOfDay(addDays(selectedDate, 1)).toISOString();

      if (isEmergency) {
        const response = await slotsApi.getEmergencySlots(doctorId);
        // Filter to selected date
        const filteredSlots = response.data.filter((slot: Slot) =>
          isSameDay(parseISO(slot.start_time), selectedDate)
        );
        return { items: filteredSlots };
      }

      const response = await slotsApi.getAvailable(doctorId, start, end);
      // API returns array directly, wrap it in {items: [...]}
      const slotsData = Array.isArray(response.data) ? response.data : response.data.items || [];
      return { items: slotsData };
    },
    enabled: !!selectedDate,
  });

  const createBookingMutation = useMutation({
    mutationFn: async () => {
      if (!selectedSlot) throw new Error('No slot selected');
      return bookingsApi.create(
        selectedSlot.id,
        doctorId,
        reason,
        isEmergency,
        isEmergency ? urgencyReason : undefined
      );
    },
    onSuccess: () => {
      navigate('/bookings');
    },
  });

  const canBook = bookingWindow?.can_book ?? false;

  // Check if date has available slots
  const isDateAvailable = (date: Date) => {
    return availableDateSet.has(startOfDay(date).toISOString());
  };

  // Get slot type display info
  const getSlotTypeInfo = (slotType: string) => {
    switch (slotType) {
      case 'first_visit':
        return { label: 'First Visit', color: 'bg-purple-100 text-purple-800' };
      case 'emergency':
        return { label: 'Emergency', color: 'bg-red-100 text-red-800' };
      default:
        return { label: 'Follow-up', color: 'bg-blue-100 text-blue-800' };
    }
  };

  // Generate dates for the next 30 days
  // For follow-ups, start from the earliest booking date (based on visit frequency)
  const getStartDate = () => {
    if (isEmergency) return new Date(); // Emergency can book immediately
    if (bookingWindow?.earliest_date) {
      const earliest = parseISO(bookingWindow.earliest_date);
      return earliest > new Date() ? earliest : new Date();
    }
    return new Date();
  };

  const startDate = getStartDate();
  const availableDates = (canBook || isEmergency)
    ? Array.from({ length: 30 }, (_, i) => addDays(startDate, i))
    : [];

  const handleConfirm = () => {
    createBookingMutation.mutate();
  };

  if (!canBook && bookingWindow && !isEmergency) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-yellow-600 mt-0.5" />
            <div>
              <h2 className="text-lg font-semibold text-yellow-800">
                Cannot Book at This Time
              </h2>
              <p className="text-yellow-700 mt-1">{bookingWindow.reason}</p>
              {bookingWindow.earliest_date && (
                <p className="text-yellow-700 mt-2">
                  You can book from:{' '}
                  {format(new Date(bookingWindow.earliest_date), 'MMMM d, yyyy')}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Emergency booking option */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5" />
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-red-800">
                Need an Emergency Appointment?
              </h2>
              <p className="text-red-700 mt-1">
                If you have an urgent medical issue, you can book an emergency slot.
              </p>
              <button
                onClick={() => setIsEmergency(true)}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Book Emergency Appointment
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{t('booking.title', language)}</h1>
        {isEmergency && (
          <button
            onClick={() => {
              setIsEmergency(false);
              setUrgencyReason('');
              setSelectedDate(null);
              setSelectedSlot(null);
              setStep(1);
            }}
            className="text-sm text-gray-600 hover:text-gray-800"
          >
            ← Back to normal booking
          </button>
        )}
      </div>

      {/* Emergency Mode Banner */}
      {isEmergency && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-medium text-red-800">Emergency Booking Mode</span>
          </div>
          <p className="text-sm text-red-700 mt-1">
            You are booking an emergency slot. Please provide details about your urgent situation.
          </p>
        </div>
      )}

      {/* Emergency Toggle (when booking is allowed) */}
      {canBook && !isEmergency && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={isEmergency}
              onChange={(e) => {
                setIsEmergency(e.target.checked);
                setSelectedDate(null);
                setSelectedSlot(null);
                setStep(1);
              }}
              className="w-4 h-4 text-red-600 rounded border-gray-300 focus:ring-red-500"
            />
            <div>
              <span className="font-medium text-gray-800">I need an emergency appointment</span>
              <p className="text-sm text-gray-600">
                Check this if you have urgent symptoms that cannot wait for a regular appointment
              </p>
            </div>
          </label>
        </div>
      )}

      {/* Progress Steps */}
      <div className="flex items-center justify-between">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                step >= s
                  ? isEmergency ? 'bg-red-600 text-white' : 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {step > s ? <CheckCircle className="w-5 h-5" /> : s}
            </div>
            {s < 3 && (
              <div
                className={`w-24 h-1 mx-2 ${
                  step > s ? (isEmergency ? 'bg-red-600' : 'bg-primary-600') : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Select Date */}
      {step === 1 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Calendar className={`w-5 h-5 ${isEmergency ? 'text-red-600' : ''}`} />
            {t('booking.selectDate', language)}
          </h2>

          {/* Smart start date info */}
          {bookingWindow?.earliest_date && !isEmergency && (
            <p className="text-sm text-gray-600 mb-4">
              Based on your visit frequency, your booking window starts from{' '}
              <span className="font-medium">
                {format(parseISO(bookingWindow.earliest_date), 'MMMM d, yyyy')}
              </span>
            </p>
          )}

          <div className="react-calendar" data-testid="calendar">
            <div className="react-calendar__month-view__days grid grid-cols-3 md:grid-cols-5 gap-2">
            {availableDates.map((date) => {
              const hasSlots = isDateAvailable(date);
              const isSelected = selectedDate?.toDateString() === date.toDateString();

              return (
                <button
                  key={date.toISOString()}
                  name={`day-${format(date, 'yyyy-MM-dd')}`}
                  onClick={() => {
                    if (hasSlots) {
                      setSelectedDate(date);
                      setStep(2);
                    }
                  }}
                  disabled={!hasSlots}
                  className={`react-calendar__tile p-3 rounded-lg text-center border transition-colors ${
                    isSelected
                      ? isEmergency
                        ? 'border-red-600 bg-red-50'
                        : 'border-primary-600 bg-primary-50'
                      : hasSlots
                      ? isEmergency
                        ? 'border-gray-200 hover:bg-red-50 hover:border-red-300'
                        : 'border-gray-200 hover:bg-primary-50'
                      : 'border-gray-100 bg-gray-50 cursor-not-allowed'
                  }`}
                >
                  <div className={`text-xs ${hasSlots ? 'text-gray-500' : 'text-gray-300'}`}>
                    {format(date, 'EEE')}
                  </div>
                  <div className={`font-medium ${hasSlots ? '' : 'text-gray-300'}`}>
                    {format(date, 'd')}
                  </div>
                  <div className={`text-xs ${hasSlots ? 'text-gray-500' : 'text-gray-300'}`}>
                    {format(date, 'MMM')}
                  </div>
                  {!hasSlots && (
                    <div className="text-xs text-gray-400 mt-1">No slots</div>
                  )}
                </button>
              );
            })}
            </div>
          </div>

          {availableDatesData?.total_slots === 0 && (
            <p className="text-center text-gray-500 mt-4">
              No available slots in this period. Please try again later.
            </p>
          )}
        </div>
      )}

      {/* Step 2: Select Time */}
      {step === 2 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5" />
              {t('booking.selectTime', language)}
            </h2>
            <button
              onClick={() => setStep(1)}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              {t('button.back', language)}
            </button>
          </div>

          <p className="text-gray-600 mb-4">
            {selectedDate && format(selectedDate, 'EEEE, MMMM d, yyyy')}
          </p>

          {slotsLoading ? (
            <p className="text-gray-500 py-8 text-center">{t('loading', language)}</p>
          ) : slots?.items?.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">{t('booking.noSlots', language)}</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {slots?.items?.map((slot: Slot) => {
                const typeInfo = getSlotTypeInfo(slot.slot_type);
                const isSelected = selectedSlot?.id === slot.id;

                return (
                  <button
                    key={slot.id}
                    onClick={() => {
                      setSelectedSlot(slot);
                      setStep(3);
                    }}
                    className={`p-3 rounded-lg text-left border transition-colors ${
                      isSelected
                        ? isEmergency
                          ? 'border-red-600 bg-red-50'
                          : 'border-primary-600 bg-primary-50'
                        : isEmergency
                        ? 'border-gray-200 hover:bg-red-50 hover:border-red-300'
                        : 'border-gray-200 hover:bg-primary-50'
                    }`}
                  >
                    <div className="font-medium">
                      {format(new Date(slot.start_time), 'h:mm a')}
                    </div>
                    <div className="text-sm text-gray-500">
                      {slot.duration_minutes} min
                    </div>
                    <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs ${typeInfo.color}`}>
                      {typeInfo.label}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Step 3: Confirm */}
      {step === 3 && selectedSlot && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">{t('booking.confirm', language)}</h2>
            <button
              onClick={() => setStep(2)}
              className={`text-sm ${isEmergency ? 'text-red-600 hover:text-red-700' : 'text-primary-600 hover:text-primary-700'}`}
            >
              {t('button.back', language)}
            </button>
          </div>

          <div className="space-y-4 mb-6">
            <div className={`flex items-center gap-3 p-4 rounded-lg ${isEmergency ? 'bg-red-50' : 'bg-gray-50'}`}>
              <Calendar className={`w-5 h-5 ${isEmergency ? 'text-red-600' : 'text-primary-600'}`} />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="font-medium">
                    {format(new Date(selectedSlot.start_time), 'EEEE, MMMM d, yyyy')}
                  </p>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${getSlotTypeInfo(selectedSlot.slot_type).color}`}>
                    {getSlotTypeInfo(selectedSlot.slot_type).label}
                  </span>
                </div>
                <p className="text-gray-600">
                  {format(new Date(selectedSlot.start_time), 'h:mm a')} -{' '}
                  {format(new Date(selectedSlot.end_time), 'h:mm a')}
                </p>
              </div>
            </div>

            {/* Emergency urgency reason - required for emergency bookings */}
            {isEmergency && (
              <div>
                <label className="block text-sm font-medium text-red-700 mb-1">
                  Urgency Reason <span className="text-red-600">*</span>
                </label>
                <textarea
                  value={urgencyReason}
                  onChange={(e) => setUrgencyReason(e.target.value)}
                  rows={3}
                  required
                  className="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500"
                  placeholder="Please describe your urgent symptoms or situation (required)"
                />
                {urgencyReason.length < 10 && (
                  <p className="text-red-600 text-sm mt-1">
                    Please provide at least 10 characters describing your urgent situation
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('booking.reason', language)}
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Optional: Describe the reason for your visit"
              />
            </div>
          </div>

          <button
            onClick={handleConfirm}
            disabled={createBookingMutation.isPending || (isEmergency && urgencyReason.length < 10)}
            className={`w-full py-3 text-white rounded-lg disabled:opacity-50 font-medium ${
              isEmergency
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-primary-600 hover:bg-primary-700'
            }`}
          >
            {createBookingMutation.isPending
              ? t('loading', language)
              : isEmergency
              ? 'Confirm Emergency Booking'
              : t('booking.confirm', language)}
          </button>

          {createBookingMutation.isError && (
            <p className="text-red-600 text-sm mt-2 text-center">
              {t('error', language)}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
