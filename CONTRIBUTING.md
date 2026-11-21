# Contributing to FlowPDF

Thank you for your interest in contributing to **FlowPDF**! 🎉

FlowPDF is an open-source report generation library made in the Dominican Republic 🇩🇴, and contributions from anywhere are welcome.

We welcome contributions from the community, whether it's fixing bugs, improving documentation, adding new components to the document engine, or building SDK client libraries in other programming languages.

---

## 🛠️ Development Setup

1. **Fork & Clone:**
   ```bash
   git clone https://github.com/<your-username>/flowpdf.git
   cd flowpdf
   ```

2. **Environment & Dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements/base.txt
   pip install -r requirements/development.txt
   ```

3. **Run Automated Tests:**
   ```bash
   pytest
   ```

4. **Run via Docker:**
   ```bash
   docker compose up --build -d
   ```

---

## 📐 Architecture Rules

1. **Keep the Engine Decoupled:**
   - Any code under `engine/` MUST NOT import Django models, views, or settings. It must remain a pure, standalone Python library.
2. **Deterministic Layout Protocol:**
   - Components implement `measure(constraints, context)` and `draw(rect, context)`.
   - Never rely on hardcoded coordinates when implementing responsive layouts.
3. **Security First:**
   - No `eval()`, `exec()`, or dynamic module loading in templates.
   - All file and asset paths must pass through path traversal guards (`validate_safe_path`).

---

## 🧪 Testing Guidelines

- Every new component must have a corresponding unit test in `tests/unit/`.
- API endpoints require integration tests in `tests/integration/`.
- Ensure all 33+ tests pass cleanly before submitting your PR.

---

## 📜 Pull Request Process

1. Create a feature branch (`git checkout -b feature/awesome-component`).
2. Commit your changes with clear, semantic commit messages.
3. Ensure CI tests pass.
4. Open a Pull Request against `main` explaining your changes and motivation.
