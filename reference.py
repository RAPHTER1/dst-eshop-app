#!/usr/bin/env python3
import argparse, os, subprocess, sys, re

def run(args):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return p.stdout

def list_refs(proj_abs):
    out = run(["dotnet", "list", proj_abs, "reference"])
    refs = []
    for line in out.splitlines():
        m = re.search(r'([^\s]+\.csproj)\s*$', line.strip())
        if m:
            # normalise les chemins Windows en POSIX
            refs.append(m.group(1).replace("\\", "/"))
    return refs

def crawl(root, proj_abs, seen):
    proj_abs = os.path.abspath(proj_abs)
    if proj_abs in seen:
        return
    seen.add(proj_abs)
    base = os.path.dirname(proj_abs)
    for relref in list_refs(proj_abs):
        # join + normpath pour résoudre ../
        child = os.path.normpath(os.path.join(base, relref))
        crawl(root, child, seen)

def relpath(root, p):
    return os.path.relpath(os.path.abspath(p), root)

def find_linked_dirs(csproj_abs):
    try:
        txt = open(csproj_abs, encoding="utf-8", errors="ignore").read()
    except Exception:
        return set()
    dirs = set()
    for m in re.finditer(r'Include="(\.\.[^"]+)"', txt):
        path = m.group(1).replace("\\", "/")
        full = os.path.normpath(os.path.join(os.path.dirname(csproj_abs), path))
        if os.path.isfile(full):
            full = os.path.dirname(full)
        dirs.add(full)
    return dirs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", help="ex: src/Basket.API/Basket.API.csproj")
    args = ap.parse_args()

    root = os.getcwd()
    proj_abs = os.path.abspath(args.project)

    seen = set()
    crawl(root, proj_abs, seen)

    linked = set()
    for p in list(seen):
        linked |= find_linked_dirs(p)

    globals_files = ["nuget.config","Directory.Packages.props","Directory.Build.props","Directory.Build.targets","global.json"]
    globals_existing = [g for g in globals_files if os.path.exists(os.path.join(root, g))]

    all_rel = sorted(relpath(root, p) for p in seen)

    print("### ALL .csproj (directs + transitifs)")
    for p in all_rel: print(p)

    print("\n### COPY-CSProj (bloc RESTORE)")
    for p in all_rel:
        d = os.path.dirname(p)
        dest = d[4:] if d.startswith("src/") else d
        if dest and not dest.endswith("/"): dest += "/"
        print(f"COPY {p} {dest}")

    print("\n### COPY-Code (bloc PUBLISH)")
    code_dirs = sorted(set(os.path.dirname(p) for p in all_rel))
    for d in code_dirs:
        if d.startswith("src/"):
            print(f"COPY {d}/ {d[4:]}/")
    for d in sorted(linked):
        r = relpath(root, d)
        if r.startswith("src/"):
            print(f"COPY {r}/ {r[4:]}/")

    print("\n### Globals à copier avant RESTORE (si présents)")
    for g in globals_existing:
        print(f"COPY {g} ./")

if __name__ == "__main__":
    sys.exit(main())
