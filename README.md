# HFSS Codex Bingo

A reusable Codex skill for interpreting Visio layouts, antenna papers, marked screenshots, existing AEDT projects, and a user's modeling instructions—then building, auditing, simulating, and reporting an HFSS antenna model within that scope.

面向 **Visio + 论文 + 对话 → HFSS建模复现** 的通用技能。每个项目的结构、目标、频段和修改权限由该项目的用户材料决定。

## Capabilities / 可以做什么

- **Interpret intent:** select the intended prototype, resolve source authority, distinguish copper from slots, and understand local replacement or movement requests.
- **Build and audit:** parameterize real geometry, check dimensions and layer heights, and verify electrical continuity, feed contacts, clearances, and port assignments.
- **Use the right port:** support single-ended coax/probe S11 and differential Terminal mixed-mode Sdd/Scc without imposing one feed type on every antenna.
- **Evaluate RF results:** inspect actual convergence, requested-direction realized gain, efficiency, power balance, radiation nulls, and paper simulation versus measurement.
- **Deliver native evidence:** export HFSS plots and CSV, orthographic/layer views, multiple 3D camera views, and verified project/results pairs.
- **Continue work:** use project-local handoff records to recover progress and avoid duplicate solves.

This is an agent skill and a set of helper scripts, not a universal one-command antenna generator. It does not supply HFSS, a license, unpublished paper details, or access to conversations that were not provided. Successful geometry construction does not guarantee full electromagnetic reproduction.

## Requirements / 环境要求

- Windows for native HFSS automation.
- A licensed Ansys Electronics Desktop / HFSS installation. Native automation has primarily been verified with **HFSS 2021 R1**; check APIs before using another version.
- Python 3.10+ and `pywin32` for COM automation. Read-only CSV, delivery, and Visio inspection helpers use the Python standard library.
- Codex with local skill loading and appropriate access to the project files and application.

## Install / 安装

Clone the repository into your own skills directory in PowerShell:

```powershell
git clone https://github.com/kongkongya367-glitch/hfss-codex-bingo.git "$env:USERPROFILE\.codex\skills\hfss-codex-bingo"
python -m pip install -r "$env:USERPROFILE\.codex\skills\hfss-codex-bingo\requirements.txt"
```

If you have configured a different Codex skills directory, use that location. Alternatively, download the repository ZIP and extract its contents into a folder named `hfss-codex-bingo` under your skills directory. `SKILL.md` should be immediately inside that folder.

Do not clone over an existing installation with local changes; review or back it up first.

## Use / 使用

Attach or provide accessible paths to the Visio, paper, screenshot, or AEDT project. State the selected structure and what you want done:

```text
使用 $hfss-codex-bingo，结合这份Visio、论文和我们的对话，复现我指定的结构。
先确认尺寸来源、物理层、开槽和馈电方式；未公开的细节请列为假设。
本轮先完成建模和尺寸核对，不启动仿真。
```

When simulation is wanted, specify it along with the frequency range, observables, and physical direction as needed. Requirements already established in the current conversation do not need to be restated at every step.

```text
使用 $hfss-codex-bingo，在这个已核对工程的独立副本中进行仿真。
输出原生S参数、指定方向的实现总增益和效率，并分别与论文模拟和实测数据比较。
```

The skill uses accessible conversation context and source files. Project-local `HFSS_RESUME.md`, `HFSS_TASK_STATE.json`, and `HFSS_TARGET_PLAN.md`, when present, preserve that project's continuation context; installing this repository does not import anyone else's conversation or project history.

See the [Chinese usage guide](references/user-guide.md), [quick start](references/quick-start-zh.md), and [skill instructions](SKILL.md).

## Included helpers

| Script | Purpose |
|---|---|
| `scripts/check_environment.py` | Inspect prerequisites; optional COM check is explicit. |
| `scripts/inspect_vsdx.py` | Extract Visio shape, transform, geometry, and media metadata. |
| `scripts/native_sdd11_report.py` | Create/export a native mixed-mode Sdd report in an authorized working project; this helper saves that project. |
| `scripts/verify_native_frequency_csv.py` | Check native quantities, units, frequency grids, finite values, and supplied fixed-angle columns. |
| `scripts/verify_delivery.py` | Check packaged project/results and figure files. |
| `scripts/verify_task_checkpoint.py` | Check supported schema-1 continuation records on disk. |

Use each helper's `--help`. File checks do not establish native solver convergence, source phases, or far-field coordinate provenance. Native model/report operations require the correct live application and full project path.

## Development

```text
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

CI checks portable data validation and repository structure. It does not run licensed HFSS, certify other HFSS versions, or validate a particular antenna design. Contributions should contain reusable instructions, code, or synthetic test inputs; keep personal projects, credentials, proprietary papers, and simulation results outside the repository.

## License

MIT. See [LICENSE](LICENSE). The license covers this repository's content, not Ansys software, third-party papers, or their trademarks. This project is not an official Ansys product.
