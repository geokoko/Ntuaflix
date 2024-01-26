from pydantic import BaseModel
from typing import List, Optional

class gqueryObject(BaseModel):
    qgenre: str
    minrating: Optional[str]
    yrFrom: Optional[str]
    yrTo: Optional[str]

class GenreTitle(BaseModel):
    genreTitle: Optional[str]

class AkaTitle(BaseModel):
    akaTitle: Optional[str]
    regionAbbrev: Optional[str]

class PrincipalsObject(BaseModel):
    nameID: str
    name: str
    category: str

class RatingObject(BaseModel):
    avRating: str
    nVotes: str

class NameTitleObject(BaseModel):
    titleID: str
    category: str

class TitleObject(BaseModel):
    titleID: str
    type: str
    originalTitle: str
    titlePoster: Optional[str]
    startYear: str
    endYear: Optional[str] = None
    genres: List[GenreTitle]
    titleAkas: List[AkaTitle]
    principals: List[PrincipalsObject]
    rating: RatingObject

class NameObject(BaseModel):
    nameID: str
    name: str
    namePoster: str
    birthYr: str
    deathYr: str
    profession: str
    nameTitles: List[NameTitleObject]