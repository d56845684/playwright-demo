from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class CampsiteType:
    name: str
    capacity_tents: int


@dataclass(frozen=True)
class Camp:
    camp_id: str
    name: str
    county: str
    district: str
    altitude_m: int
    tags: List[str]
    sites: List[CampsiteType]


AREAS: Dict[str, List[str]] = {
    "新竹縣": ["尖石鄉", "五峰鄉", "關西鎮"],
    "苗栗縣": ["泰安鄉", "南庄鄉"],
}

CAMPS: List[Camp] = [
    Camp(
        camp_id="C001",
        name="高台山露營區",
        county="新竹縣",
        district="尖石鄉",
        altitude_m=980,
        tags=["雲海", "夜景", "親子"],
        sites=[CampsiteType("草地營位", 2), CampsiteType("雨棚營位", 2), CampsiteType("小木屋", 1)],
    ),
    Camp(
        camp_id="C002",
        name="雲嶺秘境露營區",
        county="新竹縣",
        district="五峰鄉",
        altitude_m=1200,
        tags=["高海拔", "雲海", "觀星"],
        sites=[CampsiteType("碎石營位", 2), CampsiteType("棧板營位", 2)],
    ),
    Camp(
        camp_id="C003",
        name="松林露營區",
        county="苗栗縣",
        district="泰安鄉",
        altitude_m=850,
        tags=["溫泉", "森林"],
        sites=[CampsiteType("草地營位", 2), CampsiteType("雨棚營位", 2)],
    ),
]