package compiler

// Resolver harness for ca-skills#7 acceptance. It is NOT part of the Toolchain
// repository; it is injected with `go test -overlay` so the Toolchain checkout
// stays untouched. It exercises the real compiler COMPOSITION_RESOLVE phase on
// the shipped ca-skills 5gc-file-transfer package with a filesystem-backed
// DependencyResolver that re-hashes each declared dependency from the frozen
// sibling source package, exactly as a production resolver is required to.

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/odango-chan/ca-skill-toolchain/backend/internal/registry"
)

func TestPrereq7Harness(t *testing.T) {
	skillsRoot := os.Getenv("CA_SKILLS_ROOT")
	if skillsRoot == "" {
		t.Skip("CA_SKILLS_ROOT required")
	}
	core := testCore(t)
	snap, err := registry.Load("../../../registry", core)
	if err != nil {
		t.Fatalf("registry: %v", err)
	}
	resolver := func(ref string) (map[string][]byte, bool) {
		dir := filepath.Join(skillsRoot, "skills", ref)
		files, finding, err := discover(dir, 256, 1<<20, 10<<20)
		if err != nil || finding != nil {
			return nil, false
		}
		return files, true
	}
	pkgDir := os.Getenv("PREREQ7_PKG")
	if pkgDir == "" {
		pkgDir = filepath.Join(skillsRoot, "skills", "5gc-file-transfer")
	}
	result, err := Compile(pkgDir, Options{
		Core:               core,
		SchemaDigest:       schemaDigestOf(core),
		Registry:           snap,
		ReportID:           "00000000-0000-0000-0000-0000000000a7",
		RunID:              "00000000-0000-0000-0000-0000000000b7",
		WorkspaceRevision:  1,
		MaxFiles:           256,
		MaxFileBytes:       1 << 20,
		MaxPackageBytes:    10 << 20,
		DependencyResolver: resolver,
	})
	if err != nil {
		t.Fatalf("compile: %v", err)
	}
	out, _ := json.MarshalIndent(result.Report, "", "  ")
	t.Logf("STATUS=%s\n%s", result.Report.Status, string(out))
	if os.Getenv("PREREQ7_DUMP") != "" && result.Package != nil && result.Package.ProcedureSet != nil {
		for _, p := range result.Package.ProcedureSet.Spec.Procedures {
			t.Logf("PROCEDURE %s entry=%s", p.Name, p.Entry)
			for i := range p.Nodes {
				t.Logf("  node %s type=%s", p.Nodes[i].ID, p.Nodes[i].Type)
			}
		}
	}
}
