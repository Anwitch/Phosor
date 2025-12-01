# Phosor – Documentation Index

**Photo Sorting Orchestrator for Faces**

---

## Documentation Structure

This project has been reorganized into focused documents:

### 1. **PHOSOR_SPEC.md** – Project Specification
**For:** External stakeholders, documentation, reports  
**Contains:**
- Feature overview
- Architecture & technology stack
- API endpoint reference (13 endpoints)
- Configuration guide
- Data models
- Deployment instructions

→ **[Read PHOSOR_SPEC.md](./PHOSOR_SPEC.md)**

---

### 2. **AGENT_STEPS.md** – AI Agent Instructions
**For:** AI agents working on NEW features  
**Contains:**
- Work rules & restrictions
- File scope boundaries (what's frozen, what's allowed)
- Future work tasks (Phase 12+)
- Session scope guidelines
- Version control info

→ **[Read AGENT_STEPS.md](./AGENT_STEPS.md)**

⚠️ **IMPORTANT:** All Phase 1-11 tasks are **COMPLETED**. Do not repeat them.

---

### 3. **DEVLOG.md** – Development History
**For:** Developers, debugging, learning from past issues  
**Contains:**
- Bug history with root causes & fixes
- Date-stamped changes
- Performance optimizations
- Architecture decisions
- Testing results
- Lessons learned

→ **[Read DEVLOG.md](./DEVLOG.md)**

---

## Quick Start

### For Users
```bash
# Scan photos
phosor scan --input-dir /photos --output-dir /output

# Start web dashboard
phosor serve --reload
```

### For Developers
1. Read **PHOSOR_SPEC.md** for architecture overview
2. Check **AGENT_STEPS.md** for available tasks
3. Consult **DEVLOG.md** when debugging

### For AI Agents
1. **MUST READ:** AGENT_STEPS.md (work restrictions)
2. **Reference:** PHOSOR_SPEC.md (API docs)
3. **DO NOT READ:** DEVLOG.md (historical context only)

---

## Project Status

**Version:** 1.0.0  
**Release Date:** December 1, 2025  
**Status:** Production-ready

**Completed:**
- ✅ CLI pipeline (Phases 1-10)
- ✅ Web dashboard (Phase 11)
- ✅ All MVP features
- ✅ 19/19 tests passing

**Pending:**
- Phase 12+ (Future enhancements in AGENT_STEPS.md)

---

## File Organization

```
Phosor/
├── PHOSOR_SPEC.md          # Specification (for reports/docs)
├── AGENT_STEPS.md          # AI agent instructions
├── DEVLOG.md               # Bug history & changes
├── Agent_Guide.md          # This index file
│
├── src/
│   ├── core/               # CLI pipeline (FROZEN)
│   └── frontend/           # Web dashboard (FROZEN)
│
├── configs/
│   └── config.toml         # Configuration
│
├── tests/                  # Unit tests
└── pyproject.toml          # Dependencies
```

---

## Why This Structure?

### Problem with Old Agent_Guide.md:
- ❌ Mixed specification + history + instructions
- ❌ Status inconsistencies (PLANNED vs COMPLETED)
- ❌ Hard to find relevant info
- ❌ Confusing for both humans and AI agents

### Benefits of New Structure:
- ✅ Clear separation of concerns
- ✅ Easy to find what you need
- ✅ Prevents agent confusion
- ✅ Better for version control
- ✅ Professional documentation

---

## Contributing

When working on new features:

1. **Check AGENT_STEPS.md** for available tasks
2. **Follow file scope restrictions** (FROZEN vs ALLOWED)
3. **Update DEVLOG.md** when fixing bugs
4. **Update PHOSOR_SPEC.md** when adding features
5. **Update AGENT_STEPS.md** when completing tasks

---

## License

[Add license information]

---

*Last Updated: December 1, 2025*

