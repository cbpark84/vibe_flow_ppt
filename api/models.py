from typing import Literal, Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="PPT 주제")
    style: Literal["modern", "academic", "creative", "minimal", "corporate"] = "modern"
    color: str = Field("auto", description="auto / HEX (#3B82F6) / 자연어 ('파란 계열') / 이미지 경로")
    lang: Literal["ko", "en", "auto"] = "ko"
    slide_count: Optional[int] = Field(None, ge=3, le=30)
    output: list[Literal["pptx", "html"]] = Field(["pptx"], description="출력 포맷 목록")
    provider: Optional[str] = Field(None, description="LiteLLM 모델 문자열")
    additional_instructions: Optional[str] = Field(None, max_length=1000)


class FilesResponse(BaseModel):
    pptx: Optional[str] = None
    html: Optional[str] = None


class MetaResponse(BaseModel):
    slide_count: int
    provider_used: str
    generation_time_ms: int
    theme_name: Optional[str] = None


class GenerateResponse(BaseModel):
    job_id: str
    status: Literal["completed", "failed"]
    files: FilesResponse
    meta: MetaResponse


class ProviderInfo(BaseModel):
    id: str
    name: str
    available: bool
    note: Optional[str] = None


class ProvidersResponse(BaseModel):
    providers: list[ProviderInfo]


class ThemeInfo(BaseModel):
    id: str
    name: str
    colors: dict


class ThemesResponse(BaseModel):
    themes: list[ThemeInfo]


class PreviewRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    style: Literal["modern", "academic", "creative", "minimal", "corporate"] = "modern"
    color: str = "auto"
    lang: Literal["ko", "en", "auto"] = "ko"
    slide_count: Optional[int] = Field(None, ge=3, le=10)
    provider: Optional[str] = None
    additional_instructions: Optional[str] = Field(None, max_length=500)


class PreviewResponse(BaseModel):
    html: str
    slide_count: int


class HealthResponse(BaseModel):
    status: str
    version: str = "0.3.0"
    marp_worker: bool = False
