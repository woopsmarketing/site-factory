# v0.1 - 파이프라인 실행 뼈대 추가 (2026-01-16)
# 기능: Mock 기반으로 어댑터 적용과 리포트 생성 (예: run_pipeline(..., use_mock=True))

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .contracts import validate_adapter, validate_site_spec
from .patcher import apply_patches_to_elementor
from .utils.error_utils import FriendlyError
from .utils.io_utils import ensure_directory, read_json_file, write_json_file
from .utils.time_utils import get_iso_timestamp


@dataclass(frozen=True)
class PipelineDependencies:
    """테스트를 위한 의존성 묶음. 예: PipelineDependencies(read_json=mock_read_json, ...)"""

    read_json: Callable[[Path], Dict[str, Any]]
    write_json: Callable[[Path, Dict[str, Any]], None]
    ensure_dir: Callable[[Path], Path]
    now_iso: Callable[[], str]


def default_dependencies() -> PipelineDependencies:
    """기본 의존성 세트를 반환한다. 예: deps = default_dependencies()"""

    return PipelineDependencies(
        read_json=read_json_file,
        write_json=write_json_file,
        ensure_dir=ensure_directory,
        now_iso=get_iso_timestamp,
    )


def run_pipeline(
    *,
    config_path: Path,
    site_spec_path: Optional[Path],
    adapter_path: Optional[Path],
    elementor_path: Optional[Path],
    output_dir: Path,
    use_mock: bool,
    logger,
    dependencies: Optional[PipelineDependencies] = None,
) -> Dict[str, Any]:
    """파이프라인 실행. 예: run_pipeline(..., use_mock=True)"""

    deps = dependencies or default_dependencies()

    config = _load_config(config_path=config_path, deps=deps)

    if use_mock:
        site_spec_path = Path("data/mock/site_spec.sample.json")
        adapter_path = Path("data/mock/template_adapter.sample.json")
        elementor_path = Path("data/mock/elementor.sample.json")

    if not site_spec_path or not adapter_path or not elementor_path:
        raise FriendlyError(
            user_message="site_spec, adapter, elementor 경로가 필요합니다. --use-mock 또는 경로를 지정해주세요."
        )

    site_spec = deps.read_json(site_spec_path)
    adapter = deps.read_json(adapter_path)
    elementor_data = deps.read_json(elementor_path)

    validate_site_spec(site_spec)
    validate_adapter(adapter)

    logger.info("어댑터 패치를 적용합니다.")
    patched_elementor, patch_results = apply_patches_to_elementor(
        elementor_data=elementor_data,
        adapter=adapter,
        site_spec=site_spec,
        strict_path=True,
    )

    output_root = deps.ensure_dir(output_dir)
    patched_path = output_root / "patched_elementor.json"
    results_path = output_root / "patch_results.json"
    report_path = output_root / "run_report.json"

    deps.write_json(patched_path, patched_elementor)
    deps.write_json(results_path, {"results": patch_results})

    run_report = _build_run_report(
        config=config,
        site_spec_path=site_spec_path,
        adapter_path=adapter_path,
        elementor_path=elementor_path,
        output_dir=output_root,
        patch_results=patch_results,
        deps=deps,
    )
    deps.write_json(report_path, run_report)

    logger.info("파이프라인이 완료되었습니다.")
    return run_report


def _load_config(config_path: Path, deps: PipelineDependencies) -> Dict[str, Any]:
    """설정 파일을 로드한다. 예: _load_config(Path("config.sample.json"), deps)"""

    try:
        return deps.read_json(config_path)
    except FriendlyError:
        # 그대로 상위로 전달한다.
        raise
    except Exception as error:
        # 예상치 못한 에러를 FriendlyError로 변환한다.
        raise FriendlyError(
            user_message=f"설정 파일을 읽을 수 없습니다: {config_path}",
            detail=str(error),
        ) from error


def _build_run_report(
    *,
    config: Dict[str, Any],
    site_spec_path: Path,
    adapter_path: Path,
    elementor_path: Path,
    output_dir: Path,
    patch_results: list,
    deps: PipelineDependencies,
) -> Dict[str, Any]:
    """실행 리포트를 생성한다. 예: report = _build_run_report(...)"""

    return {
        "status": "completed",
        "timestamp": deps.now_iso(),
        "config": {
            "project": config.get("project", {}),
            "paths": config.get("paths", {}),
        },
        "inputs": {
            "site_spec_path": str(site_spec_path),
            "adapter_path": str(adapter_path),
            "elementor_path": str(elementor_path),
        },
        "outputs": {
            "output_dir": str(output_dir),
            "patched_elementor": str(output_dir / "patched_elementor.json"),
            "patch_results": str(output_dir / "patch_results.json"),
        },
        "summary": {
            "total_patches": len(patch_results),
            "applied": sum(1 for result in patch_results if result.get("status") == "applied"),
            "skipped": sum(1 for result in patch_results if result.get("status") == "skipped"),
            "errors": sum(1 for result in patch_results if result.get("status") == "error"),
            "deleted": sum(1 for result in patch_results if result.get("status") == "deleted"),
        },
    }
