import random


PREFIXES = ["TRL-EAST-", "TRL-WEST-"]

REEFER_UNITS = [
    "Carrier X4 7500", "Carrier X4 7300", "Carrier Vector 8600",
    "Carrier Vector 8500", "Thermo King Precedent", "Thermo King C-600",
]

DRY_VAN_ATTRS = [
    "swing doors", "roll door", "e-track interior", "logistics posts",
    "air ride suspension", "liftgate 3000 lb", "load bars x6",
    "spare tire mounted", "floor rated 20k lbs",
]

FLATBED_ATTRS = [
    "tarps onboard", "coil package", "conestoga rolling tarp",
    "chains and binders onboard", "headache rack installed",
    "edge protectors onboard", "lumber tarps", "steel hauling config",
]

CHASSIS_ATTRS = [
    "twist locks OK", "sliding tandem", "DOT sticker current",
    "tires at 60%", "tires at 45%",
]

NOTES = [
    "last DOT inspection", "annual inspection", "brake job due",
    "tires replaced", "door seal replaced", "kingpin inspected",
]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer",
    "Michael", "Linda", "David", "Elizabeth", "William", "Barbara",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
]


def random_date():
    return f"2026-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"


def random_timestamp():
    return f"{random_date()} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_info():
    trailer_type = random.choice([
        "53ft dry van", "48ft flatbed", "53ft reefer", "40ft container chassis"
    ])

    if trailer_type == "53ft reefer":
        parts = [
            trailer_type,
            random.choice(REEFER_UNITS),
            f"setpoint {random.randint(25, 40)}F",
            f"fuel {random.randint(30, 95)}%",
        ]
    elif trailer_type == "48ft flatbed":
        parts = [trailer_type] + random.sample(FLATBED_ATTRS, 2)
    elif trailer_type == "40ft container chassis":
        parts = [trailer_type] + random.sample(CHASSIS_ATTRS, 2)
    else:
        parts = [trailer_type] + random.sample(DRY_VAN_ATTRS, 2)

    if random.random() < 0.5:
        parts.append(f"{random.choice(NOTES)} {random_date()}")

    return ", ".join(parts)
