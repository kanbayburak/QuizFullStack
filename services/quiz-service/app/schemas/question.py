from pydantic import BaseModel, Field, computed_field, field_validator


class QuestionBase(BaseModel):
    text: str = Field(min_length=1)
    option_a: str = Field(min_length=1, max_length=500)
    option_b: str = Field(min_length=1, max_length=500)
    option_c: str = Field(min_length=1, max_length=500)
    option_d: str = Field(min_length=1, max_length=500)
    correct_index: int = Field(ge=0, le=3)


class QuestionCreate(QuestionBase):
    category_id: int


class QuestionUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    option_a: str | None = Field(default=None, min_length=1, max_length=500)
    option_b: str | None = Field(default=None, min_length=1, max_length=500)
    option_c: str | None = Field(default=None, min_length=1, max_length=500)
    option_d: str | None = Field(default=None, min_length=1, max_length=500)
    correct_index: int | None = Field(default=None, ge=0, le=3)
    category_id: int | None = None

    @field_validator("option_a", "option_b", "option_c", "option_d", mode="before")
    @classmethod
    def strip_strings(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip() if isinstance(v, str) else v


class QuestionRead(QuestionBase):
    id: int
    category_id: int
    owner_id: int | None = None

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def is_system(self) -> bool:
        return self.owner_id is None
