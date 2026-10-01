package proceduretemplate

// Template harness for ca-skills#7 acceptance. It compiles the composed
// ca-skills 5gc-file-transfer package with a resolver, then asks the real
// Artifact ProcedureTemplate compiler to freeze each Procedure. It demonstrates
// that a composed `for` body (a sub-graph, not a single action) is rejected on
// the production Artifact build path. Not part of the Toolchain repository;
// injected with `go test -overlay`.

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/odango-chan/ca-skill-toolchain/backend/internal/compiler"
	"github.com/odango-chan/ca-skill-toolchain/backend/internal/registry"
	"github.com/odango-chan/ca-skill-toolchain/backend/internal/schemas"
	"github.com/odango-chan/ca-skill-toolchain/embedassets"
)

func TestPrereq7TemplateHarness(t *testing.T) {
	root := os.Getenv("CA_SKILLS_ROOT")
	if root == "" {
		t.Skip("CA_SKILLS_ROOT required")
	}
	core, err := schemas.LoadSetFS(embedassets.FS, "schemas/v1alpha1")
	if err != nil {
		t.Fatal(err)
	}
	snap, err := registry.Load("../../../registry", core)
	if err != nil {
		t.Fatal(err)
	}
	resolver := func(ref string) (map[string][]byte, bool) {
		files := walkSkillFiles(filepath.Join(root, "skills", ref))
		if files == nil {
			return nil, false
		}
		return files, true
	}
	result, err := compiler.Compile(filepath.Join(root, "skills", "5gc-file-transfer"), compiler.Options{
		Core: core, SchemaDigest: "", Registry: snap,
		ReportID: "00000000-0000-0000-0000-0000000000c7",
		RunID:    "00000000-0000-0000-0000-0000000000d7",
		WorkspaceRevision: 1, MaxFiles: 256, MaxFileBytes: 1 << 20, MaxPackageBytes: 10 << 20,
		DependencyResolver: resolver,
	})
	if err != nil {
		t.Fatalf("compile: %v", err)
	}
	if result.Package.ProcedureSet == nil {
		t.Fatal("no procedure set")
	}
	for i := range result.Package.ProcedureSet.Spec.Procedures {
		proc := &result.Package.ProcedureSet.Spec.Procedures[i]
		// Nil Tool/Script resolvers are irrelevant here: the loop-body kind
		// check runs before tool resolution.
		_, err := Compile(Options{
			Procedure:  proc,
			Digest:     ProcedureDigest(proc),
			MaxActions: result.Package.Contract.Spec.Planning.MaxActions,
		})
		if err != nil {
			t.Logf("TEMPLATE procedure=%s ERROR=%v", proc.Name, err)
		} else {
			t.Logf("TEMPLATE procedure=%s OK", proc.Name)
		}
	}
}

func walkSkillFiles(dir string) map[string][]byte {
	out := map[string][]byte{}
	err := filepath.WalkDir(dir, func(p string, d os.DirEntry, err error) error {
		if err != nil || d.IsDir() {
			return err
		}
		rel, _ := filepath.Rel(dir, p)
		b, e := os.ReadFile(p)
		if e != nil {
			return e
		}
		out[filepath.ToSlash(rel)] = b
		return nil
	})
	if err != nil {
		return nil
	}
	return out
}
