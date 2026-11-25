# PROJECT_MAP

Dosya yolları hazır. Senin işin iki sütunu doldurmak:
- **Ne yapıyor:** dosyayı oku, kapat, kendi cümlenle yaz (tek cümle yeter).
- **Açıklayabilir miyim:** 30 saniyede açıklayabiliyorsan `evet`, değilse `hayır`. Hayır yazmak sorun değil, "hayır"lar haftanın çalışma listesi.

## Harita

| Bileşen | Dosya yolu | Ne yapıyor | Açıklayabilir miyim |
|---|---|---|---|
| FastAPI giriş noktası | `src/api/app.py` | | |
| Router: auth | `src/api/v1/routes/auth.py` | | |
| Router: task | `src/api/v1/routes/task.py` | | |
| Schema: auth | `src/api/v1/schemas/auth_schema.py` | | |
| Schema: task | `src/api/v1/schemas/task_schema.py` | | |
| Use case: task oluştur | `src/application/use_cases/create_task.py` | | |
| Use case: task iptal | `src/application/use_cases/cancel_task.py` | | |
| Use case: task durumu | `src/application/use_cases/get_task_status.py` | | |
| Use case: task listele | `src/application/use_cases/list_tasks.py` | | |
| Repository arayüzü | `src/application/interfaces/task_repository.py` | | |
| Domain entity: Task | `src/domain/entities/task.py` | | |
| Domain entity: User | `src/domain/entities/user.py` | | |
| Enum: task durumu | `src/domain/enums/task_status.py` | | |
| Domain hataları | `src/domain/exceptions/domain_exceptions.py` | | |
| Repository: task (PostgreSQL) | `src/infrastructure/repositories/pg_task_repository.py` | | |
| Repository: user (PostgreSQL) | `src/infrastructure/repositories/pg_user_repository.py` | | |
| DB modelleri | `src/infrastructure/database/models.py` | | |
| DB bağlantısı | `src/infrastructure/database/session.py` | | |
| Config | `src/core/config.py` | | |
| Güvenlik (hash, JWT) | `src/core/security.py` | | |
| Dependency'ler | `src/core/dependencies.py` | | |
| Worker | `src/worker.py` | | |
| Migration (aktif) | `migrations/` | | |
| Migration (kullanılmıyor gibi, doğrula) | `versions/` | | |
| Testler | `tests/test_tasks.py` | | |
| Docker | `Dockerfile`, `docker-compose.yml` | | |

## Bugün bulduklarım (28 Eylül)

1. Docker Desktop kapalıyken `docker compose` hata veriyor. Önce Docker Desktop'ı aç.
2. Dört servis (api, db, redis, worker) ayakta.
3. Testler: 3 geçti, 1 kaldı. `test_create_task` 401 alıyor, çünkü test auth eklenmeden önce yazılmış (25 Haziran test, 26 Haziran auth).
4. `GET /tasks`, `GET /tasks/{id}`, `DELETE /tasks/{id}` endpoint'lerinde giriş kontrolü yok (doğrulanacak).
5. `create_task`, `current_user`'ı kullanmıyor, `user_id` istemcinin gönderdiği JSON'dan geliyor.
6. `create_task` task'ı PostgreSQL'e `PENDING` yazıyor ama Redis kuyruğuna eklemiyor, worker task'ı göremiyor.
7. Sabit şifreler ve `.env.example` boş (H2'de bakılacak).
