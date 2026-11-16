# Neo autonomous training operations

Lifecycle extension for the existing Neo Vast.ai / A1 SSH infrastructure. No model, objective, corpus, checkpoint or historical result was changed. No paid instance is launched during installation or tests.

## Launch

Prepare the already bundled contrastive experiment, without training or rental:

```bash
cd /home/dani.pp/research/neo-architecture-recovery/neo-f2-corpus-release-v1/neo-training-operations
python3 prepare.py --output private/job.json
```

Fill `authorization_reference` with the actual job-specific user authorization and choose `offer_id` within the explicit price/runtime/transfer envelope. Null authorization/offer defaults are intentionally not runnable. The wrapper queries the live offer and existing credit again. It does not buy credit or choose replacement hosts. Adjusting operational budget is not authorization to change the scientific protocol.

**Single supervised launch command:**

```bash
python3 operations.py launch private/job.json
```

The command installs/enables a per-job systemd user service, with absolute paths, `Restart=on-failure`, persistent private state and `UMask=0077`. The existing user manager has `Linger=yes`. Closing Codex or the terminal does not terminate that service. A workstation reboot restarts it; a recorded create attempt is reconciled by unique label and never repeated. There are no automatic scientific retries or replacement rentals.

The service first checks credentials, Torch interpreter, frozen bundle, approved configuration, credit, live GPU/storage/transfer price and storage write/readback. It publishes a minimal plan to the authorized research branch, waits for GitHub Actions to authenticate to Vast and publish a matching SHA-256 armed receipt, **then** calls the existing Vast CLI create/SSH helpers. Failure to arm prevents rental. The existing scientific CUDA contracts run before the original training command.

## Storage and recovery

Private durable destination: **`pa-drive:NEO-Research-Archives-v1/<unique-job-id>/`** using the existing working rclone credential. `pa-drive-owned` is expired and is not used. The retired shared connection is not used. Provider/Drive credentials remain on this workstation; only a Vast API key is stored as a GitHub Actions secret. No storage credentials are transferred to the GPU or committed.

SCP recovery hashes are checked against remote SHA-256. Each uploaded tar is content addressed and verified by downloading and streaming SHA-256 over the actual bytes. Complete configurations, exit receipts, stdout/stderr, metrics, checkpoint payloads (including optimizer/RNG/cursor when supplied by the experiment), scientific CPU verification, upload status and cleanup status are recorded separately. A checkpoint verifier failure does not prevent recovering its bytes as evidence.

Rolling operational snapshots keep the latest verified cloud snapshot; an older operational snapshot is deleted **only after** its replacement verifies. Original local/remote scientific checkpoints and final archives are never overwritten or pruned. Final archives are immutable. Missing/corrupt outputs are not called successful training. Upload retries are bounded (three artifact attempts with exponential backoff; one final manifest attempt after cleanup). A failed upload keeps the local recovered tar and manifest; it cannot delay deletion indefinitely.

Local manifests: `private/<job-id>/manifest.json`. Restore with the local tar or `rclone copyto` from the manifest's `archive.uri`, then check SHA-256. To recover a supervisor after a crash, restart its existing systemd unit; do not generate a new job ID or rerent. The remote wrapper prevents duplicate training, records the actual child return code, handles SIGTERM/SIGINT/timeout, and refuses to infer success when an old wrapper disappeared without a receipt. `attach_only` refuses an unwrapped legacy process rather than restarting it or inventing an exit code. There was no live job to attach during deployment.

## Independent shutdown

1. GPU-local detached worker with a training soft deadline.
2. Workstation systemd lifecycle `finally` teardown, plus an enabled persistent one-minute fallback timer.
3. **GitHub-hosted external watchdog**, independent of both the GPU and workstation: read-only credential preflight, armed receipt artifact, exact unique job label/optional instance-ID ownership check, absolute deadline, destroy then API absence verification. It never deletes unrelated instances or volumes. These jobs create no volumes. A fresh job is refused when unexpected volumes exist.

The watchdog workflow runs on a push to the designated research branch, so no merge into `main` or default-branch workflow dispatch is required. See [GitHub push event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push). Only a non-sensitive plan and automation are published; checkpoint archives remain private. The public repository's hosted runner is used, not Vast GPU compute. The watchdog has a four-hour supported maximum plus a bounded verification interval; jobs exceeding that are rejected.

No software watchdog can guarantee successful deletion while the provider API is persistently unavailable. Such a case is explicitly `shutdown_attempted_unconfirmed`, not success. GitHub cancellation/outage and provider outage are residual risks; the local persistent guard is a separate fallback. A workstation power outage may prevent the most recent recovery transfer; previously verified cloud snapshots survive and the GitHub deadline still enforces cleanup. Artifacts inaccessible on a failed GPU cannot be invented. No job is marked archived until readback verifies.

## Inspect / stop

```bash
journalctl --user -u neo-training-<job-id> -f
systemctl --user status neo-deadline-guard.timer
systemctl --user stop neo-training-<job-id>.service
gh run list -R PapLion/Akemi --branch neo-contextual-causal-diagnosis-v1 --workflow neo-watchdog.yml
python3 -m unittest discover -s tests -v
```

Stopping the service signals recovery/finalization; the independent cloud deadline remains active. Do not cancel a live GitHub watchdog before API-confirmed cleanup.

## Deployment evidence

`results/tests.log`: success/failure, interruption, timeout, upload failure, corrupt upload, missing credentials/authorization, wrong ownership, deletion failure, repeat finalization, repeat worker start and launcher disconnect. Destructive operations use a fake provider.

`results/storage-service-test.json`: real detached systemd dummy execution, Drive upload and SHA-256 readback; provider strictly mocked. This is an operational test, not an ML checkpoint or training result.

`results/deployment.json`: actual local service/timer, external workflow read-only probe, publication and zero-resource receipts. **Configured is distinct from armed**: there is no paid job and no armed paid-job watchdog at delivery. Each future launch must obtain a fresh authenticated external receipt before renting.
