# ⚔️ Iron Rules of Development
> — Alexander Aptus

---

## Rule 1: Definition of Done

> **"It's not done until it's tested AS DEPLOYED!"**

- ❌ "Works on my machine" = **NOT DONE**
- ❌ "Tests pass in dev environment" = **NOT DONE**
- ✅ "Tests pass against PRODUCTION/STAGING URL" = **DONE**

### Requirements

1. **Deploy first** - Push to target environment (AWS, Vercel, etc.)
2. **Test deployed** - Run E2E tests against actual deployed URLs
3. **Real browser** - Use Playwright with real Chrome/DevTools
4. **User perspective** - Test what actual users will experience

---

## Rule 2: No localhost Contamination

> **"localhost is ONLY for local_test - NEVER in demo, staging, or production!"**

### The Problem (Learned 2026-02-03)

Frontend was built with `http://localhost:3000` hardcoded. Deployed to AWS CloudFront. 
E2E tests passed locally. But USERS couldn't login because frontend called localhost 
instead of AWS API. Wasted hours debugging "Invalid email/password" that was actually 
a wrong URL.

### The Rules

1. **Environment variables ONLY** - Never hardcode URLs in source code
2. **Build-time injection** - Use `VITE_API_URL`, `NEXT_PUBLIC_API_URL`, etc.
3. **Test configs** - E2E tests MUST read URLs from environment variables
4. **Three tiers:**
   - `local_test` → localhost allowed (ONLY here)
   - `demo/staging` → MUST use real URLs
   - `production` → MUST use production URLs

### Detection (Add to CI/CD)

```bash
# Fail build if localhost found in production artifacts
if grep -r "localhost" dist/ 2>/dev/null; then
    echo "❌ FAIL: localhost contamination detected in build!"
    exit 1
fi
```

---

## Testing Commands

```bash
# Test against AWS (production) - THE REAL TEST
PATIENT_PWA_URL=https://d2wowd7dw25och.cloudfront.net \
DOCTOR_PWA_URL=https://d24gl9ln0vt8cq.cloudfront.net \
API_URL=https://nmpjiqngaz.us-east-1.awsapprunner.com \
pytest tests/e2e/ --headed

# Test against local (development ONLY - not Definition of Done!)
pytest tests/e2e/
```

---

## Remember

**The user doesn't run your dev environment. Test what they'll actually use.**

**Silent failures where app "works" but calls wrong backend are the worst bugs.**
