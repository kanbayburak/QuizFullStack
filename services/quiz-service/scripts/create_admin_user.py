"""
Veritabanına doğrudan kullanıcı ekler (CLI).

Kullanım (quiz-service klasöründen):
  python scripts/create_admin_user.py kullaniciadi sifre

Normalde kullanıcılar /auth/register ile de oluşturulabilir.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.core.security import hash_password  # noqa: E402
from app.db.session import async_session_factory, init_db  # noqa: E402
from app.repositories import user_repository  # noqa: E402
from app.repositories.user_repository import create_user  # noqa: E402


async def main() -> None:
    if len(sys.argv) != 3:
        print("Kullanım: python scripts/create_admin_user.py <kullanici_adi> <sifre>")
        sys.exit(2)
    username = sys.argv[1].strip()
    password = sys.argv[2]
    if not username:
        print("Kullanıcı adı boş olamaz.")
        sys.exit(2)
    await init_db()
    async with async_session_factory() as session:
        if await user_repository.get_by_username(session, username):
            print(f"'{username}' zaten kayıtlı. Login ile giriş yapın veya başka ad seçin.")
            sys.exit(1)
        await create_user(session, username, hash_password(password), role="member")
        await session.commit()
    print(f"Tamam: '{username}' oluşturuldu. Şimdi POST /api/v1/auth/login ile giriş yapabilirsiniz.")


if __name__ == "__main__":
    asyncio.run(main())
