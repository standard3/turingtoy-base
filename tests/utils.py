import shutil
from decimal import (
    Decimal,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
)

import simplejson as json
from deepdiff import (
    DeepDiff,
)


def write_text(path: Path, text: str) -> None:
    """
    Write text in file with consistend encoding and newline endings.
    Ensure parent directories exist.
    """
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as io:
        io.write(text if text[-1] == "\n" else f"{text}\n")


def write_json(path: Path, obj: Any, **dumps_kwargs: Any) -> None:
    return write_text(
        path,
        to_json_str(
            obj,
            **dumps_kwargs,
        ),
    )


def to_json_str(obj: Any, **dumps_kwargs: Any) -> str:
    return json.dumps(
        obj,
        indent=2,
        **dumps_kwargs,
    )


def to_json_obj(obj: Any, **dumps_kwargs: Any) -> Any:
    return json.loads(
        to_json_str(
            obj,
            **dumps_kwargs,
        ),
        parse_float=Decimal,
    )


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_float=Decimal,
    )


def regression_test(
    data: Any,
    regression_test_ref_file: Path,
    force_regen: bool,
    **dumps_kwargs: Any,
) -> None:
    def _write() -> None:
        regression_test_ref_file.parent.mkdir(parents=True, exist_ok=True)
        write_json(
            regression_test_ref_file,
            data,
            **dumps_kwargs,
        )

    if not regression_test_ref_file.is_file() or force_regen:
        _write()
    else:
        diff = DeepDiff(
            to_json_obj(data, **dumps_kwargs),
            load_json(regression_test_ref_file),
        )
        if diff:
            shutil.copy(
                regression_test_ref_file,
                regression_test_ref_file.with_suffix(".old.json"),
            )
            # If a diff is detected write the file to enable git manual comparison
            _write()
        assert not diff
