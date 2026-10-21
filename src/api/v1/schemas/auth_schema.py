from pydantic import BaseModel,Field, field_validator


class RegisterRequest(BaseModel):
    email: str
    password: str= Field(min_length=8)

    @field_validator("password")
    def check_password_strenght(cls,value):
        if not any(c.isupper()for c in value):
            raise ValueError("The password must contain at least one uppercase letter")
        return value
