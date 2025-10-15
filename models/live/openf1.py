"""Pydantic models for OpenF1 API responses."""

from pydantic import BaseModel, Field
from typing import Optional


class TeamRadioMessage(BaseModel):
    """Team radio message data."""
    date: str = Field(..., description="Timestamp of radio message")
    driver_number: int = Field(..., description="Driver number (1-99)")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")
    recording_url: Optional[str] = Field(None, description="URL to audio recording")


class TeamRadioResponse(BaseModel):
    """Response for team radio messages."""
    session_name: Optional[str] = Field(None, description="Session name")
    year: Optional[int] = Field(None, description="Year")
    country: Optional[str] = Field(None, description="Country name")
    messages: list[TeamRadioMessage] = Field(..., description="List of radio messages")
    total_messages: int = Field(..., description="Total number of messages")


class PitStopData(BaseModel):
    """Pit stop data."""
    date: str = Field(..., description="Timestamp of pit stop")
    driver_number: int = Field(..., description="Driver number (1-99)")
    lap_number: int = Field(..., description="Lap number of pit stop")
    pit_duration: float = Field(..., description="Duration of pit stop in seconds")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")


class PitStopsResponse(BaseModel):
    """Response for pit stop data."""
    session_name: Optional[str] = Field(None, description="Session name")
    year: Optional[int] = Field(None, description="Year")
    country: Optional[str] = Field(None, description="Country name")
    pit_stops: list[PitStopData] = Field(..., description="List of pit stops")
    total_pit_stops: int = Field(..., description="Total number of pit stops")
    fastest_stop: Optional[float] = Field(None, description="Fastest pit stop duration")
    slowest_stop: Optional[float] = Field(None, description="Slowest pit stop duration")
    average_duration: Optional[float] = Field(None, description="Average pit stop duration")


class IntervalData(BaseModel):
    """Interval and gap data."""
    date: str = Field(..., description="Timestamp")
    driver_number: int = Field(..., description="Driver number (1-99)")
    gap_to_leader: Optional[str] = Field(None, description="Gap to race leader")
    interval: Optional[str] = Field(None, description="Interval to car ahead")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")


class IntervalsResponse(BaseModel):
    """Response for intervals data."""
    session_name: Optional[str] = Field(None, description="Session name")
    year: Optional[int] = Field(None, description="Year")
    country: Optional[str] = Field(None, description="Country name")
    intervals: list[IntervalData] = Field(..., description="List of interval data points")
    total_data_points: int = Field(..., description="Total number of data points")
