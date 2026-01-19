# v0.2 - 스캐너 명령 추가 (2026-01-19)
# 기능: 파이프라인/스캐너 실행을 위한 CLI 제공 (예: python -m site_factory.cli scan --input ...)

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .pipeline import default_dependencies, run_pipeline
from .scanner import scan_elementor_json
from .utils.error_utils import FriendlyError, build_user_friendly_message
from .utils.log_utils import create_logger


def build_parser() -> argparse.ArgumentParser:
    """CLI 파서를 만든다. 예: parser = build_parser()"""

    parser = argparse.ArgumentParser(
        description="WordPress Site Factory 파이프라인 실행 CLI",
    )

    parser.add_argument(
        "command",
        choices=["run", "scan"],
        help="실행할 명령",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="설정 파일 경로 (json)",
    )
    parser.add_argument(
        "--site-spec",
        default=None,
        help="site_spec.json 경로",
    )
    parser.add_argument(
        "--adapter",
        default=None,
        help="template_adapter.json 경로",
    )
    parser.add_argument(
        "--elementor",
        default=None,
        help="Elementor JSON 경로",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="결과 저장 디렉터리",
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="Mock 데이터로 실행",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="로그 레벨 (DEBUG/INFO/WARNING/ERROR)",
    )

    parser.add_argument(
        "--input",
        default=None,
        help="Elementor JSON 입력 파일 경로 (scan 명령용)",
    )
    parser.add_argument(
        "--page-slug",
        default="home",
        help="페이지 슬러그 (scan 명령용)",
    )
    parser.add_argument(
        "--template-id",
        default="unknown",
        help="템플릿 ID (scan 명령용)",
    )
    parser.add_argument(
        "--max-candidates",
        default=300,
        type=int,
        help="추출 후보 최대 개수 (scan 명령용)",
    )
    parser.add_argument(
        "--max-depth",
        default=12,
        type=int,
        help="Elementor 트리 최대 탐색 깊이 (scan 명령용)",
    )

    return parser


def run_command(args: argparse.Namespace) -> Dict[str, Any]:
    """명령을 실행한다. 예: run_command(args)"""

    logger = create_logger("site_factory", level_text=args.log_level)
    deps = default_dependencies()

    if args.command == "run":
        return run_pipeline(
            config_path=Path(args.config),
            site_spec_path=Path(args.site_spec) if args.site_spec else None,
            adapter_path=Path(args.adapter) if args.adapter else None,
            elementor_path=Path(args.elementor) if args.elementor else None,
            output_dir=Path(args.output_dir),
            use_mock=args.use_mock,
            logger=logger,
            dependencies=deps,
        )

    if args.command == "scan":
        if not args.input:
            raise FriendlyError(user_message="scan 명령에는 --input이 필요합니다.")
        return scan_elementor_json(
            input_path=Path(args.input),
            output_dir=Path(args.output_dir),
            page_slug=args.page_slug,
            template_id=args.template_id,
            max_candidates=args.max_candidates,
            max_depth=args.max_depth,
        )

    raise FriendlyError(user_message="지원하지 않는 명령입니다.")


def main() -> int:
    """CLI 엔트리 포인트. 예: sys.exit(main())"""

    parser = build_parser()
    args = parser.parse_args()

    try:
        result = run_command(args)
        # 결과 요약을 콘솔에 표시한다.
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except FriendlyError as error:
        print(f"[오류] {error.user_message}", file=sys.stderr)
        if error.detail:
            print(f"[상세] {error.detail}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"[오류] {build_user_friendly_message(error)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
