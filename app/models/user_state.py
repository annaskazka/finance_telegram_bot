from enum import Enum


class UserState(Enum):
    IDLE = "idle"
    CHOOSING_CATEGORY = "choosing_category"
    ENTERING_AMOUNT = "entering_amount"
    ENTERING_COMMENT = "entering_comment"
