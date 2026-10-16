"""Demo đăng ký: một sinh viên chỉ đăng ký một lần cho mỗi phiên."""
from contextlib import asynccontextmanager, closing
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StrictStr, field_validator


class DangKy(BaseModel):
    ma_sv: StrictStr = Field(min_length=1, max_length=64)
    ma_phien: StrictStr = Field(min_length=1, max_length=64)

    @field_validator('ma_sv', 'ma_phien', mode='before')
    @classmethod
    def strip_spaces(cls, value):
        return value.strip() if isinstance(value, str) else value


def create_app(database_path: Path | None = None) -> FastAPI:
    path = Path(database_path) if database_path is not None else Path(__file__).with_name('ngayhoi.db')

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute('''
                CREATE TABLE IF NOT EXISTS dang_ky (
                    ma_sv TEXT NOT NULL,
                    ma_phien TEXT NOT NULL,
                    UNIQUE (ma_sv, ma_phien)
                )
            ''')
        yield

    application = FastAPI(title='Đăng ký Ngày hội việc làm', lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:5173'],
        allow_credentials=False,
        allow_methods=['POST'],
        allow_headers=['Content-Type'],
    )

    @application.post(
        '/api/dang-ky', status_code=201,
        responses={409: {'description': 'Đã đăng ký cùng mã sinh viên và mã phiên'},
                   500: {'description': 'Lỗi cơ sở dữ liệu'}},
    )
    def register(registration: DangKy) -> dict[str, bool]:
        try:
            with closing(sqlite3.connect(path, timeout=10)) as connection, connection:
                connection.execute(
                    'INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)',
                    (registration.ma_sv, registration.ma_phien),
                )
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                raise HTTPException(status_code=409, detail='DA_DANG_KY') from error
            raise HTTPException(status_code=500, detail='LOI_CSDL') from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=500, detail='LOI_CSDL') from error
        return {'ok': True}

    return application


app = create_app()
