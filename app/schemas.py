from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingCreate(BaseModel):
    """DTO для создания бронирования (id и статус задаёт сервер)."""
    building: str = Field(..., min_length=1, max_length=50,
                          description="Корпус", examples=["Главный корпус"])
    classroom_number: str = Field(..., min_length=1, max_length=20,
                                  description="Номер аудитории", examples=["А-301"])
    booked_by: str = Field(..., min_length=1, max_length=100,
                           description="ФИО того, кто бронирует",
                           examples=["Иванов Иван Иванович"])
    purpose: str = Field(..., min_length=1, max_length=200,
                         description="Цель бронирования",
                         examples=["Консультация по базам данных"])
    attendees: int = Field(..., gt=0, description="Количество участников",
                           examples=[25])
    start_time: datetime = Field(..., description="Начало брони",
                                 examples=["2026-11-10T10:00:00"])
    end_time: datetime = Field(..., description="Окончание брони",
                               examples=["2026-11-10T11:30:00"])


class BookingResponse(BookingCreate):
    """DTO ответа: поля создания + id, статус и дата создания."""
    id: int = Field(..., description="Уникальный идентификатор брони")
    status: BookingStatus = Field(..., description="Статус брони")
    created_at: datetime = Field(..., description="Дата и время создания записи")


class MessageResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
