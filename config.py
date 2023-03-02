class DefaultConfig(object):
    SCHEMA = {
        "roles": [
            {
                "name": str(),
                "callTime": str(),
                "qualifiedStaff": [
                    str()
                ],
                "day": str()
            }
        ],
        "staff": [
            {
                "name": str(),
                "maxShifts": int(),
                "rolePreference": [
                    str()
                ],
                "doubles": bool(),
                "availability": {
                    "MONDAY": [
                        str()
                    ],
                    "TUESDAY": [
                        str()
                    ],
                    "WEDNESDAY": [
                        str()
                    ],
                    "THURSDAY": [
                        str()
                    ],
                    "FRIDAY": [
                        str()
                    ],
                    "SATURDAY": [
                        str()
                    ],
                    "SUNDAY": [
                        str()
                    ]
                }
            }
        ]
    }