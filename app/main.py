from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, FastAPI, HTTPException, status

from app.schemas import (BookingCreate, BookingResponse, BookingStatus,
                         ErrorResponse, MessageResponse)

app = FastAPI(
    title="Classroom Booking Service API",
    description="Микросервис бронирования аудиторного фонда университета",
    version="1.0.0",
)

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])

# Хранилище в памяти (In-Memory)
bookings_db: Dict[int, BookingResponse] = {}
_next_id = 1


def _naive(dt: datetime) -> datetime:
    """Убираем часовой пояс, чтобы времена можно было сравнивать."""
    return dt.replace(tzinfo=None)


def _has_conflict(building: str, classroom: str,
                  start: datetime, end: datetime) -> bool:
    """Есть ли активная бронь этой аудитории, пересекающаяся по времени."""
    for b in bookings_db.values():
        if b.status == BookingStatus.CANCELLED:
            continue
        if b.building != building or b.classroom_number != classroom:
            continue
        if start < b.end_time and b.start_time < end:
            return True
    return False


@router.get(
    "/",
    response_model=List[BookingResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список бронирований",
)
def get_bookings():
    return list(bookings_db.values())


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить бронирование по id",
    responses={404: {"model": ErrorResponse,
                     "description": "Бронирование не найдено"}},
)
def get_booking(booking_id: int):
    booking = bookings_db.get(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бронирование",
    responses={400: {"model": ErrorResponse,
                     "description": "Некорректное время или аудитория уже занята"}},
)
def create_booking(data: BookingCreate):
    global _next_id

    start = _naive(data.start_time)
    end = _naive(data.end_time)

    if end <= start:
        raise HTTPException(
            status_code=400,
            detail="end_time must be later than start_time")

    if _has_conflict(data.building, data.classroom_number, start, end):
        raise HTTPException(
            status_code=400,
            detail="Classroom is already booked for this time")

    payload = data.model_dump()
    payload["start_time"] = start
    payload["end_time"] = end

    booking = BookingResponse(
        id=_next_id,
        status=BookingStatus.CONFIRMED,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        **payload,
    )
    bookings_db[_next_id] = booking
    _next_id += 1
    return booking


@router.delete(
    "/{booking_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить бронирование",
    responses={404: {"model": ErrorResponse,
                     "description": "Бронирование не найдено"}},
)
def delete_booking(booking_id: int):
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    del bookings_db[booking_id]
    return MessageResponse(detail="Booking deleted")


app.include_router(router)
