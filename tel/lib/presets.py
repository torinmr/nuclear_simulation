from lib.enums import TELKind

tel_kinds_continental_us = {TELKind.DF_31A, TELKind.DF_31AG}
tel_kinds_alaska_hawaii = tel_kinds_continental_us | {TELKind.DF_31}
tel_kinds_guam = tel_kinds_alaska_hawaii | {TELKind.DF_26}
tel_kinds_us_allies = tel_kinds_guam | {TELKind.DF_21AE}
