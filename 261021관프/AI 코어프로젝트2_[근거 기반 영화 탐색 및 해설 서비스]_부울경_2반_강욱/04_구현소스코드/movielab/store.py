import hashlib
import json
import threading

from .config import UserError
from .retrieval import mmr_indices

_STORE_LOCK = threading.RLock()


class Store:
    def __init__(self, settings, embeddings, domain):
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        self.settings = settings
        self.embeddings = embeddings
        self.domain = domain
        self.lock = _STORE_LOCK
        self.client = chromadb.PersistentClient(
            path=str(settings.storage_path / "chroma"),
            settings=ChromaSettings(anonymized_telemetry=False))
        # 모델 변경 시 다른 벡터 공간을 같은 컬렉션에서 검색하지 않는다.
        identity = hashlib.sha256((settings.embedding_model + settings.base_url).encode()).hexdigest()[:12]
        self.meta = self.client.get_or_create_collection(
            f"{domain.metadata_collection}_{identity}", metadata={"hnsw:space": "cosine"}, embedding_function=None)
        self.external = self.client.get_or_create_collection(
            f"{domain.external_collection}_{identity}", metadata={"hnsw:space": "cosine"}, embedding_function=None)

    def _upsert(self, collection, records):
        size = self.settings.embedding_batch_size
        for offset in range(0, len(records), size):
            batch = records[offset:offset + size]
            vectors = self.embeddings.embed_documents([r["text"] for r in batch])
            collection.upsert(ids=[r["id"] for r in batch],
                              documents=[r["text"] for r in batch],
                              metadatas=[r["metadata"] for r in batch], embeddings=vectors)

    def index_items(self, items, progress=lambda message: None):
        with self.lock:
            existing = self.meta.get(include=["metadatas"])
            hashes = {key: metadata.get("content_hash") for key, metadata
                      in zip(existing["ids"], existing["metadatas"])}
            pending = []
            for item in items:
                record = self.domain.item_record(item)
                digest = hashlib.sha256(record["text"].encode()).hexdigest()
                if hashes.get(record["id"]) != digest:
                    record["metadata"]["content_hash"] = digest
                    pending.append(record)
            for start in range(0, len(pending), self.settings.embedding_batch_size):
                self._upsert(self.meta, pending[start:start + self.settings.embedding_batch_size])
                progress(f"항목 색인 {min(start + self.settings.embedding_batch_size, len(pending))}/{len(pending)}")
            obsolete = set(existing["ids"]) - {self.domain.item_id(item) for item in items}
            if obsolete:
                self.meta.delete(ids=list(obsolete))
            return {"loaded": len(items), "indexed": self.meta.count(), "updated": len(pending)}

    def document_signature(self, document):
        value = [document["text"], document["title"], document["url"],
                 self.settings.chunk_size, self.settings.chunk_overlap]
        return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode()).hexdigest()

    def document_current(self, item_id, document):
        rows = self.external.get(where={"$and": [{self.domain.item_id_field: str(item_id)},
                                     {self.domain.document_id_field: str(document[self.domain.document_id_field])}]},
                             include=["metadatas"])
        expected = self.document_signature(document)
        return bool(rows["ids"]) and all(m.get("index_signature") == expected for m in rows["metadatas"])

    def index_document(self, item, document):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        with self.lock:
            if self.document_current(self.domain.item_id(item), document):
                return 0
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.settings.chunk_size, chunk_overlap=self.settings.chunk_overlap)
            chunks = splitter.split_text(document["text"])
            if not chunks:
                raise UserError("선별한 문서의 본문이 비어 있습니다. 다른 문서 모드를 사용하세요.")
            mid, pid = self.domain.item_id(item), str(document[self.domain.document_id_field])
            where = {"$and": [{self.domain.item_id_field: mid}, {self.domain.document_id_field: pid}]}
            previous = self.external.get(where=where, include=[])["ids"]
            records = [{"id": f"{mid}:{pid}:{i}", "text": text, "metadata": {
                **self.domain.document_metadata(item, document), "chunk_index": i,
                "index_signature": self.document_signature(document)}} for i, text in enumerate(chunks)]
            self._upsert(self.external, records)
            stale = set(previous) - {r["id"] for r in records}
            if stale:
                self.external.delete(ids=list(stale))
            return len(records)

    @staticmethod
    def rows(result, query=False):
        if query:
            result = {k: v[0] for k, v in result.items() if k in {"ids", "documents", "metadatas"}}
        return [{"id": key, "text": text, **metadata} for key, text, metadata in
                zip(result["ids"], result["documents"], result["metadatas"])]

    def retrieve(self, item_id, question, top_k, method=None):
        method = method or self.settings.search_method
        if method not in {"similarity", "mmr"}:
            raise UserError("지원하지 않는 검색 방식입니다.")
        meta = self.meta.get(ids=[str(item_id)], include=["documents", "metadatas"])
        sources = self.rows(meta)
        if not sources:
            raise UserError("선택한 항목의 색인이 없습니다. 메타데이터 색인을 먼저 실행하세요.")
        where = {self.domain.item_id_field: str(item_id)}
        inventory = self.external.get(where=where, include=["metadatas"])
        available = len(inventory["ids"])
        if available:
            query = self.embeddings.embed_query(question)
            # 서로 다른 언어/유형의 문서가 한 유형의 긴 문서에 밀리지 않도록
            # 유형별 의미 검색 후보를 모은다. 항목 필터는 모든 검색에 유지한다.
            kinds = {m.get("source_kind") for m in inventory["metadatas"]}
            pools = []
            for kind in sorted(kinds, key=lambda value: value or ""):
                count = sum(m.get("source_kind") == kind for m in inventory["metadatas"])
                scoped = ({"$and": [where, {"source_kind": kind}]} if kind else where)
                result = self.external.query(query_embeddings=[query],
                    n_results=min(max(top_k - 1, self.settings.mmr_fetch_k), count), where=scoped,
                    include=["documents", "metadatas", "embeddings", "distances"])
                pools.extend(zip(self.rows(result, query=True), result["embeddings"][0], result["distances"][0]))
            pools.sort(key=lambda row: row[2])
            candidates = [row[0] for row in pools]
            vectors = [row[1] for row in pools]
            unique, unique_vectors, seen = [], [], set()
            for candidate, vector in zip(candidates, vectors):
                digest = hashlib.sha256(candidate["text"].encode()).hexdigest()
                if digest not in seen:
                    seen.add(digest)
                    unique.append(candidate)
                    unique_vectors.append(list(vector))
            indices = (mmr_indices(query, unique_vectors, top_k-1, self.settings.mmr_lambda)
                       if method == "mmr" else list(range(min(top_k-1, len(unique)))))
            # 근거 슬롯이 충분하면 각 유형의 최상위 후보를 최소 한 개 보존한다.
            # 질문의 사실을 확정하는 단계는 생성 노드가 원문을 대조해 수행한다.
            represented = {unique[i].get("source_kind") for i in indices}
            for kind in sorted(kinds - represented, key=lambda value: value or ""):
                best = next((i for i, row in enumerate(unique) if row.get("source_kind") == kind), None)
                if best is None:
                    continue
                replace_at = next((j for j in range(len(indices)-1, -1, -1)
                    if sum(unique[i].get("source_kind") == unique[indices[j]].get("source_kind")
                           for i in indices) > 1), None)
                if replace_at is not None:
                    indices[replace_at] = best
            sources.extend(unique[i] for i in indices)
        seen_ids, seen_text, unique = set(), set(), []
        for source in sources:
            digest = hashlib.sha256(source["text"].encode()).hexdigest()
            if source["id"] not in seen_ids and digest not in seen_text:
                seen_ids.add(source["id"])
                seen_text.add(digest)
                unique.append(source)
        return unique[:top_k]

    def explore_candidates(self, query, allowed_ids, limit):
        if not allowed_ids:
            return []
        result = self.meta.query(query_embeddings=[self.embeddings.embed_query(query)],
                                 where={self.domain.item_id_field: {"$in": allowed_ids}},
                                 n_results=min(limit, len(allowed_ids)),
                                 include=["documents", "metadatas"])
        return self.rows(result, query=True)
