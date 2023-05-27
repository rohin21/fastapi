from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic.types import conint


class VotesBase(BaseModel):
    post_id: int
    dir: conint(le=1)
