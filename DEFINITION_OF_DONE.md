# ⚔️ Definition of Done - Iron Rule

> **"It's not done until it's tested AS DEPLOYED!"**
> — Alexander Aptus

## The Rule

- ❌ "Works on my machine" = **NOT DONE**
- ❌ "Tests pass in dev environment" = **NOT DONE**
- ✅ "Tests pass against PRODUCTION/STAGING URL" = **DONE**

## Requirements

1. **Deploy first** - Push to target environment (AWS, Vercel, etc.)
2. **Test deployed** - Run E2E tests against actual deployed URLs
3. **Real browser** - Use Playwright with real Chrome/DevTools
4. **User perspective** - Test what actual users will experience

## Why?

Because "it works in dev but not for users" is unacceptable.

## Testing Commands

```bash
# Test against AWS (production)
API_URL=https://nmpjiqngaz.us-east-1.awsapprunner.com \
PATIENT_URL=https://d2wowd7dw25och.cloudfront.net \
DOCTOR_URL=https://d24gl9ln0vt8cq.cloudfront.net \
pytest tests/e2e/ --headed

# Test against local (development only)
pytest tests/e2e/
```

## Remember

**The user doesn't run your dev environment. Test what they'll actually use.**
