import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { CheckCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { patientApi } from '../api/client';
import { t } from '../i18n/translations';

export default function ComplianceQuestionnairePage() {
  const navigate = useNavigate();
  const { language } = useAuthStore();

  const [ratings, setRatings] = useState({
    q1: 3,
    q2: 3,
    q3: 3,
    q4: 3,
    q5: 3,
  });

  const [agreements, setAgreements] = useState({
    agree24h: false,
    agreePenalty: false,
    agreeReschedule: false,
    agreeComms: false,
  });

  const submitMutation = useMutation({
    mutationFn: async () => {
      return patientApi.submitComplianceQuestionnaire({
        missed_appointments_rating: ratings.q1,
        cancellation_notice_rating: ratings.q2,
        schedule_importance_rating: ratings.q3,
        reschedule_commitment_rating: ratings.q4,
        flexibility_rating: ratings.q5,
        agrees_24h_cancellation: agreements.agree24h,
        agrees_no_show_penalty: agreements.agreePenalty,
        agrees_reschedule_policy: agreements.agreeReschedule,
        agrees_communication_preferences: agreements.agreeComms,
      });
    },
    onSuccess: () => {
      navigate('/dashboard');
    },
  });

  const questions = [
    { key: 'q1', text: t('compliance.q1', language) },
    { key: 'q2', text: t('compliance.q2', language) },
    { key: 'q3', text: t('compliance.q3', language) },
    { key: 'q4', text: t('compliance.q4', language) },
    { key: 'q5', text: t('compliance.q5', language) },
  ] as const;

  const agreementItems = [
    { key: 'agree24h', text: t('compliance.agree24h', language) },
    { key: 'agreePenalty', text: t('compliance.agreePenalty', language) },
    { key: 'agreeReschedule', text: t('compliance.agreeReschedule', language) },
    { key: 'agreeComms', text: t('compliance.agreeComms', language) },
  ] as const;

  const allAgreed = Object.values(agreements).every(Boolean);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('compliance.title', language)}
        </h1>
        <p className="text-gray-600">{t('compliance.intro', language)}</p>
      </div>

      {/* Rating Questions */}
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {questions.map(({ key, text }) => (
          <div key={key}>
            <p className="font-medium text-gray-900 mb-3">{text}</p>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  onClick={() => setRatings({ ...ratings, [key]: value })}
                  className={`flex-1 py-2 px-3 rounded-lg border text-center transition-colors ${
                    ratings[key] === value
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">{value}</div>
                  <div className="text-xs text-gray-500">
                    {t(`compliance.scale.${value}` as keyof typeof t, language)}
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Agreement Checkboxes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Commitments</h2>
        <div className="space-y-4">
          {agreementItems.map(({ key, text }) => (
            <label key={key} className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={agreements[key]}
                onChange={(e) =>
                  setAgreements({ ...agreements, [key]: e.target.checked })
                }
                className="mt-1 h-5 w-5 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
              />
              <span className="text-gray-700">{text}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={() => submitMutation.mutate()}
        disabled={!allAgreed || submitMutation.isPending}
        className="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
      >
        {submitMutation.isPending ? (
          t('loading', language)
        ) : (
          <>
            <CheckCircle className="w-5 h-5" />
            {t('button.submit', language)}
          </>
        )}
      </button>

      {!allAgreed && (
        <p className="text-center text-sm text-gray-500">
          Please accept all commitments to continue
        </p>
      )}

      {submitMutation.isError && (
        <p className="text-center text-sm text-red-600">{t('error', language)}</p>
      )}
    </div>
  );
}
