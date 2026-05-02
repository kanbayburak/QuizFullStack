from pydantic import BaseModel, Field, computed_field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=64)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_lowercase(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "-")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_lowercase(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip().lower().replace(" ", "-")


class CategoryRead(CategoryBase):
    id: int
    owner_id: int | None = None

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def is_system(self) -> bool:
        return self.owner_id is None
