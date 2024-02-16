from pydantic import BaseModel
from typing import List, Optional

class tqueryObject(BaseModel):
    titlePart: str

class nqueryObject(BaseModel):
    namePart: str

class gqueryObject(BaseModel):
    qgenre: str
    minrating: str = None
    yrFrom: Optional[str] = None
    yrTo: Optional[str] = None

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
    category: List[str]

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
    namePoster: Optional[str]
    birthYr: str
    deathYr: Optional[str]
    profession: Optional[List[str]]
    nameTitles: Optional[List[NameTitleObject]]