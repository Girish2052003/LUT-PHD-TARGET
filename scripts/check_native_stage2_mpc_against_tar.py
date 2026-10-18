#!/usr/bin/env python3
"""Independent TAR-to-raw-MPC content comparison for all 626 stage-2 candidates.

This auditor neither executes original/generated code nor trusts the runtime
harness's assertion that it injected a particular original candidate. It
reopens the SHA256-pinned author archive and literally finds the author's
original saved candidate string in each compiled source input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import zipfile

ARCHIVE_SHA256 = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
EXPECTED_COUNTS = {
    "array_test":43,"loop_test":97,"branch_test":34,"math_test":38,
    "numpy_operation_test":32,"numpy_ufunc_test":34,"syntax_test":35,
}
PREFIX = "SPDZCoder/"
MAX_SOURCE = 12_000_000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_tar(tar, relative):
    item = tar.getmember(PREFIX + relative)
    if not item.isfile() or item.size > MAX_SOURCE:
        raise ValueError("Original candidate or template not bounded/regular: " + relative)
    data = tar.extractfile(item).read(MAX_SOURCE+1)
    if len(data) != item.size:
        raise ValueError("Truncated author source: " + relative)
    return data


def audit(tar_path, zip_paths):
    if len(zip_paths) != 7:
        raise ValueError("Exactly seven original native category archives required")
    tar_path = Path(tar_path)
    if sha(tar_path.read_bytes()) != ARCHIVE_SHA256:
        raise ValueError("Official authors' source archive is not authentic")
    checked, categories, archive_files = 0, {}, {}
    with tarfile.open(tar_path,"r:*") as tar:
        if sha(read_tar(tar,"evaluation/evaluate_experimental-mp.py")) != "7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2":
            raise ValueError("Original native evaluator not pinned")
        for path in zip_paths:
            with zipfile.ZipFile(path) as z:
                if z.testzip() is not None:
                    raise ValueError("Original native ZIP CRC mismatch")
                names = {name.split("/",1)[0] for name in z.namelist()}
                if len(names) != 1:
                    raise ValueError("Malformed native category artifact")
                category = next(iter(names))
                if category not in EXPECTED_COUNTS or category in categories:
                    raise ValueError("Unknown or duplicate native category")
                stage_path = f"data/stage_2_SPDZ_output/experiment-1-{category}.jsonl"
                raw = read_tar(tar,stage_path)
                source_rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
                if len(source_rows) != EXPECTED_COUNTS[category]:
                    raise ValueError("Authentic original category/source count differs")
                ledger = json.loads(z.read(category+"/stage2_identity.json"))
                by_task={row["task_id"]:row for row in ledger["task_records"]}
                if (len(by_task)!=313 or ledger["categories"][category]["candidate_source_sha256"]!=sha(raw)):
                    raise ValueError("Original stage2 source file or ledger pin differs")
                rows=[json.loads(line) for line in z.read(category+"/outcomes.jsonl").splitlines() if line.strip()]
                if len(rows)!=2*EXPECTED_COUNTS[category]:
                    raise ValueError("Original native outcome count differs")
                seen=set()
                for r in rows:
                    task,c=r["task_id"],r["candidate_id"]
                    if (task,c) in seen or type(c) is not int or c not in (0,1):
                        raise ValueError("Duplicate or foreign original native candidate")
                    seen.add((task,c))
                    ref=by_task.get(task)
                    if ref is None or ref["category"]!=category or r["stage"]!="stage2":
                        raise ValueError("Unrecognized stage2 source task")
                    pos=ref["position_in_split"]
                    if type(pos) is not int or pos<0 or pos>=len(source_rows) or source_rows[pos]["test_name"]!=task.split("/",1)[1]:
                        raise ValueError("Author candidate identity/order changed")
                    code=source_rows[pos][f"response_{c}"]
                    if not isinstance(code,str) or sha(code.encode())!=r["source_sha256"]:
                        raise ValueError("Original author source candidate text differs")
                    template=f"data/input_data/{category}/{task.split('/',1)[1]}.mpc"
                    if sha(read_tar(tar,template))!=r["template_sha256"]:
                        raise ValueError("Original native test template differs")
                    for i,attempt in enumerate(r["attempts"]):
                        mpc=z.read(category+"/"+r["log_path"]+f"/attempt-{i}.mpc")
                        if sha(mpc)!=attempt["combined_source_sha256"]:
                            raise ValueError("Raw executed MPC input source hash differs")
                        if code and code.encode("utf-8") not in mpc:
                            raise ValueError("Exact author stage2 candidate text absent from compiled MPC program")
                    if not code and r["attempts"]:
                        raise ValueError("Empty candidate was compiled as a nonempty original program")
                    checked+=1
                categories[category]={"tasks":len(source_rows),"candidates":len(rows),
                                      "authentic_stage2_file_sha256":sha(raw),
                                      "source_texts_found_in_mpc":sum(bool(source_rows[by_task[r["task_id"]]["position_in_split"]][f"response_{r['candidate_id']}"]) for r in rows)}
        if set(categories)!=set(EXPECTED_COUNTS) or checked!=626:
            raise ValueError("All seven authentic categories/626 candidate strings are required")
    return {"scope":"Independent author-Zenodo-TAR to original native source input bytes",
            "source_archive_sha256":ARCHIVE_SHA256,"verified_candidate_count":checked,
            "categories":categories,"models_called":0,
            "source_strings_reconstructed":0,
            "limitations":"Exact text inclusion and source identity, not proof of native functional correctness, privacy, or fresh LLM generation."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-tar",type=Path,required=True)
    parser.add_argument("category_zips",type=Path,nargs=7)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    record=audit(args.author_tar,args.category_zips)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record,indent=2))


if __name__=="__main__":
    main()
