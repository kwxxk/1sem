"""python manage.py inspect / index-movies / reindex-docs / graph"""
import argparse
import json

from movielab.config import UserError, load_settings
from movielab.preparation.movies import read_movies, movie_text


def main():
    parser = argparse.ArgumentParser(description="Movie Lab 데이터 및 색인 관리")
    parser.add_argument("command", choices=["inspect", "index-movies", "reindex-docs", "graph", "fetch-pdfs",
                                            "inspect-pdfs", "index-pdfs", "evaluate", "benchmark", "export-evaluation"])
    parser.add_argument("--id", help="내보낼 비교 기록 UUID")
    parser.add_argument("--output", help="내보낼 보고서 경로")
    args = parser.parse_args()
    settings = load_settings()
    movies = read_movies(settings.movies_path)
    if args.command in {"fetch-pdfs", "inspect-pdfs"}:
        from movielab.preparation.pdf_documents import fetch_registered, pages_for_item, manifest
        if args.command == "fetch-pdfs":
            print(json.dumps(fetch_registered(settings), ensure_ascii=False))
        else:
            for identity in sorted({str(mid) for entry in manifest(settings) for mid in entry["movie_ids"]}):
                documents, warnings = pages_for_item(settings, identity)
                print(json.dumps({"movie_id": identity, "pages": len(documents), "warnings": warnings,
                                  "titles": [doc["title"] for doc in documents]}, ensure_ascii=False))
        return
    if args.command == "export-evaluation":
        from pathlib import Path
        from movielab.evaluation import load_evaluation, markdown_report
        if not args.id or not args.output:
            raise UserError("--id와 --output을 지정하세요.")
        Path(args.output).write_text(markdown_report(load_evaluation(settings, args.id)), encoding="utf-8")
        return
    if args.command == "inspect":
        print(json.dumps({"movies": len(movies), "korean": sum(m.get("original_language") == "ko" for m in movies),
                          "wiki_files": len(list(settings.wiki_bundle_path.glob('*.json')))}, ensure_ascii=False))
        print(movie_text(movies[0]))
        return
    if args.command == "graph":
        from movielab.pipeline import build_graph
        from movielab.preparation.domain import MovieDomain
        print(build_graph(None, None, settings.top_k, MovieDomain().answer_prompt()).get_graph().draw_mermaid())
        return
    from movielab.service import Service
    service = Service(settings)
    if args.command == "evaluate":
        from movielab.evaluation import run_evaluation
        print(run_evaluation(service, movies, print)["id"])
    elif args.command == "benchmark":
        from movielab.evaluation import benchmark
        print(json.dumps(benchmark(service, movies, print), ensure_ascii=False))
    elif args.command == "index-pdfs":
        from movielab.preparation.pdf_documents import index_for_item, manifest
        registered = {str(mid) for entry in manifest(settings) for mid in entry["movie_ids"]}
        for movie in movies:
            if service.domain.item_id(movie) in registered:
                print(index_for_item(settings, movie, service.store, service.domain, print))
    elif args.command == "index-movies":
        print(service.index_items(movies, print))
    elif args.command == "reindex-docs":
        by_id = {str(m["movie_id"]): m for m in movies}
        updated = 0
        for path in sorted((settings.storage_path / "collection" / "documents").glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            movie = by_id.get(str(doc["movie_id"]))
            if movie:
                updated += service.store.index_document(movie, doc)
        print({"updated_chunks": updated, "total_chunks": service.store.external.count()})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc) if isinstance(exc, UserError) else
              "실행에 실패했습니다. 설치 상태, API 권한, 모델 설정, 네트워크를 확인하세요.")
        raise SystemExit(1)
