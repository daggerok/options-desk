# Options Desk [![CI](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml/badge.svg)](https://github.com/daggerok/options-desk/actions/workflows/ci.yaml)
TODO

---

## 🚀 Features & Architecture
TODO

---

## 🛠️ Tech Stack

* **Runtime:** and **Build Tool:** [Bun](https://bun.sh/)
* **Frontend Library:** React (TypeScript: TSX)
* **Styling Framework:** TailwindCSS v4 (Utility-first, fully embedded optimized SVGs)

---

## 📦 Getting Started

### Prerequisites
Ensure you have [Bun](https://bun.sh/) installed locally on your development machine.

### Installation & Local Run

1. Clone the repository and navigate to the root directory:
   ```bash
   git clone https://github.com/daggerok/options-desk.git && cd $_
   ```

2. Install the necessary development dependencies:
   ```bash
   bun install -E
   ```

3. Launch the local Vite development server with Hot Module Replacement (HMR):
   ```bash
   bun serve
   ```

4. Upgrade all ecosystem packages to their latest absolute versions:
   ```bash
   bunx npm-check-updates -u
   ```

## 📖 Production Deployment & Standalone Build

Since the entire system compiles into a self-contained Single Page Application (SPA) without requiring any heavy node
backend or cloud infrastructure, you can generate a static deployment bundle:

```bash
bun run build && bunx serve ./dist
```

The resulting optimized assets will be located inside the `./dist` folder, ready to be served from any static hosting
architecture or local offline workspace.
