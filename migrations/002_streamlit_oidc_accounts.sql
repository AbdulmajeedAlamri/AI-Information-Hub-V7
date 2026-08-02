-- شغّل هذا الملف مرة واحدة في Supabase SQL Editor بعد الجداول الأساسية.

create unique index if not exists profiles_email_unique
on public.profiles (lower(email))
where email is not null and email <> '';

create index if not exists favorites_user_item_idx
on public.favorites(user_id, item_type, item_key);

create index if not exists search_history_user_type_idx
on public.search_history(user_id, search_type, created_at desc);

-- لا تغيّر سياسات RLS الحالية. التطبيق يستخدم Secret key على الخادم فقط،
-- ويطبق عزل المستخدمين في كل استعلام بواسطة user_id.
