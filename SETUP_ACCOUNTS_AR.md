# تشغيل الحسابات: Google + Supabase

## 1. أضف رابط Streamlit إلى Google OAuth Client

في Google Cloud → Clients → AI Information Hub Web → Authorized redirect URIs أضف:

```text
http://localhost:8501/oauth2callback
```

اترك رابط Supabase callback الموجود لديك؛ يمكن وجود الرابطين معًا.

## 2. شغّل Migration

افتح Supabase → SQL Editor، والصق محتوى:

```text
migrations/002_streamlit_oidc_accounts.sql
```

ثم Run.

## 3. احصل على Supabase Secret key

من Supabase → Project Settings → API Keys:

- استخدم Secret key الجديدة، أو service_role القديمة.
- لا تستخدم Publishable/anon key لهذا المشروع.
- لا تضع المفتاح داخل GitHub.

## 4. أنشئ ملف الأسرار

انسخ:

```text
.streamlit/secrets.example.toml
```

إلى:

```text
.streamlit/secrets.toml
```

ثم ضع Client ID وClient Secret ورابط Supabase وSecret key.

ولإنشاء cookie_secret نفّذ في PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 5. التشغيل

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```

افتح:

```text
http://localhost:8501
```

## 6. عند النشر

غيّر redirect_uri إلى:

```text
https://YOUR-APP.streamlit.app/oauth2callback
```

وأضف نفس الرابط في Google Cloud، ثم انسخ الأسرار إلى Streamlit Cloud Secrets.

## ملاحظة هندسية

تسجيل الدخول يتم عبر Streamlit OIDC الرسمي. Supabase يُستخدم كقاعدة بيانات سحابية،
ويُنشئ التطبيق سجلًا مقابلاً داخل auth.users لكل مستخدم Google. Secret key تبقى على
الخادم فقط، وجميع عمليات القراءة والكتابة تُفلتر باستخدام user_id.
