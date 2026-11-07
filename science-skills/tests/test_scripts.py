"""Tests for the helper scripts. Run:  python3 -m unittest discover -s tests -v
Stdlib only. Network is never touched."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "skills")


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(S, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_tool(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def git(cwd, *a):
    r = run("git", *a, cwd=cwd)
    assert r.returncode == 0, r.stderr
    return r.stdout


class PreregTests(unittest.TestCase):
    PREREG = os.path.join(S, "preregister", "scripts", "prereg.py")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        git(self.d, "init", "-q")
        git(self.d, "config", "user.email", "t@example.com")
        git(self.d, "config", "user.name", "t")
        os.makedirs(os.path.join(self.d, "data/raw"))
        os.makedirs(os.path.join(self.d, "results"))
        os.makedirs(os.path.join(self.d, "plans"))
        with open(os.path.join(self.d, "data/raw/a.csv"), "w") as f:
            f.write("x,y\n1,2\n3,4\n")
        with open(os.path.join(self.d, "plans/p.md"), "w") as f:
            f.write("# plan\nH1: x raises y\n")
        # unrelated staged file must NOT be swept into the freeze commit
        with open(os.path.join(self.d, "other.txt"), "w") as f:
            f.write("unrelated\n")
        git(self.d, "add", "other.txt")

    def tearDown(self):
        self.tmp.cleanup()

    def prereg(self, *a):
        return run(sys.executable, "-I", self.PREREG, *a, cwd=self.d)

    def freeze(self):
        return self.prereg("freeze", "plans/p.md", "--data", "data/raw", "--outputs", "results")

    def audit(self):
        return self.prereg("audit", "plans/p.md", "--data", "data/raw", "--outputs", "results")

    def test_freeze_then_audit_passes_and_commits_only_plan(self):
        r = self.freeze()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        files = git(self.d, "show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(sorted(files), ["plans/p.md", "plans/p.md.checksums.json"])
        self.assertIn("prereg-freeze: plans/p.md", git(self.d, "log", "-1", "--format=%s"))
        a = self.audit()
        self.assertEqual(a.returncode, 0, a.stdout + a.stderr)

    def test_refuses_to_freeze_when_outputs_exist(self):
        with open(os.path.join(self.d, "results/r.txt"), "w") as f:
            f.write("p=0.03\n")
        r = self.freeze()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("output files already exist", r.stderr)

    def test_gitkeep_in_outputs_is_ignored(self):
        open(os.path.join(self.d, "results/.gitkeep"), "w").close()
        self.assertEqual(self.freeze().returncode, 0)

    def test_cannot_freeze_twice(self):
        self.assertEqual(self.freeze().returncode, 0)
        r = self.freeze()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already has commits", r.stderr)

    def test_audit_fails_after_plan_edit(self):
        self.freeze()
        with open(os.path.join(self.d, "plans/p.md"), "a") as f:
            f.write("H1 reworded after seeing results\n")
        self.assertNotEqual(self.audit().returncode, 0)  # uncommitted edit
        git(self.d, "commit", "-aq", "-m", "tweak plan")
        a = self.audit()
        self.assertNotEqual(a.returncode, 0)
        self.assertIn("edited after the freeze", a.stdout)

    def test_audit_fails_when_data_changes(self):
        self.freeze()
        with open(os.path.join(self.d, "data/raw/a.csv"), "a") as f:
            f.write("5,6\n")
        a = self.audit()
        self.assertNotEqual(a.returncode, 0)
        self.assertIn("CHANGED", a.stdout)

    def test_audit_notes_added_data_but_passes(self):
        self.freeze()
        with open(os.path.join(self.d, "data/raw/b.csv"), "w") as f:
            f.write("x\n1\n")
        a = self.audit()
        self.assertEqual(a.returncode, 0)
        self.assertIn("added after freeze", a.stdout)

    def test_output_committed_before_freeze_is_caught(self):
        # plan committed ordinarily (not via freeze) AFTER an output exists
        with open(os.path.join(self.d, "results/r.txt"), "w") as f:
            f.write("effect=0.4\n")
        git(self.d, "add", "results/r.txt")
        git(self.d, "commit", "-qm", "results first")
        git(self.d, "add", "plans/p.md")
        git(self.d, "commit", "-qm", "prereg-freeze: plans/p.md")
        a = self.audit()
        self.assertNotEqual(a.returncode, 0)
        self.assertIn("output committed at or before freeze", a.stdout)

    def test_output_committed_after_freeze_is_fine(self):
        self.freeze()
        with open(os.path.join(self.d, "results/r.txt"), "w") as f:
            f.write("effect=0.4\n")
        git(self.d, "add", "results/r.txt")
        git(self.d, "commit", "-qm", "results")
        self.assertEqual(self.audit().returncode, 0)

    def test_plain_commit_is_not_a_freeze(self):
        git(self.d, "add", "plans/p.md")
        git(self.d, "commit", "-qm", "add plan")
        a = self.audit()
        self.assertNotEqual(a.returncode, 0)
        self.assertIn("not a 'prereg-freeze: ' commit", a.stdout)

    def test_outside_git_repo_errors_cleanly(self):
        with tempfile.TemporaryDirectory() as nogit:
            open(os.path.join(nogit, "p.md"), "w").write("x")
            r = run(sys.executable, "-I", self.PREREG, "freeze", "p.md", cwd=nogit)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("not inside a git repository", r.stderr)


class ManifestTests(unittest.TestCase):
    M = os.path.join(S, "data-intake", "scripts", "manifest.py")

    def test_manifest_roundtrip_and_verify(self):
        with tempfile.TemporaryDirectory() as d:
            raw = os.path.join(d, "raw")
            os.makedirs(raw)
            p = os.path.join(raw, "a.csv")
            open(p, "w").write("a,b\n1,2\n3,4\n5,6\n")
            open(os.path.join(raw, ".gitkeep"), "w").close()
            out = os.path.join(d, "m.json")
            r = run(sys.executable, "-I", self.M, raw, "-o", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            m = json.load(open(out))["files"]
            self.assertEqual(len(m), 1)  # .gitkeep skipped
            entry = next(iter(m.values()))
            self.assertEqual(entry["rows"], 3)
            self.assertEqual(entry["header"], ["a", "b"])
            self.assertEqual(len(entry["sha256"]), 64)
            self.assertEqual(run(sys.executable, "-I", self.M, raw, "--verify", out).returncode, 0)
            open(p, "a").write("7,8\n")
            v = run(sys.executable, "-I", self.M, raw, "--verify", out)
            self.assertEqual(v.returncode, 1)
            self.assertIn("CHANGED", v.stdout)
            open(os.path.join(raw, "new.csv"), "w").write("x\n1\n")
            v = run(sys.executable, "-I", self.M, raw, "--verify", out)
            self.assertIn("ADDED", v.stdout)


class DoiTests(unittest.TestCase):
    def test_extraction(self):
        m = load("check_dois", "source-verification/scripts/check_dois.py")
        text = (
            "Smith 2020, doi:10.1038/nature12373. Also (https://doi.org/10.1126/science.1260419). "
            "Dup 10.1038/NATURE12373; bad 10.12/short. Bib: doi = {10.1371/journal.pmed.0020124},"
        )
        got = m.extract_dois(text)
        self.assertIn("10.1038/nature12373", got)
        self.assertIn("10.1126/science.1260419", got)
        self.assertIn("10.1371/journal.pmed.0020124", got)
        self.assertEqual(len(got), 3)  # case-insensitive dedupe; "10.12/short" rejected

    def test_offline_mode_makes_no_network_calls(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "r.txt")
            open(f, "w").write("10.1038/nature12373")
            r = run(sys.executable, "-I", os.path.join(S, "source-verification/scripts/check_dois.py"), f, "--offline")
            self.assertEqual(r.returncode, 0)
            self.assertIn("EXTRACTED", r.stdout)

    def test_unreachable_network_is_unchecked_not_pass(self):
        m = load("check_dois2", "source-verification/scripts/check_dois.py")
        import urllib.request

        def boom(*a, **k):
            raise OSError("network blocked")

        orig = urllib.request.urlopen
        urllib.request.urlopen = boom
        try:
            status, info = m.lookup("10.1038/nature12373")
        finally:
            urllib.request.urlopen = orig
        self.assertEqual(status, "UNCHECKED")


class RetractionTests(unittest.TestCase):
    def test_detects_retraction_notice(self):
        m = load("check_dois3", "source-verification/scripts/check_dois.py")
        self.assertTrue(m.is_retraction([{"type": "retraction", "DOI": "10.1/x"}]))
        self.assertTrue(m.is_retraction([{"type": "Withdrawal"}]))
        self.assertFalse(m.is_retraction([{"type": "correction"}]))
        self.assertFalse(m.is_retraction([]))

    def test_retracted_doi_fails_exit_code(self):
        m = load("check_dois4", "source-verification/scripts/check_dois.py")
        info = {"title": "T", "year": 2020, "journal": "J", "type": "journal-article", "authors": "A",
                "update_notices": [{"type": "retraction"}]}
        m.lookup = lambda doi, **k: ("RESOLVED", info)
        self.assertEqual(m.main(["--doi", "10.1038/nature12373"]), 1)


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            sh = os.path.join(S, "setup-science-skills", "scripts", "scaffold.sh")
            for _ in range(2):
                r = run("bash", sh, "docs/science", "data/raw", "results", cwd=d)
                self.assertEqual(r.returncode, 0, r.stderr)
            for sub in ("questions", "preregistrations", "reviews", "reports", "sources", "data", "surveys", "deviations"):
                self.assertTrue(os.path.isdir(os.path.join(d, "docs/science", sub)), sub)
            self.assertTrue(os.path.isdir(os.path.join(d, "data/raw")))
            self.assertTrue(os.path.isdir(os.path.join(d, "docs/science/retro")))
            log = os.path.join(d, "docs/science/LOG.md")
            self.assertIn("Append only", open(log).read())
            open(log, "a").write("entry\n")
            run("bash", sh, "docs/science", "data/raw", "results", cwd=d)
            self.assertIn("entry", open(log).read())  # re-running never clobbers the log


class CaptureEnvTests(unittest.TestCase):
    def test_capture(self):
        script = os.path.join(S, "reproducible-compute", "scripts", "capture_env.py")
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q")
            git(d, "config", "user.email", "t@example.com")
            git(d, "config", "user.name", "t")
            open(os.path.join(d, "a.txt"), "w").write("a")
            git(d, "add", "a.txt")
            git(d, "commit", "-qm", "init")
            out = os.path.join(d, "prov.json")
            r = run(sys.executable, "-I", script, "-o", out, "--seed", "42", "--cmd", "python run.py", cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            p = json.load(open(out))
            self.assertEqual(p["seed"], 42)
            self.assertEqual(p["command"], "python run.py")
            self.assertEqual(len(p["git"]["commit"]), 40)
            self.assertIn("python", p)
            self.assertFalse(p["git"]["dirty"])  # prov.json itself is untracked; tracked tree is clean
            open(os.path.join(d, "a.txt"), "w").write("changed")
            r = run(sys.executable, "-I", script, "-o", out, cwd=d)
            self.assertTrue(json.load(open(out))["git"]["dirty"])


if __name__ == "__main__":
    unittest.main()


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.v = load_tool("validate", "validate.py")

    def test_repository_is_valid(self):
        problems = self.v.validate(S, os.path.join(ROOT, "agents"), os.path.join(ROOT, "commands"))
        self.assertEqual(problems, [])

    def _mk(self, d, name, fm_name=None, body="body", desc="a description"):
        os.makedirs(os.path.join(d, name))
        with open(os.path.join(d, name, "SKILL.md"), "w") as fh:
            fh.write(f"---\nname: {fm_name or name}\ndescription: {desc}\n---\n{body}\n")

    def test_catches_name_mismatch_and_bad_names(self):
        with tempfile.TemporaryDirectory() as d:
            self._mk(d, "good-one", fm_name="other")
            self._mk(d, "Bad_Name")
            out = "\n".join(self.v.validate(d, None))
            self.assertIn("!= directory name", out)
            self.assertIn("invalid name", out)

    def test_catches_long_description_and_missing_command_and_script(self):
        with tempfile.TemporaryDirectory() as d:
            self._mk(d, "a-skill", desc="x" * 1025)
            self._mk(d, "b-skill", body="run `/nope` and <skill-dir>/scripts/ghost.py")
            out = "\n".join(self.v.validate(d, None, os.path.join(d, "none")))
            self.assertIn("not 1-1024", out)
            self.assertIn("commands/nope.md does not exist", out)
            self.assertIn("missing script b-skill/scripts/ghost.py", out)

    def test_agent_shell_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            sk, ag = os.path.join(d, "s"), os.path.join(d, "a")
            os.makedirs(sk); os.makedirs(ag)
            with open(os.path.join(ag, "r.md"), "w") as fh:
                fh.write("---\ndescription: x\nmode: subagent\npermission:\n  shell:\n    \"*\": ask\n---\nbody\n")
            self.assertIn("use `bash`", "\n".join(self.v.validate(sk, ag)))


class InstallTests(unittest.TestCase):
    def test_install_copies_skills_agents_commands_and_skips_existing(self):
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, "proj", ".opencode", "skills")
            r = run("bash", os.path.join(ROOT, "install.sh"), "--dest", dest)
            self.assertEqual(r.returncode, 0, r.stderr)
            base = os.path.join(d, "proj", ".opencode")
            self.assertTrue(os.path.isfile(os.path.join(dest, "red-team", "SKILL.md")))
            self.assertTrue(os.path.isfile(os.path.join(dest, "preregister", "scripts", "prereg.py")))
            self.assertTrue(os.path.isfile(os.path.join(base, "agents", "science-reviewer.md")))
            self.assertTrue(os.path.isfile(os.path.join(base, "commands", "red-team.md")))
            r2 = run("bash", os.path.join(ROOT, "install.sh"), "--dest", dest)
            self.assertEqual(r2.returncode, 0)
            self.assertIn("skip (exists)", r2.stderr)
