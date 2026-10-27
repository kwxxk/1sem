from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchOptions(StrictModel):
    search_method: Literal["similarity", "mmr"] = "similarity"
    top_k: int = Field(default=6, ge=2, le=20)
    chunk_size: int = Field(default=1000, ge=100, le=8000)
    chunk_overlap: int = Field(default=200, ge=0, le=7999)

    @model_validator(mode="after")
    def check_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        return self


class OptionsRequest(StrictModel):
    options: SearchOptions | None = None


class QuestionRequest(OptionsRequest):
    movie_id: str = Field(min_length=1, max_length=32, pattern=r"^[0-9]+$")
    message: str = Field(default="", max_length=3000)
    mode: Literal["question", "guide"] = "question"


class ExploreRequest(OptionsRequest):
    query: str = Field(min_length=1, max_length=1000)


class ReviewRequest(StrictModel):
    case_id: str = Field(min_length=1, max_length=80)
    without_accuracy: Literal["적절", "부적절", "판단보류"]
    with_accuracy: Literal["적절", "부적절", "판단보류"]
    without_unknown_handling: Literal["적절", "부적절", "판단보류"]
    with_unknown_handling: Literal["적절", "부적절", "판단보류"]
    notes: str = Field(min_length=1, max_length=2000)
