# AI Information Hub V10 Ultimate

Final professional redesign built on V9.2 Production Fix.

# AI Information Hub V9 Professional

نسخة صقل وتحسين مبنية على V8.1، مع الحفاظ على Google OIDC وSupabase وRender.

## أبرز التحسينات

- واجهة أكثر اتساقًا ووضوحًا بعد تسجيل الدخول.
- تحسينات كبيرة للجوال والمساحات والأزرار والبطاقات والجداول.
- حفظ الصفحة الحالية في رابط URL لتبقى بعد التحديث ويمكن مشاركتها.
- عزل أخطاء الصفحات حتى لا يتوقف التطبيق كاملًا عند فشل خدمة خارجية.
- تقليل مهلة الاتصالات الخارجية وعدد المحاولات لتجنب التعليق الطويل.
- جعل فحص Wikipedia/Ollama يدويًا ومخزنًا مؤقتًا بدل تأخير لوحة التحكم.
- تصدير PDF وWord وPNG وTXT وJSON.
- إبقاء دعم العربية والإنجليزية في ملفات التقارير.
- بنية حزمة نظيفة: الملفات في الجذر مباشرة، وليس داخل مجلد إضافي.

## النشر

ضع ملفات هذا المجلد في جذر مستودع GitHub. في Render اجعل Root Directory فارغًا عند رفع الملفات للجذر، أو احتفظ بإعدادك الحالي إذا وضعت النسخة داخل مجلد فرعي.

لا ترفع `.streamlit/secrets.toml` إلى GitHub.

## V9.1 Polished fixes

- Actual Arabic/English UI preference with translated navigation, home, settings, and shared page headers.
- Immediate dark/light appearance switching with stronger styling for native Streamlit controls.
- Global RTL/LTR direction based on the selected interface language.
- Optional service health checks so the settings page does not block on external services.
- Arabic report language is explicitly preserved in exports instead of being guessed from mixed content.
- Arabic PDF/PNG cards align all report content to the right, including proper names and mixed-language lines.
- DOCX headings follow the selected report language.
- When local Ollama is unavailable on Render, article text is translated before building the Arabic fallback summary.
- Added `deep-translator` for production fallback translation.
- No real secrets are included.

### Render

Because the files are in the repository root, keep **Root Directory empty**.

## V9.2 Production Fix

- News date filters are now included in the Google News query itself, not only applied after downloading the latest feed.
- Custom date ranges support the selected end date correctly.
- Entity search validates input, retries Arabic and English Wikipedia, and shows the real failure message.
- AI chat and article Q&A support an OpenAI-compatible cloud provider through Render secrets.
- Ollama remains available for local development.
- Production AI status is visible in Settings.


## V10 highlights
- Complete visual redesign with mint, coral, and deep evergreen palette.
- New intelligence-workspace home experience.
- Responsive mobile layout.
- Redesigned navigation and account identity panel.
- Improved bilingual dashboard and fault-tolerant metrics.
- Production error logging without exposing stack traces to users.
- Preserves news, people, comparison, entities, assistant, account, export, Google login, and Supabase flows.


## V10.2 Visual & Mobile Fix
- إصلاح اختفاء الشريط الجانبي بالكامل على الجوال دون ترك مساحة فارغة.
- إزالة ألوان الهوية البنفسجية القديمة من الأزرار والنقاط والاختيارات والمنزلقات.
- توحيد الهوية على Mint وEvergreen وCoral.
- إضافة اختبارات رجعية للطي والألوان.


## V10.3 News Search Fix
- جلب Google News RSS باستخدام جلسة HTTP وهوية متصفح واضحة بدل عميل feedparser الافتراضي.
- إعادة المحاولة تلقائيًا بدون معاملات التاريخ إذا أعادت Google خلاصة فارغة.
- تطبيق الفترة الزمنية محليًا بعد الجلب لمنع النتائج الصفرية الكاذبة.
- تحسين اكتشاف فشل الاتصال بدل عرضه كأنه لا توجد أخبار.
- إضافة اختبارات رجعية للبحث العربي وفشل معاملات التاريخ.

## V10.4 Language & Theme Fix

- Rebuilt news filters around stable internal values, with complete Arabic/English display labels.
- Translated the major user-facing workflows: News, People, Entities, Comparisons, AI Assistant, Account, and Settings.
- Language selection now forces a clean rerun so widgets and direction update together.
- Appearance selection now forces a clean rerun and applies stronger light/dark CSS to the Streamlit shell, sidebar, forms, menus, alerts, and code blocks.
- Country and category names are localized without changing the values used by the news service.
- AI chat direction, role names, buttons, and messages follow the selected interface language.
- Added regression tests for bilingual filters, major page translations, and theme switching.


## Aurora Intelligence V11

A complete visual redesign of AI Information Hub:

- New Aurora identity with electric blue, violet, cyan, amber, and rose accents.
- New command-center home page and bento-style capability system.
- Rebuilt sidebar, account card, navigation states, headers, controls, tabs, forms, tables, alerts, and responsive behavior.
- Full dark/light palette support and RTL/LTR support.
- Mobile sidebar fully collapses without leaving reserved space.
- Existing features, Google sign-in, Supabase, news analysis, exports, people, entities, comparisons, account, and settings are preserved.
- No real secrets are included.


## V11.1 Startup Fix

- Fixed the missing `get_entity_profile` service contract that prevented the app from starting.
- Added an import-contract regression test for every page entry point.
- Verified all internal imports, Python syntax, and the complete test suite.


## V11.3 Strict Summary Fix
- فرض 5 إلى 8 أسطر مستقلة في ملخص الخبر.
- فرض 3 إلى 6 نقاط رئيسية.
- رفض استجابة النموذج إذا لم تحقق الحد الأدنى وإعادة المحاولة.
- تحسين استخراج نص المقال وحل روابط Google News الوسيطة.
- عرض كل سطر داخل صف مستقل وترقيمه بصريًا.
- الحفاظ على الصدق عند نقص المصدر بإظهار حدود البيانات بدل اختلاق معلومات.
