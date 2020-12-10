from lib.enums import TELKinds

tel_kinds_continental_us = {TELKinds.DF_31A, TELKinds.DF_31AG}
tel_kinds_alaska_hawaii = tel_kinds_continental_us | {TELKinds.DF_31}
tel_kinds_guam = tel_kinds_alaska_hawaii | {TELKinds.DF_26}
tel_kinds_us_allies = tel_kinds_guam | {TELKinds.DF_21AE}
