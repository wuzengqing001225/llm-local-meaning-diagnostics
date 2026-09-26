#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local one-click runner: uses an OpenAI-compatible API (DeepSeek / OpenAI / Moonshot / vLLM...) to run the full PDW pipeline + baseline + E_qa + scorecard.
Supports distinct models for the three roles "reader / drafter / judge" (drafting from a different model family is required by ALGORITHM §7), plus multi-reader diff (E8 / I4).

Configuration is written in JSON (see configs/local_example.json):
{
  "readers": [ {"name": "deepseek", "model": "deepseek-v4-flash", "base_url": "https://api.deepseek.com/v1", "api_key_env": "DEEPSEEK_API_KEY",
                "extra_body": {"thinking": {"type": "disabled"}}},
               {"name": "gpt", "model": "gpt-5.6-terra", "base_url": "https://api.openai.com/v1", "api_key_env": "OPENAI_API_KEY",
                "extra_body": {"reasoning_effort": "minimal"}} ],
  "drafter": {"model": "gpt-5.6-terra", "base_url": "...", "api_key_env": "OPENAI_API_KEY"},
  "judge":   {"model": "deepseek-v4-flash", "base_url": "...", "api_key_env": "DEEPSEEK_API_KEY"},
  "datasets": [ {"name": "synth", "terms": "data/synth_terms.jsonl", "corpus": "data/synth_corpus.jsonl",
                 "distractor": "data/synth_distractor_qa.jsonl", "domain": "auto", "budget": 10},
                {"name": "v1", "terms": "data/v1/v1_terms.jsonl", "corpus": "data/v1/v1_corpus.jsonl",
                 "distractor": "data/v1/v1_distractor_qa.jsonl", "domain": "auto", "budget": 12} ],
  "stages": ["weights", "downstream", "selfreport", "eqa", "scorecard", "diff"],
  "out": "runs/local"
}
Reader and drafter/judge should be from different families: e.g. when the reader is deepseek, use gpt as drafter; when the reader is gpt, use deepseek as drafter (override with "drafter_for": {"deepseek": {...}, "gpt": {...}}).
Reasoning-type models: the reader must have thinking disabled (silent misreading is defined as answering without reasoning); for DeepSeek use extra_body {"thinking": {"type": "disabled"}},
for the OpenAI family use {"reasoning_effort": "minimal"} (if the model rejects this field, simply remove it; llm.py will retry once with an enlarged budget when content is empty and reasoning fills the whole budget).

Usage:
  export DEEPSEEK_API_KEY=... OPENAI_API_KEY=...
  python3 run_local.py --config configs/local_example.json
  python3 run_local.py --config configs/local_example.json --stages weights scorecard --readers deepseek   # run only part of it
All calls are cached by content (runs/local/<reader>/cache/); reruns after interruption will resume.
"""
import argparse, json, os, subprocess, sys, shlex

HERE = os.path.dirname(os.path.abspath(__file__))


def env_for(role_cfg, prefix):
    env = {}
    if not role_cfg:
        return env
    if role_cfg.get("backend") == "mock":  # dry run: {"backend": "mock"}
        return {f"{prefix}_BACKEND": "mock", f"{prefix}_MODEL": "mock"}
    key = os.environ.get(role_cfg.get("api_key_env", ""), role_cfg.get("api_key"))
    if not key:
        sys.exit(f"[config] API key not found: set environment variable {role_cfg.get('api_key_env')}")
    env[f"{prefix}_BACKEND"] = "openai"
    env[f"{prefix}_MODEL"] = role_cfg["model"]
    env[f"{prefix}_BASE_URL"] = role_cfg["base_url"]
    env[f"{prefix}_API_KEY"] = key
    if role_cfg.get("extra_body"):
        env[f"{prefix}_EXTRA_BODY"] = json.dumps(role_cfg["extra_body"])
    return env


def sh(cmd, env, log):
    print("$", " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    with open(log, "a", encoding="utf-8") as lf:
        lf.write("$ " + " ".join(cmd) + "\n")
        r = subprocess.run(cmd, env={**os.environ, **env}, cwd=HERE, stderr=subprocess.STDOUT, stdout=lf)
    if r.returncode != 0:
        sys.exit(f"[fail] exit {r.returncode}; see {log}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--stages", nargs="*")
    ap.add_argument("--readers", nargs="*")
    ap.add_argument("--datasets", nargs="*")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    stages = a.stages or cfg.get("stages", ["weights", "downstream", "selfreport", "eqa", "scorecard", "diff"])
    readers = [r for r in cfg["readers"] if not a.readers or r["name"] in a.readers]
    datasets = [d for d in cfg["datasets"] if not a.datasets or d["name"] in a.datasets]
    out_root = os.path.join(HERE, cfg.get("out", "runs/local"))
    py = sys.executable

    for rd in readers:
        drafter = (cfg.get("drafter_for") or {}).get(rd["name"], cfg.get("drafter"))
        judge = (cfg.get("judge_for") or {}).get(rd["name"], cfg.get("judge"))
        if drafter and drafter["model"] == rd["model"]:
            print(f"[warn] Reader {rd['name']} uses the same model as the drafter ({rd['model']}), risking circularity (ALGORITHM §7)", file=sys.stderr)
        env = {**env_for(rd, "LLM"), **env_for(drafter, "DRAFT"), **env_for(judge, "JUDGE")}
        for ds in datasets:
            od = os.path.join(out_root, rd["name"], ds["name"]); os.makedirs(od, exist_ok=True)
            cache = os.path.join(out_root, rd["name"], "cache"); log = os.path.join(od, "run.log")
            W, F, D = os.path.join(od, "weights.jsonl"), os.path.join(od, "failures.jsonl"), os.path.join(od, "distractor.jsonl")
            if "weights" in stages:
                sh([py, "run_pdw.py", "--terms", ds["terms"], "--out", W, "--gloss-mode", "both", "--robust", "--self-report",
                    "--prior-mode", "ctx", "--domain", ds.get("domain", "auto"), "--cache-dir", cache], env, log)
            if "downstream" in stages:
                for task in ("mc", "definition"):
                    sh([py, "run_downstream.py", "--terms", ds["terms"], "--task", task, "--inject-from", W, "--prior-from", W,
                        "--budget", str(ds.get("budget", 10)), "--inject-template", ds.get("inject_template", "scoped"), "--out", F, "--cache-dir", cache], env, log)
                if ds.get("distractor") and os.path.exists(os.path.join(HERE, ds["distractor"])):
                    sh([py, "run_downstream.py", "--distractor", ds["distractor"], "--inject-from", W, "--budget", str(ds.get("budget", 10)), "--inject-template", ds.get("inject_template", "scoped"),
                        "--out", D, "--cache-dir", cache], env, log)
            if "selfreport" in stages:
                sh([py, "run_selfreport.py", "--terms", ds["terms"], "--corpus", ds["corpus"], "--out", os.path.join(od, "selfreport.jsonl"),
                    "--ref-out", os.path.join(od, "refs.jsonl"), "--main-only", "--cache-dir", cache], env, log)
            if "eqa" in stages:
                # v0.5: E_qa is the main estimator -- --robust produces E_qa variants for E6/E7/E6b, --placebo gives a control for terms without a prior;
                # when the dataset entry has eqa_main_only=true, only run on main terms; eqa_from_gold=true anchors question generation on gloss_gold (real corpus)
                sh([py, "run_eqa.py", "--terms", ds["terms"], "--weights", W, "--out", os.path.join(od, "eqa.jsonl"), "--n-q", "4",
                    "--robust", "--placebo"] + (["--main-only"] if ds.get("eqa_main_only") else []) + (["--from-gold"] if ds.get("eqa_from_gold") else []) + (["--q-lang", ds["q_lang"]] if ds.get("q_lang") else [])
                   + ["--cache-dir", cache], env, log)
            if "eqa_usage" in stages:
                # v0.7 E_qa v2: one question per context (question distribution = usage distribution), questions carry half -> retest.py computes E18
                sh([py, "run_eqa.py", "--terms", ds["terms"], "--weights", W, "--out", os.path.join(od, "eqa_usage.jsonl"),
                    "--from-usage", "--max-ctx", str(ds.get("max_ctx", 16)), "--placebo"] + (["--q-lang", ds["q_lang"]] if ds.get("q_lang") else []) + ["--cache-dir", cache], env, log)
                sh([py, "retest.py", "--eqa", os.path.join(od, "eqa_usage.jsonl")], env, log)
            if "scorecard" in stages:
                extra = [p for p in (os.path.join(od, "selfreport.jsonl"), os.path.join(od, "eqa.jsonl"), os.path.join(od, "emb.jsonl"))
                         if os.path.exists(p)]
                extra += [p for p in (os.path.join(od, "logprob.jsonl"),) if os.path.exists(p)]
                base = [py, "evaluate.py", "--weights", W]
                if os.path.exists(F):
                    base += ["--failures", F]
                if os.path.exists(D):
                    base += ["--distractor-failures", D]
                if ds.get("corpus"):
                    base += ["--corpus", ds["corpus"]]
                if extra:
                    base += ["--extra-scores"] + extra
                sh(base + ["--out", os.path.join(od, "scorecard.md")], env, log)                                    # cloze as main score (historically comparable)
                if os.path.exists(os.path.join(od, "eqa.jsonl")):
                    sh(base + ["--main-score", "delta_qa", "--out", os.path.join(od, "scorecard_eqa.md")], env, log)  # v0.5 main estimator E_qa
                print(f"[ok] {rd['name']}/{ds['name']} → {os.path.join(od, 'scorecard.md')}", file=sys.stderr)

    if "diff" in stages and len(readers) >= 2:
        for ds in datasets:
            files = [os.path.join(out_root, r["name"], ds["name"], "weights.jsonl") for r in readers]
            if all(os.path.exists(f) for f in files):
                sh([py, "diff_readers.py", "--weights", *files, "--names", *[r["name"] for r in readers],
                    "--out", os.path.join(out_root, f"diff_{ds['name']}.md")], {}, os.path.join(out_root, "diff.log"))

if __name__ == "__main__":
    main()