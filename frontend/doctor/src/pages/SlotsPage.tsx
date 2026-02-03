import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, addDays } from 'date-fns';
import { Plus, Trash2, Ban, Settings, Zap, Calendar } from 'lucide-react';
import { slotsApi, doctorApi } from '../api/client';

type SlotType = 'first_visit' | 'follow_up' | 'emergency';

export default function SlotsPage() {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [bulkForm, setBulkForm] = useState({
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate: format(addDays(new Date(), 30), 'yyyy-MM-dd'),
    weekdays: [0, 1, 2, 3, 4], // Mon-Fri (0-indexed: Mon=0)
    startTimes: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
    durationMinutes: 30,
    slotType: 'follow_up' as SlotType,
  });

  // Slot distribution settings
  const [distribution, setDistribution] = useState({
    first_visit: 20,
    follow_up: 70,
    emergency: 10,
  });

  // Auto-generate settings
  const [autoGenForm, setAutoGenForm] = useState({
    days: 90,
    weekdays: [0, 1, 2, 3, 4], // Mon-Fri
    startTimes: ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30', '16:00'],
    durationMinutes: 30,
  });

  const { data: _doctor } = useQuery({
    queryKey: ['doctor'],
    queryFn: async () => {
      const response = await doctorApi.getMe();
      // Load distribution from doctor settings
      if (response.data.slot_distribution) {
        setDistribution(response.data.slot_distribution);
      }
      return response.data;
    },
  });

  const { data: slots, isLoading } = useQuery({
    queryKey: ['slots'],
    queryFn: async () => {
      const response = await slotsApi.getAll({ page_size: 100 });
      return response.data;
    },
  });

  const createBulkMutation = useMutation({
    mutationFn: async () => {
      return slotsApi.createBulk({
        start_date: new Date(bulkForm.startDate).toISOString(),
        end_date: new Date(bulkForm.endDate).toISOString(),
        weekdays: bulkForm.weekdays,
        start_times: bulkForm.startTimes,
        duration_minutes: bulkForm.durationMinutes,
        slot_type: bulkForm.slotType,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slots'] });
      setShowCreateModal(false);
    },
  });

  const autoGenerateMutation = useMutation({
    mutationFn: async () => {
      return slotsApi.autoGenerate({
        days: autoGenForm.days,
        weekdays: autoGenForm.weekdays,
        start_times: autoGenForm.startTimes,
        duration_minutes: autoGenForm.durationMinutes,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slots'] });
      setShowSettingsModal(false);
    },
  });

  const updateDistributionMutation = useMutation({
    mutationFn: async () => {
      return doctorApi.updateMe({
        slot_distribution: distribution,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor'] });
    },
  });

  const blockMutation = useMutation({
    mutationFn: async (slotId: string) => {
      return slotsApi.block(slotId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slots'] });
    },
  });

  const deleteRecurringMutation = useMutation({
    mutationFn: async (recurrenceGroupId: string) => {
      return slotsApi.deleteRecurring(recurrenceGroupId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['slots'] });
    },
  });

  const handleWeekdayToggle = (day: number) => {
    setBulkForm((prev) => ({
      ...prev,
      weekdays: prev.weekdays.includes(day)
        ? prev.weekdays.filter((d) => d !== day)
        : [...prev.weekdays, day].sort(),
    }));
  };

  const weekdays = [
    { value: 0, label: 'Mon' },
    { value: 1, label: 'Tue' },
    { value: 2, label: 'Wed' },
    { value: 3, label: 'Thu' },
    { value: 4, label: 'Fri' },
    { value: 5, label: 'Sat' },
    { value: 6, label: 'Sun' },
  ];

  const slotTypes = [
    { value: 'first_visit', label: 'First Visit', color: 'purple' },
    { value: 'follow_up', label: 'Follow-up', color: 'blue' },
    { value: 'emergency', label: 'Emergency', color: 'red' },
  ];

  const handleDistributionChange = (type: keyof typeof distribution, value: number) => {
    const total = Object.entries(distribution)
      .filter(([key]) => key !== type)
      .reduce((sum, [, val]) => sum + val, value);

    if (total <= 100) {
      setDistribution((prev) => ({ ...prev, [type]: value }));
    }
  };

  const getSlotTypeColor = (slotType: string) => {
    switch (slotType) {
      case 'first_visit':
        return 'bg-purple-100 text-purple-800';
      case 'emergency':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const handleAutoGenWeekdayToggle = (day: number) => {
    setAutoGenForm((prev) => ({
      ...prev,
      weekdays: prev.weekdays.includes(day)
        ? prev.weekdays.filter((d) => d !== day)
        : [...prev.weekdays, day].sort(),
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Manage Slots</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowSettingsModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Settings className="w-5 h-5" />
            Distribution Settings
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
          >
            <Plus className="w-5 h-5" />
            Create Slots
          </button>
        </div>
      </div>

      {/* Slots List */}
      {isLoading ? (
        <p className="text-gray-500 py-8 text-center">Loading...</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {slots?.items?.map((slot: {
                id: string;
                start_time: string;
                end_time: string;
                duration_minutes: number;
                slot_type: string;
                status: string;
                recurrence_group_id: string | null;
              }) => (
                <tr key={slot.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <p className="font-medium">
                      {format(new Date(slot.start_time), 'MMM d, yyyy')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {format(new Date(slot.start_time), 'h:mm a')} -{' '}
                      {format(new Date(slot.end_time), 'h:mm a')}
                    </p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {slot.duration_minutes} min
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getSlotTypeColor(slot.slot_type)}`}
                    >
                      {slot.slot_type?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        slot.status === 'available'
                          ? 'bg-green-100 text-green-800'
                          : slot.status === 'booked'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {slot.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-2">
                      {slot.status === 'available' && (
                        <button
                          onClick={() => blockMutation.mutate(slot.id)}
                          className="p-1 text-orange-600 hover:bg-orange-50 rounded"
                          title="Block slot"
                        >
                          <Ban className="w-4 h-4" />
                        </button>
                      )}
                      {slot.recurrence_group_id && (
                        <button
                          onClick={() =>
                            deleteRecurringMutation.mutate(slot.recurrence_group_id!)
                          }
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          title="Delete all recurring"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Create Recurring Slots</h2>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={bulkForm.startDate}
                    onChange={(e) =>
                      setBulkForm({ ...bulkForm, startDate: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={bulkForm.endDate}
                    onChange={(e) =>
                      setBulkForm({ ...bulkForm, endDate: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Days of Week
                </label>
                <div className="flex flex-wrap gap-2">
                  {weekdays.map((day) => (
                    <button
                      key={day.value}
                      type="button"
                      onClick={() => handleWeekdayToggle(day.value)}
                      className={`px-3 py-1 rounded-full text-sm ${
                        bulkForm.weekdays.includes(day.value)
                          ? 'bg-emerald-600 text-white'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {day.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (minutes)
                </label>
                <select
                  value={bulkForm.durationMinutes}
                  onChange={(e) =>
                    setBulkForm({
                      ...bulkForm,
                      durationMinutes: parseInt(e.target.value),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value={15}>15 min</option>
                  <option value={30}>30 min</option>
                  <option value={45}>45 min</option>
                  <option value={60}>60 min</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Slot Type
                </label>
                <div className="flex flex-wrap gap-2">
                  {slotTypes.map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setBulkForm({ ...bulkForm, slotType: type.value as SlotType })}
                      className={`px-3 py-1 rounded-full text-sm ${
                        bulkForm.slotType === type.value
                          ? type.color === 'purple'
                            ? 'bg-purple-600 text-white'
                            : type.color === 'red'
                            ? 'bg-red-600 text-white'
                            : 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => createBulkMutation.mutate()}
                disabled={createBulkMutation.isPending}
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
              >
                {createBulkMutation.isPending ? 'Creating...' : 'Create Slots'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings & Auto-Generate Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Slot Distribution & Auto-Generate
            </h2>

            {/* Distribution Settings */}
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">Slot Type Distribution</h3>
              <p className="text-sm text-gray-500 mb-4">
                Set the percentage of each slot type when auto-generating. Total must equal 100%.
              </p>

              <div className="space-y-4">
                {slotTypes.map((type) => (
                  <div key={type.value} className="flex items-center gap-4">
                    <span className={`w-24 text-sm font-medium ${
                      type.color === 'purple' ? 'text-purple-600' :
                      type.color === 'red' ? 'text-red-600' : 'text-blue-600'
                    }`}>
                      {type.label}
                    </span>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={distribution[type.value as keyof typeof distribution]}
                      onChange={(e) =>
                        handleDistributionChange(
                          type.value as keyof typeof distribution,
                          parseInt(e.target.value)
                        )
                      }
                      className="flex-1"
                    />
                    <span className="w-12 text-right text-sm font-medium">
                      {distribution[type.value as keyof typeof distribution]}%
                    </span>
                  </div>
                ))}
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total:</span>
                  <span className={`font-medium ${
                    distribution.first_visit + distribution.follow_up + distribution.emergency === 100
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}>
                    {distribution.first_visit + distribution.follow_up + distribution.emergency}%
                  </span>
                </div>
              </div>

              <button
                onClick={() => updateDistributionMutation.mutate()}
                disabled={
                  updateDistributionMutation.isPending ||
                  distribution.first_visit + distribution.follow_up + distribution.emergency !== 100
                }
                className="mt-4 w-full py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                {updateDistributionMutation.isPending ? 'Saving...' : 'Save Distribution'}
              </button>
            </div>

            {/* Auto-Generate Section */}
            <div className="border-t pt-6">
              <h3 className="text-md font-medium text-gray-700 mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Auto-Generate Slots
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Generate slots for the next {autoGenForm.days} days with the distribution above.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Days Ahead
                  </label>
                  <select
                    value={autoGenForm.days}
                    onChange={(e) => setAutoGenForm({ ...autoGenForm, days: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value={30}>30 days</option>
                    <option value={60}>60 days</option>
                    <option value={90}>90 days (Recommended)</option>
                    <option value={180}>180 days</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Days of Week
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {weekdays.map((day) => (
                      <button
                        key={day.value}
                        type="button"
                        onClick={() => handleAutoGenWeekdayToggle(day.value)}
                        className={`px-3 py-1 rounded-full text-sm ${
                          autoGenForm.weekdays.includes(day.value)
                            ? 'bg-emerald-600 text-white'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {day.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <select
                    value={autoGenForm.durationMinutes}
                    onChange={(e) =>
                      setAutoGenForm({ ...autoGenForm, durationMinutes: parseInt(e.target.value) })
                    }
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value={15}>15 min</option>
                    <option value={30}>30 min</option>
                    <option value={45}>45 min</option>
                    <option value={60}>60 min</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => autoGenerateMutation.mutate()}
                disabled={
                  autoGenerateMutation.isPending ||
                  distribution.first_visit + distribution.follow_up + distribution.emergency !== 100
                }
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Calendar className="w-4 h-4" />
                {autoGenerateMutation.isPending ? 'Generating...' : 'Auto-Generate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
