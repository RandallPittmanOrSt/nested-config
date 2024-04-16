from typing import Optional, Type

import pydantic

from nested_config.expand import ispydmodel


class MyModel(pydantic.BaseModel):
    x: int


def requires_mymodel_cls(mm: Type[MyModel]):
    print(mm.x)


def might_have_mymodel_cls(mm: Optional[Type[MyModel]]):
    if ispydmodel(mm, MyModel):
        requires_mymodel_cls(mm)
