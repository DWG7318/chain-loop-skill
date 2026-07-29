# Post-Merge GitHub Rename and 2.3.1 Tag

1. Merge `agent/clk-2.3.1` into `main` in the repository whose immutable database
   ID is `1298120736`.
2. Rename `DWG7318/multi-small-loop-skill` to the canonical
   `DWG7318/chain-loop-skill` if the legacy name is still active.
3. Confirm repository ID remains `1298120736`, default branch is `main`, old URL
   redirects, and remote HEAD is the verified merge commit.
4. Update the local remote to `https://github.com/DWG7318/chain-loop-skill.git`.
5. Run the complete repository, plan, runtime, Receipt-chain, and pytest gates on
   the merged `main` checkout.
6. Create and push annotated tag `v2.3.1` only from that verified `main` commit.
7. Reinstall the Codex skill under `chain-loop-skill/`; a GitHub URL redirect does
   not rename or update local installations.
